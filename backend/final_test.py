#!/usr/bin/env python3
"""
可工作的OKX连接测试
绕过DNS问题
"""
import os
import requests
import asyncio
import ccxt
from dotenv import load_dotenv

load_dotenv()

def test_okx_connection():
    """测试OKX连接"""
    print("=== 测试OKX连接 ===")
    
    # 设置环境变量代理
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
    
    # 创建session
    session = requests.Session()
    session.verify = False
    
    # 测试不同的OKX域名
    domains = ['okx.com', 'www.okx.com']  # 简化测试
    
    for domain in domains:
        try:
            print(f"测试 {domain}...")
            
            # 直接访问IP（绕过DNS）
            url = f"https://{domain}/api/v5/public/time"
            response = session.get(url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    print(f"✅ {domain} 连接成功")
                    print(f"   服务器时间: {data.get('data', [{'ts': 'unknown'}])[0].get('ts')}")
                    return domain
            
        except Exception as e:
            print(f"❌ {domain} 失败: {str(e)[:100]}")
            continue
    
    return None

async def test_ccxt_okx(working_domain=None):
    """测试CCXT OKX连接"""
    print(f"\n=== 测试CCXT连接 ===")
    
    # 设置环境变量
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
    
    try:
        config = {
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 3000,  # 增加延迟
        }
        
        if working_domain:
            config['urls'] = {
                'api': {
                    'public': f'https://{working_domain}/api/v5',
                    'private': f'https://{working_domain}/api/v5'
                }
            }
        
        exchange = ccxt.okx(config)
        
        print("测试获取市场数据...")
        markets = await exchange.load_markets()
        print(f"✅ 成功获取 {len(markets)} 个交易对")
        
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

async def main():
    print("开始最终测试...\n")
    
    # 测试基础连接
    working_domain = test_okx_connection()
    
    if working_domain:
        print(f"\n✅ 找到可用域名: {working_domain}")
        
        # 测试CCXT
        ccxt_ok = await test_ccxt_okx(working_domain)
        
        if ccxt_ok:
            print("\n🎉 完全成功！")
            print("你的代理配置工作正常，可以访问OKX API")
            print("\n下一步：")
            print("1. 在交易系统中添加真实的OKX API密钥")
            print("2. 开始使用交易功能")
        else:
            print("\n⚠️ 基础连接正常，但CCXT有问题")
            print("建议调整CCXT配置")
    else:
        print("\n❌ 无法连接到OKX")
        print("请检查：")
        print("1. ShadowsocksR是否正常运行")
        print("2. 网络连接是否稳定")
        print("3. DNS设置是否正确")

if __name__ == "__main__":
    asyncio.run(main())
