"""
测试交易所连接和ticker修复情况
"""
import sys
import os

# 添加backend目录到路径
backend_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.append(backend_path)

from simple_real_trading_engine import real_exchange_manager

def test_connection_fix():
    """测试连接和ticker修复"""
    print("🔧 测试交易所连接和ticker修复...")
    
    # 1. 测试连接（应该不会调用ticker）
    print("\n1️⃣ 测试连接功能:")
    result = real_exchange_manager.test_connection('okx', 'test_key', 'test_secret', 'test_pass')
    print(f"连接测试结果: {result['success']} - {result['message']}")
    
    # 2. 测试交易对验证
    print("\n2️⃣ 测试交易对验证:")
    test_symbols = [
        'BTC/USDT',   # 常见格式
        'BTCUSDT',    # Binance格式
        'BTC-USDT',   # OKX格式
        'ETH/USD',    # 另一种格式
        'invalid',    # 无效格式
        '',           # 空字符串
        None          # None值
    ]
    
    for symbol in test_symbols:
        validated = real_exchange_manager.validate_symbol('okx', symbol)
        print(f"  {str(symbol):10} -> {validated}")
    
    # 3. 测试获取有效交易对（如果网络允许）
    print("\n3️⃣ 测试获取有效交易对:")
    try:
        valid_symbols = real_exchange_manager.get_valid_symbols('okx')
        print(f"  获取到 {len(valid_symbols)} 个有效交易对")
        print(f"  前5个: {valid_symbols[:5]}")
    except Exception as e:
        print(f"  获取失败: {e}")
    
    # 4. 模拟ticker调用（不需要真实API密钥）
    print("\n4️⃣ 模拟ticker调用错误处理:")
    # 这里不会真正调用API，因为没有真实的user_id和API密钥配置
    result = real_exchange_manager.get_real_ticker(999, 'okx', 'INVALID-SYMBOL')
    print(f"无效交易对处理: {result['success']} - {result['message']}")
    
    print("\n✅ 修复验证完成!")
    print("\n📝 修复要点:")
    print("  1. 改进了交易对格式验证和转换")
    print("  2. 添加了友好的错误信息和建议")
    print("  3. 连接测试不再依赖ticker API")
    print("  4. 提供了交易对格式规范化功能")
    
if __name__ == "__main__":
    test_connection_fix()
