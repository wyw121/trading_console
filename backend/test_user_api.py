"""
测试用户的OKX API密钥
"""
import ccxt
import asyncio

async def test_user_okx_api():
    """测试用户的OKX API密钥"""
    
    # 用户提供的测试API密钥
    config = {
        'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'passphrase': 'vf5Y3UeUFiz6xfF!',
        'sandbox': True,  # 使用测试环境
        'enableRateLimit': True,
        'timeout': 30000,
    }
    
    print(f"🔑 使用API密钥: {config['apiKey'][:8]}...")
    print(f"🔑 使用测试环境: {config['sandbox']}")
    
    exchange = None
    try:
        print("\n🔗 测试OKX API连接...")
        exchange = ccxt.okx(config)
        
        # 测试1: 加载市场
        print("1️⃣ 加载市场数据...")
        markets = await exchange.load_markets()
        print(f"   ✅ 成功加载 {len(markets)} 个交易市场")
        
        # 测试2: 获取账户配置
        print("2️⃣ 获取账户配置...")
        try:
            account_config = await exchange.private_get_account_config()
            print(f"   ✅ 账户配置: {account_config}")
        except Exception as e:
            print(f"   ❌ 账户配置失败: {e}")
        
        # 测试3: 获取余额
        print("3️⃣ 获取账户余额...")
        balance = await exchange.fetch_balance()
        print("   ✅ 成功获取余额信息")
        
        # 显示余额详情
        total = balance.get('total', {})
        free = balance.get('free', {})
        used = balance.get('used', {})
        
        print("\n💰 余额详情:")
        has_balance = False
        for currency in total:
            if total[currency] > 0 or free[currency] > 0 or used[currency] > 0:
                print(f"     {currency}: 总计={total[currency]}, 可用={free[currency]}, 冻结={used[currency]}")
                has_balance = True
        
        if not has_balance:
            print("     账户余额为空（测试环境正常现象）")
        
        # 测试4: 获取行情
        print("\n4️⃣ 获取BTC-USDT行情...")
        try:
            ticker = await exchange.fetch_ticker('BTC/USDT')
            print(f"   ✅ BTC/USDT价格: ${ticker['last']}")
        except Exception as e:
            print(f"   ❌ 获取行情失败: {e}")
        
        print("\n✅ 所有API测试完成！您的API密钥配置正确。")
        return True
        
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        print(f"❌ 错误类型: {type(e).__name__}")
        
        if "Invalid API" in str(e) or "Invalid sign" in str(e):
            print("\n💡 可能的原因:")
            print("   1. API密钥格式错误")
            print("   2. Passphrase不正确")
            print("   3. 签名验证失败")
        elif "timeout" in str(e).lower():
            print("\n💡 可能的原因:")
            print("   1. 网络连接超时")
            print("   2. OKX服务器响应慢")
        else:
            print(f"\n💡 详细错误信息: {str(e)}")
        
        return False
        
    finally:
        if exchange:
            try:
                await exchange.close()
            except:
                pass

if __name__ == "__main__":
    print("🧪 测试用户提供的OKX API密钥")
    print("=" * 50)
    
    result = asyncio.run(test_user_okx_api())
    
    if result:
        print("\n🎯 接下来的操作:")
        print("1. 在前端页面添加这个API账户")
        print("2. 选择 '使用测试网络'")
        print("3. 保存后即可查看余额")
    else:
        print("\n🔧 故障排除建议:")
        print("1. 检查网络连接")
        print("2. 确认API密钥是否正确复制")
        print("3. 验证Passphrase是否正确")
        print("4. 检查OKX API服务状态")
