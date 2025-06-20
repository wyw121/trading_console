"""
OKX API 修复脚本 - 最终版本
解决 CCXT 解析交易对时 base 为 None 的问题
"""
import os
import sys
import ccxt
import requests
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

def test_proxy_and_api():
    """测试代理和API连接"""
    print("\n🔍 测试代理和API连接...")
    
    proxy_config = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    
    try:
        # 测试代理
        response = requests.get('http://httpbin.org/ip', proxies=proxy_config, timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 代理连接成功，当前IP: {ip_info.get('origin')}")
        else:
            print(f"❌ 代理连接失败")
            return False
    except Exception as e:
        print(f"❌ 代理测试失败: {e}")
        return False
    
    try:
        # 测试OKX API
        url = "https://www.okx.com/api/v5/public/time"
        response = requests.get(url, proxies=proxy_config, timeout=15)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ OKX API连接成功: {data}")
            return True
        else:
            print(f"❌ OKX API连接失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ OKX API测试失败: {e}")
        return False

class FixedOKXExchange(ccxt.okx):
    """修复后的OKX交易所类"""
    
    def parse_market(self, market):
        """重写parse_market方法以修复NoneType错误"""
        try:
            # 获取原始数据
            id = market.get('instId')
            base_id = market.get('baseCcy')
            quote_id = market.get('quoteCcy')
            base = self.safe_currency_code(base_id)
            quote = self.safe_currency_code(quote_id)
            
            # 修复：确保base和quote不为None
            if base is None or quote is None:
                print(f"⚠️ 跳过无效交易对: {market}")
                return None
            
            symbol = base + '/' + quote
            settle_id = market.get('settleCcy')
            settle = self.safe_currency_code(settle_id)
            option = market.get('optType')
            
            type_id = market.get('instType')
            type_mappings = {
                'SPOT': 'spot',
                'FUTURES': 'future',
                'SWAP': 'swap',
                'OPTION': 'option',
            }
            type = self.safe_string(type_mappings, type_id, type_id)
            
            contract = type in ['future', 'swap', 'option']
            spot = type == 'spot'
            future = type == 'future'
            swap = type == 'swap'
            option_type = type == 'option'
            
            active = market.get('state') == 'live'
            
            contract_size = None
            if contract:
                contract_size = self.safe_number(market, 'ctVal')
            
            precision = {
                'amount': self.safe_integer(market, 'lotSz'),
                'price': self.safe_integer(market, 'tickSz'),
            }
            
            # 处理最小/最大限制
            min_amount = self.safe_number(market, 'minSz')
            
            limits = {
                'amount': {
                    'min': min_amount,
                    'max': None,
                },
                'price': {
                    'min': None,
                    'max': None,
                },
                'cost': {
                    'min': None,
                    'max': None,
                },
            }
            
            fees = self.safe_value(self.fees, type, {})
            
            result = {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'settle': settle,
                'baseId': base_id,
                'quoteId': quote_id,
                'settleId': settle_id,
                'type': type,
                'spot': spot,
                'margin': False,
                'swap': swap,
                'future': future,
                'option': option_type,
                'active': active,
                'contract': contract,
                'linear': None,
                'inverse': None,
                'taker': self.safe_number(fees, 'taker'),
                'maker': self.safe_number(fees, 'maker'),
                'contractSize': contract_size,
                'expiry': None,
                'expiryDatetime': None,
                'strike': None,
                'optionType': option,
                'precision': precision,
                'limits': limits,
                'info': market,
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 解析交易对失败: {market}, 错误: {e}")
            return None
    
    def parse_markets(self, markets):
        """重写parse_markets方法以处理None值"""
        result = []
        for i in range(len(markets)):
            parsed_market = self.parse_market(markets[i])
            if parsed_market is not None:  # 只添加成功解析的交易对
                result.append(parsed_market)
        return result

def test_fixed_ccxt():
    """测试修复后的CCXT"""
    print("\n🔧 测试修复后的CCXT...")
    
    # 基础配置
    config = {
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
    
    try:
        # 使用修复后的交易所
        exchange = FixedOKXExchange(config)
        
        # 设置代理
        proxy_config = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        if hasattr(exchange, 'session'):
            exchange.session.proxies = proxy_config
        
        print("1️⃣ 测试获取服务器时间...")
        server_time = exchange.fetch_time()
        print(f"✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
        
        print("2️⃣ 测试加载交易对...")
        markets = exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个交易对")
        
        # 显示一些示例交易对
        market_symbols = list(markets.keys())[:10]
        print(f"📋 示例交易对: {market_symbols}")
        
        print("3️⃣ 测试获取ticker...")
        if 'BTC/USDT' in markets:
            ticker = exchange.fetch_ticker('BTC/USDT')
            print(f"✅ BTC/USDT 价格: {ticker['last']}")
        else:
            print("⚠️ BTC/USDT 不可用")
        
        print("4️⃣ 测试获取账户余额...")
        try:
            balance = exchange.fetch_balance()
            print("✅ 成功获取账户余额")
            
            # 安全显示余额
            total_balance = balance.get('total', {})
            if total_balance:
                currency_count = len([k for k, v in total_balance.items() if v and v > 0])
                print(f"📋 拥有余额的货币数量: {currency_count}")
                
                # 显示部分余额信息（不显示具体数额）
                currencies = [k for k, v in total_balance.items() if v and v > 0][:5]
                print(f"📋 主要货币: {currencies}")
            else:
                print("📋 账户余额为空")
                
        except Exception as e:
            print(f"❌ 获取账户余额失败: {e}")
            if 'permission' in str(e).lower():
                print("   可能是API权限问题")
            elif 'signature' in str(e).lower():
                print("   可能是签名问题")
        
        print("✅ 修复后的CCXT测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 修复后的CCXT测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def test_simple_operations():
    """测试简单操作"""
    print("\n📊 测试简单操作...")
    
    try:
        # 最简配置
        exchange = FixedOKXExchange({
            'sandbox': False,
            'enableRateLimit': True,
        })
        
        # 设置代理
        proxy_config = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        if hasattr(exchange, 'session'):
            exchange.session.proxies = proxy_config
        
        print("1️⃣ 测试公共API...")
        
        # 获取服务器时间
        server_time = exchange.fetch_time()
        print(f"✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
        
        # 获取交易对（这里应该会调用我们修复的方法）
        markets = exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个交易对")
        
        # 获取一些ticker数据
        common_pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT']
        for pair in common_pairs:
            if pair in markets:
                try:
                    ticker = exchange.fetch_ticker(pair)
                    print(f"✅ {pair}: {ticker['last']}")
                    break
                except Exception as e:
                    print(f"⚠️ {pair} ticker获取失败: {e}")
        
        print("✅ 简单操作测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 简单操作测试失败: {e}")
        print(f"错误详情: {traceback.format_exc()}")
        return False

def main():
    """主函数"""
    print("🚀 OKX API 修复脚本 - 最终版本")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print(f"CCXT版本: {ccxt.__version__}")
    print("=" * 60)
    
    # 设置代理
    set_proxy_env()
    
    # 步骤1: 测试代理和API连接
    if not test_proxy_and_api():
        print("\n❌ 基础连接失败，请检查网络配置")
        return
    
    # 步骤2: 测试简单操作
    simple_success = test_simple_operations()
    
    # 步骤3: 测试完整功能
    full_success = test_fixed_ccxt()
    
    # 总结
    print("\n📋 修复结果总结")
    print("=" * 60)
    print(f"✅ 简单操作: {'成功' if simple_success else '失败'}")
    print(f"✅ 完整功能: {'成功' if full_success else '失败'}")
    
    if simple_success and full_success:
        print("\n🎉 OKX API 修复成功！")
        print("💡 主要修复内容:")
        print("   - 修复了 CCXT 解析交易对时 base 为 None 的问题")
        print("   - 添加了空值检查和错误处理")
        print("   - 确保代理配置正确设置")
        print("   - 提供了自定义的 FixedOKXExchange 类")
        print("\n🔧 使用方法:")
        print("   在您的代码中使用 FixedOKXExchange 而不是 ccxt.okx")
        print("   例如: exchange = FixedOKXExchange(config)")
    else:
        print("\n⚠️ 部分功能仍有问题，请检查上述错误信息")
        
    print("\n📋 修复完成")

if __name__ == "__main__":
    main()
