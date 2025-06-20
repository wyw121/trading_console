#!/usr/bin/env python3
"""
测试修复后的OKX API认证和余额查询
"""

import os
import sys
sys.path.append('backend')

import logging
from okx_api_manager import OKXAPIManager
from simple_real_trading_engine import SimpleRealExchangeManager

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_okx_fixed_api():
    """测试修复后的OKX API"""
    print("=== 测试修复后的OKX API ===\n")
    
    # 使用实际的API凭据
    API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    print(f"API Key: {API_KEY}")
    print(f"Secret Key: {SECRET_KEY}")
    print(f"Passphrase: {PASSPHRASE}\n")
    
    # 1. 直接测试OKX API管理器
    print("1. 测试OKX API管理器...")
    try:
        manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
        
        # 测试连接
        connection_result = manager.test_connection()
        print(f"连接测试结果: {connection_result}")
        
        # 测试余额查询（带详细错误信息）
        print("\n2. 测试余额查询（带重试和详细错误）...")
        balance_result = manager.get_balance_with_retry(max_retries=2)
        print(f"余额查询结果: {balance_result}")
        
        # 检查错误信息和建议
        if not balance_result.get('code') == '0':
            print(f"\n错误代码: {balance_result.get('code')}")
            print(f"错误信息: {balance_result.get('msg')}")
            if balance_result.get('suggestion'):
                print(f"建议: {balance_result.get('suggestion')}")
        
    except Exception as e:
        print(f"直接API测试失败: {e}")
    
    # 2. 测试通过交易引擎
    print("\n" + "="*50)
    print("3. 测试通过SimpleRealExchangeManager...")
    try:
        exchange_manager = SimpleRealExchangeManager()
        
        # 添加OKX账户
        user_id = 1
        add_result = exchange_manager.add_okx_account(user_id, API_KEY, SECRET_KEY, PASSPHRASE)
        print(f"添加OKX账户结果: {add_result}")
        
        if add_result:
            # 测试连接
            print("\n4. 测试OKX连接...")
            conn_result = exchange_manager.test_okx_connection(user_id)
            print(f"连接测试: {conn_result}")
            
            # 测试余额查询
            print("\n5. 测试余额查询...")
            balance_result = exchange_manager.get_real_balance(user_id, 'okx')
            print(f"余额查询结果: {balance_result}")
            
            # 如果有错误，显示详细信息
            if not balance_result.get('success'):
                print(f"\n错误详情:")
                print(f"- 消息: {balance_result.get('message')}")
                if balance_result.get('data'):
                    data = balance_result['data']
                    if data.get('error_code'):
                        print(f"- 错误代码: {data['error_code']}")
                    if data.get('suggestion'):
                        print(f"- 建议: {data['suggestion']}")
        
    except Exception as e:
        print(f"交易引擎测试失败: {e}")

def test_connection_with_troubleshooting():
    """测试连接并提供故障排除指导"""
    print("\n" + "="*50)
    print("6. 连接故障排除指导")
    print("="*50)
    
    try:
        API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
        SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
        PASSPHRASE = "vf5Y3UeUFiz6xfF!"
        
        manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
        
        # 调试API凭据
        debug_result = manager.debug_api_credentials()
        print(f"API凭据调试: {debug_result}")
        
        # 测试公开API
        print("\n测试公开API（无需认证）...")
        time_result = manager.get_server_time()
        if time_result.get('code') == '0':
            print("✅ 公开API正常 - 网络连接和代理配置正确")
        else:
            print("❌ 公开API失败 - 网络连接或代理问题")
            
        # 测试价格查询
        ticker_result = manager.get_ticker('BTC-USDT')
        if ticker_result.get('code') == '0':
            price = ticker_result['data'][0]['last']
            print(f"✅ 价格查询正常 - BTC价格: ${price}")
        else:
            print("❌ 价格查询失败")
        
        # 最终余额测试
        print("\n最终余额查询测试...")
        balance_result = manager.get_balance_with_retry(max_retries=1)
        
        if balance_result.get('code') == '0':
            print("✅ 余额查询成功！问题已解决。")
        else:
            print("❌ 余额查询仍然失败")
            print("\n可能的解决方案：")
            print("1. 检查OKX账户API密钥权限：登录OKX -> API管理 -> 检查权限设置")
            print("2. 检查IP白名单：如果设置了IP白名单，请添加当前IP或清空白名单")
            print("3. 重新生成API密钥：删除现有密钥，重新创建一个新的")
            print("4. 检查账户状态：确认OKX账户正常，没有被限制")
            print("5. 联系OKX客服：如果以上方法都无效")
            
    except Exception as e:
        print(f"故障排除测试失败: {e}")

if __name__ == "__main__":
    print("OKX API 修复验证测试")
    print("=" * 50)
    
    # 运行所有测试
    test_okx_fixed_api()
    test_connection_with_troubleshooting()
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("如果余额查询仍然失败，这很可能是OKX API密钥权限或IP限制问题，")
    print("而不是代码问题。请按照上述建议检查OKX账户设置。")
