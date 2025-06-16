#!/usr/bin/env python3
"""
OKX连接调试脚本
专门用于诊断OKX API连接问题
"""
import asyncio
import ccxt
import requests
import json
from dotenv import load_dotenv

load_dotenv()

from proxy_config import proxy_config

async def debug_okx_connection():
    print("=== OKX连接调试 ===")
    
    # 1. 测试基础代理连接
    print("\n1. 测试基础代理连接...")
    try:
        proxies = proxy_config.get_proxy_dict()
        print(f"代理配置: {proxies}")
        
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        ip_info = response.json()
        print(f"✅ 代理工作正常，外部IP: {ip_info['origin']}")
    except Exception as e:
        print(f"❌ 代理连接失败: {e}")
        return False
    
    # 2. 测试OKX域名连接
    print("\n2. 测试OKX域名连接...")
    okx_domains = [
        'https://www.okx.com',
        'https://okx.com', 
        'https://api.okx.com',
        'https://aws.okx.com'
    ]
    
    working_domains = []
    for domain in okx_domains:
        try:
            print(f"测试 {domain}...")
            response = requests.get(f"{domain}/api/v5/public/time", 
                                  proxies=proxies, timeout=15, verify=False)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':
                    print(f"✅ {domain} - API响应正常")
                    working_domains.append(domain)
                else:
                    print(f"⚠️ {domain} - API错误: {data.get('msg')}")
            else:
                print(f"❌ {domain} - HTTP错误: {response.status_code}")
        except Exception as e:
            print(f"❌ {domain} - 连接失败: {str(e)[:100]}")
    
    if not working_domains:
        print("\n❌ 所有OKX域名都无法访问")
        return False
    
    print(f"\n✅ 可用域名: {working_domains}")
    
    # 3. 测试CCXT OKX连接
    print("\n3. 测试CCXT OKX连接...")
    best_domain = working_domains[0]
    
    try:
        # 创建自定义requests会话
        session = requests.Session()
        session.proxies.update(proxies)
        session.verify = False
        
        # 配置CCXT
        config = {
            'urls': {
                'api': {
                    'public': f"{best_domain}/api/v5",
                    'private': f"{best_domain}/api/v5"
                }
            },
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 2000,
            'session': session,  # 使用自定义session
            'options': {
                'defaultType': 'spot'
            }
        }
        
        print(f"使用域名: {best_domain}")
        exchange = ccxt.okx(config)
        
        # 测试市场数据
        print("测试加载市场数据...")
        markets = await exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个交易对")
        
        # 测试获取ticker
        print("测试获取BTC价格...")
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC价格: {ticker['last']} USDT")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ CCXT连接失败: {e}")
        try:
            await exchange.close()
        except:
            pass
        return False

async def test_real_trading_engine():
    print("\n=== 测试真实交易引擎 ===")
    
    try:
        from real_trading_engine import RealExchangeManager
        
        engine = RealExchangeManager()
        
        # 使用测试配置
        test_config = {
            'apiKey': 'test_key',
            'secret': 'test_secret', 
            'passphrase': 'test_passphrase',
            'sandbox': True
        }
        
        print("测试创建OKX连接...")
        try:
            exchange = await engine.create_real_exchange('okx', test_config)
            print("✅ 交易引擎创建OKX连接成功")
            
            if hasattr(exchange, 'close'):
                await exchange.close()
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api" in error_msg.lower():
                print("✅ 网络连接正常（API认证失败是正常的，因为使用测试密钥）")
                return True
            else:
                print(f"❌ 交易引擎连接失败: {error_msg}")
                return False
                
    except Exception as e:
        print(f"❌ 交易引擎导入失败: {e}")
        return False

def main():
    print("开始OKX连接调试...\n")
    
    # 检查代理配置
    print(f"代理状态: {'启用' if proxy_config.proxy_enabled else '禁用'}")
    print(f"代理地址: {proxy_config.proxy_host}:{proxy_config.proxy_port}")
    print(f"代理类型: {proxy_config.proxy_type}")
    
    async def run_tests():
        # 测试直接连接
        direct_ok = await debug_okx_connection()
        
        # 测试交易引擎
        if direct_ok:
            engine_ok = await test_real_trading_engine()
        else:
            engine_ok = False
        
        print(f"\n=== 调试结果 ===")
        print(f"直接OKX连接: {'✅ 成功' if direct_ok else '❌ 失败'}")
        print(f"交易引擎连接: {'✅ 成功' if engine_ok else '❌ 失败'}")
        
        if direct_ok and engine_ok:
            print("\n🎉 所有测试通过！你的代理配置完全正常。")
            print("如果仍然有连接问题，可能是:")
            print("1. API密钥配置问题")
            print("2. 交易所临时限制")
            print("3. 网络波动")
        elif direct_ok and not engine_ok:
            print("\n⚠️ 直连正常，但交易引擎有问题。")
            print("需要检查 real_trading_engine.py 的代理集成。")
        else:
            print("\n❌ 网络连接异常，需要检查代理配置。")
    
    asyncio.run(run_tests())

if __name__ == "__main__":
    main()
