"""
代理配置模块
支持SOCKS5代理配置，适配ShadowsocksR等代理工具
"""
import os
import logging
from typing import Dict, Optional
from dotenv import load_dotenv

# 确保加载环境变量
load_dotenv()

logger = logging.getLogger(__name__)

class ProxyConfig:
    """代理配置管理"""
    
    def __init__(self):
        # 从环境变量读取代理配置
        self.proxy_enabled = os.getenv('USE_PROXY', 'false').lower() == 'true'
        self.proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
        self.proxy_port = int(os.getenv('PROXY_PORT', '1080'))
        self.proxy_type = os.getenv('PROXY_TYPE', 'socks5')  # socks5, http, https
        self.proxy_username = os.getenv('PROXY_USERNAME', '')
        self.proxy_password = os.getenv('PROXY_PASSWORD', '')
        
        logger.info(f"代理配置: enabled={self.proxy_enabled}, type={self.proxy_type}, host={self.proxy_host}, port={self.proxy_port}")
    
    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """获取requests库使用的代理字典格式"""
        if not self.proxy_enabled:
            return None
        
        try:
            # 构建代理URL
            if self.proxy_username and self.proxy_password:
                auth_part = f"{self.proxy_username}:{self.proxy_password}@"
            else:
                auth_part = ""
            
            if self.proxy_type.lower() == 'socks5':
                proxy_url = f"socks5://{auth_part}{self.proxy_host}:{self.proxy_port}"
            elif self.proxy_type.lower() == 'http':
                proxy_url = f"http://{auth_part}{self.proxy_host}:{self.proxy_port}"
            elif self.proxy_type.lower() == 'https':
                proxy_url = f"https://{auth_part}{self.proxy_host}:{self.proxy_port}"
            else:
                logger.error(f"不支持的代理类型: {self.proxy_type}")
                return None
            
            proxy_dict = {
                'http': proxy_url,
                'https': proxy_url
            }            
            logger.info(f"生成代理配置: {proxy_dict}")
            return proxy_dict
            
        except Exception as e:
            logger.error(f"构建代理配置失败: {str(e)}")
            return None
    
    def get_ccxt_proxy_config(self) -> Dict:
        """获取CCXT库使用的代理配置"""
        if not self.proxy_enabled:
            return {}
        
        try:
            proxy_dict = self.get_proxy_dict()
            if not proxy_dict:
                return {}
            
            # CCXT代理配置 - 使用不同的方式
            config = {
                'timeout': 30000,  # 30秒超时
                'enableRateLimit': True,
                'rateLimit': 1200,  # 适当增加请求间隔
                'agent': False,  # 禁用默认agent
                'headers': {
                    'User-Agent': 'Trading Console/1.0'
                }
            }
            
            # 对于requests库的代理设置
            if self.proxy_type.lower() == 'socks5':
                config['proxies'] = proxy_dict
                config['session'] = self._create_proxy_session()
            
            logger.info("生成CCXT代理配置成功")
            return config
            
        except Exception as e:
            logger.error(f"构建CCXT代理配置失败: {str(e)}")
            return {}
    
    def _create_proxy_session(self):
        """创建带代理的requests会话"""
        import requests
        session = requests.Session()
        proxy_dict = self.get_proxy_dict()
        if proxy_dict:
            session.proxies.update(proxy_dict)
        return session

# 全局代理配置实例
proxy_config = ProxyConfig()

def test_proxy_connection() -> bool:
    """测试代理连接"""
    if not proxy_config.proxy_enabled:
        logger.info("代理未启用，跳过代理测试")
        return True
    
    try:
        import requests
        
        proxy_dict = proxy_config.get_proxy_dict()
        if not proxy_dict:
            logger.error("无法获取代理配置")
            return False
        
        # 测试连接到Google
        test_urls = [
            'https://www.google.com',
            'https://httpbin.org/ip',
            'https://www.okx.com'
        ]
        
        for url in test_urls:
            try:
                logger.info(f"测试代理连接: {url}")
                response = requests.get(
                    url, 
                    proxies=proxy_dict, 
                    timeout=10,
                    headers={'User-Agent': 'Trading Console/1.0'}
                )
                
                if response.status_code == 200:
                    logger.info(f"代理连接测试成功: {url}")
                    if 'httpbin.org' in url:
                        logger.info(f"外部IP: {response.json().get('origin', 'unknown')}")
                    return True
                else:
                    logger.warning(f"代理连接测试失败: {url}, 状态码: {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"代理连接测试失败: {url}, 错误: {str(e)}")
                continue
        
        logger.error("所有代理连接测试都失败")
        return False
        
    except Exception as e:
        logger.error(f"代理连接测试异常: {str(e)}")
        return False

if __name__ == "__main__":
    # 测试代理配置
    logging.basicConfig(level=logging.INFO)
    
    print("=== 代理配置信息 ===")
    print(f"代理启用: {proxy_config.proxy_enabled}")
    print(f"代理类型: {proxy_config.proxy_type}")
    print(f"代理地址: {proxy_config.proxy_host}:{proxy_config.proxy_port}")
    
    if proxy_config.proxy_enabled:
        print(f"Requests代理配置: {proxy_config.get_proxy_dict()}")
        print(f"CCXT代理配置: {proxy_config.get_ccxt_proxy_config()}")
        
        print("\n=== 测试代理连接 ===")
        success = test_proxy_connection()
        print(f"代理连接测试结果: {'成功' if success else '失败'}")
