"""
测试按钮修复 - 验证前端按钮调用的API是否正常工作
"""
import asyncio
import aiohttp
import json

async def test_backend_apis():
    """测试后端API是否正常工作"""
    base_url = "http://localhost:8000"
    
    # 测试用户凭据 (需要根据实际情况调整)
    test_username = "testuser"
    test_password = "testpass123"
    
    async with aiohttp.ClientSession() as session:
        print("🔧 开始测试后端API修复...")
        
        # 1. 测试健康检查
        print("\n1. 测试健康检查...")
        try:
            async with session.get(f"{base_url}/health") as resp:
                if resp.status == 200:
                    print("✅ 健康检查通过")
                else:
                    print(f"❌ 健康检查失败: {resp.status}")
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
          # 2. 测试注册用户 (如果不存在)
        print("\n2. 测试用户注册...")
        try:
            register_data = {
                "username": test_username,
                "email": f"{test_username}@test.com",
                "password": test_password
            }
            async with session.post(f"{base_url}/api/auth/register", 
                                  json=register_data) as resp:
                if resp.status in [200, 201]:
                    print("✅ 用户注册成功")
                elif resp.status == 400:
                    print("ℹ️ 用户可能已存在")
                else:
                    print(f"❌ 用户注册失败: {resp.status}")
        except Exception as e:
            print(f"❌ 用户注册异常: {e}")
          # 3. 测试用户登录
        print("\n3. 测试用户登录...")
        try:
            # FastAPI的OAuth2PasswordRequestForm需要使用form data
            login_data = aiohttp.FormData()
            login_data.add_field('username', test_username)
            login_data.add_field('password', test_password)
            
            async with session.post(f"{base_url}/api/auth/login", 
                                  data=login_data) as resp:
                if resp.status == 200:
                    response_data = await resp.json()
                    token = response_data.get('access_token')
                    print("✅ 用户登录成功")
                      # 4. 测试获取支持的交易所
                    print("\n4. 测试获取支持的交易所...")
                    headers = {"Authorization": f"Bearer {token}"}
                    async with session.get(f"{base_url}/api/exchanges/supported", 
                                         headers=headers) as resp:
                        if resp.status == 200:
                            exchanges = await resp.json()
                            print(f"✅ 获取支持的交易所成功: {len(exchanges)}个")
                        else:
                            print(f"❌ 获取支持的交易所失败: {resp.status}")
                    
                    # 5. 测试简化的交易引擎管理器
                    print("\n5. 测试交易引擎管理器...")
                    try:
                        from simple_real_trading_engine import real_exchange_manager
                        
                        # 测试方法是否存在
                        has_balance_method = hasattr(real_exchange_manager, 'get_real_balance')
                        has_ticker_method = hasattr(real_exchange_manager, 'get_real_ticker')
                        
                        print(f"✅ get_real_balance方法存在: {has_balance_method}")
                        print(f"✅ get_real_ticker方法存在: {has_ticker_method}")
                        
                        if has_balance_method and has_ticker_method:
                            print("🎉 所有必需的方法都存在！")
                        else:
                            print("❌ 缺少必需的方法")
                            
                    except Exception as e:
                        print(f"❌ 交易引擎管理器测试异常: {e}")
                        
                else:
                    print(f"❌ 用户登录失败: {resp.status}")
                    
        except Exception as e:
            print(f"❌ 用户登录异常: {e}")
        
        print("\n🏁 API测试完成！")

async def test_simple_exchange_manager():
    """专门测试简化交易引擎管理器"""
    print("\n🔧 测试简化交易引擎管理器...")
    
    try:
        from simple_real_trading_engine import real_exchange_manager
        
        # 检查所有必需的方法
        required_methods = [
            'get_real_balance',
            'get_real_ticker', 
            'get_supported_exchanges',
            'get_exchange_markets',
            'add_exchange_account',
            'test_connection'
        ]
        
        missing_methods = []
        for method in required_methods:
            if not hasattr(real_exchange_manager, method):
                missing_methods.append(method)
        
        if missing_methods:
            print(f"❌ 缺少方法: {missing_methods}")
        else:
            print("✅ 所有必需的方法都存在")
            
        # 测试方法调用 (不需要真实API密钥)
        print("\n测试方法调用...")
        
        # 测试获取支持的交易所
        try:
            result = real_exchange_manager.get_supported_exchanges()
            print(f"✅ get_supported_exchanges: {len(result)} 个交易所")
        except Exception as e:
            print(f"❌ get_supported_exchanges 失败: {e}")
            
        print("🎉 简化交易引擎管理器测试完成！")
        
    except Exception as e:
        print(f"❌ 导入或测试失败: {e}")

if __name__ == "__main__":
    print("🚀 开始按钮修复验证测试...")
    
    # 首先测试简化交易引擎管理器
    asyncio.run(test_simple_exchange_manager())
    
    # 然后测试后端API
    asyncio.run(test_backend_apis())
    
    print("\n✨ 按钮修复验证完成！")
    print("📝 如果所有测试都通过，前端按钮应该不会再报错了。")
