#!/usr/bin/env python3
"""
完整的SSR代理测试脚本
"""
import os
import socket
import requests
import ccxt
import asyncio
from dotenv import load_dotenv

def main():
    print("🧪 完整SSR代理测试")
    print("=" * 40)
    
    # 1. 检查代理端口
    print("\n1. 检查SSR代理端口...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        if result == 0:
            print("✅ SSR代理端口1080可用")
        else:
            print("❌ SSR代理端口1080不可用")
            return
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return
    
    # 2. 加载环境变量
    print("\n2. 加载环境变量...")
    load_dotenv()
    
    # 设置环境变量（模拟main.py）
    if os.getenv('HTTP_PROXY'):
        os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
        os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
        os.environ['http_proxy'] = os.getenv('http_proxy')
        os.environ['https_proxy'] = os.getenv('https_proxy')
        print("✅ 环境变量已设置")
    else:
        print("❌ 环境变量未找到")
    
    # 3. 测试requests代理
    print("\n3. 测试requests库代理...")
    try:
        response = requests.get('https://httpbin.org/ip', timeout=10)
        ip_info = response.json()
        print(f"✅ 通过代理访问，IP: {ip_info.get('origin')}")
    except Exception as e:
        print(f"❌ requests代理测试失败: {e}")
    
    # 4. 测试OKX API
    print("\n4. 测试OKX API...")
    try:
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
        if response.status_code == 200:
            print("✅ OKX API可访问")
        else:
            print(f"❌ OKX API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ OKX API异常: {e}")
    
    # 5. 测试CCXT
    print("\n5. 测试CCXT库...")
    
    async def test_ccxt():
        try:
            exchange = ccxt.okx({'sandbox': True, 'timeout': 30000})
            markets = await exchange.load_markets()
            print(f"✅ CCXT成功加载 {len(markets)} 个市场")
            await exchange.close()
        except Exception as e:
            print(f"❌ CCXT测试失败: {e}")
    
    asyncio.run(test_ccxt())
    
    print("\n🎉 测试完成！")

if __name__ == "__main__":
    main()
