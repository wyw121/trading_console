#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import aiohttp
import json
import sys
import time
from datetime import datetime

class SimpleE2ETest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.auth_token = None
        self.test_user = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "TestPassword123"
        }
        
    async def test_backend_health(self):
        print("Step 1: Testing backend health...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Backend is healthy: {data}")
                        return True
                    else:
                        print(f"❌ Backend health check failed: {response.status}")
                        return False
        except Exception as e:
            print(f"❌ Backend connection failed: {e}")
            return False
    
    async def test_user_registration(self):
        print(f"\nStep 2: Testing user registration...")
        print(f"Registering user: {self.test_user['username']}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/auth/register",
                    json=self.test_user,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ User registration successful")
                        print(f"   User ID: {data.get('id', 'N/A')}")
                        print(f"   Username: {data.get('username', 'N/A')}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ User registration failed: {response.status}")
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Registration request failed: {e}")
            return False
    
    async def test_user_login(self):
        print(f"\nStep 3: Testing user login...")
        
        try:
            async with aiohttp.ClientSession() as session:
                form_data = aiohttp.FormData()
                form_data.add_field('username', self.test_user['username'])
                form_data.add_field('password', self.test_user['password'])
                
                async with session.post(
                    f"{self.backend_url}/api/auth/login",
                    data=form_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data.get("access_token")
                        print(f"✅ User login successful")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ User login failed: {response.status}")
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Login request failed: {e}")
            return False
    
    async def test_get_user_profile(self):
        print(f"\nStep 4: Testing get user profile...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/auth/me",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ User profile retrieved")
                        print(f"   User ID: {data.get('id')}")
                        print(f"   Username: {data.get('username')}")
                        print(f"   Email: {data.get('email')}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Get user profile failed: {response.status}")
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Get profile request failed: {e}")
            return False
    
    async def test_add_exchange_account(self):
        print(f"\nStep 5: Testing add exchange account...")
        
        if not self.auth_token:
            print("❌ No auth token available")
            return False
        
        try:
            exchange_data = {
                "exchange_name": "binance",
                "api_key": "test_api_key",
                "api_secret": "test_api_secret",
                "api_passphrase": None,
                "is_testnet": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/exchanges/",
                    json=exchange_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        print(f"✅ Exchange account added")
                        print(f"   Account ID: {data.get('id')}")
                        print(f"   Exchange: {data.get('exchange_name')}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"❌ Add exchange account failed: {response.status}")
                        print(f"   Error: {error_text}")
                        return False
        except Exception as e:
            print(f"❌ Add exchange request failed: {e}")
            return False
    
    async def run_all_tests(self):
        print("🚀 Trading Console E2E Test")
        print("Testing: Registration → Login → Profile → Exchange Setup")
        print("=" * 60)
        
        start_time = datetime.now()
        
        tests = [
            ("Backend Health Check", self.test_backend_health),
            ("User Registration", self.test_user_registration),
            ("User Login", self.test_user_login),
            ("Get User Profile", self.test_get_user_profile),
            ("Add Exchange Account", self.test_add_exchange_account),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                success = await test_func()
                if success:
                    passed += 1
                else:
                    print(f"\n❌ Test '{test_name}' failed, stopping execution")
                    break
            except Exception as e:
                print(f"\n💥 Test '{test_name}' crashed: {e}")
                break
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 60)
        print("📊 Test Results Summary")
        print("=" * 60)
        print(f"Passed: {passed}/{total} tests")
        print(f"Duration: {duration:.2f} seconds")
        print(f"Test user: {self.test_user['username']}")
        
        if passed == total:
            print("\n🎉 All tests passed! Your trading console is working correctly!")
        else:
            print(f"\n⚠️ {total - passed} tests failed. Please check the errors above.")
        
        return passed == total

async def main():
    try:
        tester = SimpleE2ETest()
        success = await tester.run_all_tests()
        return 0 if success else 1
    except Exception as e:
        print(f"Test execution failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
