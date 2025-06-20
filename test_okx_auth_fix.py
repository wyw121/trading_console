#!/usr/bin/env python3
"""
OKX API认证问题诊断和修复
针对401错误进行深度调试
"""

import os
import sys
sys.path.append('backend')

import requests
import hmac
import hashlib
import base64
import time
import json
import logging
from okx_api_manager import OKXAPIManager

# 设置详细日志
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_okx_signature_methods():
    """测试不同的签名方法"""
    print("=== OKX API签名方法测试 ===\n")
    
    # 使用实际的API凭据
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    print(f"API Key: {API_KEY}")
    print(f"Secret Key: {SECRET_KEY}")
    print(f"Passphrase: {PASSPHRASE}\n")
    
    # 1. 测试服务器时间获取
    print("1. 测试服务器时间获取...")
    try:
        manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
        server_time = manager.get_server_time()
        print(f"服务器时间响应: {server_time}")
        
        if server_time.get('code') == '0':
            server_ts = server_time['data'][0]['ts']
            local_ts = int(time.time() * 1000)
            time_diff = abs(int(server_ts) - local_ts)
            print(f"服务器时间: {server_ts}")
            print(f"本地时间: {local_ts}")
            print(f"时间差: {time_diff}ms")
            
            if time_diff > 30000:  # 超过30秒
                print("⚠️ 警告: 本地时间与服务器时间差异过大!")
            else:
                print("✅ 时间同步正常")
        print()
    except Exception as e:
        print(f"❌ 服务器时间获取失败: {e}\n")
    
    # 2. 测试签名生成
    print("2. 测试签名生成...")
    try:
        timestamp = str(int(time.time() * 1000))
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        # 按照OKX官方文档的签名方法
        message = timestamp + method + request_path + body
        print(f"签名原文: {message}")
        
        signature = base64.b64encode(
            hmac.new(SECRET_KEY.encode('utf-8'), 
                    message.encode('utf-8'), 
                    hashlib.sha256).digest()
        ).decode('utf-8')
        
        print(f"生成签名: {signature}")
        print()
    except Exception as e:
        print(f"❌ 签名生成失败: {e}\n")
    
    # 3. 手动发送请求测试
    print("3. 手动发送请求测试...")
    try:
        timestamp = str(int(time.time() * 1000))
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        # 生成签名
        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(SECRET_KEY.encode('utf-8'), 
                    message.encode('utf-8'), 
                    hashlib.sha256).digest()
        ).decode('utf-8')
        
        # 设置请求头
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        # 设置代理
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        url = f'https://www.okx.com{request_path}'
        print(f"请求URL: {url}")
        print(f"请求头: {headers}")
        
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == '0':
                print("✅ 余额获取成功!")
                return True
            else:
                print(f"❌ API返回错误: {result}")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求发送失败: {e}")
        return False

def test_different_endpoints():
    """测试不同的API端点"""
    print("\n=== 测试不同API端点 ===\n")
    
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
    
    # 测试公开API
    print("1. 测试公开API - 服务器时间...")
    result = manager.get_server_time()
    print(f"结果: {result}")
    
    print("\n2. 测试公开API - 价格信息...")
    result = manager.get_ticker('BTC-USDT')
    print(f"结果: {result}")
    
    print("\n3. 测试私有API - 账户余额...")
    result = manager.get_balance_with_retry()
    print(f"结果: {result}")
    
    print("\n4. 测试连接...")
    result = manager.test_connection()
    print(f"结果: {result}")

def test_time_sync_issue():
    """测试时间同步问题"""
    print("\n=== 时间同步问题诊断 ===\n")
    
    # 获取服务器时间
    try:
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        response = requests.get('https://www.okx.com/api/v5/public/time', 
                              proxies=proxies, timeout=10)
        
        if response.status_code == 200:
            server_data = response.json()
            if server_data.get('code') == '0':
                server_ts = int(server_data['data'][0]['ts'])
                local_ts = int(time.time() * 1000)
                
                print(f"服务器时间戳: {server_ts}")
                print(f"本地时间戳: {local_ts}")
                print(f"时间差: {server_ts - local_ts}ms")
                
                # 使用服务器时间戳进行签名测试
                print("\n使用服务器时间戳进行签名测试...")
                return test_with_server_timestamp(server_ts)
            else:
                print(f"获取服务器时间失败: {server_data}")
        else:
            print(f"HTTP请求失败: {response.status_code}")
            
    except Exception as e:
        print(f"时间同步测试失败: {e}")
    
    return False

def test_with_server_timestamp(server_timestamp):
    """使用服务器时间戳进行测试"""
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    try:
        timestamp = str(server_timestamp)
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        # 生成签名
        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(SECRET_KEY.encode('utf-8'), 
                    message.encode('utf-8'), 
                    hashlib.sha256).digest()
        ).decode('utf-8')
        
        # 设置请求头
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        # 设置代理
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        url = 'https://www.okx.com/api/v5/account/balance'
        response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
        
        print(f"使用服务器时间戳 {timestamp}:")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == '0':
                print("✅ 使用服务器时间戳成功!")
                return True
            else:
                print(f"❌ API错误: {result}")
        
        return False
        
    except Exception as e:
        print(f"❌ 服务器时间戳测试失败: {e}")
        return False

if __name__ == "__main__":
    print("OKX API 认证问题深度诊断")
    print("=" * 50)
    
    # 1. 基础签名测试
    success = test_okx_signature_methods()
    
    # 2. 如果失败，尝试时间同步修复
    if not success:
        print("\n尝试时间同步修复...")
        success = test_time_sync_issue()
    
    # 3. 测试所有端点
    test_different_endpoints()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ 认证问题已解决!")
    else:
        print("❌ 认证问题仍需解决")
