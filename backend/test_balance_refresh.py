#!/usr/bin/env python3
"""
余额刷新API测试
"""
import requests

def test_balance_refresh():
    """测试余额刷新API"""
    print("=== 余额刷新API测试 ===")
    
    base_url = "http://localhost:8000"
    
    # 1. 登录
    login_data = {'username': 'testuser', 'password': 'testpass123'}
    
    try:
        response = requests.post(f'{base_url}/api/auth/login', data=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ 登录成功")
            headers = {'Authorization': f'Bearer {token}'}
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    # 2. 快速Dashboard统计
    print("2. 快速Dashboard统计...")
    try:
        response = requests.get(f'{base_url}/api/dashboard/stats', headers=headers, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 快速加载成功，账户余额数: {len(stats.get('account_balances', []))}")
        else:
            print(f"   ❌ 快速加载失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 快速加载异常: {e}")
    
    # 3. 余额刷新（实时）
    print("3. 余额刷新（实时）...")
    try:
        response = requests.get(f'{base_url}/api/dashboard/refresh-balances', headers=headers, timeout=20)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ 实时余额获取成功")
            balances = stats.get('account_balances', [])
            print(f"   账户余额数: {len(balances)}")
            for balance in balances[:3]:
                print(f"      {balance['exchange']} {balance['currency']}: {balance['total']}")
        else:
            print(f"   ❌ 实时余额获取失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 实时余额异常: {e}")

if __name__ == "__main__":
    test_balance_refresh()
