import asyncio
import ccxt

async def test_direct():
    try:
        print("测试OKX直连...")
        exchange = ccxt.okx({
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 2000
        })
        
        markets = await exchange.load_markets()
        print(f"✅ 成功获取 {len(markets)} 个交易对")
        
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC价格: {ticker['last']} USDT")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ 直连失败: {e}")
        try:
            await exchange.close()
        except:
            pass
        return False

if __name__ == "__main__":
    result = asyncio.run(test_direct())
    if result:
        print("\n🎉 直连模式工作正常！")
        print("你现在可以使用交易系统了（不通过代理）")
    else:
        print("\n❌ 需要使用代理才能访问OKX")
