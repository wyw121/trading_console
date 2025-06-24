#!/usr/bin/env python3
"""
交易所数据加载问题诊断脚本
"""
import os
import sys
import requests
import time
from datetime import datetime

def test_backend_auth():
    """测试后端认证功能"""
    print("=== 后端认证测试 ===")
    
    base_url = "http://localhost:8000"
    
    # 1. 测试用户注册/登录
    print("1. 测试用户认证...")
      # 注册测试用户
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com', 
        'password': 'testpass123'
    }
    
    try:
        # 注册接口使用JSON数据，不使用代理
        response = requests.post(f'{base_url}/api/auth/register', json=register_data, timeout=5, proxies={'http': None, 'https': None})
        if response.status_code == 200:
            print("   ✅ 用户注册成功")
        elif "already exists" in response.text or "already registered" in response.text:
            print("   ℹ️  用户已存在")
        else:
            print(f"   ⚠️  注册响应: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        print(f"   ❌ 注册失败: {e}")
        return None
    
    # 登录获取token (使用表单数据格式)
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    try:
        # OAuth2PasswordRequestForm 需要表单数据而不是JSON，不使用代理
        response = requests.post(f'{base_url}/api/auth/login', data=login_data, timeout=5, proxies={'http': None, 'https': None})
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"   ✅ 登录成功，token: {token[:20]}...")
            return token
        else:
            print(f"   ❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ 登录请求失败: {e}")
        return None

def test_exchanges_api(token):
    """测试交易所API"""
    print("\n=== 交易所API测试 ===")
    
    if not token:
        print("❌ 没有有效token，跳过测试")
        return
    
    base_url = "http://localhost:8000"
    headers = {'Authorization': f'Bearer {token}'}
      # 测试账户列表
    print("2. 测试账户列表API...")
    try:
        start_time = time.time()
        response = requests.get(f'{base_url}/api/exchanges/', headers=headers, timeout=8, proxies={'http': None, 'https': None})
        response_time = time.time() - start_time
        
        print(f"   响应时间: {response_time:.2f}秒")
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            accounts = response.json()
            print(f"   ✅ 成功获取 {len(accounts)} 个账户")
            
            # 测试每个账户的余额
            if accounts:
                print("\n3. 测试账户余额API...")
                for i, account in enumerate(accounts[:2]):  # 只测试前2个账户
                    account_id = account.get('id')
                    exchange_name = account.get('exchange_name')
                    
                    print(f"   测试账户 {account_id} ({exchange_name})...")
                    try:
                        start_time = time.time()
                        response = requests.get(
                            f'{base_url}/api/exchanges/accounts/{account_id}/balance',
                            headers=headers,
                            timeout=10,
                            proxies={'http': None, 'https': None}
                        )
                        response_time = time.time() - start_time
                        
                        print(f"      响应时间: {response_time:.2f}秒")
                        
                        if response.status_code == 200:
                            data = response.json()
                            success = data.get('success', False)
                            message = data.get('message', '')
                            
                            if success:
                                print(f"      ✅ 余额获取成功: {message}")
                            else:
                                print(f"      ⚠️  余额获取失败: {message}")
                                error_data = data.get('data', {})
                                if 'error_type' in error_data:
                                    print(f"      错误类型: {error_data['error_type']}")
                        else:
                            print(f"      ❌ 请求失败: {response.status_code}")
                            
                    except Exception as e:
                        print(f"      ❌ 余额API异常: {e}")
            else:
                print("   ℹ️  没有配置的交易所账户")
        else:
            print(f"   ❌ 账户列表获取失败: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"   ❌ 账户列表API异常: {e}")

def check_okx_configuration():
    """检查OKX配置"""
    print("\n=== OKX配置检查 ===")
    
    # 检查环境变量
    print("4. 检查代理配置...")
    
    env_vars = ['USE_PROXY', 'PROXY_HOST', 'PROXY_PORT', 'HTTP_PROXY', 'HTTPS_PROXY']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"   {var}: {value}")
        else:
            print(f"   {var}: 未设置")
      # 测试OKX连接
    print("\n5. 测试OKX连接...")
    try:
        # 重新加载环境变量以获取正确的代理设置
        from dotenv import load_dotenv
        load_dotenv()
        
        # 使用代理设置
        proxies = None
        if os.getenv('USE_PROXY', 'false').lower() == 'true':
            proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
            proxy_port = os.getenv('PROXY_PORT', '1080')
            proxy_url = f"socks5h://{proxy_host}:{proxy_port}"
            proxies = {'http': proxy_url, 'https': proxy_url}
            print(f"   使用代理: {proxy_url}")
        else:
            print("   直接连接（未使用代理）")
        
        response = requests.get(
            'https://www.okx.com/api/v5/public/time',
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("   ✅ OKX公共API可访问")
                server_time = data.get('data', [{}])[0].get('ts')
                if server_time:
                    print(f"   服务器时间: {server_time}")
            else:
                print(f"   ⚠️  OKX API响应异常: {data}")
        else:
            print(f"   ❌ OKX连接失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ OKX连接异常: {e}")
        print("   💡 请检查:")
        print("      - SSR代理是否运行在端口1080")
        print("      - 网络连接是否正常")
        print("      - 代理配置是否正确")

def main():
    print(f"\n{'='*60}")
    print("交易所数据加载问题诊断")
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 等待后端启动
    print("等待后端服务启动...")
    time.sleep(3)
    
    # 测试认证
    token = test_backend_auth()
    
    # 测试交易所API
    test_exchanges_api(token)
    
    # 检查OKX配置
    check_okx_configuration()
    
    print(f"\n{'='*60}")
    print("诊断完成")
    print("如果发现问题，请根据上述输出进行相应修复")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
