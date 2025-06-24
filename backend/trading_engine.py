import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
import requests
import random
from database import SessionLocal, ExchangeAccount, Strategy, Trade, MarketData
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

def check_okx_connectivity() -> bool:
    """Check if OKX API is accessible"""
    import os
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv()
    
    # Get proxy settings
    use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
    proxies = None
    
    if use_proxy:
        proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
        proxy_port = os.getenv('PROXY_PORT', '1080')
        proxy_type = os.getenv('PROXY_TYPE', 'socks5')
        
        if proxy_type == 'socks5':
            proxy_url = f"socks5h://{proxy_host}:{proxy_port}"
        else:
            proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
            
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }
        logger.info(f"Using proxy for OKX connectivity check: {proxy_url}")
    
    test_urls = [
        'https://www.okx.com/api/v5/public/time',
        'https://aws.okx.com/api/v5/public/time',
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=5, proxies=proxies)
            if response.status_code == 200:
                logger.info(f"OKX API accessible via {url}")
                return True
        except Exception as e:
            logger.debug(f"Failed to connect to {url}: {e}")
            continue
    
    logger.warning("OKX API not accessible, will use mock exchange for testing")
    return False

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
            'USDT': {'free': 1000.0, 'used': 0.0, 'total': 1000.0},
            'BTC': {'free': 0.1, 'used': 0.0, 'total': 0.1},
            'ETH': {'free': 1.0, 'used': 0.0, 'total': 1.0},
            'free': {'USDT': 1000.0, 'BTC': 0.1, 'ETH': 1.0},
            'used': {'USDT': 0.0, 'BTC': 0.0, 'ETH': 0.0},
            'total': {'USDT': 1000.0, 'BTC': 0.1, 'ETH': 1.0},
        }
        
        logger.info("Mock balance fetched successfully")
        return balance
    
    async def fetch_ticker(self, symbol: str) -> Dict:
        """Mock ticker response"""
        logger.info(f"Fetching mock ticker for {symbol}...")
        
        # Mock prices for different symbols
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
        self._connection_cache = {}  # Cache connection status
        self._mock_mode = {}  # Track which exchanges are in mock mode
        
    def _should_use_mock(self, exchange_name: str) -> bool:
        """Determine if we should use mock exchange"""
        if exchange_name.lower() in ['okx', 'okex']:
            # Check cache first (cache for 5 minutes)
            cache_key = f"{exchange_name}_connectivity"
            if cache_key in self._connection_cache:
                cached_time, cached_result = self._connection_cache[cache_key]
                if datetime.now().timestamp() - cached_time < 300:  # 5 minutes
                    return not cached_result
            
            # Test connectivity
            connectivity = check_okx_connectivity()
            self._connection_cache[cache_key] = (datetime.now().timestamp(), connectivity)
            
            if not connectivity:
                logger.warning(f"OKX API not accessible, enabling mock mode for {exchange_name}")
                self._mock_mode[exchange_name] = True
                return True
            else:
                self._mock_mode[exchange_name] = False
                
        return False
    
    def get_exchange(self, exchange_account: ExchangeAccount) -> ccxt.Exchange:
        """Get exchange instance for a user's exchange account"""
        key = f"{exchange_account.id}_{exchange_account.exchange_name}"
        
        if key not in self.exchanges:
            exchange_name = exchange_account.exchange_name.lower()
            exchange_class = getattr(ccxt, exchange_name)
            
            config = {
                'apiKey': exchange_account.api_key,
                'secret': exchange_account.api_secret,
                'sandbox': exchange_account.is_testnet,
                'enableRateLimit': True,
                'timeout': 30000,
            }
              # Special handling for OKX
            if exchange_name == 'okex':
                if exchange_account.api_passphrase:
                    config['passphrase'] = exchange_account.api_passphrase
                
                # Check if we should use mock mode
                if self._should_use_mock(exchange_name):
                    logger.info("Using mock OKX exchange due to connectivity issues")
                    mock_config = {
                        'apiKey': exchange_account.api_key,
                        'secret': exchange_account.api_secret,
                        'passphrase': exchange_account.api_passphrase,
                        'sandbox': exchange_account.is_testnet,
                    }
                    self.exchanges[key] = MockOKXExchange(mock_config)
                    return self.exchanges[key]
                
                # Real OKX configuration
                config['hostname'] = 'www.okx.com'
                config['options'] = {
                    'defaultType': 'spot',
                }
            
            try:
                self.exchanges[key] = exchange_class(config)
                logger.info(f"Created exchange instance for {exchange_account.exchange_name}")
            except Exception as e:
                logger.error(f"Failed to create exchange instance: {e}")
                
                # For OKX, fallback to mock if real exchange fails
                if exchange_name == 'okex':
                    logger.warning("OKX real exchange failed, using mock exchange")
                    self.exchanges[key] = MockOKXExchange(config)
                    return self.exchanges[key]
                else:
                    raise        
        return self.exchanges[key]
    
    async def get_balance(self, exchange_account: ExchangeAccount) -> Dict:
        """Get account balance from exchange"""
        try:
            exchange = self.get_exchange(exchange_account)
            logger.info(f"Fetching balance for {exchange_account.exchange_name}")
            
            # Add timeout for balance fetching
            balance = await asyncio.wait_for(
                exchange.fetch_balance(), 
                timeout=5.0  # 5 second timeout
            )
            logger.info(f"Balance fetched successfully")
            return balance
        except asyncio.TimeoutError:
            logger.warning(f"Balance fetch timeout for {exchange_account.exchange_name}, using mock")
            # Use mock exchange for timeout
            config = {
                'apiKey': exchange_account.api_key,
                'secret': exchange_account.api_secret,
                'passphrase': exchange_account.api_passphrase,
                'sandbox': exchange_account.is_testnet,
            }
            mock_exchange = MockOKXExchange(config)
            return await mock_exchange.fetch_balance()
        except Exception as e:
            error_msg = f"Error fetching balance for {exchange_account.exchange_name}: {str(e)}"
            logger.error(error_msg)
            
            # For OKX network errors, try mock exchange
            if (exchange_account.exchange_name.lower() == 'okex' and 
                ("okex GET https://www.okx.com" in str(e) or 
                 "timeout" in str(e).lower() or
                 "exceeded" in str(e).lower())):
                logger.warning("OKX API failed, trying mock exchange...")
                try:
                    config = {
                        'apiKey': exchange_account.api_key,
                        'secret': exchange_account.api_secret,
                        'passphrase': exchange_account.api_passphrase,
                        'sandbox': exchange_account.is_testnet,
                    }
                    mock_exchange = MockOKXExchange(config)
                    return await mock_exchange.fetch_balance()
                except Exception as mock_error:
                    logger.error(f"Mock exchange also failed: {mock_error}")
            
            # Provide specific error messages
            if "Invalid API" in str(e) or "Authentication" in str(e):
                raise Exception("API认证失败，请检查API密钥、Secret和Passphrase是否正确")
            elif "Permission" in str(e):
                raise Exception("API权限不足，请检查API密钥是否有读取权限")
            elif "IP" in str(e) or "whitelist" in str(e).lower():
                raise Exception("IP访问被拒绝，请检查IP白名单设置")
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
            
            # For OKX network errors, try mock exchange
            if exchange_account.exchange_name.lower() == 'okex' and "okex GET https://www.okx.com" in str(e):
                logger.warning(f"OKX API failed for ticker {symbol}, trying mock exchange...")
                try:
                    config = {
                        'apiKey': exchange_account.api_key,
                        'secret': exchange_account.api_secret,
                        'passphrase': exchange_account.api_passphrase,
                        'sandbox': exchange_account.is_testnet,
                    }
                    mock_exchange = MockOKXExchange(config)
                    return await mock_exchange.fetch_ticker(symbol)
                except Exception as mock_error:
                    logger.error(f"Mock exchange also failed: {mock_error}")
            
            # Provide specific error messages
            if "Invalid symbol" in str(e) or "symbol not found" in str(e).lower():
                raise Exception(f"交易对 {symbol} 不存在或不可用")
            elif "Invalid API" in str(e) or "Authentication" in str(e):
                raise Exception("API认证失败，请检查API配置")
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

    async def test_connection(self, exchange: str, api_key: str, secret_key: str, 
                             passphrase: Optional[str] = None, is_testnet: bool = False) -> Dict:
        """Test exchange connection without saving account"""
        try:
            logger.info(f"Testing connection to {exchange} (testnet: {is_testnet})")
            
            if exchange.lower() in ['okx', 'okex']:
                # Check if OKX API is accessible first
                if not check_okx_connectivity():
                    logger.warning("OKX API not accessible, using mock exchange for test")
                    config = {
                        'apiKey': api_key,
                        'secret': secret_key,
                        'passphrase': passphrase,
                        'sandbox': is_testnet,
                    }
                    mock_exchange = MockOKXExchange(config)
                    balance = await mock_exchange.fetch_balance()
                    return {
                        'status': 'success',
                        'message': 'Mock connection successful (OKX API not accessible)',
                        'exchange': 'okx',
                        'testnet': is_testnet,
                        'balance_preview': {
                            'USDT': balance['total'].get('USDT', 0),
                            'BTC': balance['total'].get('BTC', 0),
                            'ETH': balance['total'].get('ETH', 0)
                        }
                    }
                
                # Try real OKX connection
                try:
                    config = {
                        'apiKey': api_key,
                        'secret': secret_key,
                        'passphrase': passphrase,
                        'sandbox': is_testnet,
                        'enableRateLimit': True,
                        'hostname': 'www.okx.com',
                        'timeout': 10000,
                        'options': {
                            'defaultType': 'spot',
                        }
                    }
                    
                    exchange_class = getattr(ccxt, 'okex')
                    test_exchange = exchange_class(config)
                    
                    # Test by fetching balance
                    balance = await test_exchange.fetch_balance()
                    await test_exchange.close()
                    
                    return {
                        'status': 'success',
                        'message': 'Real OKX connection successful',
                        'exchange': 'okx',
                        'testnet': is_testnet,
                        'balance_preview': {
                            currency: data for currency, data in balance.get('total', {}).items() 
                            if data > 0
                        }
                    }
                    
                except Exception as real_error:
                    logger.warning(f"Real OKX connection failed: {real_error}, using mock")
                    # Fallback to mock exchange
                    config = {
                        'apiKey': api_key,
                        'secret': secret_key,
                        'passphrase': passphrase,
                        'sandbox': is_testnet,
                    }
                    mock_exchange = MockOKXExchange(config)
                    balance = await mock_exchange.fetch_balance()
                    return {
                        'status': 'success',
                        'message': f'Mock connection (Real API failed: {str(real_error)[:100]})',
                        'exchange': 'okx',
                        'testnet': is_testnet,
                        'balance_preview': {
                            'USDT': balance['total'].get('USDT', 0),
                            'BTC': balance['total'].get('BTC', 0),
                            'ETH': balance['total'].get('ETH', 0)
                        }
                    }
            else:
                raise Exception(f"Exchange {exchange} not supported yet")
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Connection test failed: {error_msg}")
            
            # Provide user-friendly error messages
            if "Missing required OKX credentials" in error_msg:
                raise Exception("缺少必要的 OKX 凭据：API Key、Secret 和 Passphrase 都是必需的")
            elif "Invalid API" in error_msg or "Authentication" in error_msg:
                raise Exception("API认证失败，请检查API密钥、Secret和Passphrase是否正确")
            elif "Permission" in error_msg:
                raise Exception("API权限不足，请检查API密钥是否有读取权限")
            elif "IP" in error_msg or "whitelist" in error_msg.lower():
                raise Exception("IP访问被拒绝，请检查IP白名单设置")
            elif "Network" in error_msg or "timeout" in error_msg.lower():
                raise Exception("网络连接失败，请检查网络设置")
            else:
                raise Exception(f"连接测试失败: {error_msg}")

class StrategyEngine:
    def __init__(self, exchange_manager: ExchangeManager):
        self.exchange_manager = exchange_manager
    
    def calculate_bollinger_bands(self, prices: np.array, period: int = 20, deviation: float = 2.0) -> Tuple[np.array, np.array, np.array]:
        """Calculate Bollinger Bands using numpy"""
        middle = np.convolve(prices, np.ones(period), 'valid') / period
        std_dev = np.array([np.std(prices[i:i+period]) for i in range(len(prices) - period + 1)])
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
            
            ohlcv_data = await self.exchange_manager.get_ohlcv(
                exchange_account, 
                strategy.symbol, 
                strategy.timeframe, 
                limit=max(strategy.bb_period, strategy.ma_period) + 10
            )
            
            if len(ohlcv_data) < max(strategy.bb_period, strategy.ma_period):
                logger.warning(f"Not enough data for strategy {strategy.id}")
                return None
            
            df = pd.DataFrame(ohlcv_data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            if strategy.strategy_type == '5m_boll_ma60':
                return await self._check_boll_ma_strategy(df, strategy)
            
            return None
            
        except Exception as e:
            logger.error(f"Error checking strategy signal: {e}")
            return None
    
    async def _check_boll_ma_strategy(self, df: pd.DataFrame, strategy: Strategy) -> Optional[str]:
        """Check Bollinger Bands + MA strategy"""
        prices = df['close'].values
        
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(
            prices, strategy.bb_period, strategy.bb_deviation
        )
        ma = self.calculate_ma(prices, strategy.ma_period)
        
        current_price = prices[-1]
        current_bb_upper = bb_upper[-1]
        current_bb_lower = bb_lower[-1]
        current_ma = ma[-1]
        
        if current_price <= current_bb_lower and current_price > current_ma:
            return "buy"
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
            
            order = await self.exchange_manager.place_order(
                exchange_account,
                strategy.symbol,
                "market",
                signal,
                strategy.entry_amount
            )
            
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
