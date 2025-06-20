#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import ccxt
import requests
import socks
import socket
from urllib.parse import urljoin
import json
import time
import hmac
import hashlib
import base64

# 设置SOCKS代理
print("🔧 配置SOCKS5代理...")
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
socket.socket = socks.socksocket

# 用户API密钥
API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
PASSPHRASE = "vf5Y3UeUFiz6xfF!"

print("🔑 直接测试OKX API连接")
print("=" * 40)

def create_signature(timestamp, method, request_path, body, secret_key):
    """创建OKX API签名"""
    message = str(timestamp) + method.upper() + request_path + body
    mac = hmac.new(bytes(secret_key, encoding='utf8'), bytes(message, encoding='utf-8'), digestmod='sha256')
    d = mac.digest()
    return base64.b64encode(d).decode('utf-8')

def test_direct_api():
    """直接使用HTTP请求测试API"""
    try:
        # 1. 测试公共API
        print("1. 测试公共API...")
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
        if response.status_code == 200:
            server_time = response.json()
            print(f"✅ 公共API连接成功")
            print(f"   服务器时间: {server_time}")
        else:
            print(f"❌ 公共API失败: {response.status_code}")
            return False        # 2. 测试私有API - 获取余额
        print("\n2. 测试私有API...")
        
        # 使用服务器时间戳确保时间同步
        server_timestamp = server_time['data'][0]['ts']
        print(f"   使用服务器时间戳: {server_timestamp}")
        
        method = 'GET'
        request_path = '/api/v5/account/balance'
        body = ''
          signature = create_signature(server_timestamp, method, request_path, body, SECRET_KEY)
        
        headers = {
            'OK-ACCESS-KEY': API_KEY,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': server_timestamp,
            'OK-ACCESS-PASSPHRASE': PASSPHRASE,
            'Content-Type': 'application/json'
        }
        
        url = 'https://www.okx.com' + request_path
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 私有API连接成功！")
            print(f"   响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            if data.get('code') == '0':
                balances = data.get('data', [])
                if balances:
                    print("\n📊 账户余额:")
                    for balance_info in balances:
                        details = balance_info.get('details', [])
                        for detail in details:
                            ccy = detail.get('ccy', '')
                            cashBal = detail.get('cashBal', '0')
                            if float(cashBal) > 0:
                                print(f"   {ccy}: {cashBal}")
                else:
                    print("   账户无余额或余额为0")
            else:
                print(f"   API返回错误: {data.get('msg', '未知错误')}")
        else:
            print(f"❌ 私有API失败: {response.status_code}")
            print(f"   响应内容: {response.text}")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ 直接API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_ccxt_api():
    """使用CCXT测试API"""
    try:
        print("\n3. 测试CCXT API...")
        
        # 配置交易所
        exchange = ccxt.okx({
            'apiKey': API_KEY,
            'secret': SECRET_KEY,
            'password': PASSPHRASE,
            'sandbox': False,
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 100,  # 毫秒
        })
        
        # 测试市场数据
        markets = await exchange.load_markets()
        print(f"✅ CCXT市场数据加载成功，市场数量: {len(markets)}")
        
        # 测试余额
        balance = await exchange.fetch_balance()
        print("✅ CCXT余额获取成功！")
        
        print("\n📊 CCXT账户余额:")
        total_balances = balance.get('total', {})
        for currency, amount in total_balances.items():
            if amount > 0:
                print(f"   {currency}: {amount}")
        
        if not any(amount > 0 for amount in total_balances.values()):
            print("   账户余额为0")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ CCXT API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# 主测试函数
def main():
    print("开始API连接测试...\n")
    
    # 测试直接API
    direct_success = test_direct_api()
    
    # 测试CCXT API
    ccxt_success = asyncio.run(test_ccxt_api())
    
    print("\n" + "=" * 40)
    print("📊 测试结果总结:")
    print(f"   直接API测试: {'✅ 成功' if direct_success else '❌ 失败'}")
    print(f"   CCXT API测试: {'✅ 成功' if ccxt_success else '❌ 失败'}")
    
    if direct_success or ccxt_success:
        print("\n🎉 至少一种连接方式成功，可以进行下一步开发！")
    else:
        print("\n❌ 所有连接方式都失败，需要检查网络配置")

if __name__ == "__main__":
    main()
