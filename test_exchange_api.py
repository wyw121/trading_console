#!/usr/bin/env python3
"""
测试交易所API端点修复
"""
import requests
import json
import time

def test_exchange_api():
    """测试交易所API端点"""
    backend_url = "http://localhost:8000"
    
    print("🧪 Testing Exchange API Endpoints")
    print("=" * 50)
    
    # 1. 测试健康检查
    print("\n1. Testing Health Check...")
    try:
        response = requests.get(f"{backend_url}/health")
        if response.status_code == 200:
            print("✅ Health check successful")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False
    
    # 2. 注册测试用户
    print("\n2. Registering test user...")
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(f"{backend_url}/api/auth/register", json=test_user)
        if response.status_code == 200:
            print("✅ User registration successful")
        else:
            print(f"❌ User registration failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # 3. 登录获取token
    print("\n3. User login...")
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(f"{backend_url}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ User login successful")
        else:
            print(f"❌ User login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # 4. 测试交易所API端点
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n4. Testing Exchange Endpoints...")
    
    # 4.1 获取交易所列表 - 修复后的路径
    print("   📋 Testing GET /api/exchanges/...")
    try:
        response = requests.get(f"{backend_url}/api/exchanges/", headers=headers)
        if response.status_code == 200:
            exchanges = response.json()
            print(f"   ✅ Exchange list retrieved: {len(exchanges)} accounts")
        else:
            print(f"   ❌ Exchange list failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Exchange list error: {e}")
    
    # 4.2 创建交易所账户 - 修复后的路径
    print("   ➕ Testing POST /api/exchanges/...")
    try:
        exchange_data = {
            "exchange_name": "binance",
            "api_key": "test_api_key_12345",
            "api_secret": "test_api_secret_67890",
            "api_passphrase": "",
            "is_testnet": True
        }
        response = requests.post(f"{backend_url}/api/exchanges/", 
                               json=exchange_data, headers=headers)
        if response.status_code == 200:
            account = response.json()
            account_id = account["id"]
            print(f"   ✅ Exchange account created: ID {account_id}")
            
            # 4.3 测试子路径端点
            print("   💰 Testing GET /api/exchanges/accounts/{id}/balance...")
            try:
                response = requests.get(f"{backend_url}/api/exchanges/accounts/{account_id}/balance", 
                                      headers=headers)
                # 这个可能会失败，因为是测试API密钥，但应该返回具体错误而不是404
                print(f"   🔍 Balance endpoint response: {response.status_code}")
                if response.status_code != 404:  # 不应该是404 Not Found
                    print("   ✅ Balance endpoint exists (may fail due to invalid API keys)")
                else:
                    print("   ❌ Balance endpoint not found - route issue")
            except Exception as e:
                print(f"   ❌ Balance endpoint error: {e}")
            
            # 4.4 删除测试账户
            print("   🗑️ Testing DELETE /api/exchanges/accounts/{id}...")
            try:
                response = requests.delete(f"{backend_url}/api/exchanges/accounts/{account_id}", 
                                         headers=headers)
                if response.status_code == 200:
                    print("   ✅ Exchange account deleted successfully")
                else:
                    print(f"   ❌ Delete failed: {response.status_code}")
                    print(f"   Response: {response.text}")
            except Exception as e:
                print(f"   ❌ Delete error: {e}")
                
        else:
            print(f"   ❌ Exchange creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Exchange creation error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Exchange API test completed!")
    print("🌐 Frontend URL: http://localhost:3000")
    print("🔧 Backend URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    test_exchange_api()
