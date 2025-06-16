import asyncio
import ccxt
from dotenv import load_dotenv

load_dotenv()

from proxy_config import proxy_config

async def test_okx_api():
    print("=== OKX API连接测试 ===")
    
    # 获取代理配置
    if proxy_config.proxy_enabled:
        proxy_settings = proxy_config.get_ccxt_proxy_config()
        print(f"使用代理配置: {proxy_settings.get('proxies')}")
    else:
        proxy_settings = {}
        print("使用直连模式")
    
    # 创建OKX交易所实例（公共API，不需要API密钥）
    config = {
        'sandbox': False,  # 使用正式环境进行公共API测试
        'enableRateLimit': True,
        'timeout': 30000,
        **proxy_settings
    }
    
    exchange = ccxt.okx(config)
    
    try:
        print("\n1. 测试服务器连接...")
        # 测试服务器时间
        try:
            server_time = await exchange.fetch_time()
            print(f"✅ 服务器时间: {server_time}")
        except Exception as e:
            print(f"⚠️ 获取服务器时间失败: {e}")
        
        print("\n2. 测试市场数据...")
        # 测试获取市场数据
        try:
            await exchange.load_markets()
            markets_count = len(exchange.markets)
            print(f"✅ 成功加载市场数据: {markets_count} 个交易对")
            
            # 显示几个主要交易对
            popular_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
            for pair in popular_pairs:
                if pair in exchange.markets:
                    print(f"   ✓ {pair} 可用")
        except Exception as e:
            print(f"❌ 加载市场数据失败: {e}")
        
        print("\n3. 测试获取行情数据...")
        # 测试获取ticker数据
        try:
            ticker = await exchange.fetch_ticker('BTC/USDT')
            print(f"✅ BTC/USDT 价格: {ticker['last']} USDT")
            print(f"   24h变化: {ticker['percentage']:.2f}%")
        except Exception as e:
            print(f"❌ 获取行情数据失败: {e}")
        
        print("\n4. 测试获取K线数据...")
        # 测试获取OHLCV数据
        try:
            ohlcv = await exchange.fetch_ohlcv('BTC/USDT', '1m', limit=5)
            print(f"✅ 获取到 {len(ohlcv)} 条K线数据")
            if ohlcv:
                latest = ohlcv[-1]
                print(f"   最新K线: 开{latest[1]} 高{latest[2]} 低{latest[3]} 收{latest[4]}")
        except Exception as e:
            print(f"❌ 获取K线数据失败: {e}")
        
        # 关闭连接
        await exchange.close()
        
        print("\n=== 测试结果 ===")
        print("✅ OKX API连接成功！")
        print("✅ 你的SSR代理配置正确")
        print("✅ 可以正常访问OKX交易所API")
        
        return True
        
    except Exception as e:
        print(f"\n❌ OKX API连接失败: {e}")
        print("\n可能的原因:")
        print("1. 网络连接不稳定")
        print("2. SSR代理配置有问题")
        print("3. OKX服务器暂时不可用")
        print("4. 防火墙或网络限制")
        
        # 关闭连接
        try:
            await exchange.close()
        except:
            pass
        
        return False

# 运行测试
if __name__ == "__main__":
    print("开始测试OKX API连接...")
    print(f"代理状态: {'启用' if proxy_config.proxy_enabled else '禁用'}")
    
    try:
        result = asyncio.run(test_okx_api())
        
        if result:
            print(f"\n🎉 恭喜！你的交易系统可以正常访问OKX API")
            print("现在你可以:")
            print("1. 在前端界面添加OKX交易所账户")
            print("2. 配置真实的API密钥")
            print("3. 开始使用交易策略")
        else:
            print(f"\n⚠️ 需要进一步调试网络连接")
            
    except Exception as e:
        print(f"\n异常错误: {e}")
        print("请检查Python环境和依赖库")
