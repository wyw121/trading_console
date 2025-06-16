"""
模拟OKX API数据
当无法连接真实API时使用
"""
import asyncio
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MockOKXExchange:
    """模拟OKX交易所"""
    
    def __init__(self, config: dict):
        self.config = config
        self.id = "okx"
        self.markets = self._generate_mock_markets()
        
    def _generate_mock_markets(self):
        """生成模拟市场数据"""
        return {
            'BTC/USDT': {
                'id': 'BTC-USDT',
                'symbol': 'BTC/USDT',
                'base': 'BTC',
                'quote': 'USDT',
                'active': True,
                'type': 'spot',
                'spot': True,
                'future': False,
                'option': False,
                'contract': False,
            },
            'ETH/USDT': {
                'id': 'ETH-USDT', 
                'symbol': 'ETH/USDT',
                'base': 'ETH',
                'quote': 'USDT',
                'active': True,
                'type': 'spot',
                'spot': True,
                'future': False,
                'option': False,
                'contract': False,
            },
            # 添加更多模拟交易对...
        }
    
    async def load_markets(self):
        """模拟加载市场"""
        await asyncio.sleep(0.1)  # 模拟网络延迟
        logger.info("模拟: 加载市场数据成功")
        return self.markets
    
    async def fetch_balance(self):
        """模拟获取余额"""
        await asyncio.sleep(0.2)  # 模拟网络延迟
        
        # 模拟测试环境余额（通常为0或少量测试币）
        mock_balance = {
            'info': {'code': '0', 'msg': '', 'data': []},
            'free': {
                'USDT': 1000.0,  # 模拟测试USDT
                'BTC': 0.01,     # 模拟测试BTC
                'ETH': 0.1,      # 模拟测试ETH
            },
            'used': {
                'USDT': 0.0,
                'BTC': 0.0,
                'ETH': 0.0,
            },
            'total': {
                'USDT': 1000.0,
                'BTC': 0.01,
                'ETH': 0.1,
            }
        }
        
        logger.info("模拟: 获取余额成功")
        return mock_balance
    
    async def fetch_ticker(self, symbol='BTC/USDT'):
        """模拟获取行情"""
        await asyncio.sleep(0.1)
        
        # 模拟BTC价格
        import random
        base_price = 45000
        price = base_price + random.randint(-1000, 1000)
        
        mock_ticker = {
            'symbol': symbol,
            'timestamp': int(datetime.now().timestamp() * 1000),
            'datetime': datetime.now().isoformat(),
            'high': price + 500,
            'low': price - 500,
            'bid': price - 1,
            'ask': price + 1,
            'last': price,
            'close': price,
            'open': price - 100,
            'change': 100,
            'percentage': 0.23,
            'average': price,
            'baseVolume': 1234.56,
            'quoteVolume': price * 1234.56,
        }
        
        logger.info(f"模拟: 获取{symbol}行情成功, 价格: ${price}")
        return mock_ticker
    
    # 模拟API调用方法
    async def public_get_public_time(self):
        """模拟获取服务器时间"""
        return {
            'code': '0',
            'msg': '',
            'data': [{'ts': str(int(datetime.now().timestamp() * 1000))}]
        }
    
    async def private_get_account_balance(self):
        """模拟获取账户余额API"""
        balance = await self.fetch_balance()
        return {
            'code': '0',
            'msg': '',
            'data': [{
                'totalEq': '1450.5',  # 总权益USD
                'details': [
                    {
                        'ccy': 'USDT',
                        'eq': '1000',
                        'availEq': '1000', 
                        'frozenBal': '0',
                    },
                    {
                        'ccy': 'BTC',
                        'eq': '0.01',
                        'availEq': '0.01',
                        'frozenBal': '0',
                    },
                    {
                        'ccy': 'ETH', 
                        'eq': '0.1',
                        'availEq': '0.1',
                        'frozenBal': '0',
                    }
                ]
            }]
        }
    
    async def private_get_account_config(self):
        """模拟获取账户配置"""
        return {
            'code': '0',
            'msg': '',
            'data': [{
                'acctLv': '1',  # 简单模式
                'posMode': 'net_mode',  # 净头寸模式
                'autoLoan': False,
                'greeksType': 'PA',
                'level': 'Lv1',
                'levelTmp': '',
                'ctIsoMode': 'automatic',
                'mgnIsoMode': 'automatic',
                'spotOffsetType': '',
                'roleType': '0',
                'traderInsts': [],
                'opAuth': '0',
                'kycLv': '2',
                'ip': '',
                'perm': 'read_only',  # 只读权限
                'label': 'trading',
                'uid': '12345678'
            }]
        }

class MockExchangeManager:
    """模拟交易所管理器"""
    
    def __init__(self):
        self.mock_exchanges = {}
        
    async def create_mock_exchange(self, exchange_name: str, config: dict):
        """创建模拟交易所"""
        if exchange_name.lower() in ['okx', 'okex']:
            return MockOKXExchange(config)
        else:
            raise ValueError(f"不支持的模拟交易所: {exchange_name}")
    
    async def test_mock_connection(self, exchange_name: str, api_key: str, 
                                  api_secret: str, api_passphrase: str = None, 
                                  is_testnet: bool = False) -> Dict:
        """模拟测试连接"""
        try:
            logger.info(f"模拟测试{exchange_name}连接...")
            
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'passphrase': api_passphrase,
                'sandbox': is_testnet,
            }
            
            # 创建模拟交易所
            exchange = await self.create_mock_exchange(exchange_name, config)
            
            # 模拟测试
            await exchange.load_markets()
            balance = await exchange.fetch_balance()
            
            return {
                "success": True,
                "message": f"模拟连接{exchange_name}成功 (这是模拟数据)",
                "data": {
                    "exchange": exchange_name,
                    "testnet": is_testnet,
                    "server_time": int(datetime.now().timestamp() * 1000),
                    "total_balance_usd": 1450.5,  # 模拟总余额
                    "available_markets": len(exchange.markets),
                    "currencies": list(balance['total'].keys()),
                    "mock": True  # 标识这是模拟数据
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"模拟连接失败: {str(e)}",
                "data": None
            }

# 全局模拟管理器实例
mock_exchange_manager = MockExchangeManager()

async def test_mock_system():
    """测试模拟系统"""
    print("🎭 测试模拟OKX系统...")
    print("=" * 50)
    
    # 使用您的API密钥测试模拟系统
    result = await mock_exchange_manager.test_mock_connection(
        exchange_name="okx",
        api_key="edb07d2e-8fb5-46e8-84b8-5e1795c71ac0",
        api_secret="CD6A497EEB00AA2DC60B2B0974DD2485", 
        api_passphrase="vf5Y3UeUFiz6xfF!",
        is_testnet=True
    )
    
    if result["success"]:
        print("✅ 模拟系统测试成功!")
        print(f"   消息: {result['message']}")
        print(f"   数据: {result['data']}")
        
        # 测试获取余额
        config = {
            'apiKey': "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0",
            'secret': "CD6A497EEB00AA2DC60B2B0974DD2485",
            'passphrase': "vf5Y3UeUFiz6xfF!",
            'sandbox': True,
        }
        
        exchange = MockOKXExchange(config)
        balance = await exchange.fetch_balance()
        print(f"\n💰 模拟余额:")
        for currency, amount in balance['total'].items():
            if amount > 0:
                print(f"   {currency}: {amount}")
                
    else:
        print("❌ 模拟系统测试失败!")
        print(f"   错误: {result['message']}")

if __name__ == "__main__":
    asyncio.run(test_mock_system())
