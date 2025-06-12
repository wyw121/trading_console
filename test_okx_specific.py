#!/usr/bin/env python3
"""
专门测试OKX API连接的脚本
"""
import requests
import json

def test_okx_connection():
    """测试OKX API连接"""
    backend_url = "http://localhost:8000"
    
    print("🔗 Testing OKX API Connection")
    print("=" * 50)
    
    # 使用用户"111"登录
    print("1. Logging in as user '111'...")
    try:
        login_data = {
            "username": "111",
            "password": "111"
        }
        response = requests.post(f"{backend_url}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 检查现有的OKX账户
    print("\n2. Checking existing OKX accounts...")
    try:
        response = requests.get(f"{backend_url}/api/exchanges/", headers=headers)
        if response.status_code == 200:
            accounts = response.json()
            okx_accounts = [acc for acc in accounts if acc["exchange_name"] == "okex"]
            print(f"✅ Found {len(okx_accounts)} OKX accounts")
            
            if okx_accounts:
                account_id = okx_accounts[0]["id"]
                print(f"   Using OKX account ID: {account_id}")
                
                # 测试余额获取
                print("\n3. Testing balance retrieval...")
                response = requests.get(f"{backend_url}/api/exchanges/accounts/{account_id}/balance", 
                                      headers=headers)
                print(f"   Balance endpoint status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Balance retrieved successfully!")
                    print(f"   Response: {response.json()}")
                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "Unknown error")
                    print(f"   ⚠️ Balance failed (expected): {error_msg}")
                else:
                    print(f"   ❌ Unexpected error: {response.text}")
                
                # 测试行情数据获取
                print("\n4. Testing ticker data...")
                response = requests.get(f"{backend_url}/api/exchanges/accounts/{account_id}/ticker/BTCUSDT", 
                                      headers=headers)
                print(f"   Ticker endpoint status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Ticker retrieved successfully!")
                    ticker = response.json()
                    print(f"   BTC/USDT price: {ticker.get('last', 'N/A')}")
                elif response.status_code == 400:
                    error_msg = response.json().get("detail", "Unknown error")
                    print(f"   ⚠️ Ticker failed (expected): {error_msg}")
                else:
                    print(f"   ❌ Unexpected error: {response.text}")
                
                # 测试模拟连接
                print("\n5. Testing simulated connection...")
                response = requests.post(f"{backend_url}/api/exchanges/accounts/{account_id}/test", 
                                       headers=headers)
                print(f"   Test connection status: {response.status_code}")
                if response.status_code == 200:
                    print("   ✅ Connection test passed!")
                    print(f"   Response: {response.json()}")
                else:
                    error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {"detail": response.text}
                    error_msg = error_data.get("detail", "Unknown error")
                    print(f"   ⚠️ Connection test failed: {error_msg}")
                    
            else:
                print("   ⚠️ No OKX accounts found. Please add one first.")
                
        else:
            print(f"❌ Failed to get accounts: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking accounts: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎯 OKX API test completed!")
    print("\n📝 Next steps:")
    print("   1. Login to frontend as user '111' with password '111'")
    print("   2. Go to Exchanges page")
    print("   3. Test the connection button")
    print("   4. Check if the issues are resolved")
    
    return True

if __name__ == "__main__":
    test_okx_connection()
