"""
OKX API 连接修复脚本
专门用于修复 OKX API 连接问题
"""
import os
import sys
import asyncio
import ccxt
import requests
import socket
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 您的 API 配置
OKX_CONFIG = {
    'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
    'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',  
    'passphrase': 'vf5Y3UeUFiz6xfF!',
    'sandbox': False,  # 使用真实环境，因为您的密钥是只读权限
    'enableRateLimit': True,
    'rateLimit': 100,
    'timeout': 30000,
    'verbose': True
}

# 代理配置
PROXY_CONFIG = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

# OKX 域名列表
OKX_DOMAINS = [
    'www.okx.com',
    'aws.okx.com', 
    'okx.com',
    'www.okex.com',
    'okex.com'
]

def set_proxy_env():
    """设置代理环境变量"""
    os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
    os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
    os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'
    print("✅ 代理环境变量已设置")

def test_proxy_connection():
    """测试代理连接"""
    print("\n🔍 测试代理连接...")
    try:
        # 测试代理是否工作
        response = requests.get('http://httpbin.org/ip', proxies=PROXY_CONFIG, timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 代理连接成功，当前IP: {ip_info.get('origin')}")
            return True
        else:
            print(f"❌ 代理连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 代理连接异常: {e}")
        return False

def test_domain_connectivity():
    """测试 OKX 域名连通性"""
    print("\n🌐 测试 OKX 域名连通性...")
    
    for domain in OKX_DOMAINS:
        try:
            # 测试 DNS 解析
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} -> {ip}")
            
            # 测试 HTTP 连接
            url = f"https://{domain}"
            response = requests.get(url, proxies=PROXY_CONFIG, timeout=10, verify=False)
            print(f"   HTTP状态: {response.status_code}")
            
        except socket.gaierror as e:
            print(f"❌ {domain} DNS解析失败: {e}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {domain} 连接失败: {e}")
        except Exception as e:
            print(f"❌ {domain} 未知错误: {e}")

def test_ccxt_okx_sync():
    """测试 CCXT OKX 同步连接"""
    print("\n🔧 测试 CCXT OKX 同步连接...")
    
    try:
        # 创建 OKX 交易所实例
        exchange = ccxt.okx(OKX_CONFIG)
        
        # 设置代理 (CCXT 同步版本)
        exchange.proxies = PROXY_CONFIG
        
        print("1️⃣ 测试获取交易所状态...")
        try:
            # 测试公共API
            markets = exchange.load_markets()
            print(f"✅ 成功加载 {len(markets)} 个交易对")
            
            # 获取服务器时间
            server_time = exchange.milliseconds()
            print(f"✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
            
        except Exception as e:
            print(f"❌ 公共API失败: {e}")
            return False
            
        print("2️⃣ 测试私有API...")
        try:
            # 测试账户信息 (只读权限)
            balance = exchange.fetch_balance()
            print("✅ 成功获取账户余额信息")
            print(f"   总资产: {balance.get('total', {})}")
            
        except Exception as e:
            print(f"❌ 私有API失败: {e}")
            # 打印详细错误信息
            if hasattr(e, 'response'):
                print(f"   响应内容: {e.response}")
            return False
            
        print("✅ CCXT OKX 连接测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ CCXT 连接失败: {e}")
        return False

async def test_ccxt_okx_async():
    """测试 CCXT OKX 异步连接"""
    print("\n⚡ 测试 CCXT OKX 异步连接...")
    
    try:
        # 创建异步 OKX 交易所实例
        exchange = ccxt.pro.okx(OKX_CONFIG)
        
        # 设置代理
        exchange.session.proxies = PROXY_CONFIG
        
        print("1️⃣ 测试异步公共API...")
        try:
            # 获取ticker
            ticker = await exchange.fetch_ticker('BTC/USDT')
            print(f"✅ BTC/USDT 价格: {ticker['last']}")
            
        except Exception as e:
            print(f"❌ 异步公共API失败: {e}")
            return False
            
        print("2️⃣ 测试异步私有API...")
        try:
            # 获取账户余额
            balance = await exchange.fetch_balance()
            print("✅ 成功获取异步账户余额")
            
        except Exception as e:
            print(f"❌ 异步私有API失败: {e}")
            return False
            
        print("✅ CCXT OKX 异步连接测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 异步连接失败: {e}")
        return False
    finally:
        if 'exchange' in locals():
            await exchange.close()

def main():
    """主函数"""
    print("🚀 OKX API 连接修复诊断")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print(f"API Key (前8位): {OKX_CONFIG['apiKey'][:8]}...")
    print(f"权限: 只读")
    print("=" * 60)
    
    # 设置代理环境变量
    set_proxy_env()
    
    # 步骤1: 测试代理连接
    if not test_proxy_connection():
        print("\n❌ 代理连接失败，请检查 SSR 客户端是否运行在端口 1080")
        return
    
    # 步骤2: 测试域名连通性
    test_domain_connectivity()
    
    # 步骤3: 测试同步连接
    if test_ccxt_okx_sync():
        print("\n🎉 同步连接成功！")
    else:
        print("\n❌ 同步连接失败")
        
    # 步骤4: 测试异步连接
    try:
        asyncio.run(test_ccxt_okx_async())
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
    
    print("\n📋 诊断完成")

if __name__ == "__main__":
    main()
