"""
修复OKX域名解析问题
使用可解析的域名
"""
import requests
import asyncio
import ccxt
from dotenv import load_dotenv

load_dotenv()

def test_okx_domains():
    """测试不同的OKX域名"""
    print("=== 测试OKX域名解析 ===")
    
    domains = [
        'okx.com',           # 这个可以解析
        'www.okx.com',       # 这个无法解析
        'api.okx.com',
        'aws.okx.com'
    ]
    
    working_domains = []
    proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    for domain in domains:
        try:
            print(f"测试 {domain}...")
            url = f"https://{domain}/api/v5/public/time"
            
            response = requests.get(url, proxies=proxies, timeout=15, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    print(f"✅ {domain} - API正常")
                    working_domains.append(domain)
                else:
                    print(f"⚠️ {domain} - API错误: {data.get('msg')}")
            else:
                print(f"❌ {domain} - HTTP错误: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {domain} - 连接失败: {str(e)[:100]}")
    
    return working_domains

async def test_ccxt_with_working_domain(domain):
    """使用工作的域名测试CCXT"""
    print(f"\n=== 使用 {domain} 测试CCXT ===")
    
    try:
        # 创建requests会话
        session = requests.Session()
        session.proxies = {
            'http': 'socks5://127.0.0.1:1080',
            'https': 'socks5://127.0.0.1:1080'
        }
        session.verify = False
        
        # 配置CCXT使用特定域名
        config = {
            'urls': {
                'api': {
                    'public': f'https://{domain}/api/v5',
                    'private': f'https://{domain}/api/v5'
                }
            },
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 2000,
            'session': session
        }
        
        exchange = ccxt.okx(config)
        
        # 测试获取市场数据
        print("测试加载市场数据...")
        markets = await exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个交易对")
        
        # 测试获取价格
        print("测试获取BTC价格...")
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC价格: {ticker['last']} USDT")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ CCXT测试失败: {e}")
        try:
            await exchange.close()
        except:
            pass
        return False

def update_trading_engine():
    """更新交易引擎使用正确的域名"""
    print(f"\n=== 更新交易引擎配置 ===")
    
    # 读取现有代码
    try:
        with open('real_trading_engine.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 替换域名列表
        old_domains = '''okx_urls = [
                    'https://www.okx.com',
                    'https://aws.okx.com', 
                    'https://okx.com',
                    'https://api.okx.com'
                ]'''
        
        new_domains = '''okx_urls = [
                    'https://okx.com',           # 主域名，可以解析
                    'https://api.okx.com',       # API域名
                    'https://aws.okx.com',       # AWS域名
                    'https://www.okx.com'        # www域名（可能有DNS问题）
                ]'''
        
        if old_domains in content:
            content = content.replace(old_domains, new_domains)
            
            with open('real_trading_engine.py', 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("✅ 已更新交易引擎域名配置")
            return True
        else:
            print("⚠️ 未找到需要更新的域名配置")
            return False
            
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

async def main():
    print("开始修复OKX连接问题...\n")
    
    # 1. 测试域名
    working_domains = test_okx_domains()
    
    if not working_domains:
        print("\n❌ 没有可用的OKX域名")
        print("请检查:")
        print("1. ShadowsocksR客户端是否正常运行")
        print("2. 网络连接是否稳定")
        print("3. DNS设置是否正确")
        return
    
    print(f"\n✅ 可用域名: {working_domains}")
    
    # 2. 使用最佳域名测试CCXT
    best_domain = working_domains[0]
    ccxt_ok = await test_ccxt_with_working_domain(best_domain)
    
    # 3. 更新交易引擎
    if ccxt_ok:
        update_ok = update_trading_engine()
        
        if update_ok:
            print(f"\n🎉 修复完成！")
            print(f"✅ 使用域名: {best_domain}")
            print(f"✅ CCXT连接正常")
            print(f"✅ 交易引擎已更新")
            print(f"\n现在你可以重试添加OKX交易所账户了！")
        else:
            print(f"\n⚠️ CCXT工作正常，但交易引擎更新失败")
            print(f"请手动修改 real_trading_engine.py 中的域名顺序")
    else:
        print(f"\n❌ CCXT连接仍有问题")
        print(f"建议联系技术支持进一步调试")

if __name__ == "__main__":
    asyncio.run(main())
