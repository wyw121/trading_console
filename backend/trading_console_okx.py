"""
最终的OKX API修复方案
整合SSR代理和CCXT修复，专门为trading_console项目设计
"""

import ccxt
import os
import requests
import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class TradingConsoleOKX:
    """Trading Console专用的OKX API封装类"""
    
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str, sandbox: bool = False):
        """
        初始化OKX API连接
        
        Args:
            api_key: OKX API密钥
            api_secret: OKX API密码
            api_passphrase: OKX API口令
            sandbox: 是否使用沙盒环境
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.sandbox = sandbox
        
        # 设置代理
        self._setup_proxy()
        
        # 创建交易所实例
        self.exchange = None
        self._create_exchange()
        
        logger.info("✅ TradingConsole OKX实例初始化完成")
    
    def _setup_proxy(self):
        """设置SSR代理"""
        proxy_url = 'socks5h://127.0.0.1:1080'
        
        # 设置环境变量
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        
        logger.info("✅ SSR代理配置完成")
    
    def _create_exchange(self):
        """创建CCXT交易所实例"""
        try:
            config = {
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'passphrase': self.api_passphrase,
                'sandbox': self.sandbox,
                'enableRateLimit': True,
                'timeout': 30000,
                'options': {
                    'defaultType': 'spot',
                },
                'verbose': False,
            }
            
            self.exchange = ccxt.okx(config)
            
            # 设置代理
            proxy_config = {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            }
            
            if hasattr(self.exchange, 'session') and self.exchange.session:
                self.exchange.session.proxies = proxy_config
            
            logger.info("✅ CCXT交易所实例创建完成")
            
        except Exception as e:
            logger.error(f"❌ 创建交易所实例失败: {e}")
            raise
    
    def test_connection(self) -> Dict[str, Any]:
        """
        测试连接状态
        
        Returns:
            连接测试结果
        """
        result = {
            'success': False,
            'message': '',
            'details': {}
        }
        
        try:
            # 测试公共API
            logger.info("🔍 测试公共API连接...")
            server_time = self.exchange.fetch_time()
            result['details']['server_time'] = datetime.fromtimestamp(server_time/1000)
            logger.info(f"✅ 服务器时间: {result['details']['server_time']}")
            
            # 测试私有API
            logger.info("🔍 测试私有API连接...")
            try:
                balance = self.exchange.fetch_balance()
                result['details']['balance_test'] = '成功'
                logger.info("✅ 账户余额获取成功")
            except Exception as e:
                result['details']['balance_test'] = f'失败: {str(e)}'
                logger.warning(f"⚠️ 账户余额获取失败: {e}")
            
            result['success'] = True
            result['message'] = 'OKX API连接成功'
            
        except Exception as e:
            result['message'] = f'连接失败: {str(e)}'
            logger.error(f"❌ 连接测试失败: {e}")
        
        return result
    
    def get_server_time(self) -> int:
        """获取服务器时间"""
        return self.exchange.fetch_time()
    
    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取ticker数据
        
        Args:
            symbol: 交易对符号，如 'BTC/USDT'
            
        Returns:
            ticker数据
        """
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"❌ 获取{symbol}的ticker失败: {e}")
            raise
    
    def get_balance(self) -> Dict[str, Any]:
        """
        获取账户余额
        
        Returns:
            账户余额数据
        """
        try:
            return self.exchange.fetch_balance()
        except Exception as e:
            error_msg = str(e).lower()
            if 'password' in error_msg or 'passphrase' in error_msg:
                raise ValueError("API配置缺少passphrase参数")
            elif 'signature' in error_msg:
                raise ValueError("API签名验证失败，请检查API密钥和secret")
            elif 'permission' in error_msg:
                raise ValueError("API权限不足，请检查API权限设置")
            else:
                logger.error(f"❌ 获取账户余额失败: {e}")
                raise
    
    def get_markets(self) -> Dict[str, Any]:
        """
        获取可用的交易对
        
        Returns:
            交易对字典
        """
        try:
            # 使用简单的方法获取部分交易对
            common_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
            markets = {}
            
            for pair in common_pairs:
                try:
                    ticker = self.exchange.fetch_ticker(pair)
                    markets[pair] = {
                        'symbol': pair,
                        'active': True,
                        'base': pair.split('/')[0],
                        'quote': pair.split('/')[1],
                        'last_price': ticker.get('last'),
                    }
                except:
                    # 如果获取失败，跳过这个交易对
                    continue
            
            logger.info(f"✅ 获取到 {len(markets)} 个交易对")
            return markets
            
        except Exception as e:
            logger.error(f"❌ 获取交易对失败: {e}")
            return {}
    
    def place_order(self, symbol: str, type: str, side: str, amount: float, price: float = None) -> Dict[str, Any]:
        """
        下单（只有读取权限，这个方法会抛出权限错误）
        
        Args:
            symbol: 交易对
            type: 订单类型 ('market' 或 'limit')
            side: 买卖方向 ('buy' 或 'sell')
            amount: 数量
            price: 价格（限价单需要）
            
        Returns:
            订单信息
        """
        # 由于您的API只有读取权限，这里会返回权限错误
        raise ValueError("当前API密钥只有读取权限，无法下单")


def create_okx_for_trading_console(api_key: str, api_secret: str, api_passphrase: str, sandbox: bool = False) -> TradingConsoleOKX:
    """
    为Trading Console创建OKX实例
    
    Args:
        api_key: API密钥
        api_secret: API密码  
        api_passphrase: API口令
        sandbox: 是否使用沙盒
        
    Returns:
        TradingConsoleOKX实例
    """
    return TradingConsoleOKX(api_key, api_secret, api_passphrase, sandbox)


def test_trading_console_okx():
    """测试Trading Console OKX实例"""
    logger.info("🚀 测试Trading Console OKX")
    
    # API配置
    api_key = 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0'
    api_secret = 'CD6A497EEB00AA2DC60B2B0974DD2485'
    api_passphrase = 'vf5Y3UeUFiz6xfF!'
    
    try:
        # 创建实例
        okx = create_okx_for_trading_console(api_key, api_secret, api_passphrase)
        
        # 测试连接
        connection_result = okx.test_connection()
        logger.info(f"连接测试结果: {connection_result}")
        
        if connection_result['success']:
            # 测试获取交易对
            markets = okx.get_markets()
            logger.info(f"可用交易对: {list(markets.keys())}")
            
            # 测试获取ticker
            if 'BTC/USDT' in markets:
                ticker = okx.get_ticker('BTC/USDT')
                logger.info(f"BTC/USDT价格: {ticker.get('last')}")
        
        return connection_result['success']
        
    except Exception as e:
        logger.error(f"❌ 测试失败: {e}")
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    test_trading_console_okx()
