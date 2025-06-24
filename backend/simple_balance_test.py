"""
简单的余额API测试脚本
"""
import requests
import json

def test_balance_api():
    # 先登录获取token
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    response = requests.post(
        "http://localhost:8000/api/auth/login", 
        data=login_data, 
        proxies={'http': None, 'https': None}
    )
    
    if response.status_code != 200:
        print(f"登录失败: {response.status_code}")
        return
    
    token = response.json().get('access_token')
    headers = {"Authorization": f"Bearer {token}"}
    
    # 获取账户列表
    response = requests.get(
        "http://localhost:8000/api/exchanges/", 
        headers=headers,
        proxies={'http': None, 'https': None}
    )
    
    if response.status_code != 200:
        print(f"获取账户列表失败: {response.status_code}")
        return
    
    accounts = response.json()
    print(f"找到 {len(accounts)} 个账户")
    
    if not accounts:
        print("没有账户可测试")
        return
    
    # 测试第一个账户的余额
    account = accounts[0]
    account_id = account['id']
    
    print(f"测试账户ID {account_id} 的余额...")
    
    try:
        response = requests.get(
            f"http://localhost:8000/api/exchanges/accounts/{account_id}/balance",
            headers=headers,
            proxies={'http': None, 'https': None},
            timeout=15
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            print(f"错误响应: {response.text}")
            
    except Exception as e:
        print(f"请求异常: {e}")

if __name__ == "__main__":
    test_balance_api()
