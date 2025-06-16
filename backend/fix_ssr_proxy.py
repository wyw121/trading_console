#!/usr/bin/env python3
"""
修复SSR代理配置问题的脚本
解决验证失败的项目
"""
import os
import sys
import subprocess
import socket
from pathlib import Path

def check_and_install_dependencies():
    """检查并安装必要的依赖"""
    print("📦 检查并安装必要依赖...")
    
    required_packages = [
        'pysocks',
        'python-dotenv', 
        'requests',
        'ccxt'
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} 已安装")
        except ImportError:
            print(f"⚠️ {package} 未安装，正在安装...")
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                print(f"✅ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"❌ {package} 安装失败: {e}")
                return False
    
    return True

def test_proxy_connection():
    """测试代理连接"""
    print("\n🌐 测试代理连接...")
    
    try:
        import requests
        
        # 代理配置
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        # 测试基本连接
        print("  测试基本代理连接...")
        try:
            response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
            if response.status_code == 200:
                ip_info = response.json()
                print(f"  ✅ 代理IP: {ip_info.get('origin')}")
            else:
                print(f"  ❌ 代理连接失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ 代理连接异常: {e}")
            return False
        
        # 测试OKX API
        print("  测试OKX API访问...")
        try:
            response = requests.get(
                'https://www.okx.com/api/v5/public/time', 
                proxies=proxies, 
                timeout=15
            )
            if response.status_code == 200:
                time_data = response.json()
                if time_data.get('code') == '0':
                    print(f"  ✅ OKX API可访问")
                    return True
                else:
                    print(f"  ❌ OKX API返回错误: {time_data}")
                    return False
            else:
                print(f"  ❌ OKX API失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ OKX API异常: {e}")
            return False
            
    except ImportError:
        print("❌ requests库导入失败")
        return False

def test_environment_variables():
    """测试环境变量加载"""
    print("\n🔧 测试环境变量...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
        success_count = 0
        
        for var in proxy_vars:
            value = os.getenv(var)
            if value and 'socks5h://127.0.0.1:1080' in value:
                print(f"  ✅ {var} = {value}")
                success_count += 1
            else:
                print(f"  ❌ {var} 未正确设置")
        
        return success_count >= 2  # 至少需要HTTP_PROXY和HTTPS_PROXY
        
    except ImportError:
        print("❌ python-dotenv导入失败")
        return False

def test_ccxt_with_proxy():
    """测试CCXT库使用代理"""
    print("\n🏦 测试CCXT库代理功能...")
    
    try:
        import ccxt
        import asyncio
        
        # 设置环境变量（模拟main.py行为）
        os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
        os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
        os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
        os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'
        
        async def test_okx():
            config = {
                'sandbox': True,
                'enableRateLimit': True,
                'timeout': 30000,
                'options': {
                    'defaultType': 'spot',
                }
            }
            
            exchange = ccxt.okx(config)
            
            try:
                # 测试公共API
                print("  测试CCXT加载市场数据...")
                markets = await exchange.load_markets()
                print(f"  ✅ 成功加载 {len(markets)} 个交易对")
                
                # 测试ticker
                if 'BTC/USDT' in markets:
                    print("  测试获取BTC/USDT价格...")
                    ticker = await exchange.fetch_ticker('BTC/USDT')
                    price = ticker.get('last', 'N/A')
                    print(f"  ✅ BTC/USDT价格: {price}")
                
                return True
                
            except Exception as e:
                print(f"  ❌ CCXT请求失败: {e}")
                return False
            finally:
                await exchange.close()
        
        # 运行异步测试
        return asyncio.run(test_okx())
        
    except ImportError:
        print("❌ ccxt库导入失败")
        return False
    except Exception as e:
        print(f"❌ CCXT测试异常: {e}")
        return False

def create_test_summary():
    """创建测试摘要脚本"""
    print("\n📝 生成完整测试脚本...")
    
    test_script = '''#!/usr/bin/env python3
"""
完整的SSR代理测试脚本
"""
import os
import socket
import requests
import ccxt
import asyncio
from dotenv import load_dotenv

def main():
    print("🧪 完整SSR代理测试")
    print("=" * 40)
    
    # 1. 检查代理端口
    print("\\n1. 检查SSR代理端口...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        if result == 0:
            print("✅ SSR代理端口1080可用")
        else:
            print("❌ SSR代理端口1080不可用")
            return
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return
    
    # 2. 加载环境变量
    print("\\n2. 加载环境变量...")
    load_dotenv()
    
    # 设置环境变量（模拟main.py）
    if os.getenv('HTTP_PROXY'):
        os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
        os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
        os.environ['http_proxy'] = os.getenv('http_proxy')
        os.environ['https_proxy'] = os.getenv('https_proxy')
        print("✅ 环境变量已设置")
    else:
        print("❌ 环境变量未找到")
    
    # 3. 测试requests代理
    print("\\n3. 测试requests库代理...")
    try:
        response = requests.get('https://httpbin.org/ip', timeout=10)
        ip_info = response.json()
        print(f"✅ 通过代理访问，IP: {ip_info.get('origin')}")
    except Exception as e:
        print(f"❌ requests代理测试失败: {e}")
    
    # 4. 测试OKX API
    print("\\n4. 测试OKX API...")
    try:
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
        if response.status_code == 200:
            print("✅ OKX API可访问")
        else:
            print(f"❌ OKX API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ OKX API异常: {e}")
    
    # 5. 测试CCXT
    print("\\n5. 测试CCXT库...")
    
    async def test_ccxt():
        try:
            exchange = ccxt.okx({'sandbox': True, 'timeout': 30000})
            markets = await exchange.load_markets()
            print(f"✅ CCXT成功加载 {len(markets)} 个市场")
            await exchange.close()
        except Exception as e:
            print(f"❌ CCXT测试失败: {e}")
    
    asyncio.run(test_ccxt())
    
    print("\\n🎉 测试完成！")

if __name__ == "__main__":
    main()
'''
    
    with open('complete_proxy_test.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("✅ 完整测试脚本已生成: complete_proxy_test.py")

def main():
    """主修复函数"""
    print("🔧 SSR代理配置修复工具")
    print("=" * 50)
    
    # 1. 检查并安装依赖
    if not check_and_install_dependencies():
        print("❌ 依赖安装失败，请手动安装")
        return False
    
    # 2. 测试环境变量
    env_ok = test_environment_variables()
    
    # 3. 测试代理连接
    proxy_ok = test_proxy_connection()
    
    # 4. 测试CCXT
    ccxt_ok = test_ccxt_with_proxy()
    
    # 5. 生成测试脚本
    create_test_summary()
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 修复结果总结:")
    print(f"  依赖包安装: ✅ 完成")
    print(f"  环境变量: {'✅ 通过' if env_ok else '❌ 失败'}")
    print(f"  代理连接: {'✅ 通过' if proxy_ok else '❌ 失败'}")
    print(f"  CCXT库: {'✅ 通过' if ccxt_ok else '❌ 失败'}")
    
    if env_ok and proxy_ok and ccxt_ok:
        print("\n🎉 所有问题已修复！")
        print("💡 现在可以正常启动后端服务了")
        return True
    else:
        print("\n⚠️ 仍有问题需要解决")
        if not env_ok:
            print("  - 检查.env文件中的代理配置")
        if not proxy_ok:
            print("  - 检查SSR客户端是否正常运行")
        if not ccxt_ok:
            print("  - 检查网络连接和防火墙设置")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🚀 可以使用以下命令启动后端:")
        print("  py main.py")
        print("  # 或")
        print("  .\\start_backend_with_ssr.ps1")
    
    input("\n按Enter键退出...")
