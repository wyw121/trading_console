#!/usr/bin/env python3
"""
快速验证Python后端是否能通过SSR访问OKX
"""

import os
import requests
import ccxt
import asyncio

# 设置代理环境变量（基于你的研究）
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'

print("🎯 测试Python后端通过SSR访问OKX")
print("=" * 50)

def test_requests_proxy():
    """测试requests库代理"""
    print("\n1. 测试requests库代理...")
    
    try:
        # 显式设置代理
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        # 测试获取外部IP
        response = requests.get(
            'https://httpbin.org/ip',
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ requests代理成功")
            print(f"   外部IP: {ip_info.get('origin')}")
            return True
        else:
            print(f"❌ requests代理失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ requests代理测试失败: {e}")
        return False

async def test_ccxt_okx():
    """测试CCXT通过代理访问OKX"""
    print("\n2. 测试CCXT库访问OKX...")
    
    try:
        # 创建OKX实例（公共API，无需密钥）
        exchange = ccxt.okx({
            'sandbox': False,
            'enableRateLimit': True,
            'timeout': 30000,
        })
        
        print("   正在测试OKX公共API...")
        
        # 测试获取交易对
        markets = await exchange.load_markets()
        print(f"✅ CCXT访问OKX成功")
        print(f"   获取到 {len(markets)} 个交易对")
        
        # 测试获取价格
        if 'BTC/USDT' in markets:
            ticker = await exchange.fetch_ticker('BTC/USDT')
            print(f"   BTC/USDT价格: ${ticker['last']:,.2f}")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ CCXT访问OKX失败: {e}")
        try:
            await exchange.close()
        except:
            pass
        return False

def check_ssr_status():
    """检查SSR状态"""
    print("\n0. 检查SSR状态...")
    
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        
        if result == 0:
            print("✅ SSR端口1080可用")
            return True
        else:
            print("❌ SSR端口1080不可用")
            return False
    except Exception as e:
        print(f"❌ SSR检查失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("开始测试...")
    
    # 1. 检查SSR
    ssr_ok = check_ssr_status()
    if not ssr_ok:
        print("\n⚠️  请先启动SSR客户端并确保端口1080可用")
        return
    
    # 2. 测试requests代理
    requests_ok = test_requests_proxy()
    
    # 3. 测试CCXT访问OKX
    ccxt_ok = await test_ccxt_okx()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试结果总结:")
    print(f"SSR状态: {'✅ 正常' if ssr_ok else '❌ 异常'}")
    print(f"requests代理: {'✅ 成功' if requests_ok else '❌ 失败'}")
    print(f"CCXT访问OKX: {'✅ 成功' if ccxt_ok else '❌ 失败'}")
    
    if ssr_ok and requests_ok and ccxt_ok:
        print("\n🎉 完美！你的Python后端可以通过SSR访问OKX API")
        print("现在你可以启动交易系统，所有API调用都会通过代理")
    else:
        print("\n⚠️  需要调试。建议检查:")
        print("1. SSR客户端是否运行")
        print("2. 端口1080是否正确")
        print("3. 是否允许本地连接")

if __name__ == "__main__":
    asyncio.run(main())
