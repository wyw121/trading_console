#!/usr/bin/env python3
import requests
import time

def main():
    print("🚀 Trading Console Simple Test")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("Test 1: Backend health check...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is healthy")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Backend error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False
    
    # Test 2: User registration
    print("\nTest 2: User registration...")
    test_user = {
        "username": f"testuser_{int(time.time())}",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            user_data = response.json()
            print("✅ User registration successful")
            print(f"   User ID: {user_data.get('id')}")
            print(f"   Username: {user_data.get('username')}")
        else:
            print(f"❌ Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return False
    
    # Test 3: User login
    print("\nTest 3: User login...")
    try:
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(
            f"{backend_url}/api/auth/login",
            data=login_data,
            timeout=10
        )
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("✅ User login successful")
            print(f"   Token: {access_token[:20]}...")
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All basic tests passed!")
    print("✅ Backend API is working correctly")
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
