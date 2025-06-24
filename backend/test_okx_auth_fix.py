#!/usr/bin/env python3
"""
OKX权限验证测试脚本
"""
import asyncio
import sys
import os
import argparse

# 添加路径
sys.path.append('.')

from trading_engine import exchange_manager

async def test_okx_auth(api_key=None, secret_key=None, passphrase=None):
    """测试OKX认证"""
    print("🔧 OKX API 权限验证测试")
    print("=" * 50)
    
    # 使用传入的凭据或默认测试凭据
    test_credentials = {
        'exchange': 'okx',
        'api_key': api_key or 'test_api_key',
        'secret_key': secret_key or 'test_secret_key', 
        'passphrase': passphrase or 'test_passphrase',
        'is_testnet': False
    }
    
    print("📋 测试参数:")
    print(f"   交易所: {test_credentials['exchange']}")
    print(f"   测试网: {test_credentials['is_testnet']}")
    print(f"   API Key: {test_credentials['api_key'][:8]}...")
    print("")
    
    try:
        print("🔍 开始连接测试...")
        result = await exchange_manager.test_connection(
            exchange=test_credentials['exchange'],
            api_key=test_credentials['api_key'],
            secret_key=test_credentials['secret_key'],
            passphrase=test_credentials['passphrase'],
            is_testnet=test_credentials['is_testnet']
        )
        
        print("✅ 连接测试完成!")
        print(f"状态: {result['status']}")
        print(f"消息: {result['message']}")
        print(f"交易所: {result['exchange']}")
        print(f"余额预览: {result['balance_preview']}")
        
    except Exception as e:
        print(f"❌ 连接测试失败: {str(e)}")
        
        # 提供诊断建议
        print("\n🔧 可能的解决方案:")
        error_str = str(e).lower()
        
        if "api key" in error_str or "无效" in error_str:
            print("1. 检查API Key是否正确复制")
            print("2. 确认API Key没有过期")
        
        if "签名" in error_str or "signature" in error_str:
            print("1. 检查Secret Key是否正确")
            print("2. 检查Passphrase是否正确")
            print("3. 确认没有多余的空格")
        
        if "权限" in error_str or "permission" in error_str:
            print("1. 登录OKX账户")
            print("2. 在API管理中检查权限设置")
            print("3. 确保勾选了'读取'权限")
        
        if "ip" in error_str or "白名单" in error_str:
            print("1. 检查IP白名单设置")
            print("2. 添加当前IP到白名单")
            print("3. 或者设置为'不限制IP'")
        
        if "时间" in error_str or "timestamp" in error_str:
            print("1. 检查系统时间是否正确")
            print("2. 同步系统时间")
            print("3. 检查时区设置")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='测试OKX API权限和余额功能')
    parser.add_argument('--api-key', type=str, help='OKX API Key')
    parser.add_argument('--secret-key', type=str, help='OKX Secret Key')
    parser.add_argument('--passphrase', type=str, help='OKX Passphrase')
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("💡 注意: 请使用 --api-key, --secret-key, --passphrase 参数传入真实凭据")
        print("🔐 测试凭据应该有读取权限且IP白名单配置正确")
        print("")
        print("使用示例:")
        print("python test_okx_auth_fix.py --api-key YOUR_KEY --secret-key YOUR_SECRET --passphrase YOUR_PASSPHRASE")
        return
    
    # 运行异步测试
    asyncio.run(test_okx_auth(args.api_key, args.secret_key, args.passphrase))

if __name__ == "__main__":
    main()
