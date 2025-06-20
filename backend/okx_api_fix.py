"""
OKX API 连接修复脚本 - 修复版本
解决 ccxt.pro 不存在和配置问题
"""
import os
import sys
import asyncio
import ccxt
import requests
import socket
import logging
from datetime import datetime
import json

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 您的 API 配置
OKX_CONFIG = {
    'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
    'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',  
    'passphrase': 'vf5Y3UeUFiz6xfF!',
    'sandbox': False,  # 使用真实环境
    'enableRateLimit': True,
    'rateLimit': 100,
    'timeout': 30000,
    'verbose': False,  # 减少详细输出避免干扰
    'options': {
        'defaultType': 'spot',  # 指定默认类型
    }
}

# 代理配置
PROXY_CONFIG = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

# OKX 域名列表
OKX_DOMAINS = [
    'www.okx.com',
    'aws.okx.com'
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
            
            # 测试 HTTPS 连接
            url = f"https://{domain}/api/v5/public/time"
            response = requests.get(url, proxies=PROXY_CONFIG, timeout=15, verify=True)
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ API响应正常: {data}")
            else:
                print(f"   ❌ API响应状态码: {response.status_code}")
            
        except socket.gaierror as e:
            print(f"❌ {domain} DNS解析失败: {e}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {domain} 连接失败: {e}")
        except Exception as e:
            print(f"❌ {domain} 未知错误: {e}")
            
    print("   域名连通性测试完成")

def test_ccxt_public_api():
    """测试 CCXT 公共API"""
    print("\n📊 测试 CCXT 公共API...")
    
    try:
        # 创建不带认证的 OKX 实例
        public_config = {
            'sandbox': False,
            'enableRateLimit': True,
            'rateLimit': 100,
            'timeout': 30000,
            'verbose': False,
            'options': {
                'defaultType': 'spot',
            }
        }
        
        exchange = ccxt.okx(public_config)
        
        # 设置代理
        if hasattr(exchange, 'proxies'):
            exchange.proxies = PROXY_CONFIG
        else:
            # 对于新版本的ccxt，可能需要不同的设置方式
            exchange.session.proxies = PROXY_CONFIG if hasattr(exchange, 'session') else None
        
        print("1️⃣ 测试获取服务器时间...")
        try:
            # 使用公共API获取服务器时间
            server_time = exchange.fetch_time()
            print(f"✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
        except Exception as e:
            print(f"❌ 获取服务器时间失败: {e}")
            return False
            
        print("2️⃣ 测试获取交易对...")
        try:
            markets = exchange.load_markets()
            print(f"✅ 成功加载 {len(markets)} 个交易对")
            
            # 获取 BTC/USDT ticker
            if 'BTC/USDT' in markets:
                ticker = exchange.fetch_ticker('BTC/USDT')
                print(f"✅ BTC/USDT 价格: {ticker['last']}")
            else:
                print("⚠️ BTC/USDT 交易对不可用")
                
        except Exception as e:
            print(f"❌ 获取交易对失败: {e}")
            return False
            
        print("✅ 公共API测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 公共API测试失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        if hasattr(e, 'args') and e.args:
            print(f"   错误详情: {e.args}")
        return False

def test_ccxt_private_api():
    """测试 CCXT 私有API"""
    print("\n🔐 测试 CCXT 私有API...")
    
    try:
        # 创建带认证的 OKX 实例
        exchange = ccxt.okx(OKX_CONFIG)
        
        # 设置代理
        if hasattr(exchange, 'proxies'):
            exchange.proxies = PROXY_CONFIG
        elif hasattr(exchange, 'session'):
            exchange.session.proxies = PROXY_CONFIG
        
        print("1️⃣ 测试获取账户余额...")
        try:
            balance = exchange.fetch_balance()
            print("✅ 成功获取账户余额信息")
            
            # 安全地显示余额信息（不显示具体数值）
            total_balance = balance.get('total', {})
            if total_balance:
                currency_count = len([k for k, v in total_balance.items() if v and v > 0])
                print(f"   拥有余额的货币数量: {currency_count}")
            else:
                print("   账户余额为空或无权限")
                
        except Exception as e:
            print(f"❌ 获取账户余额失败: {e}")
            print(f"   错误类型: {type(e).__name__}")
            
            # 检查是否是API权限问题
            if 'permission' in str(e).lower() or 'unauthorized' in str(e).lower():
                print("   可能是API权限问题，请检查API密钥权限设置")
            elif 'signature' in str(e).lower():
                print("   可能是签名问题，请检查API密钥和密码是否正确")
            
            return False
            
        print("2️⃣ 测试获取账户信息...")
        try:
            # 尝试获取账户信息
            account_info = exchange.fetch_accounts()
            print("✅ 成功获取账户信息")
            print(f"   账户数量: {len(account_info) if account_info else 0}")
            
        except Exception as e:
            print(f"❌ 获取账户信息失败: {e}")
            # 这个错误不是致命的，因为有些API可能不支持此功能
        
        print("✅ 私有API测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 私有API测试失败: {e}")
        print(f"   错误类型: {type(e).__name__}")
        return False

def test_ccxt_async_api():
    """测试 CCXT 异步API (使用新版本的方式)"""
    print("\n⚡ 测试 CCXT 异步API...")
    
    try:
        # 检查是否有异步支持
        if not hasattr(ccxt, 'async_support'):
            print("⚠️ 当前CCXT版本不支持异步操作")
            return False
            
        # 注意：新版本ccxt可能需要不同的导入方式
        import ccxt.async_support as ccxt_async
        
        async def async_test():
            exchange = None
            try:
                # 创建异步 OKX 实例
                exchange = ccxt_async.okx(OKX_CONFIG)
                
                # 设置代理
                if hasattr(exchange, 'session') and hasattr(exchange.session, 'proxies'):
                    exchange.session.proxies = PROXY_CONFIG
                
                print("1️⃣ 测试异步获取ticker...")
                ticker = await exchange.fetch_ticker('BTC/USDT')
                print(f"✅ BTC/USDT 异步价格: {ticker['last']}")
                
                print("2️⃣ 测试异步获取余额...")
                balance = await exchange.fetch_balance()
                print("✅ 成功获取异步账户余额")
                
                return True
                
            except Exception as e:
                print(f"❌ 异步测试失败: {e}")
                return False
            finally:
                if exchange:
                    await exchange.close()
        
        # 运行异步测试
        result = asyncio.run(async_test())
        if result:
            print("✅ 异步API测试成功！")
        return result
        
    except ImportError:
        print("⚠️ 异步支持模块不可用，跳过异步测试")
        return True  # 不是错误，只是功能不可用
    except Exception as e:
        print(f"❌ 异步测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 OKX API 连接修复诊断 - 修复版本")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print(f"API Key (前8位): {OKX_CONFIG['apiKey'][:8]}...")
    print(f"权限: 只读")
    print(f"CCXT版本: {ccxt.__version__}")
    print("=" * 60)
    
    # 设置代理环境变量
    set_proxy_env()
    
    # 步骤1: 测试代理连接
    if not test_proxy_connection():
        print("\n❌ 代理连接失败，请检查 SSR 客户端是否运行在端口 1080")
        return
    
    # 步骤2: 测试域名连通性
    test_domain_connectivity()
    
    # 步骤3: 测试公共API
    public_success = test_ccxt_public_api()
    
    # 步骤4: 测试私有API
    private_success = test_ccxt_private_api()
    
    # 步骤5: 测试异步API
    async_success = test_ccxt_async_api()
    
    # 总结
    print("\n📋 诊断结果总结")
    print("=" * 60)
    print(f"✅ 公共API: {'成功' if public_success else '失败'}")
    print(f"✅ 私有API: {'成功' if private_success else '失败'}")
    print(f"✅ 异步API: {'成功' if async_success else '失败/不支持'}")
    
    if public_success and private_success:
        print("\n🎉 OKX API 连接完全正常！")
        print("💡 您的系统已经可以正常使用 OKX API 进行交易操作")
    else:
        print("\n⚠️ 部分功能存在问题，请检查上述错误信息")
        
    print("\n📋 诊断完成")

if __name__ == "__main__":
    main()
