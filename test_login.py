import requests

def test_login():
    """测试不同的登录组合"""
    url = "http://localhost:8000/api/auth/login"
    
    # 测试用户名和密码组合
    test_combinations = [
        ("111", "111"),
        ("111", "123456"),
        ("111", "password"),
        ("testuser_1749642149", "TestPassword123"),
        ("e2e_user_1749642158", "TestPassword123"),
    ]
    
    print("🔐 测试用户登录")
    print("=" * 30)
    
    for username, password in test_combinations:
        try:
            data = {"username": username, "password": password}
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                print(f"✅ 成功: {username}:{password}")
                token = response.json().get("access_token", "")
                print(f"   Token: {token[:20]}...")
                return username, password, token
            else:
                print(f"❌ 失败: {username}:{password} - {response.status_code}")
                
        except Exception as e:
            print(f"❌ 错误: {username}:{password} - {e}")
    
    print("\n📝 建议:")
    print("1. 使用前端注册新用户")
    print("2. 用户名: 111")
    print("3. 密码: 123456")
    print("4. 邮箱: 111@example.com")
    
    return None, None, None

if __name__ == "__main__":
    username, password, token = test_login()
    
    if token:
        print(f"\n🎉 可以使用: {username}:{password}")
    else:
        print("\n❌ 没有找到可用的登录凭据")
