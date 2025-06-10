#!/usr/bin/env python3
"""
简单的端到端测试
测试Trading Console的核心功能
"""
import requests
import time
import json

def main():
    print("🚀 Trading Console 端到端测试")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    # 测试1: 健康检查
    print("测试1: 后端健康检查...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常")
            health_data = response.json()
            print(f"   环境: {health_data.get('environment')}")
            print(f"   数据库: {health_data.get('database')}")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False
    
    # 测试2: 用户注册
    print("\n测试2: 用户注册...")
    timestamp = int(time.time())
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "TestPassword123"
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/auth/register",
            json=test_user,
            timeout=10
        )
        if response.status_code in [200, 201]:
            print("✅ 用户注册成功")
            user_data = response.json()
            print(f"   用户ID: {user_data.get('id')}")
            print(f"   用户名: {user_data.get('username')}")
        else:
            print(f"❌ 注册失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        return False
    
    # 测试3: 用户登录
    print("\n测试3: 用户登录...")
    login_data = {
        "username": test_user["username"],
        "password": test_user["password"]
    }
    
    try:
        response = requests.post(
            f"{backend_url}/api/auth/login",
            data=login_data,
            timeout=10
        )
        if response.status_code == 200:
            print("✅ 登录成功")
            token_data = response.json()
            access_token = token_data["access_token"]
            print(f"   Token类型: {token_data.get('token_type')}")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return False
    
    # 测试4: 获取用户资料
    print("\n测试4: 获取用户资料...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    try:
        response = requests.get(
            f"{backend_url}/api/auth/me",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print("✅ 用户资料获取成功")
            profile = response.json()
            print(f"   用户名: {profile.get('username')}")
            print(f"   邮箱: {profile.get('email')}")
        else:
            print(f"❌ 资料获取失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 资料获取异常: {e}")
        return False
    
    # 测试5: 交易所账户列表
    print("\n测试5: 交易所账户...")
    try:
        response = requests.get(
            f"{backend_url}/api/exchanges/",
            headers=headers,
            timeout=10
        )
        if response.status_code == 200:
            print("✅ 交易所列表获取成功")
            exchanges = response.json()
            print(f"   交易所数量: {len(exchanges)}")
        else:
            print(f"❌ 交易所列表失败: {response.status_code}")
            print(f"   错误: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 交易所列表异常: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 所有测试通过! 系统功能正常!")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 测试完成: 系统正常运行")
    else:
        print("\n❌ 测试失败: 系统存在问题")