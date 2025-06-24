import requests
import json

BASE_URL = "http://localhost:8000"

def test_dashboard_api():
    """完整测试Dashboard API流程"""
    
    print("🔍 测试Dashboard API连接...")
    
    # 1. 登录获取Token
    print("\n1. 用户登录...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code} - {login_response.text}")
        return False
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✅ 登录成功，Token: {token[:50]}...")
    
    # 2. 测试用户信息
    print("\n2. 获取用户信息...")
    me_response = requests.get(
        f"{BASE_URL}/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if me_response.status_code != 200:
        print(f"❌ 获取用户信息失败: {me_response.status_code} - {me_response.text}")
        return False
    
    user_data = me_response.json()
    print(f"✅ 用户信息: {user_data}")
    
    # 3. 测试Dashboard统计
    print("\n3. 获取Dashboard统计...")
    stats_response = requests.get(
        f"{BASE_URL}/api/dashboard/stats",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if stats_response.status_code != 200:
        print(f"❌ 获取Dashboard统计失败: {stats_response.status_code} - {stats_response.text}")
        return False
    
    stats_data = stats_response.json()
    print(f"✅ Dashboard统计数据:")
    print(f"   总策略数: {stats_data.get('total_strategies', 0)}")
    print(f"   活跃策略数: {stats_data.get('active_strategies', 0)}")
    print(f"   总交易数: {stats_data.get('total_trades', 0)}")
    print(f"   总盈亏: {stats_data.get('total_profit_loss', 0)}")
    print(f"   账户余额数量: {len(stats_data.get('account_balances', []))}")
    
    # 4. 测试交易记录
    print("\n4. 获取交易记录...")
    trades_response = requests.get(
        f"{BASE_URL}/api/trades",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if trades_response.status_code != 200:
        print(f"❌ 获取交易记录失败: {trades_response.status_code} - {trades_response.text}")
        return False
    
    trades_data = trades_response.json()
    print(f"✅ 交易记录数量: {len(trades_data)}")
    
    # 5. 测试交易所账户
    print("\n5. 获取交易所账户...")
    exchanges_response = requests.get(
        f"{BASE_URL}/api/exchanges/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if exchanges_response.status_code != 200:
        print(f"❌ 获取交易所账户失败: {exchanges_response.status_code} - {exchanges_response.text}")
        return False
    
    exchanges_data = exchanges_response.json()
    print(f"✅ 交易所账户数量: {len(exchanges_data)}")
    
    print("\n🎉 所有API测试通过！")
    return True

def test_frontend_proxy():
    """测试前端代理是否正常工作"""
    print("\n🔍 测试前端代理...")
    
    try:
        # 通过前端代理访问API
        proxy_response = requests.get("http://localhost:3000/api/health", timeout=5)
        if proxy_response.status_code == 200:
            print("✅ 前端代理工作正常")
            return True
        else:
            print(f"❌ 前端代理返回错误: {proxy_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 前端代理连接失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Trading Console API诊断测试")
    print("=" * 60)
    
    # 测试后端API
    if test_dashboard_api():
        print("\n✅ 后端API测试全部通过")
    else:
        print("\n❌ 后端API测试失败")
    
    # 测试前端代理
    if test_frontend_proxy():
        print("✅ 前端代理测试通过")
    else:
        print("❌ 前端代理测试失败")
    
    print("\n" + "=" * 60)
    print("📋 诊断完成")
    print("=" * 60)
