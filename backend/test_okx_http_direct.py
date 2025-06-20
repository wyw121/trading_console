#!/usr/bin/env python3
"""
简化的 OKX API 测试 - 使用直接 HTTP 请求
避免 CCXT 库的潜在问题
"""
import os
import sys
import requests
import json
import time
import hmac
import hashlib
import base64
from datetime import datetime, timezone

# 设置代理环境变量
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'

# 新的 OKX API 凭据
OKX_API_KEY = "7760f27c-62a1-4af1-aef6-eb25c998b83f"
OKX_SECRET_KEY = "6A44039F47D5CA690BD14CF7019BAAAA"
OKX_PASSPHRASE = "vf5Y3UeUFiz6xfF!"
OKX_BASE_URL = "https://www.okx.com"  # 主网
# OKX_BASE_URL = "https://aws.okx.com"  # 备用地址

# 代理配置
PROXIES = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

def create_signature(timestamp, method, request_path, body=''):
    """创建 OKX API 签名"""
    message = timestamp + method + request_path + body
    signature = base64.b64encode(
        hmac.new(
            OKX_SECRET_KEY.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
    ).decode('utf-8')
    return signature

def get_headers(method, request_path, body=''):
    """获取 OKX API 请求头"""
    # OKX 需要 ISO 8601 格式的时间戳
    timestamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    signature = create_signature(timestamp, method, request_path, body)
    
    return {
        'OK-ACCESS-KEY': OKX_API_KEY,
        'OK-ACCESS-SIGN': signature,
        'OK-ACCESS-TIMESTAMP': timestamp,
        'OK-ACCESS-PASSPHRASE': OKX_PASSPHRASE,
        'Content-Type': 'application/json'
    }

def test_proxy_connection():
    """测试代理连接"""
    print("🔍 Testing proxy connection...")
    try:
        response = requests.get('http://httpbin.org/ip', 
                              proxies=PROXIES, 
                              timeout=10)
        ip_info = response.json()
        print(f"✅ Proxy working, current IP: {ip_info['origin']}")
        return True
    except Exception as e:
        print(f"❌ Proxy connection failed: {e}")
        return False

def test_okx_public_api():
    """测试 OKX 公开 API"""
    print("\n📊 Testing OKX public API...")
    try:
        # 获取 BTC/USDT 行情
        url = f"{OKX_BASE_URL}/api/v5/market/ticker?instId=BTC-USDT"
        response = requests.get(url, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '0':
                ticker_data = data['data'][0]
                price = float(ticker_data['last'])
                print(f"✅ BTC/USDT price: ${price:,.2f}")
                return True
            else:
                print(f"❌ API error: {data['msg']}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Public API test failed: {e}")
        return False

def test_okx_private_api():
    """测试 OKX 私有 API"""
    print("\n🔐 Testing OKX private API...")
    try:
        # 获取账户余额
        request_path = '/api/v5/account/balance'
        headers = get_headers('GET', request_path)
        url = f"{OKX_BASE_URL}{request_path}"
        
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '0':
                print("✅ Account balance retrieved successfully")
                balance_data = data['data'][0] if data['data'] else {}
                details = balance_data.get('details', [])
                print(f"   Found {len(details)} currency balances")
                
                # 显示非零余额
                for detail in details:
                    try:
                        balance = float(detail.get('bal', 0))
                        if balance > 0:
                            print(f"   {detail.get('ccy', 'unknown')}: {balance}")
                    except (ValueError, TypeError):
                        continue
                
                return True
            else:
                print(f"❌ API error: {data['msg']}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Private API test failed: {e}")
        return False

def test_okx_trading_api():
    """测试 OKX 交易相关 API"""
    print("\n📈 Testing OKX trading API...")
    try:
        # 获取交易对信息
        request_path = '/api/v5/public/instruments?instType=SPOT'
        url = f"{OKX_BASE_URL}{request_path}"
        
        response = requests.get(url, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '0':
                instruments = data['data']
                print(f"✅ Found {len(instruments)} trading pairs")
                
                # 查找 BTC/USDT
                btc_usdt = next((inst for inst in instruments if inst['instId'] == 'BTC-USDT'), None)
                if btc_usdt:
                    print(f"   BTC-USDT trading pair found")
                    print(f"   Min size: {btc_usdt['minSz']}")
                    print(f"   Tick size: {btc_usdt['tickSz']}")
                
                return True
            else:
                print(f"❌ API error: {data['msg']}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Trading API test failed: {e}")
        return False

def test_okx_account_info():
    """测试 OKX 账户信息 API"""
    print("\n👤 Testing OKX account info...")
    try:
        # 获取账户配置
        request_path = '/api/v5/account/config'
        headers = get_headers('GET', request_path)
        url = f"{OKX_BASE_URL}{request_path}"
        
        response = requests.get(url, headers=headers, proxies=PROXIES, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data['code'] == '0':
                config = data['data'][0] if data['data'] else {}
                print("✅ Account config retrieved")
                print(f"   Account level: {config.get('acctLv', 'unknown')}")
                print(f"   Account ID: {config.get('uid', 'unknown')}")
                return True
            else:
                print(f"❌ API error: {data['msg']}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Account info test failed: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 OKX API Direct HTTP Test")
    print("=" * 60)
    print(f"🕒 Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔑 API Key: {OKX_API_KEY[:8]}...")
    print(f"🌐 Base URL: {OKX_BASE_URL}")
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
    
    # 2. 公开 API 测试
    public_ok = test_okx_public_api()
    results.append(("OKX Public API", public_ok))
    
    # 3. 私有 API 测试
    private_ok = test_okx_private_api()
    results.append(("OKX Private API", private_ok))
    
    # 4. 交易 API 测试
    trading_ok = test_okx_trading_api()
    results.append(("OKX Trading API", trading_ok))
    
    # 5. 账户信息测试
    account_ok = test_okx_account_info()
    results.append(("OKX Account Info", account_ok))
    
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
        print("✅ Authentication successful")
        print("✅ Ready for trading operations")
        print("\n💡 Next steps:")
        print("   - Configure exchange account in the web interface")
        print("   - Create trading strategies")
        print("   - Start automated trading")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("Please check the error messages above")
        print("\n🔧 Troubleshooting:")
        print("   - Verify API key permissions")
        print("   - Check IP whitelist configuration")
        print("   - Ensure proxy is running on port 1080")
    
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
        import traceback
        traceback.print_exc()
        sys.exit(1)
