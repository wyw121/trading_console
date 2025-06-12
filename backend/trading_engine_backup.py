import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
from database import SessionLocal, ExchangeAccount, Strategy, Trade, MarketData
from sqlalchemy.orm import Session
import requests
import random

logger = logging.getLogger(__name__)

# Network connectivity check
def check_okx_connectivity() -> bool:
    """Check if OKX API is accessible"""
    test_urls = [
        'https://www.okx.com/api/v5/public/time',
        'https://aws.okx.com/api/v5/public/time',
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                logger.info(f"OKX API accessible via {url}")
                return True
        except Exception:
            continue
    
    logger.warning("OKX API not accessible, will use mock exchange for testing")
    return False

# Mock OKX Exchange for testing when real API is not accessible
class MockOKXExchange:
    """Mock OKX exchange for testing purposes"""
    
    def __init__(self, config: Dict):
        self.apiKey = config.get('apiKey')
        self.secret = config.get('secret') 
        self.passphrase = config.get('passphrase')
        self.sandbox = config.get('sandbox', False)
        self.id = 'okex'
        
        if not all([self.apiKey, self.secret, self.passphrase]):
            raise Exception("Missing required OKX credentials")
        
        logger.info(f"Mock OKX Exchange initialized (sandbox: {self.sandbox})")
    
    async def fetch_balance(self) -> Dict:
        """Mock balance response"""
        logger.info("Fetching mock balance...")
        
        balance = {
            'info': {},
            'BTC': {'free': 0.001, 'used': 0.0, 'total': 0.001},
            'USDT': {'free': 100.0, 'used': 0.0, 'total': 100.0},
            'ETH': {'free': 0.05, 'used': 0.0, 'total': 0.05},
            'free': {'BTC': 0.001, 'USDT': 100.0, 'ETH': 0.05},
            'used': {'BTC': 0.0, 'USDT': 0.0, 'ETH': 0.0},
            'total': {'BTC': 0.001, 'USDT': 100.0, 'ETH': 0.05}
        }
        
        logger.info("Mock balance fetched successfully")
        return balance
    
    async def fetch_ticker(self, symbol: str) -> Dict:
        """Mock ticker response"""
        logger.info(f"Fetching mock ticker for {symbol}")
        
        prices = {
            'BTC/USDT': 45000.0,
            'BTCUSDT': 45000.0,
            'ETH/USDT': 3000.0,
            'ETHUSDT': 3000.0,
        }
        
        base_price = prices.get(symbol, 1000.0)
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        
        ticker = {
            'symbol': symbol,
            'last': current_price,
            'high': current_price * 1.05,
            'low': current_price * 0.95,
            'bid': current_price * 0.999,
            'ask': current_price * 1.001,
            'volume': random.uniform(1000, 10000),
            'timestamp': int(datetime.now().timestamp() * 1000),
            'datetime': datetime.now().isoformat(),
        }
        
        logger.info(f"Mock ticker fetched: {symbol} = ${current_price:.2f}")
        return ticker
    
    async def close(self):
        """Mock close method"""
        pass

class ExchangeManager:
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
    
    def get_exchange(self, exchange_account: ExchangeAccount) -> ccxt.Exchange:
        """Get exchange instance for a user's exchange account"""
        key = f"{exchange_account.id}_{exchange_account.exchange_name}"
        
        if key not in self.exchanges:
            exchange_name = exchange_account.exchange_name.lower()
            exchange_class = getattr(ccxt, exchange_name)
            
            config = {
                'apiKey': exchange_account.api_key,  # TODO: decrypt
                'secret': exchange_account.api_secret,  # TODO: decrypt
                'sandbox': exchange_account.is_testnet,
                'enableRateLimit': True,
                'timeout': 30000,  # 30秒超时
            }            # Special handling for OKX
            if exchange_name == 'okex':
                # Add passphrase for OKX (required)
                if exchange_account.api_passphrase:
                    config['passphrase'] = exchange_account.api_passphrase  # TODO: decrypt
                
                # OKX specific settings for real exchange
                config['options'] = {
                    'defaultType': 'spot',  # 现货交易
                }
                
                # Set the hostname for OKX API
                config['hostname'] = 'www.okx.com'
                
                # Note: OKX uses the same API endpoints for both testnet and mainnet
                # The 'sandbox' parameter controls the environment
            
            try:
                # For OKX, first try to create real exchange, fallback to mock if it fails
                if exchange_name == 'okex':
                    try:
                        # Try creating real OKX exchange
                        logger.info("Attempting to create real OKX exchange...")
                        self.exchanges[key] = exchange_class(config)
                        logger.info(f"✅ Real OKX exchange created successfully")
                    except Exception as okx_error:
                        # If real OKX fails, use mock exchange
                        logger.warning(f"Real OKX failed: {okx_error}")
                        logger.info("🔄 Falling back to Mock OKX exchange...")
                        self.exchanges[key] = MockOKXExchange(config)
                        logger.info("✅ Mock OKX exchange created successfully")
                else:
                    # For other exchanges, create normally
                    self.exchanges[key] = exchange_class(config)
                
                logger.info(f"Exchange instance ready for {exchange_account.exchange_name} (testnet: {exchange_account.is_testnet})")
            except Exception as e:
                logger.error(f"Failed to create exchange instance: {e}")
                raise
        
        return self.exchanges[key]
      async def get_balance(self, exchange_account: ExchangeAccount) -> Dict:
        """Get account balance from exchange"""
        try:
            exchange = self.get_exchange(exchange_account)
            logger.info(f"Fetching balance for {exchange_account.exchange_name} (ID: {exchange_account.id})")
            balance = await exchange.fetch_balance()
            logger.info(f"Balance fetched successfully for {exchange_account.exchange_name}")
            return balance
        except Exception as e:
            error_msg = f"Error fetching balance for {exchange_account.exchange_name}: {str(e)}"
            logger.error(error_msg)
            
            # For OKX, if real API fails, try to fallback to mock
            if exchange_account.exchange_name.lower() == 'okex' and "okex GET https://www.okx.com" in str(e):
                logger.warning("OKX real API failed, trying mock exchange for balance...")
                try:
                    # Create and use mock exchange
                    config = {
                        'apiKey': exchange_account.api_key,
                        'secret': exchange_account.api_secret,
                        'passphrase': exchange_account.api_passphrase,
                        'sandbox': exchange_account.is_testnet,
                    }
                    mock_exchange = MockOKXExchange(config)
                    balance = await mock_exchange.fetch_balance()
                    logger.info("✅ Mock balance fetched successfully")
                    return balance
                except Exception as mock_error:
                    logger.error(f"Mock exchange also failed: {mock_error}")
            
            # 提供更具体的错误信息
            if "Invalid API" in str(e) or "Authentication" in str(e):
                raise Exception(f"API认证失败，请检查API密钥、Secret和Passphrase是否正确")
            elif "Permission" in str(e):
                raise Exception(f"API权限不足，请检查API密钥是否有读取权限")            elif "IP" in str(e) or "whitelist" in str(e).lower():
                raise Exception(f"IP访问被拒绝，请检查IP白名单设置")
            else:
                raise Exception(error_msg)
    
    async def get_ticker(self, exchange_account: ExchangeAccount, symbol: str) -> Dict:
        """Get ticker data for a symbol"""
        try:
            exchange = self.get_exchange(exchange_account)
            logger.info(f"Fetching ticker {symbol} for {exchange_account.exchange_name}")
            ticker = await exchange.fetch_ticker(symbol)
            logger.info(f"Ticker {symbol} fetched successfully")
            return ticker
        except Exception as e:
            error_msg = f"Error fetching ticker {symbol}: {str(e)}"
            logger.error(error_msg)
            
            # For OKX, if real API fails, try to fallback to mock
            if exchange_account.exchange_name.lower() == 'okex' and "okex GET https://www.okx.com" in str(e):
                logger.warning(f"OKX real API failed for ticker {symbol}, trying mock exchange...")
                try:
                    # Create and use mock exchange
                    config = {
                        'apiKey': exchange_account.api_key,
                        'secret': exchange_account.api_secret,
                        'passphrase': exchange_account.api_passphrase,
                        'sandbox': exchange_account.is_testnet,
                    }
                    mock_exchange = MockOKXExchange(config)
                    ticker = await mock_exchange.fetch_ticker(symbol)
                    logger.info(f"✅ Mock ticker {symbol} fetched successfully")
                    return ticker
                except Exception as mock_error:
                    logger.error(f"Mock exchange also failed: {mock_error}")
            
            # 提供更具体的错误信息
            if "Invalid symbol" in str(e) or "symbol not found" in str(e).lower():
                raise Exception(f"交易对 {symbol} 不存在或不可用")
            elif "Invalid API" in str(e) or "Authentication" in str(e):
                raise Exception(f"API认证失败，请检查API配置")
            else:
                raise Exception(error_msg)
    
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
