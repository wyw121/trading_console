"""
尝试使用系统代理设置解决OKX连接问题
"""
import os
import requests
import asyncio
import ccxt
from dotenv import load_dotenv

load_dotenv()

def test_system_proxy():
    """测试系统代理设置"""
    print("=== 测试系统代理设置 ===")
    
    # 方法1: 使用环境变量设置代理
    print("\n方法1: 设置环境变量代理")
    
    # 保存原始环境变量
    original_http = os.environ.get('HTTP_PROXY')
    original_https = os.environ.get('HTTPS_PROXY')
    
    try:
        # 设置代理环境变量
        os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
        os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
        
        # 测试连接
        response = requests.get('http://httpbin.org/ip', timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 环境变量代理工作正常，IP: {ip_info['origin']}")
            
            # 测试OKX
            try:
                okx_response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15, verify=False)
                if okx_response.status_code == 200:
                    data = okx_response.json()
                    print(f"✅ OKX API响应: {data}")
                    return True
                else:
                    print(f"❌ OKX API错误: {okx_response.status_code}")
            except Exception as e:
                print(f"❌ OKX连接失败: {e}")
        else:
            print(f"❌ 环境变量代理失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 环境变量代理异常: {e}")
    finally:
        # 恢复环境变量
        if original_http:
            os.environ['HTTP_PROXY'] = original_http
        else:
            os.environ.pop('HTTP_PROXY', None)
            
        if original_https:
            os.environ['HTTPS_PROXY'] = original_https
        else:
            os.environ.pop('HTTPS_PROXY', None)
    
    return False

def test_without_proxy():
    """测试不使用代理的直连"""
    print("\n=== 测试直连（不使用代理）===")
    
    try:
        # 测试直连
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=10, verify=False)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 直连OKX成功: {data}")
            return True
        else:
            print(f"❌ 直连OKX失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 直连OKX异常: {e}")
    
    return False

def check_ssr_settings():
    """检查SSR设置建议"""
    print("\n=== SSR设置建议 ===")
    
    print("请检查你的ShadowsocksR客户端设置:")
    print("")
    print("1. 系统代理模式:")
    print("   - 右键SSR托盘图标")
    print("   - 选择'系统代理模式' -> 'PAC模式'或'全局模式'")
    print("")
    print("2. 代理规则:")
    print("   - 选择'代理规则' -> '绕过局域网和大陆'")
    print("")
    print("3. 本地代理设置:")
    print("   - 确保本地端口为1080")
    print("   - 勾选'允许来自局域网的连接'")
    print("")
    print("4. 测试连接:")
    print("   - 在浏览器中访问 google.com")
    print("   - 确保能正常访问")

def create_alternative_solution():
    """创建替代解决方案"""
    print("\n=== 创建替代解决方案 ===")
    
    # 修改proxy_config.py来禁用代理
    alternative_config = '''
# 临时禁用代理的配置
import os
from dotenv import load_dotenv

load_dotenv()

class ProxyConfig:
    def __init__(self):
        # 临时禁用代理
        self.proxy_enabled = False
        print("⚠️ 代理已临时禁用，使用直连模式")
    
    def get_proxy_dict(self):
        return None
    
    def get_ccxt_proxy_config(self):
        return {}

proxy_config = ProxyConfig()
'''
    
    try:
        # 备份原始配置
        with open('proxy_config.py', 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        with open('proxy_config_backup.py', 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        print("✅ 已备份原始代理配置到 proxy_config_backup.py")
        
        # 询问用户是否要使用直连模式
        print("\n是否要临时切换到直连模式？")
        print("这将绕过代理直接连接OKX（如果你的网络环境允许）")
        
        return True
        
    except Exception as e:
        print(f"❌ 创建替代方案失败: {e}")
        return False

async def test_ccxt_direct():
    """测试CCXT直连模式"""
    print("\n=== 测试CCXT直连模式 ===")
    
    try:
        # 不使用代理的CCXT配置
        config = {
            'timeout': 30000,
            'enableRateLimit': True,
            'rateLimit': 2000,
        }
        
        exchange = ccxt.okx(config)
        
        # 测试连接
        print("测试加载市场数据...")
        markets = await exchange.load_markets()
        print(f"✅ 直连模式成功加载 {len(markets)} 个交易对")
        
        # 测试获取价格
        ticker = await exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC价格: {ticker['last']} USDT")
        
        await exchange.close()
        return True
        
    except Exception as e:
        print(f"❌ 直连模式失败: {e}")
        try:
            await exchange.close()
        except:
            pass
        return False

async def main():
    print("开始诊断代理连接问题...\n")
    
    # 1. 测试系统代理
    system_proxy_ok = test_system_proxy()
    
    # 2. 测试直连
    direct_ok = test_without_proxy()
    
    # 3. 根据结果给出建议
    if system_proxy_ok:
        print("\n✅ 系统代理工作正常")
        print("建议：使用环境变量代理模式")
    elif direct_ok:
        print("\n✅ 直连工作正常")
        print("建议：暂时使用直连模式")
        
        # 测试CCXT直连
        ccxt_direct_ok = await test_ccxt_direct()
        if ccxt_direct_ok:
            print("✅ CCXT直连模式工作正常")
            print("\n🎯 解决方案：")
            print("1. 临时禁用代理配置")
            print("2. 使用直连模式访问OKX")
            print("3. 稍后再配置代理")
            
            # 创建替代方案
            create_alternative_solution()
        else:
            print("❌ CCXT直连模式也失败")
    else:
        print("\n❌ 系统代理和直连都失败")
        print("建议：检查网络连接和SSR配置")
        check_ssr_settings()

if __name__ == "__main__":
    asyncio.run(main())
