#!/usr/bin/env python3
"""
完整的前后端集成测试 - 专注Dashboard
"""
import requests
import time
import json

def complete_dashboard_test():
    """完整的Dashboard功能测试"""
    print("=== 完整Dashboard功能测试 ===")
    
    base_url = "http://localhost:8000"
    
    # 1. 登录
    print("1. 用户登录...")
    login_data = {'username': 'testuser', 'password': 'testpass123'}
    
    try:
        response = requests.post(f'{base_url}/api/auth/login', data=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"   ✅ 登录成功")
            headers = {'Authorization': f'Bearer {token}'}
        else:
            print(f"   ❌ 登录失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 登录异常: {e}")
        return
    
    # 2. 获取用户信息
    print("2. 获取用户信息...")
    try:
        response = requests.get(f'{base_url}/api/auth/me', headers=headers, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            print(f"   ✅ 用户: {user_data.get('username')} (ID: {user_data.get('id')})")
        else:
            print(f"   ❌ 获取用户信息失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取用户信息异常: {e}")
    
    # 3. 获取交易所账户
    print("3. 获取交易所账户...")
    try:
        response = requests.get(f'{base_url}/api/exchanges/', headers=headers, timeout=5)
        if response.status_code == 200:
            accounts = response.json()
            print(f"   ✅ 找到 {len(accounts)} 个交易所账户")
            for account in accounts:
                print(f"      账户 {account['id']}: {account['exchange_name']} (激活: {account['is_active']})")
        else:
            print(f"   ❌ 获取交易所账户失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取交易所账户异常: {e}")
    
    # 4. 获取策略列表
    print("4. 获取策略列表...")
    try:
        response = requests.get(f'{base_url}/api/strategies/', headers=headers, timeout=5)
        if response.status_code == 200:
            strategies = response.json()
            print(f"   ✅ 找到 {len(strategies)} 个策略")
            for strategy in strategies:
                print(f"      策略 {strategy['id']}: {strategy['name']} (状态: {strategy['status']})")
        else:
            print(f"   ❌ 获取策略列表失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取策略列表异常: {e}")
    
    # 5. 获取Dashboard统计（关键测试）
    print("5. 获取Dashboard统计...")
    try:
        response = requests.get(f'{base_url}/api/dashboard/stats', headers=headers, timeout=15)
        if response.status_code == 200:
            stats = response.json()
            print(f"   ✅ Dashboard统计加载成功")
            print(f"      策略总数: {stats.get('total_strategies', 0)}")
            print(f"      活跃策略: {stats.get('active_strategies', 0)}")
            print(f"      总交易数: {stats.get('total_trades', 0)}")
            print(f"      账户余额数: {len(stats.get('account_balances', []))}")
            
            # 显示前几个余额
            balances = stats.get('account_balances', [])
            if balances:
                print("      余额详情:")
                for balance in balances[:3]:  # 只显示前3个
                    print(f"        {balance['exchange']} {balance['currency']}: {balance['total']}")
        else:
            print(f"   ❌ Dashboard统计获取失败: {response.status_code}")
            print(f"      错误内容: {response.text}")
    except Exception as e:
        print(f"   ❌ Dashboard统计异常: {e}")
    
    # 6. 获取交易记录
    print("6. 获取交易记录...")
    try:
        response = requests.get(f'{base_url}/api/trades/', headers=headers, timeout=5)
        if response.status_code == 200:
            trades = response.json()
            print(f"   ✅ 找到 {len(trades)} 条交易记录")
        else:
            print(f"   ❌ 获取交易记录失败: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 获取交易记录异常: {e}")
    
    print("\n=== 测试总结 ===")
    print("如果所有API都正常，那么问题可能在于:")
    print("1. 前端JavaScript错误")
    print("2. 浏览器网络策略限制")
    print("3. 前端组件状态管理问题")
    print("4. Vite代理配置问题")
    print("\n建议:")
    print("1. 打开浏览器开发者工具查看Console和Network")
    print("2. 检查前端是否正确传递Authorization头")
    print("3. 验证前端路由和状态管理逻辑")

if __name__ == "__main__":
    complete_dashboard_test()
