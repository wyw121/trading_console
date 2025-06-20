"""
简化版真实交易引擎
专门为Trading Console项目设计，避免复杂的缩进和导入问题
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
                
                # 创建OKX实例
                exchange = ccxt.okx(config)
                
                # 设置代理
                proxy_config = {
                    'http': 'socks5h://127.0.0.1:1080',
                    'https': 'socks5h://127.0.0.1:1080'
                }
                
                if hasattr(exchange, 'session') and exchange.session:
                    exchange.session.proxies = proxy_config
                elif hasattr(exchange, 'proxies'):
                    exchange.proxies = proxy_config
                
                # 简单测试连接
                try:
                    server_time = exchange.fetch_time()
                    logger.info(f"✅ OKX连接成功，服务器时间: {server_time}")
                except Exception as e:
                    logger.warning(f"⚠️ OKX连接测试警告: {e}")
                    # 不抛出异常，允许继续使用
                
                return exchange
                
            elif exchange_name.lower() == 'binance':
                required_keys = ['apiKey', 'secret']
                missing_keys = [key for key in required_keys if not config.get(key)]
                if missing_keys:
                    raise ValueError(f"Binance缺少必需的API密钥: {missing_keys}")
                
                exchange = ccxt.binance(config)
                logger.info(f"✅ {exchange_name}连接创建成功")
                return exchange
                
            else:
                raise ValueError(f"不支持的交易所: {exchange_name}")
                
        except Exception as e:
            error_msg = f"创建{exchange_name}真实连接失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def test_connection(self, exchange_name: str, api_key: str, api_secret: str, 
                            api_passphrase: str = None, is_testnet: bool = False) -> Dict[str, any]:
        """测试交易所连接"""
        try:
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
            
            # 存储到实例中，键格式保持一致
            account_key = f"{user_id}_{exchange_name}_{is_testnet}"
            self.exchanges[account_key] = test_result['exchange']
            
            logger.info(f"✅ 用户{user_id}的{exchange_name}账户添加成功")
            
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
                'account_key': None            }
    
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
            }    async def get_real_ticker(self, user_id: int, exchange_name: str, 
                             symbol: str, is_testnet: bool = False) -> Dict:
        """获取真实价格信息"""
        try:
            # 详细调试参数值
            logger.info(f"📊 get_real_ticker 调用参数:")
            logger.info(f"  user_id: {user_id} (type: {type(user_id)})")
            logger.info(f"  exchange_name: {exchange_name} (type: {type(exchange_name)})")
            logger.info(f"  symbol: {symbol} (type: {type(symbol)})")
            logger.info(f"  is_testnet: {is_testnet} (type: {type(is_testnet)})")
            
            # 安全的键生成，防止None值
            user_id_str = str(user_id) if user_id is not None else "unknown"
            exchange_name_str = str(exchange_name) if exchange_name is not None else "unknown"
            is_testnet_str = str(is_testnet) if is_testnet is not None else "False"
            
            logger.info(f"🔑 键组成部分:")
            logger.info(f"  user_id_str: {user_id_str}")
            logger.info(f"  exchange_name_str: {exchange_name_str}")
            logger.info(f"  is_testnet_str: {is_testnet_str}")
            
            key = f"{user_id_str}_{exchange_name_str}_{is_testnet_str}"
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
            
            # 确保 symbol 不为 None 或空
            if not symbol or symbol is None:
                raise ValueError("交易对符号不能为空")
            
            # 安全地调用 fetch_ticker，包装可能的内部错误
            try:
                ticker = exchange.fetch_ticker(symbol)
                
                # 验证返回的数据
                if ticker is None:
                    raise ValueError("交易所返回的价格数据为空")
                    
                logger.info(f"✅ 成功获取{symbol}的价格信息")
                
                return {
                    "success": True,
                    "message": "获取价格成功",
                    "data": ticker
                }
                
            except Exception as fetch_error:
                # 捕获 CCXT 内部错误，可能包括字符串拼接错误
                logger.error(f"📛 CCXT fetch_ticker 内部错误: {str(fetch_error)}")
                logger.error(f"📛 错误类型: {type(fetch_error)}")
                
                # 如果是 TypeError 且涉及字符串拼接，给出更详细的错误信息
                if isinstance(fetch_error, TypeError) and "NoneType" in str(fetch_error):
                    error_msg = f"CCXT库内部字符串拼接错误，可能是市场数据格式异常 - 交易对: {symbol}, 交易所: {exchange_name_str}"
                else:
                    error_msg = f"获取价格数据失败: {str(fetch_error)}"
                
                raise ValueError(error_msg) from fetch_error
            
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
    
    async def restore_exchange_connections(self, user_id: int, db_accounts: List) -> int:
        """从数据库恢复交易所连接"""
        restored_count = 0
        
        for account in db_accounts:
            try:
                # 重新建立连接
                result = await self.add_exchange_account(
                    user_id=account.user_id,
                    exchange_name=account.exchange_name,
                    api_key=account.api_key,
                    api_secret=account.api_secret,
                    api_passphrase=account.api_passphrase,
                    is_testnet=account.is_testnet
                )
                
                if result['success']:
                    restored_count += 1
                    logger.info(f"✅ 恢复连接: {result['account_key']}")
                else:
                    logger.warning(f"⚠️ 恢复连接失败: {account.exchange_name} - {result['message']}")
                    
            except Exception as e:
                logger.error(f"❌ 恢复连接异常: {account.exchange_name} - {str(e)}")
        
        logger.info(f"📊 恢复连接统计: {restored_count}/{len(db_accounts)}")
        return restored_count

# 创建全局实例
real_exchange_manager = SimpleRealExchangeManager()
