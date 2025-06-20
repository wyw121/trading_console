#!/usr/bin/env python3
"""
简化的OKX CCXT测试
"""
import ccxt
import os

# 设置代理
os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'

# API密钥
API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
PASSPHRASE = "vf5Y3UeUFiz6xfF!"

def test_ccxt_simple():
    """简化的CCXT测试"""
    print("🚀 测试CCXT连接OKX")
    
    try:
        # 创建交易所实例
        exchange = ccxt.okx({
            'apiKey': API_KEY,
            'secret': SECRET_KEY,
            'password': PASSPHRASE,
            'sandbox': False,
            'proxies': {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            },
            'enableRateLimit': True,
        })
        
        print("1. 测试获取市场信息...")
        markets = exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个市场")
        
        print("\n2. 测试获取价格信息...")
        ticker = exchange.fetch_ticker('BTC/USDT')
        print(f"✅ BTC/USDT 当前价格: ${ticker['last']}")
        
        print("\n3. 测试获取账户余额...")
        try:
            balance = exchange.fetch_balance()
            print("✅ 成功获取账户余额")
            
            # 显示非零余额
            total_balances = balance.get('total', {})
            non_zero = {k: v for k, v in total_balances.items() if v and v > 0}
            
            if non_zero:
                print("非零余额:")
                for currency, amount in non_zero.items():
                    print(f"  {currency}: {amount}")
            else:
                print("账户余额为空或全部为0")
                
        except Exception as e:
            print(f"⚠️ 获取余额失败: {e}")
            print("这可能是因为:")
            print("1. API密钥权限不足（需要'读取'权限）")
            print("2. IP地址未加入白名单")
            print("3. API密钥配置错误")
        
        print("\n🎉 基础连接测试完成")
        return True
        
    except Exception as e:
        print(f"❌ CCXT连接失败: {e}")
        return False

if __name__ == "__main__":
    test_ccxt_simple()
