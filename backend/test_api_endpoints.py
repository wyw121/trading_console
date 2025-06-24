import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_endpoints():
    print("=== 测试后端API端点 ===\n")
    
    # 1. 测试根路径
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"✅ 根路径: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 根路径失败: {e}")
    
    # 2. 测试健康检查
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"✅ 健康检查: {response.status_code} - {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 3. 测试登录
    try:
        login_data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(
            f"{BASE_URL}/api/auth/login", 
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ 登录: {response.status_code}")
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print(f"   Token: {token[:50]}...")
            
            # 4. 使用token测试其他端点
            headers = {"Authorization": f"Bearer {token}"}
            
            # 测试dashboard stats
            try:
                response = requests.get(f"{BASE_URL}/api/dashboard/stats", headers=headers)
                print(f"✅ Dashboard统计: {response.status_code}")
                if response.status_code == 200:
                    print(f"   数据: {response.json()}")
                else:
                    print(f"   错误: {response.text}")
            except Exception as e:
                print(f"❌ Dashboard统计失败: {e}")
            
            # 测试strategies
            try:
                response = requests.get(f"{BASE_URL}/api/strategies/", headers=headers)
                print(f"✅ 策略列表: {response.status_code}")
                if response.status_code == 200:
                    print(f"   数据: {response.json()}")
                else:
                    print(f"   错误: {response.text}")
            except Exception as e:
                print(f"❌ 策略列表失败: {e}")
            
            # 测试trades
            try:
                response = requests.get(f"{BASE_URL}/api/trades/", headers=headers)
                print(f"✅ 交易记录: {response.status_code}")
                if response.status_code == 200:
                    print(f"   数据: {response.json()}")
                else:
                    print(f"   错误: {response.text}")
            except Exception as e:
                print(f"❌ 交易记录失败: {e}")            # 测试exchange accounts
            try:
                response = requests.get(f"{BASE_URL}/api/exchanges/", headers=headers)
                print(f"✅ 交易所账户: {response.status_code}")
                if response.status_code == 200:
                    print(f"   数据: {response.json()}")
                else:
                    print(f"   错误: {response.text}")
            except Exception as e:
                print(f"❌ 交易所账户失败: {e}")
        else:
            print(f"   登录失败: {response.text}")
    except Exception as e:
        print(f"❌ 登录失败: {e}")

if __name__ == "__main__":
    test_api_endpoints()
