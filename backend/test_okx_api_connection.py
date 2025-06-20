#!/usr/bin/env python3
"""
OKX API连接测试 - 使用用户提供的API密钥
"""
import os
import sys
import requests
import ccxt
import time
import hmac
import hashlib
import base64
from datetime import datetime

# 用户提供的API密钥
API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
PASSPHRASE = "vf5Y3UeUFiz6xfF!"

# 设置SSR代理
PROXY_CONFIG = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

# 设置环境变量代理
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'

def test_proxy_connection():
    """测试代理连接"""
    print("=== 测试代理连接 ===")
    try:
        response = requests.get('http://httpbin.org/ip', 
                              proxies=PROXY_CONFIG, 
                              timeout=10)
        ip_info = response.json()
        print(f"✅ 代理连接成功，当前IP: {ip_info.get('origin')}")
        return True
    except Exception as e:
        print(f"❌ 代理连接失败: {e}")
        return False

def test_okx_public_api():
    """测试OKX公开API"""
    print("\n=== 测试OKX公开API ===")
    try:
        # 测试获取服务器时间
        response = requests.get('https://www.okx.com/api/v5/public/time', 
                              proxies=PROXY_CONFIG, 
                              timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OKX服务器时间: {data}")
            return True
        else:
            print(f"❌ OKX API响应错误: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OKX公开API访问失败: {e}")
        return False

def create_okx_signature(timestamp, method, request_path, body=''):
    """创建OKX API签名"""
    message = timestamp + method + request_path + body
    signature = base64.b64encode(
        hmac.new(SECRET_KEY.encode('utf-8'), 
                message.encode('utf-8'), 
                hashlib.sha256).digest()
    ).decode('utf-8')
    return signature

def test_okx_private_api():
    """测试OKX私有API（账户信息）"""
    print("\n=== 测试OKX私有API ===")
    try:
        # 先获取服务器时间
        server_time_response = requests.get('https://www.okx.com/api/v5/public/time', 
                                          proxies=PROXY_CONFIG, 
                                          timeout=10)
        if server_time_response.status_code == 200:
            server_time_data = server_time_response.json()
            timestamp = server_time_data['data'][0]['ts']
            print(f"使用服务器时间戳: {timestamp}")
        else:
            # 如果获取服务器时间失败，使用本地时间
            timestamp = str(int(time.time() * 1000))
            print(f"使用本地时间戳: {timestamp}")
        
        method = 'GET'
        request_path = '/api/v5/account/balance'
        
        # 创建签名
        signature = create_okx_signature(timestamp, method, request_path)
        
        # 设置请求头
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        # 发送请求
        url = f'https://www.okx.com{request_path}'
        response = requests.get(url, headers=headers, proxies=PROXY_CONFIG, timeout=10)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("✅ OKX私有API访问成功")
                print(f"账户余额数据: {data.get('data', [])}")
                return True
            else:
                print(f"❌ OKX API错误: {data.get('msg')}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ OKX私有API访问失败: {e}")
        return False

def test_ccxt_okx():
    """测试CCXT库连接OKX"""
    print("\n=== 测试CCXT库连接OKX ===")
    try:
        # 创建OKX交易所实例
        exchange = ccxt.okx({
            'apiKey': API_KEY,
            'secret': SECRET_KEY,
            'password': PASSPHRASE,
            'sandbox': False,  # 使用实盘
            'proxies': PROXY_CONFIG,
            'enableRateLimit': True,
        })
        
        # 测试获取余额
        print("正在获取账户余额...")
        balance = exchange.fetch_balance()
        print(f"✅ CCXT获取余额成功")
        
        # 显示非零余额
        non_zero_balances = {k: v for k, v in balance['total'].items() if v > 0}
        if non_zero_balances:
            print(f"非零余额: {non_zero_balances}")
        else:
            print("账户余额为空或全部为0")
            
        # 测试获取市场数据
        print("\n正在获取BTC/USDT价格...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC/USDT 价格: {ticker['last']}")
        
        return True
        
    except Exception as e:
        print(f"❌ CCXT连接失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始OKX API连接测试")
    print(f"使用API Key: {API_KEY[:8]}...")
    print(f"使用代理: {PROXY_CONFIG['https']}")
    
    # 1. 测试代理连接
    if not test_proxy_connection():
        print("❌ 代理连接失败，请检查SSR代理是否正常运行")
        return False
    
    # 2. 测试OKX公开API
    if not test_okx_public_api():
        print("❌ OKX公开API访问失败")
        return False
    
    # 3. 测试OKX私有API
    if not test_okx_private_api():
        print("❌ OKX私有API访问失败，请检查API密钥权限")
        return False
    
    # 4. 测试CCXT库
    if not test_ccxt_okx():
        print("❌ CCXT库连接失败")
        return False
    
    print("\n🎉 所有测试通过！")
    print("✅ 代理连接正常")
    print("✅ OKX API访问正常")
    print("✅ API密钥权限正常")
    print("✅ CCXT库集成正常")
    print("\n现在可以继续修复项目代码...")
    
    return True

if __name__ == "__main__":
    main()
