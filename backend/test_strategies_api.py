#!/usr/bin/env python3
"""
策略API测试脚本
"""
import requests
import json

def test_strategies_api():
    """测试策略API"""
    print("=== 策略API测试 ===")
    
    base_url = "http://localhost:8000"
    
    # 1. 登录获取token
    login_data = {'username': 'testuser', 'password': 'testpass123'}
    
    try:
        response = requests.post(f'{base_url}/api/auth/login', data=login_data, timeout=5, proxies={'http': None, 'https': None})
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"✅ 登录成功，token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return
    
    headers = {'Authorization': f'Bearer {token}'}
    
    # 2. 测试策略列表API
    print("\n2. 测试策略列表API...")
    try:
        response = requests.get(f'{base_url}/api/strategies/', headers=headers, timeout=5, proxies={'http': None, 'https': None})
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            strategies = response.json()
            print(f"   ✅ 成功获取 {len(strategies)} 个策略")
            for strategy in strategies:
                print(f"      策略 {strategy.get('id')}: {strategy.get('name')} ({strategy.get('status')})")
        else:
            print(f"   ❌ 策略列表获取失败: {response.text}")
            
    except Exception as e:
        print(f"   ❌ 策略列表API异常: {e}")

if __name__ == "__main__":
    test_strategies_api()
