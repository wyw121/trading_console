#!/usr/bin/env python3
"""
测试Dashboard API连接
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_dashboard_api():
    print("🔐 登录获取token...")
    
    # 1. 登录获取token
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ 登录成功")
        else:
            print(f"❌ 登录失败: {response.text}")
            return
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
        return

    # 2. 测试 /api/auth/me
    print("\n👤 测试用户信息API...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ 用户信息: {user_info['username']}")
        else:
            print(f"❌ 获取用户信息失败: {response.text}")
    except Exception as e:
        print(f"❌ 用户信息请求失败: {e}")

    # 3. 测试 /api/dashboard/stats  
    print("\n📊 测试Dashboard统计API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Dashboard统计: {json.dumps(stats, indent=2)}")
        else:
            print(f"❌ 获取Dashboard统计失败: {response.text}")
            print(f"状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard统计请求失败: {e}")

    # 4. 测试 /api/trades
    print("\n📈 测试交易记录API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/trades", headers=headers)
        if response.status_code == 200:
            trades = response.json()
            print(f"✅ 交易记录数量: {len(trades)}")
        else:
            print(f"❌ 获取交易记录失败: {response.text}")
            print(f"状态码: {response.status_code}")
    except Exception as e:
        print(f"❌ 交易记录请求失败: {e}")

if __name__ == "__main__":
    test_dashboard_api()
