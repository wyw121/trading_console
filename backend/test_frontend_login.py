import requests

# 测试前端代理路由
try:
    # 通过前端代理测试登录
    login_data = {'username': '111', 'password': '123456'}
    response = requests.post('http://localhost:3001/api/auth/login', json=login_data)
    print(f'前端代理登录状态: {response.status_code}')
    if response.status_code == 200:
        token_data = response.json()
        token = token_data['access_token']
        print(f'登录成功，获取token: {token[:50]}...')
        
        # 测试获取用户信息
        headers = {'Authorization': f'Bearer {token}'}
        user_response = requests.get('http://localhost:3001/api/auth/me', headers=headers)
        print(f'用户信息状态: {user_response.status_code}')
        if user_response.status_code == 200:
            user_data = user_response.json()
            username = user_data['username']
            email = user_data['email']
            print(f'用户信息: {username} ({email})')
        else:
            print(f'用户信息错误: {user_response.text}')
    else:
        print(f'登录失败: {response.text}')
except Exception as e:
    print(f'请求失败: {e}')
