#!/usr/bin/env python3
"""
OKX API连接管理器 - 实用版本
基于成功的代理测试结果
"""
import os
import requests
import hmac
import hashlib
import base64
import time
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OKXAPIManager:
    """OKX API管理器"""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str, 
                 use_proxy: bool = True, proxy_url: str = "socks5h://127.0.0.1:1080"):
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.base_url = "https://www.okx.com"
        
        # 设置代理
        if use_proxy:
            self.proxies = {
                'http': proxy_url,
                'https': proxy_url
            }
            # 同时设置环境变量
            os.environ['HTTP_PROXY'] = proxy_url
            os.environ['HTTPS_PROXY'] = proxy_url
        else:
            self.proxies = None
            # 清除代理环境变量
            for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
                if key in os.environ:
                    del os.environ[key]
    
    def _create_signature(self, timestamp: str, method: str, request_path: str, body: str = '') -> str:
        """创建OKX API签名"""
        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), 
                    message.encode('utf-8'),        signature = base64.b64encode(
            hmac.new(self.secret_key.encode('utf-8'), 
                    message.encode('utf-8'), 
                    hashlib.sha256).digest()
        ).decode('utf-8')
        return signature
    
    def _get_server_timestamp(self) -> str:
        """获取精确的时间戳，考虑网络延迟"""
        try:
            # 首先尝试获取服务器时间
            response = requests.get(f'{self.base_url}/api/v5/public/time', 
                                  proxies=self.proxies, 
                                  timeout=3)  # 减少超时时间
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == '0':
                    # 使用服务器时间戳，不加缓冲
                    server_ts = int(result['data'][0]['ts'])
                    logger.debug(f"使用服务器时间戳: {server_ts}")
                    return str(server_ts)
        except Exception as e:
            logger.warning(f"获取服务器时间失败，使用本地时间: {e}")
        
        # 备用方案：使用本地时间戳
        local_ts = int(time.time() * 1000)
        logger.debug(f"使用本地时间戳: {local_ts}")
        return str(local_ts)
        logger.debug(f"使用本地时间戳: {local_ts}")
        return str(local_ts)
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None, data: Dict = None) -> Dict:
        """发送API请求"""
        timestamp = self._get_server_timestamp()
        
        # 处理查询参数
        query_string = ''
        if params:
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        
        # 处理请求体
        body = ''
        if data:
            body = json.dumps(data)
        
        # 对于签名，使用原始endpoint + 查询参数（如果有的话）
        sign_path = endpoint
        if query_string:
            sign_path += f"?{query_string}"
        
        # 创建签名
        signature = self._create_signature(timestamp, method.upper(), sign_path, body)
        
        # 设置请求头
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
        
        # 构建完整URL
        url = f'{self.base_url}{sign_path}'
        
        try:
            logger.debug(f"OKX API请求: {method.upper()} {url}")
            logger.debug(f"Headers: {dict((k, v if k != 'OK-ACCESS-SIGN' else '***') for k, v in headers.items())}")
            
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, proxies=self.proxies, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, headers=headers, data=body, proxies=self.proxies, timeout=10)
            else:
                raise ValueError(f"不支持的HTTP方法: {method}")
            
            logger.debug(f"OKX API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.debug(f"OKX API响应: {result}")
                return result
            else:
                error_response = {
                    'code': str(response.status_code),
                    'msg': f'HTTP错误: {response.status_code}',
                    'data': None
                }
                
                # 尝试解析错误响应体
                try:
                    error_data = response.json()
                    if 'msg' in error_data:
                        error_response['msg'] = f"HTTP {response.status_code}: {error_data['msg']}"
                    logger.error(f"OKX API错误响应: {error_data}")
                except:
                    logger.error(f"OKX API错误: HTTP {response.status_code}, 响应体: {response.text}")
                
                return error_response
                
        except Exception as e:
            logger.error(f"API请求失败: {e}")
            return {
                'code': '-1',
                'msg': f'请求失败: {str(e)}',
                'data': None
            }
    
    def get_server_time(self) -> Dict:
        """获取服务器时间（公开API）"""
        try:
            response = requests.get(f'{self.base_url}/api/v5/public/time', 
                                  proxies=self.proxies, 
                                  timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {'code': str(response.status_code), 'msg': 'API访问失败', 'data': None}
        except Exception as e:
            return {'code': '-1', 'msg': str(e), 'data': None}
    
    def get_ticker(self, symbol: str = 'BTC-USDT') -> Dict:
        """获取价格信息（公开API）"""
        try:
            response = requests.get(f'{self.base_url}/api/v5/market/ticker',
                                  params={'instId': symbol},
                                  proxies=self.proxies, 
                                  timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {'code': str(response.status_code), 'msg': 'API访问失败', 'data': None}
        except Exception as e:            return {'code': '-1', 'msg': str(e), 'data': None}
    
    def get_balance(self) -> Dict:
        """获取账户余额（私有API）"""
        return self._make_request('GET', '/api/v5/account/balance')
    
    def get_balance_with_retry(self, max_retries: int = 3) -> Dict:
        """获取账户余额（带重试机制）"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"获取余额，尝试 {attempt + 1}/{max_retries}")
                
                # 每次重试都重新生成时间戳
                result = self._make_request('GET', '/api/v5/account/balance')
                
                if result.get('code') == '0':
                    logger.info("余额获取成功")
                    return result
                elif result.get('code') == '50102':  # 时间戳过期错误
                    logger.warning(f"时间戳过期，重试中... ({attempt + 1}/{max_retries})")
                    # 时间戳过期时，等待更长时间再重试
                    time.sleep(1.0)
                    last_error = result
                    continue
                elif result.get('code') == '50111':  # API key 错误
                    logger.error("API密钥无效，停止重试")
                    return result
                elif result.get('code') == '50113':  # 权限不足
                    logger.error("API权限不足，请检查API密钥权限设置")
                    return result
                else:
                    logger.error(f"余额获取失败: {result.get('msg', '未知错误')}")
                    last_error = result
                    # 对于其他错误，短暂等待后重试
                    if attempt < max_retries - 1:
                        time.sleep(0.5)
                    
            except Exception as e:
                logger.error(f"余额获取异常 (尝试 {attempt + 1}): {e}")
                last_error = {
                    'code': '-1',
                    'msg': f'请求异常: {str(e)}',
                    'data': None
                }
                if attempt < max_retries - 1:
                    time.sleep(0.5)
        
        # 返回最后一次的错误结果
        if last_error:
            return last_error
        
        return {
            'code': '-1',
            'msg': f'获取余额失败，已达到最大重试次数({max_retries})',
            'data': None
        }
    
    def test_connection(self) -> Dict:
        """测试连接"""
        result = {
            'public_api': False,
            'private_api': False,
            'error_messages': []
        }
        
        # 测试公开API
        try:
            time_result = self.get_server_time()
            if time_result.get('code') == '0':
                result['public_api'] = True
            else:
                result['error_messages'].append(f"公开API失败: {time_result.get('msg')}")
        except Exception as e:
            result['error_messages'].append(f"公开API异常: {str(e)}")
        
        # 测试私有API
        try:
            balance_result = self.get_balance()
            if balance_result.get('code') == '0':
                result['private_api'] = True
            else:
                result['error_messages'].append(f"私有API失败: {balance_result.get('msg')}")
        except Exception as e:
            result['error_messages'].append(f"私有API异常: {str(e)}")
        
        return result
    
    def debug_api_credentials(self) -> Dict:
        """调试API凭据和签名"""
        try:
            logger.info("开始调试API凭据...")
            
            # 检查API密钥格式
            api_key_valid = len(self.api_key) > 10 and '-' in self.api_key
            secret_valid = len(self.secret_key) > 10
            passphrase_valid = len(self.passphrase) > 0
            
            logger.info(f"API Key格式检查: {'✅' if api_key_valid else '❌'} (长度: {len(self.api_key)})")
            logger.info(f"Secret Key格式检查: {'✅' if secret_valid else '❌'} (长度: {len(self.secret_key)})")
            logger.info(f"Passphrase格式检查: {'✅' if passphrase_valid else '❌'} (长度: {len(self.passphrase)})")
            
            # 测试签名生成
            timestamp = self._get_server_timestamp()
            test_signature = self._create_signature(timestamp, 'GET', '/api/v5/account/balance', '')
            
            logger.info(f"时间戳: {timestamp}")
            logger.info(f"测试签名: {test_signature[:20]}...")
            
            return {
                'api_key_valid': api_key_valid,
                'secret_valid': secret_valid,
                'passphrase_valid': passphrase_valid,
                'timestamp': timestamp,
                'signature_generated': bool(test_signature)
            }
            
        except Exception as e:
            logger.error(f"调试API凭据失败: {e}")
            return {'error': str(e)}

# 全局实例
okx_manager = None

def create_okx_manager(api_key: str, secret_key: str, passphrase: str) -> OKXAPIManager:
    """创建OKX管理器实例"""
    global okx_manager
    okx_manager = OKXAPIManager(api_key, secret_key, passphrase)
    return okx_manager

def get_okx_manager() -> Optional[OKXAPIManager]:
    """获取OKX管理器实例"""
    return okx_manager

if __name__ == "__main__":
    # 测试代码
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
    
    print("测试连接...")
    result = manager.test_connection()
    print(f"连接测试结果: {result}")
    
    if result['public_api']:
        print("\n测试获取价格...")
        ticker = manager.get_ticker('BTC-USDT')
        print(f"BTC价格: {ticker}")
        
    if result['private_api']:
        print("\n测试获取余额...")
        balance = manager.get_balance()
        print(f"账户余额: {balance}")
