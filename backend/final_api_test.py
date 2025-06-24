"""
简化的API测试脚本
"""
import requests
import json

def test_complete_flow():
    print("🔍 完整API流程测试")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # 1. 注册新用户
    print("1. 测试用户注册...")
    user_data = {
        'username': f'testuser_final',
        'email': f'testfinal@example.com', 
        'password': 'testpass123'
    }
    
    response = requests.post(f'{base_url}/api/auth/register', json=user_data)
    if response.status_code == 200:
        print(f"   ✅ 注册成功: {response.json()['username']}")
    elif response.status_code == 400 and "already" in response.text:
        print("   ℹ️ 用户已存在，继续测试")
    else:
        print(f"   ❌ 注册失败: {response.status_code} - {response.text}")
        return False
    
    # 2. 登录获取token
    print("\n2. 测试用户登录...")
    login_data = {
        'username': user_data['username'],
        'password': user_data['password']
    }
    
    response = requests.post(f'{base_url}/api/auth/login', data=login_data)
    if response.status_code == 200:
        token_data = response.json()
        token = token_data['access_token']
        print(f"   ✅ 登录成功，获得token")
    else:
        print(f"   ❌ 登录失败: {response.status_code} - {response.text}")
        return False
    
    # 3. 测试需要认证的API
    print("\n3. 测试交易所账户列表API...")
    headers = {'Authorization': f'Bearer {token}'}
    
    response = requests.get(f'{base_url}/api/exchanges/', headers=headers)
    if response.status_code == 200:
        accounts = response.json()
        print(f"   ✅ 获取账户列表成功，共 {len(accounts)} 个账户")
        return True
    else:
        print(f"   ❌ 获取账户列表失败: {response.status_code} - {response.text}")
        return False

def test_frontend_api_access():
    print("\n🌐 前端API访问测试")
    print("=" * 50)
    
    # 测试前端是否能访问后端
    try:
        response = requests.get("http://localhost:3000")
        print(f"   前端状态: {response.status_code}")
    except Exception as e:
        print(f"   前端访问失败: {e}")
    
    # 测试CORS
    try:
        response = requests.get("http://localhost:8000", 
                              headers={'Origin': 'http://localhost:3000'})
        print(f"   CORS测试: {response.status_code}")
        print(f"   CORS头: {response.headers.get('Access-Control-Allow-Origin', '未设置')}")
    except Exception as e:
        print(f"   CORS测试失败: {e}")

def check_okx_auth_issues():
    print("\n🔧 OKX认证问题检查")
    print("=" * 50)
    
    # 检查数据库中的OKX账户
    try:
        from database import get_db, ExchangeAccount
        
        db = next(get_db())
        okx_accounts = db.query(ExchangeAccount).filter(
            ExchangeAccount.exchange_name.in_(['okx', 'okex'])
        ).all()
        
        print(f"   数据库中OKX账户数量: {len(okx_accounts)}")
        
        for account in okx_accounts:
            print(f"   账户ID {account.id}: {account.exchange_name}")
            print(f"     API Key: {account.api_key[:10]}..." if account.api_key else "     API Key: 未设置")
            print(f"     Secret: {'已设置' if account.api_secret else '未设置'}")
            print(f"     Passphrase: {'已设置' if account.api_passphrase else '未设置'}")
        
        db.close()
        
    except Exception as e:
        print(f"   数据库检查失败: {e}")

if __name__ == "__main__":
    print("🚀 交易控制台API测试套件")
    print("=" * 60)
    
    # 测试完整流程
    if test_complete_flow():
        print("\n✅ 基础API流程正常")
    else:
        print("\n❌ 基础API流程有问题")
    
    # 测试前端访问
    test_frontend_api_access()
    
    # 检查OKX认证问题
    check_okx_auth_issues()
    
    print("\n" + "=" * 60)
    print("测试完成")
    