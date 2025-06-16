#!/usr/bin/env python3
"""
测试Python后端通过SSR代理访问OKX API的脚本
专门用于验证CCXT库和requests库是否正确使用SSR代理
"""
import os
import sys
import requests
import ccxt
import asyncio
import logging
from dotenv import load_dotenv
import json

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_ssr_proxy_availability():
    """测试SSR代理端口是否可用"""
    print("🔍 测试SSR代理端口可用性...")
    
    import socket
    proxy_host = '127.0.0.1'
    proxy_port = 1080
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((proxy_host, proxy_port))
        sock.close()
        
        if result == 0:
            print(f"✅ SSR代理端口 {proxy_host}:{proxy_port} 可用")
            return True
        else:
            print(f"❌ SSR代理端口 {proxy_host}:{proxy_port} 不可用")
            return False
    except Exception as e:
        print(f"❌ 测试代理端口失败: {e}")
        return False

def test_requests_with_proxy():
    """测试requests库使用SSR代理"""
    print("\n🌐 测试requests库通过SSR代理访问...")
    
    # SSR代理配置 - 使用socks5h协议确保DNS通过代理
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    
    test_urls = [
        'https://httpbin.org/ip',  # 测试IP检测
        'https://www.okx.com/api/v5/public/time',  # OKX公共API
        'https://aws.okx.com/api/v5/public/time',  # OKX AWS节点
    ]
    
    success_count = 0
    for url in test_urls:
        try:
            print(f"  测试访问: {url}")
            response = requests.get(
                url, 
                proxies=proxies, 
                timeout=15,
                headers={'User-Agent': 'Trading Console/1.0'}
            )
            
            if response.status_code == 200:
                print(f"  ✅ 成功 (状态: {response.status_code})")
                if 'httpbin.org/ip' in url:
                    ip_info = response.json()
                    print(f"  📍 代理IP: {ip_info.get('origin', 'unknown')}")
                elif 'okx.com' in url:
                    time_info = response.json()
                    print(f"  ⏰ OKX服务器时间: {time_info.get('data', [{}])[0].get('ts', 'unknown')}")
                success_count += 1
            else:
                print(f"  ❌ 失败 (状态: {response.status_code})")
                
        except Exception as e:
            print(f"  ❌ 请求失败: {e}")
    
    return success_count > 0

async def test_ccxt_with_proxy():
    """测试CCXT库使用SSR代理访问OKX"""
    print("\n🏦 测试CCXT库通过SSR代理访问OKX...")
    
    # 配置OKX (使用沙盒环境)
    config = {
        'apiKey': 'test-key',  # 测试用，不需要真实密钥
        'secret': 'test-secret',
        'passphrase': 'test-passphrase',
        'sandbox': True,
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {
            'defaultType': 'spot',
        },
        # 代理配置
        'proxies': {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
    }
    
    try:
        print("  创建OKX交易所实例...")
        exchange = ccxt.okx(config)
        
        # 测试公共API - 不需要API密钥
        print("  测试加载市场数据...")
        try:
            markets = await exchange.load_markets()
            market_count = len(markets) if markets else 0
            print(f"  ✅ 成功加载 {market_count} 个交易对")
            
            # 测试获取ticker
            if market_count > 0:
                print("  测试获取BTC/USDT价格...")
                ticker = await exchange.fetch_ticker('BTC/USDT')
                price = ticker.get('last', 'N/A')
                print(f"  ✅ BTC/USDT 价格: {price}")
                
            return True
            
        except Exception as e:
            print(f"  ❌ CCXT请求失败: {e}")
            return False
            
    except Exception as e:
        print(f"  ❌ 创建CCXT实例失败: {e}")
        return False
    finally:
        try:
            if 'exchange' in locals():
                await exchange.close()
        except:
            pass

def test_environment_variables():
    """测试环境变量代理配置"""
    print("\n🔧 检查环境变量代理配置...")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value}")
        else:
            print(f"  ⚠️ {var} 未设置")
    
    # 检查.env文件
    load_dotenv()
    print("\n  检查.env文件中的代理配置:")
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"  ✅ {var} = {value}")

def setup_environment_proxy():
    """设置环境变量代理（确保所有库都使用代理）"""
    print("\n⚙️ 设置环境变量代理...")
    
    proxy_url = 'socks5h://127.0.0.1:1080'
    
    # 设置环境变量
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        os.environ[var] = proxy_url
        print(f"  设置 {var} = {proxy_url}")

async def main():
    """主测试函数"""
    print("🚀 Python后端SSR代理配置测试")
    print("=" * 60)
    
    # 1. 测试SSR代理可用性
    if not test_ssr_proxy_availability():
        print("\n❌ SSR代理不可用，请确保:")
        print("   1. SSR客户端正在运行")
        print("   2. 本地SOCKS5端口1080已开放")
        print("   3. 防火墙允许本地连接")
        return
    
    # 2. 设置环境变量
    setup_environment_proxy()
    
    # 3. 测试环境变量
    test_environment_variables()
    
    # 4. 测试requests库
    requests_success = test_requests_with_proxy()
    
    # 5. 测试CCXT库
    ccxt_success = await test_ccxt_with_proxy()
    
    # 总结
    print("\n" + "=" * 60)
    print("📊 测试结果总结:")
    print(f"  SSR代理端口: ✅ 可用")
    print(f"  requests库代理: {'✅ 成功' if requests_success else '❌ 失败'}")
    print(f"  CCXT库代理: {'✅ 成功' if ccxt_success else '❌ 失败'}")
    
    if requests_success and ccxt_success:
        print("\n🎉 所有测试通过！Python后端可以通过SSR代理访问OKX API")
        print("\n💡 后续步骤:")
        print("   1. 确保后端启动时加载.env文件中的代理配置")
        print("   2. 确保所有API请求都通过代理")
        print("   3. 在生产环境中使用真实的API密钥")
    else:
        print("\n⚠️ 部分测试失败，请检查:")
        print("   1. SSR客户端配置是否正确")
        print("   2. 代理协议是否为socks5h://")
        print("   3. 网络连接是否正常")

if __name__ == "__main__":
    # 确保安装了必要的依赖
    try:
        import pysocks
        print("✅ pysocks 已安装")
    except ImportError:
        print("❌ 需要安装 pysocks: pip install pysocks")
        sys.exit(1)
    
    asyncio.run(main())
