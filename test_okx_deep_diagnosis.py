#!/usr/bin/env python3
"""
深度诊断OKX API认证问题
专门针对时间戳过期问题
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

# 设置详细日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_immediate_request():
    """测试立即发送请求，减少延迟"""
    print("=== 测试立即发送请求（最小延迟）===\n")
    
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    
    try:
        # 1. 获取服务器时间戳
        print("1. 获取服务器时间戳...")
        server_resp = requests.get('https://www.okx.com/api/v5/public/time', 
                                 proxies=proxies, timeout=5)
        
        if server_resp.status_code != 200:
            print("❌ 获取服务器时间失败")
            return False
            
        server_data = server_resp.json()
        if server_data.get('code') != '0':
            print("❌ 服务器时间API错误")
            return False
            
        server_ts = int(server_data['data'][0]['ts'])
        print(f"服务器时间戳: {server_ts}")
        
        # 2. 立即构造签名并发送请求
        print("2. 立即构造签名并发送请求...")
        
        # 使用服务器时间戳，不加任何缓冲
        timestamp = str(server_ts)
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
        
        print(f"时间戳: {timestamp}")
        print(f"签名: {signature[:20]}...")
        
        # 立即发送请求
        url = 'https://www.okx.com/api/v5/account/balance'
        start_time = time.time()
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        end_time = time.time()
        
        request_time = (end_time - start_time) * 1000
        print(f"请求耗时: {request_time:.0f}ms")
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == '0':
                print("✅ 立即请求成功!")
                return True
            else:
                print(f"❌ API错误: {result}")
        
        return False
        
    except Exception as e:
        print(f"❌ 立即请求测试失败: {e}")
        return False

def test_without_proxy():
    """测试不使用代理的直接连接"""
    print("\n=== 测试不使用代理的直接连接 ===\n")
    
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    try:
        # 不使用代理，直接连接
        print("1. 获取服务器时间（无代理）...")
        server_resp = requests.get('https://www.okx.com/api/v5/public/time', timeout=5)
        
        if server_resp.status_code == 200:
            server_data = server_resp.json()
            if server_data.get('code') == '0':
                server_ts = int(server_data['data'][0]['ts'])
                print(f"服务器时间戳: {server_ts}")
                
                # 立即发送私有API请求
                timestamp = str(server_ts)
                method = 'GET'
                request_path = '/api/v5/account/balance'
                body = ''
                
                message = timestamp + method + request_path + body
                signature = base64.b64encode(
                    hmac.new(SECRET_KEY.encode('utf-8'), 
                            message.encode('utf-8'), 
                            hashlib.sha256).digest()
                ).decode('utf-8')
                
                headers = {
                    'OK-ACCESS-KEY': API_KEY,
                    'OK-ACCESS-SIGN': signature,
                    'OK-ACCESS-TIMESTAMP': timestamp,
                    'OK-ACCESS-PASSPHRASE': PASSPHRASE,
                    'Content-Type': 'application/json'
                }
                
                print("2. 发送余额请求（无代理）...")
                url = 'https://www.okx.com/api/v5/account/balance'
                response = requests.get(url, headers=headers, timeout=10)
                
                print(f"响应状态码: {response.status_code}")
                print(f"响应内容: {response.text}")
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == '0':
                        print("✅ 无代理请求成功!")
                        return True
                    else:
                        print(f"❌ API错误: {result}")
                else:
                    print(f"❌ HTTP错误: {response.status_code}")
            else:
                print(f"❌ 服务器时间API错误: {server_data}")
        else:
            print(f"❌ 获取服务器时间失败: {server_resp.status_code}")
            
    except Exception as e:
        print(f"❌ 无代理连接失败: {e}")
        # 可能是网络限制，这很正常
        
    return False

def test_api_key_validity():
    """测试API密钥的有效性和权限"""
    print("\n=== 测试API密钥有效性和权限 ===\n")
    
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    print(f"API Key: {API_KEY}")
    print(f"Secret长度: {len(SECRET_KEY)}")
    print(f"Passphrase: {PASSPHRASE}")
    
    # 检查API密钥格式
    if len(API_KEY) < 30 or '-' not in API_KEY:
        print("⚠️ API Key格式可能不正确")
    else:
        print("✅ API Key格式正常")
        
    if len(SECRET_KEY) < 30:
        print("⚠️ Secret Key长度可能不够")
    else:
        print("✅ Secret Key长度正常")
        
    if len(PASSPHRASE) < 5:
        print("⚠️ Passphrase长度可能不够")
    else:
        print("✅ Passphrase长度正常")
    
    # 测试其他私有API端点
    print("\n测试其他私有API端点...")
    
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    
    # 测试账户配置信息
    try:
        print("测试账户配置API...")
        server_resp = requests.get('https://www.okx.com/api/v5/public/time', 
                                 proxies=proxies, timeout=5)
        server_data = server_resp.json()
        server_ts = int(server_data['data'][0]['ts'])
        
        timestamp = str(server_ts)
        method = 'GET'
        request_path = '/api/v5/account/config'
        body = ''
        
        message = timestamp + method + request_path + body
        signature = base64.b64encode(
            hmac.new(SECRET_KEY.encode('utf-8'), 
                    message.encode('utf-8'), 
                    hashlib.sha256).digest()
        ).decode('utf-8')
        
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = 'https://www.okx.com/api/v5/account/config'
        response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
        
        print(f"账户配置API - 状态码: {response.status_code}")
        print(f"账户配置API - 响应: {response.text}")
        
    except Exception as e:
        print(f"账户配置API测试失败: {e}")

def main():
    print("OKX API 深度认证诊断")
    print("=" * 50)
    
    # 1. 测试立即发送请求
    success1 = test_immediate_request()
    
    # 2. 测试不使用代理
    success2 = test_without_proxy()
    
    # 3. 测试API密钥有效性
    test_api_key_validity()
    
    print("\n" + "=" * 50)
    print("诊断总结:")
    print(f"立即请求（代理）: {'✅ 成功' if success1 else '❌ 失败'}")
    print(f"直连请求（无代理）: {'✅ 成功' if success2 else '❌ 失败'}")
    
    if not success1 and not success2:
        print("\n可能的问题:")
        print("1. API密钥权限不足或已过期")
        print("2. IP白名单限制")
        print("3. 账户状态异常")
        print("4. OKX API服务器时间验证异常严格")
        print("\n建议:")
        print("- 检查OKX账户API密钥权限设置")
        print("- 确认API密钥是否设置了IP白名单")
        print("- 检查账户是否正常且未被限制")
        print("- 尝试重新生成API密钥")

if __name__ == "__main__":
    main()
