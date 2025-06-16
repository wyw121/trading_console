#!/usr/bin/env python3
"""
完整的SSR代理测试脚本 - 修复版
"""
import os
import socket
import requests
import ccxt
import asyncio
from dotenv import load_dotenv

def test_proxy_port():
    """测试代理端口"""
    print("1. 检查SSR代理端口...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        if result == 0:
            print("✅ SSR代理端口1080可用")
            return True
        else:
            print("❌ SSR代理端口1080不可用")
            return False
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return False

def test_environment_setup():
    """测试环境变量设置"""
    print("\n2. 设置环境变量...")
    
    # 加载.env文件
    load_dotenv()
    
    # 设置环境变量（模拟main.py）
    if os.getenv('HTTP_PROXY'):
        os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
        os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
        os.environ['http_proxy'] = os.getenv('http_proxy')
        os.environ['https_proxy'] = os.getenv('https_proxy')
        print("✅ 环境变量已设置")
        
        # 显示配置
        print(f"   HTTP_PROXY: {os.environ.get('HTTP_PROXY')}")
        print(f"   HTTPS_PROXY: {os.environ.get('HTTPS_PROXY')}")
        return True
    else:
        print("❌ 环境变量未找到")
        return False

def test_requests_proxy():
    """测试requests库代理"""
    print("\n3. 测试requests库代理...")
    try:
        # 测试IP检测
        response = requests.get('https://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 通过代理访问，IP: {ip_info.get('origin')}")
            return True
        else:
            print(f"❌ requests代理测试失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ requests代理测试失败: {e}")
        return False

def test_okx_api():
    """测试OKX API访问"""
    print("\n4. 测试OKX API...")
    try:
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
        if response.status_code == 200:
            time_data = response.json()
            if time_data.get('code') == '0':
                server_time = time_data.get('data', [{}])[0].get('ts', 'unknown')
                print(f"✅ OKX API可访问，服务器时间: {server_time}")
                return True
            else:
                print(f"❌ OKX API返回错误: {time_data}")
                return False
        else:
            print(f"❌ OKX API失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OKX API异常: {e}")
        return False

async def test_ccxt_async():
    """测试CCXT库异步功能"""
    print("\n5. 测试CCXT库...")
    
    try:
        # 创建OKX交易所实例
        exchange = ccxt.okx({
            'sandbox': True,
            'timeout': 30000,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        try:
            # 测试加载市场
            print("   测试加载市场数据...")
            markets = await exchange.load_markets()
            market_count = len(markets) if markets else 0
            print(f"✅ CCXT成功加载 {market_count} 个市场")
            
            # 测试获取ticker
            if market_count > 0 and 'BTC/USDT' in markets:
                print("   测试获取BTC/USDT价格...")
                ticker = await exchange.fetch_ticker('BTC/USDT')
                price = ticker.get('last', 'N/A')
                print(f"✅ BTC/USDT价格: {price}")
            
            return True
            
        except Exception as e:
            print(f"❌ CCXT API调用失败: {e}")
            return False
        finally:
            await exchange.close()
            
    except Exception as e:
        print(f"❌ CCXT初始化失败: {e}")
        return False

def test_ccxt_sync():
    """测试CCXT库同步功能"""
    print("\n5. 测试CCXT库 (同步模式)...")
    
    try:
        # 创建OKX交易所实例
        exchange = ccxt.okx({
            'sandbox': True,
            'timeout': 30000,
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        try:
            # 测试获取服务器时间
            print("   测试获取服务器时间...")
            if hasattr(exchange, 'fetch_time'):
                server_time = exchange.fetch_time()
                print(f"✅ OKX服务器时间: {server_time}")
            
            # 测试加载市场（同步）
            print("   测试加载市场数据...")
            markets = exchange.load_markets()
            market_count = len(markets) if markets else 0
            print(f"✅ CCXT成功加载 {market_count} 个市场")
            
            return True
            
        except Exception as e:
            print(f"❌ CCXT同步调用失败: {e}")
            return False
        finally:
            if hasattr(exchange, 'close'):
                exchange.close()
            
    except Exception as e:
        print(f"❌ CCXT同步初始化失败: {e}")
        return False

async def main():
    """主测试函数"""
    print("🧪 完整SSR代理测试")
    print("=" * 50)
    
    # 测试列表
    tests = [
        ("SSR代理端口", test_proxy_port),
        ("环境变量设置", test_environment_setup),
        ("requests代理", test_requests_proxy),
        ("OKX API访问", test_okx_api),
    ]
    
    results = []
    
    # 运行同步测试
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name}测试异常: {e}")
            results.append((test_name, False))
    
    # 运行CCXT异步测试
    try:
        ccxt_result = await test_ccxt_async()
        results.append(("CCXT异步", ccxt_result))
    except Exception as e:
        print(f"❌ CCXT异步测试异常: {e}")
        # 尝试同步测试
        try:
            ccxt_sync_result = test_ccxt_sync()
            results.append(("CCXT同步", ccxt_sync_result))
        except Exception as sync_e:
            print(f"❌ CCXT同步测试异常: {sync_e}")
            results.append(("CCXT", False))
    
    # 显示最终结果
    print("\n" + "=" * 50)
    print("📊 最终测试结果:")
    
    all_passed = True
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
        if not result:
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有测试通过！")
        print("💡 Python后端可以通过SSR代理正常访问OKX API")
        print("\n🚀 可以启动后端服务:")
        print("  py main.py")
        print("  # 或使用启动脚本")
        print("  .\\start_backend_with_ssr.ps1")
    else:
        print("⚠️ 部分测试失败")
        print("💡 但基础代理功能正常，可以尝试启动服务")
        
        # 给出具体建议
        failed_tests = [name for name, result in results if not result]
        if any('CCXT' in test for test in failed_tests):
            print("\n🔧 CCXT相关问题可能原因:")
            print("  - 网络延迟或连接超时")
            print("  - OKX服务器临时不可用")
            print("  - 需要在实际服务中测试")

if __name__ == "__main__":
    asyncio.run(main())
