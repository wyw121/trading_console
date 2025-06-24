"""
OKX API 认证修复器
解决时间戳和权限验证问题
"""
import hmac
import hashlib
import base64
import time
import json
from datetime import datetime, timezone
import requests
import os
from dotenv import load_dotenv

class OKXAuthFixer:
    """OKX API认证修复器"""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str, is_testnet: bool = False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.is_testnet = is_testnet
        
        # 设置基础URL
        if is_testnet:
            self.base_url = "https://www.okx.com"  # OKX实际没有公开的测试网
        else:
            self.base_url = "https://www.okx.com"
    
    def get_timestamp(self) -> str:
        """获取正确格式的时间戳"""
        # OKX需要ISO格式的时间戳
        return datetime.now(timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z')
    
    def sign(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """生成OKX API签名"""
        # 构建签名字符串
        message = timestamp + method.upper() + request_path + body
        
        # 使用HMAC-SHA256生成签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Base64编码
        return base64.b64encode(signature).decode('utf-8')
    
    def get_headers(self, method: str, request_path: str, body: str = '') -> dict:
        """获取完整的请求头"""
        timestamp = self.get_timestamp()
        signature = self.sign(timestamp, method, request_path, body)
        
        return {
            'Content-Type': 'application/json',
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'x-simulated-trading': '1' if self.is_testnet else '0'
        }
    
    def test_auth(self) -> dict:
        """测试API认证"""
        try:
            # 使用账户信息接口测试认证
            request_path = '/api/v5/account/config'
            headers = self.get_headers('GET', request_path)
            
            # 设置代理（如果需要）
            proxies = self._get_proxies()
            
            response = requests.get(
                f"{self.base_url}{request_path}",
                headers=headers,
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    return {
                        'success': True,
                        'message': '认证成功',
                        'data': data.get('data', [])
                    }
                else:
                    return {
                        'success': False,
                        'message': f"API错误: {data.get('msg', 'Unknown error')}",
                        'code': data.get('code')
                    }
            else:
                return {
                    'success': False,
                    'message': f"HTTP错误: {response.status_code}",
                    'response': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'message': f"连接错误: {str(e)}"
            }
    
    def _get_proxies(self) -> dict:
        """获取代理设置"""
        load_dotenv()
        
        use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
        if not use_proxy:
            return None
        
        proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
        proxy_port = os.getenv('PROXY_PORT', '1080')
        proxy_type = os.getenv('PROXY_TYPE', 'socks5')
        
        if proxy_type == 'socks5':
            proxy_url = f"socks5h://{proxy_host}:{proxy_port}"
        else:
            proxy_url = f"{proxy_type}://{proxy_host}:{proxy_port}"
        
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_balance(self) -> dict:
        """获取账户余额"""
        try:
            request_path = '/api/v5/account/balance'
            headers = self.get_headers('GET', request_path)
            proxies = self._get_proxies()
            
            response = requests.get(
                f"{self.base_url}{request_path}",
                headers=headers,
                proxies=proxies,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    return {
                        'success': True,
                        'message': '获取余额成功',
                        'data': data.get('data', [])
                    }
                else:
                    # 提供详细的错误信息和建议
                    error_code = data.get('code', '')
                    error_msg = data.get('msg', 'Unknown error')
                    
                    suggestion = ""
                    if error_code == '50111':
                        suggestion = "请检查API Key是否正确"
                    elif error_code == '50112':
                        suggestion = "请检查时间戳和系统时间"
                    elif error_code == '50113':
                        suggestion = "请检查API签名算法"
                    elif error_code == '50114':
                        suggestion = "请检查请求头中的Passphrase"
                    elif error_code == '50102':
                        suggestion = "时间戳错误，请检查系统时间"
                    elif error_code == '50001':
                        suggestion = "API密钥权限不足，请检查API设置"
                    
                    return {
                        'success': False,
                        'message': f"API错误 {error_code}: {error_msg}",
                        'code': error_code,
                        'suggestion': suggestion
                    }
            elif response.status_code == 401:
                return {
                    'success': False,
                    'message': "API认证失败，请检查API密钥、Secret和Passphrase是否正确",
                    'code': '401',
                    'suggestion': "请确认API密钥有效并且具有读取权限，检查IP白名单设置"
                }
            else:
                return {
                    'success': False,
                    'message': f"HTTP错误: {response.status_code}",
                    'response': response.text[:200],
                    'suggestion': "请检查网络连接和API端点"
                }
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': "请求超时",
                'suggestion': "请检查网络连接或代理设置"
            }
        except Exception as e:
            return {
                'success': False,
                'message': f"获取余额失败: {str(e)}",
                'suggestion': "请检查网络连接和API配置"
            }

def test_okx_auth_fix():
    """测试OKX认证修复"""
    print("🔧 OKX API 认证修复测试")
    print("=" * 50)
    
    # 这里需要使用真实的API凭据
    # 注意：请确保这些是测试凭据或者有适当的权限
    api_key = "your_api_key_here"
    secret_key = "your_secret_key_here" 
    passphrase = "your_passphrase_here"
    is_testnet = True
    
    if api_key == "your_api_key_here":
        print("⚠️  请先在代码中设置真实的API凭据")
        return
    
    # 创建认证修复器
    auth_fixer = OKXAuthFixer(api_key, secret_key, passphrase, is_testnet)
    
    # 测试认证
    print("1. 测试API认证...")
    auth_result = auth_fixer.test_auth()
    if auth_result['success']:
        print(f"   ✅ 认证成功: {auth_result['message']}")
    else:
        print(f"   ❌ 认证失败: {auth_result['message']}")
        if 'suggestion' in auth_result:
            print(f"   💡 建议: {auth_result['suggestion']}")
        return
    
    # 测试余额获取
    print("\n2. 测试余额获取...")
    balance_result = auth_fixer.get_balance()
    if balance_result['success']:
        print(f"   ✅ 余额获取成功: {balance_result['message']}")
        balance_data = balance_result.get('data', [])
        if balance_data:
            print(f"   📊 账户数量: {len(balance_data)}")
        else:
            print("   ℹ️  暂无余额数据")
    else:
        print(f"   ❌ 余额获取失败: {balance_result['message']}")
        if 'suggestion' in balance_result:
            print(f"   💡 建议: {balance_result['suggestion']}")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_okx_auth_fix()
