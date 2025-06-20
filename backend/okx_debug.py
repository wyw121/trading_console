"""
OKX API 调试脚本 - 深度调试版本
专门解决 NoneType + str 错误
"""
import os
import sys
import ccxt
import traceback
import json
from datetime import datetime

# 设置代理环境变量
def set_proxy_env():
    os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
    os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
    os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'
    print("✅ 代理环境变量已设置")

def debug_ccxt_config():
    """调试 CCXT 配置"""
    print("\n🔍 调试 CCXT 配置...")
    
    # 基础配置测试
    basic_configs = [
        # 配置1: 最小配置
        {
            'name': '最小配置',
            'config': {}
        },
        # 配置2: 基本配置
        {
            'name': '基本配置',
            'config': {
                'sandbox': False,
                'enableRateLimit': True,
            }
        },
        # 配置3: 完整公共配置
        {
            'name': '完整公共配置',
            'config': {
                'sandbox': False,
                'enableRateLimit': True,
                'rateLimit': 100,
                'timeout': 30000,
                'verbose': False,
                'options': {
                    'defaultType': 'spot',
                }
            }
        },
        # 配置4: 带认证的配置
        {
            'name': '带认证配置',
            'config': {
                'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
                'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
                'passphrase': 'vf5Y3UeUFiz6xfF!',
                'sandbox': False,
                'enableRateLimit': True,
                'rateLimit': 100,
                'timeout': 30000,
                'verbose': False,
                'options': {
                    'defaultType': 'spot',
                }
            }
        }
    ]
    
    for test_config in basic_configs:
        print(f"\n📋 测试 {test_config['name']}:")
        try:
            exchange = ccxt.okx(test_config['config'])
            
            # 设置代理
            proxy_config = {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            }
            
            if hasattr(exchange, 'proxies'):
                exchange.proxies = proxy_config
            elif hasattr(exchange, 'session'):
                exchange.session.proxies = proxy_config
            
            print(f"   ✅ 交易所实例创建成功")
            print(f"   📊 实例信息:")
            print(f"      - ID: {exchange.id}")
            print(f"      - 名称: {exchange.name}")
            print(f"      - 版本: {getattr(exchange, 'version', 'Unknown')}")
            print(f"      - URLs: {getattr(exchange, 'urls', {}).get('api', 'Unknown')}")
            
            # 测试简单操作
            try:
                print("   🕐 测试获取服务器时间...")
                server_time = exchange.fetch_time()
                print(f"      ✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
            except Exception as e:
                print(f"      ❌ 获取服务器时间失败: {e}")
                print(f"      📋 错误详情: {traceback.format_exc()}")
                continue
            
            # 测试加载市场数据
            try:
                print("   📊 测试加载市场数据...")
                markets = exchange.load_markets()
                print(f"      ✅ 成功加载 {len(markets)} 个交易对")
                
                # 显示前几个交易对
                market_symbols = list(markets.keys())[:5]
                print(f"      📋 示例交易对: {market_symbols}")
                
            except Exception as e:
                print(f"      ❌ 加载市场数据失败: {e}")
                print(f"      📋 错误详情: {traceback.format_exc()}")
                continue
            
            # 如果有认证信息，测试账户信息
            if test_config['config'].get('apiKey'):
                try:
                    print("   🔐 测试账户信息...")
                    balance = exchange.fetch_balance()
                    print(f"      ✅ 成功获取账户信息")
                    
                    # 安全显示余额信息
                    total_balance = balance.get('total', {})
                    if total_balance:
                        currency_count = len([k for k, v in total_balance.items() if v and v > 0])
                        print(f"      📋 拥有余额的货币数量: {currency_count}")
                    
                except Exception as e:
                    print(f"      ❌ 获取账户信息失败: {e}")
                    print(f"      📋 错误详情: {traceback.format_exc()}")
                    
            print(f"   ✅ {test_config['name']} 测试成功!")
            
        except Exception as e:
            print(f"   ❌ {test_config['name']} 测试失败: {e}")
            print(f"   📋 错误详情: {traceback.format_exc()}")

def debug_ccxt_internals():
    """深度调试 CCXT 内部状态"""
    print("\n🔬 深度调试 CCXT 内部状态...")
    
    try:
        # 创建实例
        exchange = ccxt.okx({
            'sandbox': False,
            'enableRateLimit': True,
            'verbose': True  # 启用详细日志
        })
        
        print("📊 交易所实例属性:")
        
        # 检查关键属性
        key_attrs = ['id', 'name', 'version', 'rateLimit', 'timeout', 'urls', 'api', 'has', 'options']
        for attr in key_attrs:
            if hasattr(exchange, attr):
                value = getattr(exchange, attr)
                if isinstance(value, dict) and len(str(value)) > 200:
                    print(f"   {attr}: <复杂对象，长度: {len(str(value))}>")
                else:
                    print(f"   {attr}: {value}")
            else:
                print(f"   {attr}: <不存在>")
        
        # 检查代理设置
        print(f"\n🌐 代理设置:")
        if hasattr(exchange, 'proxies'):
            print(f"   proxies属性: {exchange.proxies}")
        if hasattr(exchange, 'session'):
            print(f"   session属性: {hasattr(exchange.session, 'proxies') if exchange.session else 'session为None'}")
        
        # 检查URLs配置
        print(f"\n🔗 URLs配置:")
        urls = getattr(exchange, 'urls', {})
        for key, value in urls.items():
            print(f"   {key}: {value}")
            
        # 检查API配置
        print(f"\n🔧 API配置:")
        api_config = getattr(exchange, 'api', {})
        for key, value in api_config.items():
            if isinstance(value, dict):
                print(f"   {key}: {list(value.keys())}")
            else:
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ 深度调试失败: {e}")
        print(f"📋 错误详情: {traceback.format_exc()}")

def test_direct_api_call():
    """直接测试API调用"""
    print("\n🌐 直接测试API调用...")
    
    import requests
    
    proxy_config = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    
    # 测试公共API
    try:
        print("1️⃣ 测试直接公共API调用...")
        url = "https://www.okx.com/api/v5/public/time"
        response = requests.get(url, proxies=proxy_config, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 公共API响应: {data}")
        else:
            print(f"   ❌ 公共API状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 直接公共API调用失败: {e}")
    
    # 测试获取交易对信息
    try:
        print("2️⃣ 测试获取交易对信息...")
        url = "https://www.okx.com/api/v5/public/instruments"
        params = {'instType': 'SPOT'}
        response = requests.get(url, params=params, proxies=proxy_config, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0':
                instruments = data.get('data', [])
                print(f"   ✅ 获取到 {len(instruments)} 个交易对")
                if instruments:
                    print(f"   📋 示例交易对: {instruments[0].get('instId', 'Unknown')}")
            else:
                print(f"   ❌ API返回错误: {data}")
        else:
            print(f"   ❌ 获取交易对状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 获取交易对失败: {e}")

def main():
    """主函数"""
    print("🚀 OKX API 深度调试")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print(f"CCXT版本: {ccxt.__version__}")
    print("=" * 60)
    
    # 设置代理
    set_proxy_env()
    
    # 直接API测试
    test_direct_api_call()
    
    # 深度调试
    debug_ccxt_internals()
    
    # 配置调试
    debug_ccxt_config()
    
    print("\n📋 深度调试完成")

if __name__ == "__main__":
    main()
