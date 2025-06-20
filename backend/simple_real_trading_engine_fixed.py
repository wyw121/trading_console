"""
简化版真实交易引擎 - 修复版本
专门为Trading Console项目设计，解决按钮错误问题
"""
import ccxt
import logging
from typing import Dict, Optional, List
from database import SessionLocal
from sqlalchemy.orm import Session
import os

logger = logging.getLogger(__name__)

class SimpleRealExchangeManager:
    """简化的真实交易所管理器"""
    
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.db_session = None
        logger.info("初始化简化真实交易所管理器")
    
    def get_db_session(self) -> Session:
        """获取数据库会话"""
        if not self.db_session:
            self.db_session = SessionLocal()
        return self.db_session
    
    def setup_proxy_environment(self):
        """设置代理环境变量"""
        proxy_url = 'socks5h://127.0.0.1:1080'
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        logger.info("✅ 代理环境变量已设置")
    
    async def create_real_exchange(self, exchange_name: str, config: Dict) -> ccxt.Exchange:
        """创建真实交易所连接"""
        try:
            logger.info(f"创建真实{exchange_name}交易所连接...")
            
            # 设置代理环境
            self.setup_proxy_environment()
            
            if exchange_name.lower() in ['okx', 'okex']:
                # 验证OKX所需参数
                required_keys = ['apiKey', 'secret', 'passphrase']
                missing_keys = [key for key in required_keys if not config.get(key)]
                if missing_keys:
                    raise ValueError(f"OKX缺少必需的API密钥: {missing_keys}")
                
                # 创建OKX交易所实例
                exchange = ccxt.okx({
                    'apiKey': config['apiKey'],
                    'secret': config['secret'],
                    'passphrase': config['passphrase'],
                    'sandbox': config.get('sandbox', False),
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
                
                logger.info("✅ OKX交易所实例创建成功")
                
            elif exchange_name.lower() == 'binance':
                exchange = ccxt.binance({
                    'apiKey': config['apiKey'],
                    'secret': config['secret'],
                    'sandbox': config.get('sandbox', False),
                    'enableRateLimit': True,
                    'timeout': 30000,
                })
                
                logger.info("✅ Binance交易所实例创建成功")
                
            else:
                raise ValueError(f"不支持的交易所: {exchange_name}")
            
            return exchange
            
        except Exception as e:
            logger.error(f"创建{exchange_name}交易所连接失败: {str(e)}")
            raise
    
    async def test_connection(self, exchange_name: str, api_key: str, 
                            api_secret: str, api_passphrase: str = None, 
                            is_testnet: bool = False) -> Dict[str, any]:
        """测试交易所连接"""
        try:
            logger.info(f"测试{exchange_name}连接...")
            
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': is_testnet,
                'enableRateLimit': True,
                'timeout': 30000,
            }
            
            if api_passphrase:
                config['passphrase'] = api_passphrase
            
            exchange = await self.create_real_exchange(exchange_name, config)
            
            return {
                'success': True,
                'message': f'{exchange_name}连接测试成功',
                'exchange': exchange
            }
            
        except Exception as e:
            return {
                'success': False,
                'message': f'{exchange_name}连接测试失败: {str(e)}',
                'exchange': None
            }
    
    async def add_exchange_account(self, user_id: int, exchange_name: str, 
                                 api_key: str, api_secret: str, 
                                 api_passphrase: str = None, is_testnet: bool = False) -> Dict[str, any]:
        """添加交易所账户"""
        try:
            # 首先测试连接
            test_result = await self.test_connection(
                exchange_name, api_key, api_secret, api_passphrase, is_testnet
            )
            
            if not test_result['success']:
                return test_result
            
            # 存储到实例中，键格式统一
            account_key = f"{user_id}_{exchange_name}_{is_testnet}"
            self.exchanges[account_key] = test_result['exchange']
            
            logger.info(f"✅ 用户{user_id}的{exchange_name}账户添加成功，键: {account_key}")
            
            return {
                'success': True,
                'message': f'{exchange_name}账户添加成功',
                'account_key': account_key
            }
            
        except Exception as e:
            error_msg = f"添加{exchange_name}账户失败: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'message': error_msg,
                'account_key': None
            }
    
    async def get_real_balance(self, user_id: int, exchange_name: str, 
                              is_testnet: bool = False) -> Dict:
        """获取真实余额信息"""
        try:
            key = f"{user_id}_{exchange_name}_{is_testnet}"
            logger.info(f"🔍 查找交易所连接: {key}")
            logger.info(f"🔍 当前存储的连接: {list(self.exchanges.keys())}")
            
            # 如果连接不存在，返回错误
            if key not in self.exchanges:
                logger.warning(f"交易所连接{key}不存在")
                return {
                    "success": False,
                    "message": "交易所连接不存在，请先添加交易所账户",
                    "data": None
                }
            
            exchange = self.exchanges[key]
            logger.info(f"🔍 找到交易所实例: {type(exchange)}")
            
            # 获取账户余额
            balance = exchange.fetch_balance()
            
            logger.info(f"✅ 成功获取{exchange_name}余额信息")
            
            return {
                "success": True,
                "message": "获取余额成功",
                "data": balance
            }
            
        except Exception as e:
            error_msg = f"获取余额时发生错误: {str(e)}"
            logger.error(error_msg)
            logger.error(f"错误类型: {type(e)}")
            logger.error(f"错误详情: {repr(e)}")
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
    
    async def get_real_ticker(self, user_id: int, exchange_name: str, 
                             symbol: str, is_testnet: bool = False) -> Dict:
        """获取真实价格信息"""
        try:
            key = f"{user_id}_{exchange_name}_{is_testnet}"
            logger.info(f"🔍 查找交易所连接: {key}")
            logger.info(f"🔍 当前存储的连接: {list(self.exchanges.keys())}")
            
            if key not in self.exchanges:
                logger.warning(f"交易所连接{key}不存在")
                return {
                    "success": False,
                    "message": "交易所连接不存在，请先添加交易所账户",
                    "data": None
                }
            
            exchange = self.exchanges[key]
            logger.info(f"🔍 找到交易所实例: {type(exchange)}")
            logger.info(f"🔍 获取价格的交易对: {symbol}")
            
            # 获取ticker信息
            ticker = exchange.fetch_ticker(symbol)
            
            logger.info(f"✅ 成功获取{symbol}的价格信息")
            
            return {
                "success": True,
                "message": "获取价格成功",
                "data": ticker
            }
            
        except Exception as e:
            error_msg = f"获取价格时发生错误: {str(e)}"
            logger.error(error_msg)
            logger.error(f"错误类型: {type(e)}")
            logger.error(f"错误详情: {repr(e)}")
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
    
    def get_supported_exchanges(self) -> List[str]:
        """获取支持的交易所列表"""
        return ['okx', 'binance']
    
    async def get_exchange_markets(self, user_id: int, exchange_name: str, 
                                  is_testnet: bool = False) -> Dict:
        """获取交易所的交易对列表"""
        try:
            key = f"{user_id}_{exchange_name}_{is_testnet}"
            
            if key not in self.exchanges:
                return {
                    "success": False,
                    "message": "交易所连接不存在，请先添加交易所账户",
                    "data": []
                }
            
            exchange = self.exchanges[key]
            
            # 对于OKX，使用简单的方法获取常用交易对
            if exchange_name.lower() in ['okx', 'okex']:
                common_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
                markets = {}
                
                for pair in common_pairs:
                    try:
                        # 尝试获取ticker来验证交易对是否存在
                        ticker = exchange.fetch_ticker(pair)
                        markets[pair] = {
                            'symbol': pair,
                            'base': pair.split('/')[0],
                            'quote': pair.split('/')[1],
                            'active': True,
                            'last_price': ticker.get('last')
                        }
                    except:
                        # 如果获取失败，跳过这个交易对
                        continue
                
                return {
                    "success": True,
                    "message": "获取交易对成功",
                    "data": list(markets.values())
                }
            else:
                # 其他交易所使用标准方法
                markets = exchange.load_markets()
                market_list = [
                    {
                        'symbol': symbol,
                        'base': market.get('base'),
                        'quote': market.get('quote'),
                        'active': market.get('active', True)
                    }
                    for symbol, market in markets.items()
                ][:50]  # 限制返回数量
                
                return {
                    "success": True,
                    "message": "获取交易对成功",
                    "data": market_list
                }
            
        except Exception as e:
            error_msg = f"获取交易对时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": []
            }

# 创建全局实例
real_exchange_manager = SimpleRealExchangeManager()
