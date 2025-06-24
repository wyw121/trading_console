#!/usr/bin/env python3
"""
OKX API合规性功能测试脚本
测试新的权限验证、IP白名单等功能
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_login():
    """测试登录并获取token"""
    print("🔐 测试登录...")
    
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ 登录成功")
        return token
    else:
        print(f"❌ 登录失败: {response.text}")
        return None

def test_exchange_accounts(token):
    """测试获取交易所账户列表"""
    print("\n📋 测试获取交易所账户...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/exchanges/", headers=headers)
    
    if response.status_code == 200:
        accounts = response.json()
        print(f"✅ 获取到 {len(accounts)} 个交易所账户")
        return accounts
    else:
        print(f"❌ 获取账户失败: {response.text}")
        return []

def test_create_okx_account(token):
    """测试创建OKX账户（包含新的合规性字段）"""
    print("\n🔧 测试创建OKX账户...")
    
    headers = {"Authorization": f"Bearer {token}"}
    account_data = {
        "exchange_name": "okex",
        "api_key": "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0",
        "api_secret": "CD6A497EEB00AA2DC60B2B0974DD2485", 
        "api_passphrase": "vf5Y3UeUFiz6xfF!",
        "is_testnet": True,
        "permissions": ["read", "trade"],
        "ip_whitelist": ["127.0.0.1", "192.168.1.100"]
    }
    
    response = requests.post(f"{BASE_URL}/api/exchanges/", headers=headers, json=account_data)
    
    if response.status_code == 200:
        account = response.json()
        print(f"✅ 创建账户成功，ID: {account['id']}")
        return account
    else:
        print(f"❌ 创建账户失败: {response.text}")
        return None

def test_validate_permissions(token, account_id):
    """测试权限验证"""
    print(f"\n🔍 测试权限验证 (账户ID: {account_id})...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"account_id": account_id}
    
    response = requests.post(f"{BASE_URL}/api/exchanges/validate-permissions", headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 权限验证完成: {result}")
        return result
    else:
        print(f"❌ 权限验证失败: {response.text}")
        return None

def test_update_permissions(token, account_id):
    """测试更新权限"""
    print(f"\n📝 测试更新权限 (账户ID: {account_id})...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"permissions": ["read", "trade", "withdraw"]}
    
    response = requests.put(f"{BASE_URL}/api/exchanges/accounts/{account_id}/permissions", headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 权限更新成功: {result}")
        return result
    else:
        print(f"❌ 权限更新失败: {response.text}")
        return None

def test_update_ip_whitelist(token, account_id):
    """测试更新IP白名单"""
    print(f"\n🌐 测试更新IP白名单 (账户ID: {account_id})...")
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"ip_whitelist": ["127.0.0.1", "192.168.1.100", "10.0.0.1"]}
    
    response = requests.put(f"{BASE_URL}/api/exchanges/accounts/{account_id}/ip-whitelist", headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ IP白名单更新成功: {result}")
        return result
    else:
        print(f"❌ IP白名单更新失败: {response.text}")
        return None

def test_get_current_ip(token):
    """测试获取当前IP"""
    print("\n🌍 测试获取当前IP...")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/exchanges/current-ip", headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 当前IP: {result['ip']}")
        return result
    else:
        print(f"❌ 获取当前IP失败: {response.text}")
        return None

def main():
    """主测试流程"""
    print("🚀 开始OKX API合规性功能测试\n")
    
    # 1. 登录
    token = test_login()
    if not token:
        return
    
    # 2. 获取现有账户
    accounts = test_exchange_accounts(token)
    
    # 3. 创建新的OKX账户（如果没有的话）
    okx_account = None
    for acc in accounts:
        if acc.get('exchange_name') == 'okex':
            okx_account = acc
            break
    
    if not okx_account:
        okx_account = test_create_okx_account(token)
        if not okx_account:
            return
    
    account_id = okx_account['id']
    print(f"\n📊 使用账户ID: {account_id} 进行测试")
    
    # 4. 测试权限验证
    test_validate_permissions(token, account_id)
    
    # 5. 测试更新权限
    test_update_permissions(token, account_id)
    
    # 6. 测试更新IP白名单
    test_update_ip_whitelist(token, account_id)
    
    # 7. 测试获取当前IP
    test_get_current_ip(token)
    
    # 8. 再次获取账户列表查看更新结果
    print("\n📋 测试完成后的账户状态:")
    final_accounts = test_exchange_accounts(token)
    for acc in final_accounts:
        if acc['id'] == account_id:
            print(f"  - 权限: {acc.get('permissions', [])}")
            print(f"  - IP白名单: {acc.get('ip_whitelist', [])}")
            print(f"  - 验证状态: {acc.get('validation_status', 'unknown')}")
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    main()
