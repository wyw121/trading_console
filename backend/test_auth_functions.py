import requests
import time

def test_registration_and_login():
    print("=== 测试注册和登录功能 ===\n")
    
    # 1. 测试注册
    timestamp = str(int(time.time()))
    register_data = {
        'username': f'test_user_{timestamp}',
        'email': f'test_{timestamp}@example.com',
        'password': 'test123456'
    }
    
    print(f"1. 测试注册用户: {register_data['username']}")
    try:
        response = requests.post('http://localhost:8000/api/auth/register', 
                               json=register_data, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            print(f"✅ 注册成功: ID={user_data['id']}, 用户名={user_data['username']}")
        else:
            print(f"❌ 注册失败: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ 注册请求失败: {e}")
        return
    
    # 2. 测试新用户登录
    print(f"\n2. 测试新用户登录")
    try:
        login_data = {
            'username': register_data['username'],
            'password': register_data['password']
        }
        response = requests.post('http://localhost:8000/api/auth/login', 
                               data=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data['access_token']
            print(f"✅ 登录成功: Token={token[:50]}...")
            
            # 3. 测试获取用户信息
            print(f"\n3. 测试获取用户信息")
            headers = {'Authorization': f'Bearer {token}'}
            response = requests.get('http://localhost:8000/api/auth/me', 
                                  headers=headers, timeout=5)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ 获取用户信息成功: {user_info['username']} ({user_info['email']})")
            else:
                print(f"❌ 获取用户信息失败: {response.status_code}")
        else:
            print(f"❌ 登录失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 登录请求失败: {e}")
    
    # 4. 测试已存在用户
    print(f"\n4. 测试已存在用户登录: 111")
    try:
        login_data = {'username': '111', 'password': '123456'}
        response = requests.post('http://localhost:8000/api/auth/login', 
                               data=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ 用户111登录成功")
        else:
            print(f"❌ 用户111登录失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 用户111登录请求失败: {e}")

if __name__ == "__main__":
    test_registration_and_login()
