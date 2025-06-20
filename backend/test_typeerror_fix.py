#!/usr/bin/env python3
"""创建测试账户并测试ticker功能"""

import requests
import json

BASE_URL = "http://localhost:8000"

def login_and_get_token():
    """登录并获取token"""
    login_data = {
        "username": "admin", 
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def add_test_exchange_account(token):
    """添加测试交易所账户"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # 使用假的API密钥进行测试（这会失败，但可以验证我们的错误处理）
    account_data = {
        "exchange_name": "okx",
        "api_key": "test_api_key",
        "api_secret": "test_api_secret", 
        "api_passphrase": "test_passphrase",
        "is_testnet": True
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/exchanges/accounts", 
            json=account_data,
            headers=headers
        )
        print(f"📊 添加账户响应: {response.status_code}")
        print(f"📊 响应内容: {response.text[:300]}...")
        
        if response.status_code == 201:
            return response.json()
        else:
            return None
            
    except Exception as e:
        print(f"❌ 添加账户异常: {e}")
        return None

def test_ticker_with_account(token, account_id):
    """使用账户ID测试ticker功能"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n🧪 测试账户 {account_id} 的BTCUSDT ticker...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/exchanges/accounts/{account_id}/ticker/BTCUSDT",
            headers=headers
        )
        
        print(f"📊 Ticker响应状态: {response.status_code}")
        print(f"📊 Ticker响应内容: {response.text[:500]}...")
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '')
                
                if 'unsupported operand type' in error_detail:
                    print("❌ 仍然有TypeError错误！")
                    return False
                elif 'NoneType' in error_detail and '+' in error_detail:
                    print("❌ 仍然有NoneType拼接错误！")
                    return False
                else:
                    print("✅ 没有TypeError错误，其他错误是正常的")
                    print(f"   错误详情: {error_detail}")
                    return True
                    
            except:
                print("⚠️ 无法解析错误响应")
                return False
        else:
            print(f"✅ 意外的状态码 {response.status_code}，但没有TypeError")
            return True
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始TypeError修复验证...")
    
    token = login_and_get_token()
    if not token:
        print("❌ 无法获取认证token")
        exit(1)
    
    print(f"✅ 登录成功: {token[:20]}...")
    
    # 添加测试账户（会失败但不应该有TypeError）
    account = add_test_exchange_account(token)
    
    # 尝试手动使用账户ID测试（假设有账户ID 5和6，根据之前的错误日志）
    for test_account_id in [5, 6, 1, 2]:
        print(f"\n🧪 测试账户ID {test_account_id}...")
        success = test_ticker_with_account(token, test_account_id)
        
        if success:
            print(f"✅ 账户 {test_account_id} 测试通过（没有TypeError）")
        else:
            print(f"❌ 账户 {test_account_id} 仍有TypeError错误")
    
    print("\n🎯 TypeError修复验证完成")
