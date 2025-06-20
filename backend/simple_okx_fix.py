"""
简化版的OKX修复模块
专注于解决核心问题
"""

import ccxt
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class SimpleOKXExchange(ccxt.okx):
    """简化的OKX交易所修复类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化"""
        super().__init__(config or {})
        self._setup_proxy()
    
    def _setup_proxy(self):
        """设置代理"""
        proxy_config = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        if hasattr(self, 'session') and self.session:
            self.session.proxies = proxy_config
        elif hasattr(self, 'proxies'):
            self.proxies = proxy_config
        
        # 设置环境变量
        os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
        os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
        os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
        os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'
        
        logger.info("✅ 代理配置已设置")
    
    def parse_market(self, market):
        """修复的市场解析方法"""
        try:
            id = market.get('instId')
            base_id = market.get('baseCcy')
            quote_id = market.get('quoteCcy')
            
            # 使用安全的货币代码转换
            base = self.safe_currency_code(base_id)
            quote = self.safe_currency_code(quote_id)
            
            # 关键修复：确保base和quote不为None
            if not base or not quote:
                return None
            
            symbol = f"{base}/{quote}"
            
            return {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'settle': None,
                'baseId': base_id,
                'quoteId': quote_id,
                'settleId': None,
                'type': 'spot',
                'spot': True,
                'margin': False,
                'swap': False,
                'future': False,
                'option': False,
                'active': market.get('state') == 'live',
                'contract': False,
                'linear': None,
                'inverse': None,
                'taker': None,
                'maker': None,
                'contractSize': None,
                'expiry': None,
                'expiryDatetime': None,
                'strike': None,
                'optionType': None,
                'precision': {
                    'amount': self.safe_number(market, 'lotSz'),
                    'price': self.safe_number(market, 'tickSz'),
                },
                'limits': {
                    'amount': {'min': self.safe_number(market, 'minSz'), 'max': None},
                    'price': {'min': None, 'max': None},
                    'cost': {'min': None, 'max': None},
                },
                'info': market,
            }
        except Exception as e:
            logger.debug(f"解析市场失败 {market.get('instId', 'Unknown')}: {e}")
            return None
    
    def fetch_balance(self, params=None):
        """修复的余额获取方法"""
        try:
            return super().fetch_balance(params)
        except Exception as e:
            error_msg = str(e).lower()
            if 'password' in error_msg or 'passphrase' in error_msg:
                raise ValueError("❌ API配置缺少passphrase参数")
            elif 'signature' in error_msg:
                raise ValueError("❌ API签名验证失败，请检查API密钥")
            elif 'permission' in error_msg:
                raise ValueError("❌ API权限不足")
            else:
                raise


def create_simple_okx(api_key: str, api_secret: str, api_passphrase: str, sandbox: bool = False):
    """创建简化的OKX实例"""
    config = {
        'apiKey': api_key,
        'secret': api_secret,
        'passphrase': api_passphrase,
        'sandbox': sandbox,
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {
            'defaultType': 'spot',
        }
    }
    
    return SimpleOKXExchange(config)


def test_simple_okx():
    """测试简化的OKX实例"""
    logger.info("🚀 测试简化的OKX实例")
    
    # 您的API配置
    api_key = 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0'
    api_secret = 'CD6A497EEB00AA2DC60B2B0974DD2485'
    api_passphrase = 'vf5Y3UeUFiz6xfF!'
    
    try:
        # 创建实例
        exchange = create_simple_okx(api_key, api_secret, api_passphrase)
        
        # 测试服务器时间
        logger.info("🕐 测试服务器时间...")
        server_time = exchange.fetch_time()
        from datetime import datetime
        logger.info(f"✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
        
        # 测试ticker
        logger.info("📊 测试ticker...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        logger.info(f"✅ BTC/USDT: {ticker['last']}")
        
        # 测试余额
        logger.info("💰 测试余额...")
        try:
            balance = exchange.fetch_balance()
            logger.info("✅ 余额获取成功")
        except Exception as e:
            logger.error(f"❌ 余额获取失败: {e}")
        
        logger.info("🎉 简化测试完成!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_simple_okx()
