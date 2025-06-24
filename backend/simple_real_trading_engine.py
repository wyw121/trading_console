"""
简化版真实交易引擎 - 集成OKX API版本
"""
import logging
from typing import Dict, List
from okx_api_manager import OKXAPIManager

logger = logging.getLogger(__name__)

class SimpleRealExchangeManager:
    """简化的真实交易所管理器 - 集成OKX API"""
    
    def __init__(self):
        self.exchanges = {}
        self.okx_managers = {}  # 存储每个用户的OKX管理器
        logger.info("初始化简化真实交易所管理器（支持OKX API）")
    
    def add_okx_account(self, user_id: int, api_key: str, secret_key: str, passphrase: str):
        """添加OKX账户"""
        try:
            manager = OKXAPIManager(api_key, secret_key, passphrase)
            self.okx_managers[user_id] = manager
            logger.info(f"为用户 {user_id} 添加OKX账户")
            return True
        except Exception as e:
            logger.error(f"添加OKX账户失败: {e}")
            return False
    
    def get_real_ticker(self, user_id: int, exchange_name: str, 
                       symbol: str, is_testnet: bool = False) -> Dict:
        """获取真实价格信息 - 集成OKX API"""
        try:
            # 安全的键生成，防止None值
            user_id_str = str(user_id) if user_id is not None else "unknown"
            exchange_name_str = str(exchange_name) if exchange_name is not None else "unknown"
            is_testnet_str = str(is_testnet) if is_testnet is not None else "False"
            
            key = f"{user_id_str}_{exchange_name_str}_{is_testnet_str}"
            
            logger.info(f"get_real_ticker 调用 - key: {key}, symbol: {symbol}")
            
            # 验证和规范化symbol
            validated_symbol = self.validate_symbol(exchange_name_str, symbol)
            logger.info(f"Symbol验证: {symbol} -> {validated_symbol}")
            
            # 如果是OKX且有对应的管理器
            if exchange_name_str.lower() in ['okx', 'okex'] and user_id in self.okx_managers:
                try:
                    manager = self.okx_managers[user_id]
                    
                    logger.info(f"使用OKX symbol: {validated_symbol}")
                    result = manager.get_ticker(validated_symbol)
                    
                    if result.get('code') == '0' and result.get('data'):
                        ticker_data = result['data'][0]
                        return {
                            "success": True,
                            "message": "获取价格成功",
                            "data": {
                                "symbol": symbol,
                                "validated_symbol": validated_symbol,
                                "price": float(ticker_data['last']),
                                "bid": float(ticker_data['bidPx']),
                                "ask": float(ticker_data['askPx']),
                                "high": float(ticker_data['high24h']),
                                "low": float(ticker_data['low24h']),
                                "volume": float(ticker_data['vol24h']),
                                "timestamp": ticker_data['ts']
                            }
                        }
                    else:
                        error_msg = result.get('msg', '未知错误')
                        logger.error(f"OKX API错误: {error_msg} (symbol: {validated_symbol})")
                        
                        # 如果是交易对不存在，提供更友好的错误信息和建议
                        if "doesn't exist" in error_msg.lower() or "instrument" in error_msg.lower():
                            # 获取建议的交易对
                            valid_symbols = self.get_valid_symbols(exchange_name_str)
                            suggestions = valid_symbols[:5] if valid_symbols else ['BTC-USDT', 'ETH-USDT']
                            
                            return {
                                "success": False,
                                "message": f"交易对 {validated_symbol} 不存在。建议使用: {', '.join(suggestions)}",
                                "data": {
                                    "error_type": "invalid_symbol",
                                    "requested_symbol": symbol,
                                    "validated_symbol": validated_symbol,
                                    "suggestions": suggestions
                                }
                            }
                        else:
                            return {
                                "success": False,
                                "message": f"OKX API错误: {error_msg}",
                                "data": None
                            }
                except Exception as e:
                    logger.error(f"OKX API调用失败: {e}")
                    return {
                        "success": False,
                        "message": f"OKX API调用失败: {str(e)}",
                        "data": None
                    }
            
            # 默认返回（没有配置API或不是OKX）
            return {
                "success": False,
                "message": "连接未配置，需要先设置API密钥",
                "data": None
            }
            
        except Exception as e:
            error_msg = f"获取价格时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
    
    async def get_real_balance(self, user_id: int, exchange_name: str, 
                        is_testnet: bool = False) -> Dict:
        """获取真实余额信息 - 集成OKX API"""
        try:
            user_id_str = str(user_id) if user_id is not None else "unknown"
            exchange_name_str = str(exchange_name) if exchange_name is not None else "unknown"
            is_testnet_str = str(is_testnet) if is_testnet is not None else "False"
            
            key = f"{user_id_str}_{exchange_name_str}_{is_testnet_str}"
            
            logger.info(f"get_real_balance 调用 - key: {key}")
            
            # 如果是OKX且有对应的管理器
            if exchange_name_str.lower() in ['okx', 'okex'] and user_id in self.okx_managers:
                try:
                    manager = self.okx_managers[user_id]
                    
                    # 使用带重试机制的余额获取方法
                    result = manager.get_balance_with_retry()
                    
                    if result.get('code') == '0' and result.get('data'):
                        balance_data = result['data'][0]['details'] if result['data'] else []
                        formatted_balances = {}
                        
                        for item in balance_data:
                            currency = item.get('ccy', '')
                            available = float(item.get('availBal', 0))
                            if available > 0:
                                formatted_balances[currency] = {
                                    'available': available,
                                    'frozen': float(item.get('frozenBal', 0)),
                                    'total': float(item.get('bal', 0))
                                }
                        
                        return {
                            "success": True,
                            "message": "获取余额成功",
                            "data": formatted_balances
                        }
                    else:
                        error_msg = result.get('msg', '未知错误')
                        error_code = result.get('code', '-1')
                        suggestion = result.get('suggestion', '')
                        
                        logger.error(f"OKX余额API错误: {error_msg}")
                        
                        # 根据错误代码提供友好的错误信息
                        if error_code == '50102':
                            friendly_msg = "时间同步问题，这通常是API密钥权限问题"
                            if suggestion:
                                friendly_msg += f"。建议：{suggestion}"
                        elif error_code == '50111':
                            friendly_msg = "API密钥无效，请检查密钥配置"
                            if suggestion:
                                friendly_msg += f"。{suggestion}"
                        elif error_code == '50113':
                            friendly_msg = "API权限不足，请检查API密钥权限设置"
                            if suggestion:
                                friendly_msg += f"。{suggestion}"
                        elif error_code in ['401', '50114']:
                            friendly_msg = "IP访问限制，请检查API密钥IP白名单设置"
                            if suggestion:
                                friendly_msg += f"。{suggestion}"
                        else:
                            friendly_msg = f"OKX API错误: {error_msg}"
                            if suggestion:
                                friendly_msg += f"。建议：{suggestion}"
                        
                        return {
                            "success": False,
                            "message": friendly_msg,
                            "data": {
                                "error_code": error_code,
                                "original_error": error_msg,
                                "suggestion": suggestion
                            }
                        }
                except Exception as e:
                    logger.error(f"OKX余额API调用失败: {e}")
                    return {
                        "success": False,
                        "message": f"OKX余额API调用失败: {str(e)}",
                        "data": None
                    }
            
            # 默认返回
            return {
                "success": False,
                "message": "连接未配置，需要先设置API密钥",
                "data": None
            }
            
        except Exception as e:
            error_msg = f"获取余额时发生错误: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
    
    def add_exchange_account(self, user_id: int, exchange_name: str, 
                           api_key: str, api_secret: str, api_passphrase: str = None, 
                           is_testnet: bool = False) -> Dict:
        """添加交易所账户到管理器"""
        try:
            exchange_name = exchange_name.lower()
            
            if exchange_name in ['okx', 'okex']:
                # 添加OKX账户
                if self.add_okx_account(user_id, api_key, api_secret, api_passphrase):
                    logger.info(f"成功添加OKX账户: 用户{user_id}")
                    return {"success": True, "message": "OKX账户添加成功"}
                else:
                    return {"success": False, "message": "OKX账户添加失败"}
            else:
                return {"success": False, "message": f"不支持的交易所: {exchange_name}"}
                
        except Exception as e:
            logger.error(f"添加交易所账户失败: {e}")
            return {"success": False, "message": f"添加账户失败: {str(e)}"}
        """获取支持的交易所列表"""
        return ['okx', 'binance']
    
    def restore_exchange_connections(self, user_id: int, db_accounts: List) -> int:
        """从数据库恢复交易所连接 - 自动配置API"""
        logger.info(f"恢复连接: 用户{user_id}, 账户数量{len(db_accounts)}")
        
        restored_count = 0
        for account in db_accounts:
            try:
                exchange_name = account.exchange_name.lower()
                
                # 如果是OKX账户且有API密钥
                if exchange_name in ['okx', 'okex']:
                    if hasattr(account, 'api_key') and account.api_key:
                        # 使用数据库中存储的API密钥（在生产环境中应该解密）
                        api_key = account.api_key
                        api_secret = account.api_secret
                        api_passphrase = account.api_passphrase
                        
                        if self.add_okx_account(user_id, api_key, api_secret, api_passphrase):
                            restored_count += 1
                            logger.info(f"成功恢复OKX连接: 用户{user_id}")
                        else:
                            logger.error(f"恢复OKX连接失败: 用户{user_id}")
                
            except Exception as e:
                logger.error(f"恢复账户连接失败: {e}")
        
        return restored_count
    
    def test_okx_connection(self, user_id: int) -> Dict:
        """测试OKX连接"""
        if user_id in self.okx_managers:
            manager = self.okx_managers[user_id]
            return manager.test_connection()
        else:
            return {
                'public_api': False,
                'private_api': False,
                'error_messages': ['OKX账户未配置']
            }
    
    def test_connection(self, exchange_name: str, api_key: str, api_secret: str, 
                       api_passphrase: str = None, is_testnet: bool = False) -> Dict:
        """测试交易所连接"""
        try:
            logger.info(f"测试连接: {exchange_name}, testnet: {is_testnet}")
            
            # 规范化交易所名称
            exchange_name = exchange_name.lower()
            
            if exchange_name in ['okx', 'okex']:
                # 测试OKX连接
                try:
                    from okx_api_manager import OKXAPIManager
                    # 创建临时管理器进行连接测试
                    temp_manager = OKXAPIManager(api_key, api_secret, api_passphrase)
                    connection_result = temp_manager.test_connection()
                    
                    if connection_result.get('public_api', False):
                        return {
                            "success": True,
                            "message": "OKX API连接测试成功",
                            "data": {
                                "exchange": exchange_name,
                                "public_api": connection_result.get('public_api', False),
                                "private_api": connection_result.get('private_api', False),
                                "testnet": is_testnet
                            }
                        }
                    else:
                        error_msgs = connection_result.get('error_messages', ['连接失败'])
                        return {
                            "success": False,
                            "message": f"OKX连接失败: {'; '.join(error_msgs)}",
                            "data": None
                        }
                        
                except Exception as e:
                    logger.error(f"OKX连接测试异常: {e}")
                    return {
                        "success": False,
                        "message": f"OKX连接测试异常: {str(e)}",
                        "data": None
                    }
            
            elif exchange_name == 'binance':
                # 模拟Binance连接测试
                return {
                    "success": True,
                    "message": "Binance连接测试成功（模拟）",
                    "data": {
                        "exchange": exchange_name,
                        "public_api": True,
                        "private_api": True,
                        "testnet": is_testnet
                    }
                }
            
            else:
                return {
                    "success": False,
                    "message": f"不支持的交易所: {exchange_name}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"连接测试失败: {e}")
            return {
                "success": False,
                "message": f"连接测试异常: {str(e)}",
                "data": None
            }
    
    def add_exchange_account(self, user_id: int, exchange_name: str, api_key: str, 
                           api_secret: str, api_passphrase: str = None, is_testnet: bool = False) -> Dict:
        """添加交易所账户到管理器"""
        try:
            logger.info(f"添加交易所账户: 用户{user_id}, 交易所{exchange_name}")
            
            # 规范化交易所名称
            exchange_name = exchange_name.lower()
            
            if exchange_name in ['okx', 'okex']:
                # 添加OKX账户
                if self.add_okx_account(user_id, api_key, api_secret, api_passphrase):
                    return {
                        "success": True,
                        "message": "OKX账户添加成功",
                        "data": {
                            "user_id": user_id,
                            "exchange": exchange_name,
                            "testnet": is_testnet
                        }
                    }
                else:
                    return {
                        "success": False,
                        "message": "OKX账户添加失败",
                        "data": None
                    }
            
            elif exchange_name == 'binance':
                # 模拟Binance账户添加
                return {
                    "success": True,
                    "message": "Binance账户添加成功（模拟）",
                    "data": {
                        "user_id": user_id,
                        "exchange": exchange_name,
                        "testnet": is_testnet
                    }
                }
            
            else:
                return {
                    "success": False,
                    "message": f"不支持的交易所: {exchange_name}",
                    "data": None
                }
                
        except Exception as e:
            logger.error(f"添加交易所账户失败: {e}")
            return {
                "success": False,
                "message": f"添加账户异常: {str(e)}",
                "data": None
            }
    
    def get_valid_symbols(self, exchange_name: str) -> List[str]:
        """获取交易所支持的有效交易对列表"""
        try:
            exchange_name = exchange_name.lower()
            
            if exchange_name in ['okx', 'okex']:
                # 获取OKX支持的现货交易对
                try:
                    import requests
                    response = requests.get('https://www.okx.com/api/v5/public/instruments?instType=SPOT', 
                                          proxies={"http": None, "https": None}, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('code') == '0' and data.get('data'):
                            symbols = [inst['instId'] for inst in data['data']]
                            logger.info(f"获取到 {len(symbols)} 个OKX现货交易对")
                            return symbols
                    
                    # 如果API调用失败，返回常用交易对
                    logger.warning("获取OKX交易对列表失败，使用默认列表")
                    return ['BTC-USDT', 'ETH-USDT', 'BTC-USD', 'ETH-USD', 'SOL-USDT', 'ADA-USDT']
                    
                except Exception as e:
                    logger.error(f"获取OKX交易对失败: {e}")
                    return ['BTC-USDT', 'ETH-USDT', 'BTC-USD', 'ETH-USD']
            
            elif exchange_name == 'binance':
                # Binance常用交易对（模拟）
                return ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
            
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取交易对列表失败: {e}")
            return ['BTC-USDT']
    
    def validate_symbol(self, exchange_name: str, symbol: str) -> str:
        """验证并规范化交易对格式"""
        try:
            exchange_name = exchange_name.lower()
            
            if not symbol or symbol.strip() == "":
                if exchange_name in ['okx', 'okex']:
                    return 'BTC-USDT'
                elif exchange_name == 'binance':
                    return 'BTCUSDT'
                else:
                    return 'BTC-USDT'
            
            symbol = symbol.strip().upper()
            
            if exchange_name in ['okx', 'okex']:
                # OKX格式: BTC-USDT
                if '/' in symbol:
                    # 从 BTC/USDT 转换为 BTC-USDT
                    symbol = symbol.replace('/', '-')
                elif '_' in symbol:
                    # 从 BTC_USDT 转换为 BTC-USDT
                    symbol = symbol.replace('_', '-')
                
                # 确保有连字符
                if '-' not in symbol and len(symbol) > 3:
                    # 尝试智能分割 (BTCUSDT -> BTC-USDT)
                    common_quotes = ['USDT', 'USD', 'BTC', 'ETH', 'EUR', 'JPY']
                    for quote in common_quotes:
                        if symbol.endswith(quote):
                            base = symbol[:-len(quote)]
                            if len(base) >= 2:
                                symbol = f"{base}-{quote}"
                                break
                
                return symbol
                
            elif exchange_name == 'binance':
                # Binance格式: BTCUSDT (无分隔符)
                symbol = symbol.replace('/', '').replace('-', '').replace('_', '')
                return symbol
            
            else:
                return symbol
                
        except Exception as e:
            logger.error(f"验证交易对格式失败: {e}")
            return 'BTC-USDT'

# 创建全局实例
real_exchange_manager = SimpleRealExchangeManager()
