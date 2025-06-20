"""
SSR代理配置模块
专门用于配置Python通过SSR访问被限制的API服务
支持requests、ccxt、urllib等多种HTTP客户端
"""

import os
import socket
import socks
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.connection import create_connection
from urllib3.poolmanager import PoolManager
import logging

logger = logging.getLogger(__name__)

class SSRProxyConfig:
    """SSR代理配置类"""
    
    def __init__(self, 
                 proxy_host: str = "127.0.0.1", 
                 proxy_port: int = 1080,
                 proxy_type: str = "socks5"):
        """
        初始化SSR代理配置
        
        Args:
            proxy_host: 代理服务器地址
            proxy_port: 代理服务器端口
            proxy_type: 代理类型 (socks5, socks4, http)
        """
        self.proxy_host = proxy_host
        self.proxy_port = proxy_port
        self.proxy_type = proxy_type.lower()
        
        # 代理URL格式
        if self.proxy_type in ['socks5', 'socks5h']:
            self.proxy_url = f"socks5h://{proxy_host}:{proxy_port}"
        elif self.proxy_type == 'socks4':
            self.proxy_url = f"socks4://{proxy_host}:{proxy_port}"
        elif self.proxy_type == 'http':
            self.proxy_url = f"http://{proxy_host}:{proxy_port}"
        else:
            raise ValueError(f"不支持的代理类型: {proxy_type}")
        
        logger.info(f"SSR代理配置: {self.proxy_url}")
    
    def get_requests_proxies(self) -> dict:
        """
        获取requests库使用的代理配置
        
        Returns:
            代理配置字典
        """
        return {
            'http': self.proxy_url,
            'https': self.proxy_url
        }
    
    def get_environment_vars(self) -> dict:
        """
        获取环境变量格式的代理配置
        
        Returns:
            环境变量字典
        """
        return {
            'HTTP_PROXY': self.proxy_url,
            'HTTPS_PROXY': self.proxy_url,
            'http_proxy': self.proxy_url,
            'https_proxy': self.proxy_url
        }
    
    def set_environment_vars(self):
        """设置代理环境变量"""
        env_vars = self.get_environment_vars()
        for key, value in env_vars.items():
            os.environ[key] = value
        logger.info("✅ 代理环境变量已设置")
    
    def get_socks_proxy_settings(self) -> tuple:
        """
        获取socks代理设置
        
        Returns:
            (proxy_type, host, port) 元组
        """
        if self.proxy_type in ['socks5', 'socks5h']:
            return (socks.SOCKS5, self.proxy_host, self.proxy_port)
        elif self.proxy_type == 'socks4':
            return (socks.SOCKS4, self.proxy_host, self.proxy_port)
        elif self.proxy_type == 'http':
            return (socks.HTTP, self.proxy_host, self.proxy_port)
        else:
            raise ValueError(f"不支持的代理类型: {self.proxy_type}")
    
    def patch_socket(self):
        """
        使用代理替换全局socket（Monkey Patching）
        这会影响所有使用socket的库
        """
        try:
            proxy_type, host, port = self.get_socks_proxy_settings()
            socks.set_default_proxy(proxy_type, host, port)
            socket.socket = socks.socksocket
            logger.info("✅ Socket已全局代理化")
        except Exception as e:
            logger.error(f"❌ Socket代理化失败: {e}")
            raise
    
    def unpatch_socket(self):
        """恢复原始socket"""
        socket.socket = socket._realsocket if hasattr(socket, '_realsocket') else socket.socket
        logger.info("✅ Socket已恢复原始状态")


class SSRHTTPAdapter(HTTPAdapter):
    """
    支持SSR代理的HTTP适配器
    用于requests库的高级代理配置
    """
    
    def __init__(self, proxy_config: SSRProxyConfig, *args, **kwargs):
        self.proxy_config = proxy_config
        super().__init__(*args, **kwargs)


def create_ssr_session(proxy_config: SSRProxyConfig = None) -> requests.Session:
    """
    创建配置了SSR代理的requests会话
    
    Args:
        proxy_config: 代理配置，如果为None则使用默认配置
        
    Returns:
        配置了代理的requests.Session对象
    """
    if proxy_config is None:
        proxy_config = SSRProxyConfig()
    
    session = requests.Session()
    
    # 设置代理
    session.proxies = proxy_config.get_requests_proxies()
    
    # 设置超时
    session.timeout = 30
    
    # 设置重试策略
    adapter = SSRHTTPAdapter(proxy_config, max_retries=3)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    logger.info("✅ SSR代理会话已创建")
    return session


def test_ssr_connection(proxy_config: SSRProxyConfig = None) -> bool:
    """
    测试SSR代理连接
    
    Args:
        proxy_config: 代理配置
        
    Returns:
        连接是否成功
    """
    if proxy_config is None:
        proxy_config = SSRProxyConfig()
    
    try:
        # 测试基本代理连接
        session = create_ssr_session(proxy_config)
        
        # 测试IP检查
        logger.info("🔍 测试代理连接...")
        response = session.get('http://httpbin.org/ip', timeout=10)
        
        if response.status_code == 200:
            ip_info = response.json()
            current_ip = ip_info.get('origin')
            logger.info(f"✅ 代理连接成功，当前IP: {current_ip}")
            
            # 测试访问OKX API
            logger.info("🔍 测试OKX API访问...")
            okx_response = session.get('https://www.okx.com/api/v5/public/time', timeout=15)
            
            if okx_response.status_code == 200:
                okx_data = okx_response.json()
                logger.info(f"✅ OKX API访问成功: {okx_data}")
                return True
            else:
                logger.error(f"❌ OKX API访问失败，状态码: {okx_response.status_code}")
                return False
        else:
            logger.error(f"❌ 代理连接失败，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 代理连接测试失败: {e}")
        return False


def configure_ccxt_proxy(exchange, proxy_config: SSRProxyConfig = None):
    """
    为CCXT交易所实例配置代理
    
    Args:
        exchange: CCXT交易所实例
        proxy_config: 代理配置
    """
    if proxy_config is None:
        proxy_config = SSRProxyConfig()
    
    try:
        # 方法1: 直接设置proxies属性
        if hasattr(exchange, 'proxies'):
            exchange.proxies = proxy_config.get_requests_proxies()
            logger.info("✅ CCXT代理设置方法1: proxies属性")
        
        # 方法2: 设置session.proxies
        if hasattr(exchange, 'session') and exchange.session:
            exchange.session.proxies = proxy_config.get_requests_proxies()
            logger.info("✅ CCXT代理设置方法2: session.proxies")
        
        # 方法3: 设置环境变量（全局影响）
        proxy_config.set_environment_vars()
        
    except Exception as e:
        logger.error(f"❌ CCXT代理配置失败: {e}")
        raise


def create_okx_with_ssr(api_config: dict, proxy_config: SSRProxyConfig = None):
    """
    创建配置了SSR代理的OKX交易所实例
    
    Args:
        api_config: OKX API配置
        proxy_config: 代理配置
        
    Returns:
        配置了代理的OKX交易所实例
    """
    if proxy_config is None:
        proxy_config = SSRProxyConfig()
    
    # 导入修复后的OKX交易所
    from fixed_ccxt import FixedOKXExchange
    
    try:
        # 设置环境变量
        proxy_config.set_environment_vars()
        
        # 创建交易所实例
        exchange = FixedOKXExchange(api_config)
        
        # 配置代理
        configure_ccxt_proxy(exchange, proxy_config)
        
        logger.info("✅ 配置SSR代理的OKX交易所实例已创建")
        return exchange
        
    except Exception as e:
        logger.error(f"❌ 创建SSR代理OKX实例失败: {e}")
        raise


# 默认代理配置实例
default_ssr_config = SSRProxyConfig()

# 便捷函数
def get_default_proxies() -> dict:
    """获取默认代理配置"""
    return default_ssr_config.get_requests_proxies()

def set_global_proxy():
    """设置全局代理"""
    default_ssr_config.set_environment_vars()
    default_ssr_config.patch_socket()

def test_connection() -> bool:
    """测试默认代理连接"""
    return test_ssr_connection(default_ssr_config)


if __name__ == "__main__":
    # 测试SSR代理配置
    logging.basicConfig(level=logging.INFO)
    
    print("🚀 SSR代理配置测试")
    print("=" * 50)
    
    # 测试连接
    if test_connection():
        print("🎉 SSR代理配置成功！")
    else:
        print("❌ SSR代理配置失败！")
