import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from database import SessionLocal, ExchangeAccount, Strategy, Trade, MarketData
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class ExchangeManager:
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
    
    def get_exchange(self, exchange_account: ExchangeAccount) -> ccxt.Exchange:
        """Get exchange instance for a user's exchange account"""
        key = f"{exchange_account.id}_{exchange_account.exchange_name}"
        
        if key not in self.exchanges:
            exchange_class = getattr(ccxt, exchange_account.exchange_name.lower())
            
            config = {
                'apiKey': exchange_account.api_key,  # TODO: decrypt
                'secret': exchange_account.api_secret,  # TODO: decrypt
                'sandbox': exchange_account.is_testnet,
                'enableRateLimit': True,
            }
            
            # Add passphrase for OKEx
            if exchange_account.exchange_name.lower() == 'okex' and exchange_account.api_passphrase:
                config['password'] = exchange_account.api_passphrase  # TODO: decrypt
            
            self.exchanges[key] = exchange_class(config)
        
        return self.exchanges[key]
    
    async def get_balance(self, exchange_account: ExchangeAccount) -> Dict:
        """Get account balance from exchange"""
        try:
            exchange = self.get_exchange(exchange_account)
            balance = await exchange.fetch_balance()
            return balance
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise
    
    async def get_ticker(self, exchange_account: ExchangeAccount, symbol: str) -> Dict:
        """Get ticker data for a symbol"""
        try:
            exchange = self.get_exchange(exchange_account)
            ticker = await exchange.fetch_ticker(symbol)
            return ticker
        except Exception as e:
            logger.error(f"Error fetching ticker for {symbol}: {e}")
            raise
    
    async def get_ohlcv(self, exchange_account: ExchangeAccount, symbol: str, timeframe: str, limit: int = 100) -> List:
        """Get OHLCV data for a symbol"""
        try:
            exchange = self.get_exchange(exchange_account)
            ohlcv = await exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            return ohlcv
        except Exception as e:
            logger.error(f"Error fetching OHLCV for {symbol}: {e}")
            raise
    
    async def place_order(self, exchange_account: ExchangeAccount, symbol: str, order_type: str, 
                         side: str, amount: float, price: Optional[float] = None) -> Dict:
        """Place an order on the exchange"""
        try:
            exchange = self.get_exchange(exchange_account)
            
            if order_type == 'market':
                order = await exchange.create_market_order(symbol, side, amount)
            else:
                order = await exchange.create_limit_order(symbol, side, amount, price)
            
            return order
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise

class StrategyEngine:
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
    
    def calculate_bollinger_bands(self, prices: np.array, period: int = 20, deviation: float = 2.0) -> Tuple[np.array, np.array, np.array]:
        """Calculate Bollinger Bands using numpy"""
        # Calculate middle band (SMA)
        middle = np.convolve(prices, np.ones(period), 'valid') / period
        
        # Calculate standard deviation
        std_dev = np.array([np.std(prices[i:i+period]) for i in range(len(prices) - period + 1)])
        
        # Calculate upper and lower bands
        upper = middle + (std_dev * deviation)
        lower = middle - (std_dev * deviation)
        
        return upper, middle, lower
    
    def calculate_ma(self, prices: np.array, period: int = 60) -> np.array:
        """Calculate Moving Average using numpy"""
        return np.convolve(prices, np.ones(period), 'valid') / period
    
    async def check_strategy_signal(self, strategy: Strategy, db: Session) -> Optional[str]:
        """Check if strategy should generate a trading signal"""
        try:
            exchange_account = db.query(ExchangeAccount).filter(
                ExchangeAccount.id == strategy.exchange_account_id
            ).first()
            
            if not exchange_account:
                logger.error(f"Exchange account not found for strategy {strategy.id}")
                return None
            
            # Get OHLCV data
            ohlcv_data = await self.exchange_manager.get_ohlcv(
                exchange_account, 
                strategy.symbol, 
                strategy.timeframe, 
                limit=max(strategy.bb_period, strategy.ma_period) + 10
            )
            
            if len(ohlcv_data) < max(strategy.bb_period, strategy.ma_period):
                logger.warning(f"Not enough data for strategy {strategy.id}")
                return None
            
            # Convert to pandas DataFrame
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            # Calculate indicators
            prices = df['close'].values
            
            if strategy.strategy_type == '5m_boll_ma60':
                return await self._check_boll_ma_strategy(df, strategy)
            
            # Add more strategy types here
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking strategy signal: {e}")
            return None
    
    async def _check_boll_ma_strategy(self, df: pd.DataFrame, strategy: Strategy) -> Optional[str]:
        """Check Bollinger Bands + MA strategy"""
        prices = df['close'].values
        
        # Calculate indicators
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(
            prices, strategy.bb_period, strategy.bb_deviation
        )
        ma = self.calculate_ma(prices, strategy.ma_period)
        
        # Get latest values
        current_price = prices[-1]
        current_bb_upper = bb_upper[-1]
        current_bb_lower = bb_lower[-1]
        current_ma = ma[-1]
        
        # Strategy logic: Buy when price touches lower Bollinger Band and is above MA
        if current_price <= current_bb_lower and current_price > current_ma:
            return "buy"
        
        # Sell when price touches upper Bollinger Band
        elif current_price >= current_bb_upper:
            return "sell"
        
        return None
    
    async def execute_trade(self, strategy: Strategy, signal: str, db: Session) -> Optional[Trade]:
        """Execute a trade based on strategy signal"""
        try:
            exchange_account = db.query(ExchangeAccount).filter(
                ExchangeAccount.id == strategy.exchange_account_id
            ).first()
            
            if not exchange_account:
                logger.error(f"Exchange account not found for strategy {strategy.id}")
                return None
            
            # Place order
            order = await self.exchange_manager.place_order(
                exchange_account,
                strategy.symbol,
                "market",
                signal,
                strategy.entry_amount
            )
            
            # Create trade record
            trade = Trade(
                user_id=strategy.user_id,
                strategy_id=strategy.id,
                symbol=strategy.symbol,
                side=signal,
                order_type="market",
                amount=strategy.entry_amount,
                order_id=order.get('id'),
                status="pending"
            )
            
            db.add(trade)
            db.commit()
            db.refresh(trade)
            
            logger.info(f"Trade executed for strategy {strategy.id}: {signal} {strategy.entry_amount} {strategy.symbol}")
            return trade
            
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return None

# Global instances
exchange_manager = ExchangeManager()
strategy_engine = StrategyEngine(exchange_manager)
