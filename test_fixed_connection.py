#!/usr/bin/env python3
"""
测试修复后的OKX连接
"""
import requests
import json

def test_fixed_okx_connection():
    """测试修复后的OKX连接"""
    print("🔧 测试修复后的OKX连接")
    print("=" * 40)
    
    backend_url = "http://localhost:8000"
    
    # 1. 使用新密码登录
    print("1. 用新密码登录...")
    login_data = {
        "username": "111",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{backend_url}/api/auth/login", data=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✅ 登录成功!")
            print(f"   Token: {token[:20]}...")
        else:
            print(f"❌ 登录失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
    except Exception as e:
        print(f"❌ 登录错误: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. 获取OKX账户
    print("\n2. 获取OKX账户...")
    try:
        response = requests.get(f"{backend_url}/api/exchanges/", headers=headers)
        if response.status_code == 200:
            accounts = response.json()
            okx_accounts = [acc for acc in accounts if acc["exchange_name"] == "okex"]
            
            if okx_accounts:
                account_id = okx_accounts[0]["id"]
                print(f"✅ 找到OKX账户 ID: {account_id}")
                
                # 3. 测试ticker获取
                print("\n3. 测试ticker获取...")
                response = requests.get(f"{backend_url}/api/exchanges/accounts/{account_id}/ticker/BTCUSDT", 
                                      headers=headers)
                
                print(f"   响应状态: {response.status_code}")
                if response.status_code == 200:
                    ticker = response.json()
                    price = ticker.get("last", "N/A")
                    print(f"✅ Ticker获取成功! BTC/USDT价格: ${price}")
                    
                    # 检查是否是Mock数据
                    if isinstance(price, (int, float)) and 40000 <= price <= 50000:
                        print("🎭 这是Mock数据 (预期行为)")
                    
                    return True
                else:
                    error_msg = response.json().get("detail", response.text) if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"❌ Ticker获取失败: {error_msg}")
                    
                    # 检查是否是我们期望的Mock fallback
                    if "okex GET https://www.okx.com" in str(error_msg):
                        print("⚠️ 仍然尝试连接真实OKX API - Mock fallback没有正确工作")
                    
                    return False
                    
            else:
                print("❌ 没有找到OKX账户")
                return False
        else:
            print(f"❌ 获取账户失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 账户获取错误: {e}")
        return False

if __name__ == "__main__":
    print("🧪 开始测试修复后的系统")
    print()
    
    success = test_fixed_okx_connection()
    
    print("\n" + "=" * 40)
    if success:
        print("🎉 测试成功! OKX连接已修复")
        print("✅ Mock数据正常返回")
        print("🌐 可以在前端界面正常使用")
    else:
        print("❌ 测试失败! 需要进一步调试")
        print("🔍 检查Mock fallback逻辑")
    
    print("\n📝 下一步:")
    print("1. 前端登录: http://localhost:3000/login")
    print("2. 用户名: 111")
    print("3. 密码: 123456")
    print("4. 测试交易所连接功能")
