#!/usr/bin/env python3
"""
快速系统测试
"""
import requests
import json

def test_backend():
    """测试后端"""
    print("🔍 Testing backend...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        print(f"✅ Backend health: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Backend error: {e}")
        return False

def test_registration():
    """测试用户注册"""
    print("\n👤 Testing user registration...")
    try:
        import time
        timestamp = int(time.time())
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPassword123"
        }
        
        response = requests.post("http://localhost:8000/api/auth/register", 
                               json=user_data, timeout=10)
        if response.status_code == 201:
            print("✅ User registration successful")
            return True, user_data
        else:
            print(f"❌ Registration failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False, None

def test_login(user_data):
    """测试用户登录"""
    print("\n🔐 Testing user login...")
    try:
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        response = requests.post("http://localhost:8000/api/auth/login", 
                               data=login_data, timeout=10)
        if response.status_code == 200:
            token_data = response.json()
            print("✅ User login successful")
            return True, token_data["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False, None

def main():
    print("🚀 Quick System Test")
    print("=" * 50)
    
    # 1. 测试后端
    backend_ok = test_backend()
    if not backend_ok:
        return False
    
    # 2. 测试注册
    reg_ok, user_data = test_registration()
    if not reg_ok:
        return False
    
    # 3. 测试登录
    login_ok, token = test_login(user_data)
    if not login_ok:
        return False
    
    print("\n" + "=" * 50)
    print("🎉 ALL BASIC TESTS PASSED!")
    print("✅ Backend API working")
    print("✅ User registration working") 
    print("✅ User authentication working")
    print("🌐 Frontend: http://localhost:3000")
    print("🔧 Backend: http://localhost:8000")
    print("=" * 50)
    return True

if __name__ == "__main__":
    main()
