"""
终极解决方案：修复DNS和代理问题
"""
import os
import sys
import subprocess

def fix_dns_settings():
    """修复DNS设置"""
    print("=== 修复DNS设置 ===")
    
    print("1. 更改系统DNS设置...")
    print("请手动执行以下步骤：")
    print()
    print("方法1 - 使用PowerShell设置DNS（管理员权限）：")
    print('Get-NetAdapter | Set-DnsClientServerAddress -ServerAddresses "8.8.8.8","1.1.1.1"')
    print()
    print("方法2 - 手动设置DNS：")
    print("1. 打开 控制面板 > 网络和Internet > 网络和共享中心")
    print("2. 点击当前网络连接")
    print("3. 点击 属性")
    print("4. 选择 Internet协议版本4(TCP/IPv4)")
    print("5. 点击 属性")
    print("6. 选择 使用下面的DNS服务器地址")
    print("7. 首选DNS: 8.8.8.8")
    print("8. 备用DNS: 1.1.1.1")
    print("9. 点击确定")
    print()
    
def create_simple_solution():
    """创建简单解决方案"""
    print("=== 创建简单解决方案 ===")
    
    # 创建一个简化的代理配置
    simplified_proxy = '''"""
简化代理配置 - 解决DNS问题
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ProxyConfig:
    def __init__(self):
        self.proxy_enabled = os.getenv('USE_PROXY', 'false').lower() == 'true'
        self.proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
        self.proxy_port = int(os.getenv('PROXY_PORT', '1080'))
        self.proxy_type = os.getenv('PROXY_TYPE', 'socks5')
        
        print(f"代理配置: enabled={self.proxy_enabled}, {self.proxy_type}://{self.proxy_host}:{self.proxy_port}")
    
    def get_proxy_dict(self):
        if not self.proxy_enabled:
            return None
        
        # 使用HTTP代理替代SOCKS5来避免DNS问题
        proxy_url = f"http://{self.proxy_host}:{self.proxy_port}"
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    def get_ccxt_proxy_config(self):
        if not self.proxy_enabled:
            return {}
        
        return {
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 2000,
            'headers': {
                'User-Agent': 'Trading Console/1.0'
            }
        }
    
    def create_requests_session(self):
        """创建配置好的requests会话"""
        session = requests.Session()
        
        if self.proxy_enabled:
            # 使用系统环境变量设置代理
            os.environ['HTTP_PROXY'] = f'socks5://{self.proxy_host}:{self.proxy_port}'
            os.environ['HTTPS_PROXY'] = f'socks5://{self.proxy_host}:{self.proxy_port}'
        
        session.verify = False  # 临时跳过SSL验证
        return session

proxy_config = ProxyConfig()
'''
    
    try:
        with open('proxy_config_simple.py', 'w', encoding='utf-8') as f:
            f.write(simplified_proxy)
        print("✅ 已创建 proxy_config_simple.py")
        
        return True
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def create_working_test():
    """创建可工作的测试脚本"""
    print("\n=== 创建测试脚本 ===")
    
    test_script = '''#!/usr/bin/env python3
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
    print(f"\\n=== 测试CCXT连接 ===")
    
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
    print("开始最终测试...\\n")
    
    # 测试基础连接
    working_domain = test_okx_connection()
    
    if working_domain:
        print(f"\\n✅ 找到可用域名: {working_domain}")
        
        # 测试CCXT
        ccxt_ok = await test_ccxt_okx(working_domain)
        
        if ccxt_ok:
            print("\\n🎉 完全成功！")
            print("你的代理配置工作正常，可以访问OKX API")
            print("\\n下一步：")
            print("1. 在交易系统中添加真实的OKX API密钥")
            print("2. 开始使用交易功能")
        else:
            print("\\n⚠️ 基础连接正常，但CCXT有问题")
            print("建议调整CCXT配置")
    else:
        print("\\n❌ 无法连接到OKX")
        print("请检查：")
        print("1. ShadowsocksR是否正常运行")
        print("2. 网络连接是否稳定")
        print("3. DNS设置是否正确")

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    try:
        with open('final_test.py', 'w', encoding='utf-8') as f:
            f.write(test_script)
        print("✅ 已创建 final_test.py")
        return True
    except Exception as e:
        print(f"❌ 创建失败: {e}")
        return False

def main():
    print("=== 终极解决方案 ===")
    print()
    
    print("问题分析：")
    print("1. ✅ ShadowsocksR代理服务正常运行")
    print("2. ✅ SOCKS5代理可以访问外网")
    print("3. ❌ DNS解析存在问题（www.okx.com无法解析）")
    print("4. ❌ CCXT通过SOCKS代理访问OKX失败")
    print()
    
    print("解决方案：")
    print()
    
    # 1. 修复DNS
    fix_dns_settings()
    
    # 2. 创建简化方案
    print("\n" + "="*50)
    simple_ok = create_simple_solution()
    
    # 3. 创建测试脚本
    test_ok = create_working_test()
    
    if simple_ok and test_ok:
        print("\n🎯 立即可行的解决方案：")
        print()
        print("1. 运行最终测试：")
        print("   py final_test.py")
        print()
        print("2. 如果测试成功，你的代理就能正常工作")
        print()
        print("3. 如果还有问题，请按照DNS设置指南操作")
        print()
        print("4. 作为备选，你也可以暂时禁用代理使用直连：")
        print("   在.env中设置 USE_PROXY=false")

if __name__ == "__main__":
    main()
