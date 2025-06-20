"""
测试OKX API的有效交易对格式
"""
import requests
import json

def test_okx_symbols():
    """测试OKX支持的交易对格式"""
    try:
        print("🔍 测试OKX交易对格式...")
        
        # 获取OKX支持的交易对列表
        response = requests.get('https://www.okx.com/api/v5/public/instruments?instType=SPOT')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                instruments = data['data']
                print(f"✅ 获取到 {len(instruments)} 个现货交易对")
                
                # 显示前10个交易对格式
                print("\n📋 前10个交易对格式示例:")
                for i, instrument in enumerate(instruments[:10]):
                    inst_id = instrument.get('instId', '')
                    base_ccy = instrument.get('baseCcy', '')
                    quote_ccy = instrument.get('quoteCcy', '')
                    print(f"  {i+1}. {inst_id} ({base_ccy}/{quote_ccy})")
                
                # 检查常见交易对
                common_pairs = ['BTC-USDT', 'ETH-USDT', 'BTC-USD', 'ETH-USD']
                print(f"\n🔍 检查常见交易对:")
                valid_pairs = []
                for pair in common_pairs:
                    found = any(inst['instId'] == pair for inst in instruments)
                    status = "✅" if found else "❌"
                    print(f"  {status} {pair}")
                    if found:
                        valid_pairs.append(pair)
                
                print(f"\n✅ 建议使用的默认交易对: {valid_pairs[0] if valid_pairs else 'BTC-USDT'}")
                return valid_pairs[0] if valid_pairs else 'BTC-USDT'
                
        else:
            print(f"❌ 获取交易对列表失败: HTTP {response.status_code}")
            return 'BTC-USDT'
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return 'BTC-USDT'

def test_specific_ticker(symbol='BTC-USDT'):
    """测试特定交易对的ticker"""
    try:
        print(f"\n🎯 测试交易对: {symbol}")
        response = requests.get(f'https://www.okx.com/api/v5/market/ticker?instId={symbol}')
        
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == '0' and data.get('data'):
                ticker = data['data'][0]
                print(f"✅ {symbol} 价格: {ticker.get('last', 'N/A')}")
                return True
            else:
                print(f"❌ {symbol} API错误: {data.get('msg', '未知错误')}")
                return False
        else:
            print(f"❌ {symbol} HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 测试 {symbol} 失败: {e}")
        return False

if __name__ == "__main__":
    # 测试交易对格式
    valid_symbol = test_okx_symbols()
    
    # 测试具体的ticker
    test_symbols = ['BTC-USDT', 'ETH-USDT', 'BTC-USD', valid_symbol]
    
    print(f"\n🧪 测试ticker API:")
    for symbol in set(test_symbols):  # 去重
        test_specific_ticker(symbol)
    
    print(f"\n💡 解决方案:")
    print(f"  1. 使用 'BTC-USDT' 作为默认交易对")
    print(f"  2. 确保交易对格式为 'BASE-QUOTE' (例如: BTC-USDT)")
    print(f"  3. 在调用ticker API前验证交易对格式")
    print(f"  4. 提供更友好的错误信息给用户")
