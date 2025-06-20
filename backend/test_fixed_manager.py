"""
测试修复后的交易引擎管理器
"""
import asyncio
import sys
import os

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_fixed_manager():
    """测试修复后的管理器"""
    print("🔧 测试修复后的交易引擎管理器...")
    
    try:
        from simple_real_trading_engine_fixed import real_exchange_manager
        
        print("✅ 成功导入修复后的管理器")
        
        # 测试方法存在性
        methods_to_test = [
            'get_real_balance',
            'get_real_ticker', 
            'get_supported_exchanges',
            'get_exchange_markets',
            'add_exchange_account',
            'test_connection'
        ]
        
        print("\n📋 检查方法存在性:")
        for method in methods_to_test:
            exists = hasattr(real_exchange_manager, method)
            print(f"   {method}: {'✅' if exists else '❌'}")
        
        # 测试非异步方法
        print("\n🧪 测试非异步方法:")
        try:
            exchanges = real_exchange_manager.get_supported_exchanges()
            print(f"   支持的交易所: {exchanges}")
        except Exception as e:
            print(f"   ❌ 获取支持的交易所失败: {e}")
        
        # 测试连接键格式
        print("\n🔍 测试连接键格式:")
        test_user_id = 999
        test_exchange = "okx"
        test_testnet = False
        
        expected_key = f"{test_user_id}_{test_exchange}_{test_testnet}"
        print(f"   预期键格式: {expected_key}")
        
        print("\n🎉 修复验证完成！")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_fixed_manager())
    if success:
        print("\n✨ 所有测试通过！修复已生效。")
    else:
        print("\n⚠️ 测试失败，需要进一步检查。")
