#!/usr/bin/env python3
"""
测试更新后的交易引擎
"""
import sys
sys.path.append('.')

from simple_real_trading_engine import real_exchange_manager

def test_updated_engine():
    print("🚀 测试更新后的交易引擎")
    
    # 测试添加OKX账户
    user_id = 1
    api_key = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    secret_key = "CD6A497EEB00AA2DC60B2B0974DD2485"
    passphrase = "vf5Y3UeUFiz6xfF!"
    
    print(f"\n1. 添加OKX账户 (用户ID: {user_id})")
    success = real_exchange_manager.add_okx_account(user_id, api_key, secret_key, passphrase)
    print(f"结果: {'成功' if success else '失败'}")
    
    if success:
        print("\n2. 测试OKX连接")
        connection_result = real_exchange_manager.test_okx_connection(user_id)
        print(f"连接测试结果: {connection_result}")
        
        print("\n3. 测试获取价格")
        ticker_result = real_exchange_manager.get_real_ticker(user_id, 'okx', 'BTC/USDT')
        print(f"价格结果: {ticker_result}")
        
        print("\n4. 测试获取余额")
        balance_result = real_exchange_manager.get_real_balance(user_id, 'okx')
        print(f"余额结果: {balance_result}")
    
    print("\n🎉 测试完成")

if __name__ == "__main__":
    test_updated_engine()
