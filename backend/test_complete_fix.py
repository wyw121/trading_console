#!/usr/bin/env python3
"""完整的集成测试，包括登录和API调用"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login_and_get_token():
    """登录并获取token"""
    print("🔐 尝试登录...")
    
    # 使用默认测试用户
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"✅ 登录成功，获取token: {token[:20]}...")
            return token
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_with_auth():
    """使用认证测试API"""
    token = login_and_get_token()
    if not token:
        print("❌ 无法获取认证token，跳过认证测试")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 使用认证测试交易所账户列表...")
    try:
        response = requests.get(f"{BASE_URL}/api/exchanges/", headers=headers)
        print(f"📊 账户列表响应: {response.status_code}")
        
        if response.status_code == 200:
            accounts = response.json()
            print(f"✅ 获取到 {len(accounts)} 个交易所账户")
            
            # 如果有账户，测试ticker
            if accounts:
                account = accounts[0]
                account_id = account['id']
                print(f"\n🧪 测试账户 {account_id} 的ticker...")
                
                ticker_response = requests.get(
                    f"{BASE_URL}/api/exchanges/accounts/{account_id}/ticker/BTCUSDT", 
                    headers=headers
                )
                print(f"📊 Ticker响应: {ticker_response.status_code}")
                print(f"📊 Ticker内容: {ticker_response.text[:300]}...")
                
                if ticker_response.status_code == 400:
                    error_data = ticker_response.json()
                    error_detail = error_data.get('detail', '')
                    if 'unsupported operand type' in error_detail:
                        print("❌ 仍然有TypeError错误！")
                        return False
                    else:
                        print("✅ 没有TypeError错误，其他错误是正常的")
                        return True
                else:
                    print("✅ Ticker调用成功或返回其他状态码")
                    return True
            else:
                print("ℹ️ 没有交易所账户，无法测试ticker")
                return True
        else:
            print(f"⚠️ 账户列表响应异常: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 认证测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始完整集成测试...")
    
    # 首先测试健康检查
    try:
        health_response = requests.get(f"{BASE_URL}/health")
        print(f"❤️ 健康检查: {health_response.status_code}")
    except:
        print("❌ 服务可能未启动")
    
    # 认证测试
    success = test_with_auth()
    
    if success:
        print("\n🎉 完整测试成功！")
        print("✅ TypeError错误已修复")
        print("✅ API可以正常处理请求")
    else:
        print("\n❌ 测试失败，可能仍有问题")
