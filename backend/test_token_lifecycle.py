import requests
import json
from datetime import datetime, timedelta

def test_token_lifecycle():
    """测试Token生命周期"""
    BASE_URL = "http://localhost:8000"
    
    print("🔍 测试Token生命周期...")
    
    # 1. 登录获取Token
    print("\n1. 登录获取Token...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✅ 获取到Token: {token[:50]}...")
    
    # 2. 立即测试Token
    print("\n2. 立即测试Token...")
    test_response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if test_response.status_code == 200:
        user_data = test_response.json()
        print(f"✅ Token有效，用户: {user_data.get('username')}")
    else:
        print(f"❌ Token测试失败: {test_response.status_code} - {test_response.text}")
        return
    
    # 3. 测试Dashboard API
    print("\n3. 测试Dashboard API...")
    dashboard_response = requests.get(
        f"{BASE_URL}/api/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if dashboard_response.status_code == 200:
        dashboard_data = dashboard_response.json()
        print(f"✅ Dashboard API正常，数据量: {len(str(dashboard_data))} 字符")
        print(f"   策略数: {dashboard_data.get('total_strategies', 0)}")
        print(f"   账户余额: {len(dashboard_data.get('account_balances', []))}")
    else:
        print(f"❌ Dashboard API失败: {dashboard_response.status_code} - {dashboard_response.text}")
        return
    
    # 4. 多次连续调用测试稳定性
    print("\n4. 连续调用测试...")
    success_count = 0
    fail_count = 0
    
    for i in range(5):
        test_resp = requests.get(
            f"{BASE_URL}/api/dashboard/stats",
            headers={"Authorization": f"Bearer {token}"}
        )
        if test_resp.status_code == 200:
            success_count += 1
        else:
            fail_count += 1
            print(f"   第{i+1}次调用失败: {test_resp.status_code}")
    
    print(f"连续调用结果: 成功 {success_count}, 失败 {fail_count}")
    
    if fail_count == 0:
        print("\n🎉 Token生命周期测试全部通过！")
    else:
        print(f"\n⚠️  有 {fail_count} 次调用失败，可能存在问题")

def test_different_endpoints():
    """测试不同的API端点"""
    BASE_URL = "http://localhost:8000"
    
    # 登录
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    )
    
    if login_response.status_code != 200:
        print("❌ 登录失败")
        return
    
    token = login_response.json().get("access_token")
    
    endpoints = [
        ("/api/auth/me", "用户信息"),
        ("/api/dashboard/stats", "Dashboard统计"),
        ("/api/trades", "交易记录"),
        ("/api/exchanges/", "交易所账户"),
        ("/api/strategies", "策略列表")
    ]
    
    print("\n🔍 测试各个API端点...")
    for endpoint, name in endpoints:
        try:
            response = requests.get(
                f"{BASE_URL}{endpoint}",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ {name}: 正常 ({len(data)} 项)")
                else:
                    print(f"✅ {name}: 正常 (对象)")
            else:
                print(f"❌ {name}: 错误 {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: 异常 {e}")

if __name__ == "__main__":
    test_token_lifecycle()
    test_different_endpoints()
