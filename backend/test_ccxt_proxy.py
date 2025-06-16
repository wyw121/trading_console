import asyncio
import ccxt
import requests
from dotenv import load_dotenv

load_dotenv()

async def test_ccxt_with_proxy():
    print("=== CCXT代理配置测试 ===")
    
    # 方法1: 直接在exchange配置中设置代理
    print("\n方法1: 使用requests会话代理")
    
    # 创建带代理的requests会话
    session = requests.Session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    # 修改CCXT的OKX配置
    config = {
        'timeout': 30000,
        'enableRateLimit': True,
        'rateLimit': 2000,
        'session': session  # 传入自定义session
    }
    
    try:
        exchange = ccxt.okx(config)
        
        # 测试公共API
        print("测试获取交易对...")
        markets = await exchange.load_markets()
        print(f"✅ 成功获取 {len(markets)} 个交易对")
        
        # 测试获取ticker
        print("测试获取BTC价格...")
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC价格: {ticker['last']} USDT")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ 方法1失败: {e}")
        try:
            await exchange.close()
        except:
            pass
    
    # 方法2: 设置环境变量
    print("\n方法2: 设置环境变量代理")
    import os
    
    original_proxy = os.environ.get('HTTPS_PROXY')
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
    
    try:
        exchange = ccxt.okx({
            'timeout': 30000,
            'enableRateLimit': True,
        })
        
        print("测试获取服务器时间...")
        server_time = await exchange.fetch_time()
        print(f"✅ 服务器时间: {server_time}")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ 方法2失败: {e}")
        try:
            await exchange.close()
        except:
            pass
    finally:
        # 恢复环境变量
        if original_proxy:
            os.environ['HTTPS_PROXY'] = original_proxy
        else:
            os.environ.pop('HTTPS_PROXY', None)
        os.environ.pop('HTTP_PROXY', None)
    
    # 方法3: 使用不同的OKX域名
    print("\n方法3: 尝试不同的OKX域名")
    
    okx_urls = [
        'https://www.okx.com',
        'https://aws.okx.com', 
        'https://okx.com'
    ]
    
    for base_url in okx_urls:
        try:
            print(f"尝试连接: {base_url}")
            
            # 创建带代理的session
            session = requests.Session()
            session.proxies = {
                'http': 'socks5://127.0.0.1:1080',
                'https': 'socks5://127.0.0.1:1080'
            }
            
            config = {
                'urls': {
                    'api': {
                        'public': f"{base_url}/api/v5",
                        'private': f"{base_url}/api/v5"
                    }
                },
                'timeout': 30000,
                'enableRateLimit': True,
                'session': session
            }
            
            exchange = ccxt.okx(config)
            
            # 测试简单的公共API
            ticker = await exchange.fetch_ticker('BTC/USDT')
            print(f"✅ 成功连接 {base_url}")
            print(f"   BTC价格: {ticker['last']} USDT")
            
            await exchange.close()
            return True
            
        except Exception as e:
            print(f"❌ {base_url} 失败: {str(e)[:100]}...")
            try:
                await exchange.close()
            except:
                pass
            continue
    
    return False

# 简化测试：直接用requests测试OKX API
def test_okx_api_with_requests():
    print("\n=== 直接用requests测试OKX API ===")
    
    session = requests.Session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    session.verify = False  # 跳过SSL验证
    
    # 测试OKX公共API
    api_urls = [
        ('服务器时间', 'https://www.okx.com/api/v5/public/time'),
        ('BTC价格', 'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT'),
        ('交易对', 'https://www.okx.com/api/v5/public/instruments?instType=SPOT')
    ]
    
    success_count = 0
    for name, url in api_urls:
        try:
            response = session.get(url, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':  # OKX API成功响应
                    print(f"✅ {name}: 成功")
                    success_count += 1
                    
                    if 'ticker' in url:
                        ticker_data = data['data'][0]
                        print(f"   BTC价格: {ticker_data['last']} USDT")
                else:
                    print(f"⚠️ {name}: API错误 - {data.get('msg', '未知错误')}")
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)[:100]}...")
    
    return success_count > 0

if __name__ == "__main__":
    print("开始测试CCXT代理配置...")
    
    # 先用requests测试
    requests_ok = test_okx_api_with_requests()
    
    if requests_ok:
        print("\n✅ requests方式访问OKX API成功！")
        print("现在测试CCXT...")
        
        # 再测试CCXT
        ccxt_ok = asyncio.run(test_ccxt_with_proxy())
        
        if ccxt_ok:
            print("\n🎉 CCXT代理配置成功！")
            print("你的交易系统现在可以通过SSR访问OKX API")
        else:
            print("\n⚠️ CCXT代理配置需要进一步调试")
            print("但requests方式工作正常，可以作为备选方案")
    else:
        print("\n❌ 网络连接有问题，请检查SSR配置")
