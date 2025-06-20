#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的OKX API测试 - 避免卡住问题
"""

import os
import requests
import socks
import socket
import hmac
import hashlib
import base64
import time
import json

print("🔧 开始OKX API测试...")

# 设置SOCKS代理
try:
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
    socket.socket = socks.socksocket
    print("✅ SOCKS5代理配置成功")
except Exception as e:
    print(f"❌ 代理配置失败: {e}")
    exit(1)

# API密钥
API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
PASSPHRASE = "vf5Y3UeUFiz6xfF!"

def create_signature(timestamp, method, request_path, body, secret_key):
    """创建OKX API签名"""
    message = str(timestamp) + method.upper() + request_path + body
    signature = base64.b64encode(
        hmac.new(secret_key.encode('utf-8'), 
                message.encode('utf-8'), 
                hashlib.sha256).digest()
    ).decode('utf-8')
    return signature

def test_public_api():
    """测试公共API - 简单版本"""
    print("\n1. 测试公共API...")
    try:
        # 设置较短的超时时间避免卡住
        response = requests.get('https://www.okx.com/api/v5/public/time', 
                              timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 公共API连接成功")
            print(f"   服务器时间: {data}")
            return data
        else:
            print(f"❌ 公共API失败: {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print("❌ 公共API超时 - 可能网络问题")
        return None
    except Exception as e:
        print(f"❌ 公共API异常: {e}")
        return None

def test_private_api_simple():
    """测试私有API - 简单版本"""
    print("\n2. 测试私有API...")
    try:
        # 使用当前时间戳
        timestamp = str(int(time.time() * 1000))
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
        
        signature = create_signature(timestamp, method, request_path, body, SECRET_KEY)
        
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = 'https://www.okx.com' + request_path
        
        # 设置较短超时时间
        response = requests.get(url, headers=headers, timeout=5)
        
        print(f"   HTTP状态码: {response.status_code}")
        print(f"   响应内容: {response.text[:200]}...")  # 只显示前200字符
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                print("✅ 私有API连接成功！")
                return True
            else:
                print(f"❌ API返回错误: {data.get('msg')}")
                return False
        else:
            print(f"❌ 私有API HTTP错误: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 私有API超时")
        return False
    except Exception as e:
        print(f"❌ 私有API异常: {e}")
        return False

def main():
    print("开始简单OKX API测试...\n")
    
    # 测试公共API
    public_result = test_public_api()
    
    # 测试私有API
    private_result = test_private_api_simple()
    
    print("\n" + "=" * 40)
    print("📊 测试结果:")
    print(f"   公共API: {'✅ 成功' if public_result else '❌ 失败'}")
    print(f"   私有API: {'✅ 成功' if private_result else '❌ 失败'}")
    
    if public_result:
        print("\n✅ 至少公共API可用，网络连接正常")
        if not private_result:
            print("⚠️  私有API有问题，可能是API密钥或权限问题")
    else:
        print("\n❌ 网络连接问题，请检查代理设置")

if __name__ == "__main__":
    main()
