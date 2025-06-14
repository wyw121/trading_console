"""
OKX API 最佳实践实现
基于官方文档：https://www.okx.com/docs-v5/
包含连接测试、市场数据、账户管理、订单管理等功能
"""
import ccxt
import asyncio
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib
import hmac
import base64
import time
from dataclasses import dataclass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class OKXConfig:
    """OKX配置类"""
    api_key: str
    secret_key: str
    passphrase: str
    is_sandbox: bool = True  # 默认使用测试环境
    
class OKXAPIManager:
    """OKX API管理器 - 基于官方最佳实践"""
    
    def __init__(self, config: OKXConfig):
        self.config = config
        self.exchange = None
        self.connected = False
        
    async def initialize(self) -> bool:
        """初始化OKX连接"""
        try:
            # 配置多个备用URL
            sandbox_urls = [
                "https://www.okx.com",
                "https://aws.okx.com"
            ]
            
            config = {
                'apiKey': self.config.api_key,
                'secret': self.config.secret_key,
                'passphrase': self.config.passphrase,
                'sandbox': self.config.is_sandbox,
                'enableRateLimit': True,
                'rateLimit': 100,  # 官方建议的限速
                'timeout': 30000,
                'options': {
                    'adjustForTimeDifference': True,  # 自动调整时间差
                },
            }
            
            # 如果是测试环境，使用沙盒URL
            if self.config.is_sandbox:
                config['urls'] = {
                    'api': {
                        'rest': 'https://www.okx.com',
                        'public': 'https://www.okx.com/api/v5',
                        'private': 'https://www.okx.com/api/v5'
                    }
                }
            
            self.exchange = ccxt.okx(config)
            
            # 测试连接
            await self._test_connection()
            self.connected = True
            logger.info(f"OKX API连接成功 ({'沙盒' if self.config.is_sandbox else '生产'}环境)")
            return True
            
        except Exception as e:
            logger.error(f"OKX API连接失败: {str(e)}")
            self.connected = False
            return False
    
    async def _test_connection(self):
        """测试API连接"""
        try:
            # 1. 测试公共API - 获取系统状态
            status = await self.get_system_status()
            logger.info(f"系统状态: {status}")
            
            # 2. 测试私有API - 获取账户配置
            config = await self.get_account_config()
            logger.info(f"账户配置: {config}")
            
            # 3. 测试市场数据
            instruments = await self.get_instruments("SPOT")
            logger.info(f"现货交易对数量: {len(instruments) if instruments else 0}")
            
        except Exception as e:
            raise Exception(f"连接测试失败: {str(e)}")
    
    async def get_system_status(self) -> Dict:
        """获取系统状态"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            # OKX系统状态API
            response = await self.exchange.public_get_system_status()
            return response
            
        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return {"error": str(e)}
    
    async def get_account_config(self) -> Dict:
        """获取账户配置"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            response = await self.exchange.private_get_account_config()
            return response
            
        except Exception as e:
            logger.error(f"获取账户配置失败: {str(e)}")
            return {"error": str(e)}
    
    async def get_instruments(self, inst_type: str = "SPOT") -> List[Dict]:
        """获取交易工具配置"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            params = {'instType': inst_type}
            response = await self.exchange.public_get_public_instruments(params)
            
            if response.get('code') == '0':
                return response.get('data', [])
            else:
                raise Exception(f"API错误: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"获取交易工具失败: {str(e)}")
            return []
    
    async def get_account_balance(self, currency: str = None) -> Dict:
        """获取账户余额"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            params = {}
            if currency:
                params['ccy'] = currency
                
            response = await self.exchange.private_get_account_balance(params)
            
            if response.get('code') == '0':
                return response.get('data', [])
            else:
                raise Exception(f"API错误: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"获取账户余额失败: {str(e)}")
            return {"error": str(e)}
    
    async def get_market_ticker(self, symbol: str) -> Dict:
        """获取行情数据"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            params = {'instId': symbol}
            response = await self.exchange.public_get_market_ticker(params)
            
            if response.get('code') == '0':
                data = response.get('data', [])
                return data[0] if data else {}
            else:
                raise Exception(f"API错误: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"获取行情失败: {str(e)}")
            return {"error": str(e)}
    
    async def place_spot_order(self, symbol: str, side: str, amount: float, 
                              price: float = None, order_type: str = "limit") -> Dict:
        """现货下单"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            # 构建订单参数
            params = {
                'instId': symbol,
                'tdMode': 'cash',  # 现货交易模式
                'side': side.lower(),
                'ordType': order_type.lower(),
                'sz': str(amount)
            }
            
            if order_type.lower() == 'limit' and price:
                params['px'] = str(price)
            
            # 添加客户端订单ID
            params['clOrdId'] = f"okx_{int(time.time())}"
            
            response = await self.exchange.private_post_trade_order(params)
            
            if response.get('code') == '0':
                return response.get('data', [{}])[0]
            else:
                raise Exception(f"下单失败: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"下单失败: {str(e)}")
            return {"error": str(e)}
    
    async def get_order_info(self, order_id: str, symbol: str) -> Dict:
        """获取订单信息"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            params = {
                'instId': symbol,
                'ordId': order_id
            }
            
            response = await self.exchange.private_get_trade_order(params)
            
            if response.get('code') == '0':
                data = response.get('data', [])
                return data[0] if data else {}
            else:
                raise Exception(f"API错误: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"获取订单信息失败: {str(e)}")
            return {"error": str(e)}
    
    async def cancel_order(self, order_id: str, symbol: str) -> Dict:
        """撤销订单"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            params = {
                'instId': symbol,
                'ordId': order_id
            }
            
            response = await self.exchange.private_post_trade_cancel_order(params)
            
            if response.get('code') == '0':
                return response.get('data', [{}])[0]
            else:
                raise Exception(f"撤销订单失败: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"撤销订单失败: {str(e)}")
            return {"error": str(e)}
    
    async def get_order_history(self, symbol: str = None, limit: int = 100) -> List[Dict]:
        """获取历史订单"""
        try:
            if not self.exchange:
                raise Exception("交易所未初始化")
            
            params = {
                'instType': 'SPOT',
                'limit': str(limit)
            }
            
            if symbol:
                params['instId'] = symbol
            
            response = await self.exchange.private_get_trade_orders_history(params)
            
            if response.get('code') == '0':
                return response.get('data', [])
            else:
                raise Exception(f"API错误: {response.get('msg', '未知错误')}")
                
        except Exception as e:
            logger.error(f"获取历史订单失败: {str(e)}")
            return []
    
    async def close(self):
        """关闭连接"""
        if self.exchange:
            await self.exchange.close()
            self.connected = False
            logger.info("OKX API连接已关闭")

# 使用示例和测试函数
async def test_okx_api():
    """OKX API测试函数"""
    # 配置API密钥（请使用您的真实API密钥）
    config = OKXConfig(
        api_key="your_api_key_here",
        secret_key="your_secret_key_here", 
        passphrase="your_passphrase_here",
        is_sandbox=True  # 使用沙盒环境测试
    )
    
    api = OKXAPIManager(config)
    
    try:
        # 1. 初始化连接
        print("🔗 初始化OKX API连接...")
        if not await api.initialize():
            print("❌ 连接失败")
            return
        
        # 2. 获取系统状态
        print("\n📊 获取系统状态...")
        status = await api.get_system_status()
        print(f"系统状态: {json.dumps(status, indent=2)}")
        
        # 3. 获取账户配置
        print("\n⚙️ 获取账户配置...")
        account_config = await api.get_account_config()
        print(f"账户配置: {json.dumps(account_config, indent=2)}")
        
        # 4. 获取现货交易对
        print("\n📈 获取现货交易对...")
        instruments = await api.get_instruments("SPOT")
        print(f"现货交易对数量: {len(instruments)}")
        if instruments:
            btc_usdt = next((inst for inst in instruments if inst.get('instId') == 'BTC-USDT'), None)
            if btc_usdt:
                print(f"BTC-USDT配置: {json.dumps(btc_usdt, indent=2)}")
        
        # 5. 获取账户余额
        print("\n💰 获取账户余额...")
        balance = await api.get_account_balance()
        print(f"账户余额: {json.dumps(balance, indent=2)}")
        
        # 6. 获取BTC-USDT行情
        print("\n📊 获取BTC-USDT行情...")
        ticker = await api.get_market_ticker("BTC-USDT")
        print(f"BTC-USDT行情: {json.dumps(ticker, indent=2)}")
        
        # 7. 获取历史订单
        print("\n📜 获取历史订单...")
        history = await api.get_order_history("BTC-USDT", 10)
        print(f"历史订单数量: {len(history)}")
        
        print("\n✅ 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
    
    finally:
        await api.close()

if __name__ == "__main__":
    # 运行测试
    asyncio.run(test_okx_api())
