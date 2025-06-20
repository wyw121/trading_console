"""
测试连接修复 - 验证交易所连接是否能正确建立
"""
import asyncio
import aiohttp
import json

async def test_connection_fix():
    """测试连接修复"""
    base_url = "http://localhost:8000"
    
    # 测试用户凭据
    test_username = "testuser"
    test_password = "testpass123"
    
    async with aiohttp.ClientSession() as session:
        print("🔧 测试连接修复...")
        
        # 1. 登录获取token
        print("\n1. 用户登录...")
        try:
            login_data = aiohttp.FormData()
            login_data.add_field('username', test_username)
            login_data.add_field('password', test_password)
            
            async with session.post(f"{base_url}/api/auth/login", 
                                  data=login_data) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    token = response_data.get('access_token')
                    print("✅ 登录成功")
                    
                    headers = {"Authorization": f"Bearer {token}"}
                    
                    # 2. 获取交易所账户列表（触发连接恢复）
                    print("\n2. 获取交易所账户列表（触发连接恢复）...")
                    async with session.get(f"{base_url}/api/exchanges/", 
                                         headers=headers) as resp:
                        if resp.status == 200:
                            accounts = await resp.json()
                            print(f"✅ 获取到 {len(accounts)} 个账户")
                            
                            # 3. 如果有账户，测试获取价格
                            if accounts:
                                account_id = accounts[0]['id']
                                print(f"\n3. 测试账户 {account_id} 的价格获取...")
                                
                                # 测试获取BTC/USDT价格
                                async with session.get(f"{base_url}/api/exchanges/accounts/{account_id}/ticker/BTC/USDT", 
                                                     headers=headers) as resp:
                                    if resp.status == 200:
                                        ticker = await resp.json()
                                        print("✅ 价格获取成功！")
                                        print(f"   响应: {ticker.get('message')}")
                                    else:
                                        result = await resp.json()
                                        print(f"⚠️ 价格获取响应: {resp.status}")
                                        print(f"   消息: {result.get('detail', result.get('message', ''))}")
                                
                                print(f"\n4. 测试账户 {account_id} 的余额获取...")
                                
                                # 测试获取余额
                                async with session.get(f"{base_url}/api/exchanges/accounts/{account_id}/balance", 
                                                     headers=headers) as resp:
                                    if resp.status == 200:
                                        balance = await resp.json()
                                        print("✅ 余额获取成功！")
                                        print(f"   响应: {balance.get('message')}")
                                    else:
                                        result = await resp.json()
                                        print(f"⚠️ 余额获取响应: {resp.status}")
                                        print(f"   消息: {result.get('detail', result.get('message', ''))}")
                            else:
                                print("ℹ️ 没有找到交易所账户")
                        else:
                            print(f"❌ 获取账户列表失败: {resp.status}")
                            
                else:
                    print(f"❌ 登录失败: {resp.status}")
                    
        except Exception as e:
            print(f"❌ 测试异常: {e}")

if __name__ == "__main__":
    print("🚀 开始测试连接修复...")
    asyncio.run(test_connection_fix())
    print("\n✨ 测试完成！")
