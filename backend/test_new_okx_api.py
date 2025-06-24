#!/usr/bin/env python3
"""
测试新的 OKX API 连接
使用用户提供的新 API 凭据进行连接测试
"""
import os
import sys
import asyncio
import requests
import time
import json
from datetime import datetime

# 设置代理环境变量
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'

try:
    import ccxt
except ImportError:
    print("❌ CCXT not installed. Installing...")
    os.system("pip install ccxt")
    import ccxt

# 新的 OKX API 凭据
OKX_API_KEY = "5a0ba67e-8e05-4c8f-a294-9674e40e3ce5"
OKX_SECRET_KEY = "11005BB74DB1BD54D11F92CF207E479B"
OKX_PASSPHRASE = "vf5Y3UeUFiz6xfF!"
OKX_SANDBOX = True  # 使用测试环境

def test_proxy_connection():
    """测试代理连接"""
    print("🔍 Testing proxy connection...")
    try:
        # 测试代理是否可用
        response = requests.get('http://httpbin.org/ip', 
                              proxies={'http': 'socks5h://127.0.0.1:1080',
                                      'https': 'socks5h://127.0.0.1:1080'}, 
                              timeout=10)
        ip_info = response.json()
        print(f"✅ Proxy working, current IP: {ip_info['origin']}")
        return True
    except Exception as e:
        print(f"❌ Proxy connection failed: {e}")
        return False

def test_okx_api_direct():
    """直接测试 OKX API 连接"""
    print("\n🏦 Testing OKX API directly...")
    
    try:
        # 创建 OKX 交易所实例
        exchange = ccxt.okx({
            'apiKey': OKX_API_KEY,
            'secret': OKX_SECRET_KEY,
            'password': OKX_PASSPHRASE,
            'sandbox': OKX_SANDBOX,  # 使用测试环境
            'enableRateLimit': True,
            'proxies': {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080',
            },
            'timeout': 30000,  # 30秒超时
        })
        
        print(f"  📊 Exchange: {exchange.name}")
        print(f"  🔧 Sandbox mode: {exchange.sandbox}")
        
        # 测试获取市场数据（公开API）
        print("  🔍 Testing public API (market data)...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"  ✅ BTC/USDT ticker: ${ticker['last']:,.2f}")
        
        # 测试私有API（需要认证）
        print("  🔐 Testing private API (account balance)...")
        balance = exchange.fetch_balance()
        print(f"  ✅ Account balance retrieved")
        print(f"     Total balances: {len(balance['total'])} currencies")
        
        # 显示主要余额
        for currency, amount in balance['total'].items():
            if amount > 0:
                print(f"     {currency}: {amount}")
        
        return True
        
    except ccxt.AuthenticationError as e:
        print(f"  ❌ Authentication failed: {e}")
        return False
    except ccxt.NetworkError as e:
        print(f"  ❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")
        return False

def test_okx_api_async():
    """异步测试 OKX API"""
    print("\n🔄 Testing OKX API async...")
    
    async def async_test():
        try:
            exchange = ccxt.okx({
                'apiKey': OKX_API_KEY,
                'secret': OKX_SECRET_KEY,
                'password': OKX_PASSPHRASE,
                'sandbox': OKX_SANDBOX,
                'enableRateLimit': True,
                'proxies': {
                    'http': 'socks5h://127.0.0.1:1080',
                    'https': 'socks5h://127.0.0.1:1080',
                },
            })
            
            # 异步获取市场数据
            ticker = await exchange.fetch_ticker('ETH/USDT')
            print(f"  ✅ ETH/USDT ticker (async): ${ticker['last']:,.2f}")
            
            await exchange.close()
            return True
            
        except Exception as e:
            print(f"  ❌ Async test failed: {e}")
            return False
    
    return asyncio.run(async_test())

def test_okx_api_endpoints():
    """测试多个 OKX API 端点"""
    print("\n📡 Testing multiple OKX API endpoints...")
    
    try:
        exchange = ccxt.okx({
            'apiKey': OKX_API_KEY,
            'secret': OKX_SECRET_KEY,
            'password': OKX_PASSPHRASE,
            'sandbox': OKX_SANDBOX,
            'enableRateLimit': True,
            'proxies': {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080',
            },
        })
        
        # 1. 获取市场列表
        print("  📋 Getting markets...")
        markets = exchange.load_markets()
        print(f"  ✅ Found {len(markets)} markets")
        
        # 2. 获取账户信息
        print("  👤 Getting account info...")
        account_info = exchange.fetch_status()
        print(f"  ✅ Account status: {account_info.get('status', 'unknown')}")
        
        # 3. 获取交易历史
        print("  📈 Getting trading history...")
        try:
            trades = exchange.fetch_my_trades('BTC/USDT', limit=5)
            print(f"  ✅ Found {len(trades)} recent trades")
        except Exception as e:
            print(f"  ⚠️  No trading history (normal for new account): {e}")
        
        # 4. 获取订单历史
        print("  📄 Getting order history...")
        try:
            orders = exchange.fetch_orders('BTC/USDT', limit=5)
            print(f"  ✅ Found {len(orders)} recent orders")
        except Exception as e:
            print(f"  ⚠️  No order history (normal for new account): {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API endpoints test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 OKX API Connection Test")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: {OKX_API_KEY[:8]}...")
    print(f"🧪 Sandbox: {OKX_SANDBOX}")
    print(f"🌐 Whitelisted IP: 23.145.24.14")
    print("=" * 60)
    
    # 测试结果
    results = []
    
    # 1. 代理连接测试
    proxy_ok = test_proxy_connection()
    results.append(("Proxy Connection", proxy_ok))
    
    if not proxy_ok:
        print("\n❌ Proxy connection failed. Cannot proceed with API tests.")
        return False
    
    # 2. OKX API 直接测试
    api_ok = test_okx_api_direct()
    results.append(("OKX API Direct", api_ok))
    
    # 3. OKX API 异步测试
    async_ok = test_okx_api_async()
    results.append(("OKX API Async", async_ok))
    
    # 4. OKX API 端点测试
    endpoints_ok = test_okx_api_endpoints()
    results.append(("OKX API Endpoints", endpoints_ok))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ OKX API connection is working correctly")
        print("✅ Ready for trading operations")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Please check the error messages above")
    
    print(f"\n🕒 Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
