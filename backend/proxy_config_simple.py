"""
简化代理配置 - 解决DNS问题
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ProxyConfig:
    def __init__(self):
        self.proxy_enabled = os.getenv('USE_PROXY', 'false').lower() == 'true'
        self.proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
        self.proxy_port = int(os.getenv('PROXY_PORT', '1080'))
        self.proxy_type = os.getenv('PROXY_TYPE', 'socks5')
        
        print(f"代理配置: enabled={self.proxy_enabled}, {self.proxy_type}://{self.proxy_host}:{self.proxy_port}")
    
    def get_proxy_dict(self):
        if not self.proxy_enabled:
            return None
        
        # 使用HTTP代理替代SOCKS5来避免DNS问题
        proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_ccxt_proxy_config(self):
        if not self.proxy_enabled:
            return {}
        
        return {
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 2000,
            'headers': {
                'User-Agent': 'Trading Console/1.0'
            }
        }
    
    def create_requests_session(self):
        """创建配置好的requests会话"""
        session = requests.Session()
        
        if self.proxy_enabled:
            # 使用系统环境变量设置代理
            os.environ['HTTP_PROXY'] = f'socks5://{self.proxy_host}:{self.proxy_port}'
            os.environ['HTTPS_PROXY'] = f'socks5://{self.proxy_host}:{self.proxy_port}'
        
        session.verify = False  # 临时跳过SSL验证
        return session

proxy_config = ProxyConfig()
