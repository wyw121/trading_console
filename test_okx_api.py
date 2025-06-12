#!/usr/bin/env python3
"""
测试OKX API配置
"""
import ccxt
import asyncio

async def test_okx_api():
    """测试OKX API连接"""
    print("🧪 Testing OKX API Configuration")
    print("=" * 50)
    
    # 您提供的API信息
    api_credentials = {
        'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'passphrase': 'vf5Y3UeUFiz6xfF!',
        'sandbox': True,  # 测试网
        'enableRateLimit': True,
    }
    
    print(f"API Key: {api_credentials['apiKey'][:8]}...")
    print(f"Secret: {api_credentials['secret'][:8]}...")
    print(f"Passphrase: {api_credentials['passphrase'][:4]}...")
    print(f"Sandbox Mode: {api_credentials['sandbox']}")
    
    try:
        # 创建OKX交易所实例
        print("\n📡 Creating OKX exchange instance...")
        exchange = ccxt.okex(api_credentials)
        
        print(f"Exchange URL: {exchange.urls['api']['public']}")
        print(f"Sandbox: {exchange.sandbox}")
        
        # 测试连接 - 获取账户信息
        print("\n🔍 Testing account info...")
        try:
            account_info = await exchange.fetch_balance()
            print("✅ Account balance fetched successfully!")
            
            # 显示非零余额
            for currency, balance in account_info['total'].items():
                if balance > 0:
                    print(f"   {currency}: {balance}")
                    
        except Exception as e:
            print(f"❌ Account balance failed: {e}")
            
        # 测试获取ticker
        print("\n📈 Testing ticker data...")
        try:
            ticker = await exchange.fetch_ticker('BTC/USDT')
            print("✅ Ticker data fetched successfully!")
            print(f"   BTC/USDT Price: {ticker['last']}")
        except Exception as e:
            print(f"❌ Ticker fetch failed: {e}")
            
        # 测试市场数据
        print("\n📊 Testing market data...")
        try:
            markets = await exchange.load_markets()
            print(f"✅ Markets loaded: {len(markets)} trading pairs available")
        except Exception as e:
            print(f"❌ Markets load failed: {e}")
            
    except Exception as e:
        print(f"❌ Exchange creation failed: {e}")
        
    print("\n" + "=" * 50)
    print("🎯 Test Summary:")
    print("如果看到上述测试成功，说明API配置正确")
    print("如果失败，可能需要:")
    print("1. 检查API密钥是否正确")
    print("2. 确认IP白名单设置")
    print("3. 验证API权限配置")

if __name__ == "__main__":
    asyncio.run(test_okx_api())
