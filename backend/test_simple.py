"""
简化的OKX API测试脚本
"""
import ccxt
import asyncio

async def simple_okx_test():
    """简单的OKX API测试"""
      # 用户提供的测试API密钥
    config = {
        'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'passphrase': 'vf5Y3UeUFiz6xfF!',
        'sandbox': True,  # 使用测试环境
        'enableRateLimit': True,
        'timeout': 30000,
    }
      if not config['apiKey']:
        print("❌ API密钥配置为空")
        return
    
    print(f"� 使用API密钥: {config['apiKey'][:8]}...")
    print(f"🔑 使用测试环境: {config['sandbox']}")
    
    exchange = None
    try:
        print("🔗 测试OKX API连接...")
        exchange = ccxt.okx(config)
        
        # 加载市场
        print("📊 加载市场数据...")
        markets = await exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个交易市场")
        
        # 获取余额
        print("💰 获取账户余额...")
        balance = await exchange.fetch_balance()
        print("✅ 成功获取余额信息")
        
        # 显示余额
        total = balance.get('total', {})
        free = balance.get('free', {})
        used = balance.get('used', {})
        
        print("\n余额详情:")
        for currency in total:
            if total[currency] > 0 or free[currency] > 0 or used[currency] > 0:
                print(f"  {currency}: 总计={total[currency]}, 可用={free[currency]}, 冻结={used[currency]}")
        
        print("\n✅ API连接测试完成！您的API密钥配置正确。")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("\n可能的原因:")
        print("1. API密钥错误")
        print("2. Passphrase错误")
        print("3. API权限不足")
        print("4. 网络连接问题")
        
    finally:
        if exchange:
            try:
                await exchange.close()
            except:
                pass

if __name__ == "__main__":
    print("🚨 提醒：请确保您已经在OKX删除了之前暴露的API密钥")
    print("🔑 并重新生成了新的API密钥用于测试")
    print()
    
    asyncio.run(simple_okx_test())
