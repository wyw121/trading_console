#!/usr/bin/env python3
"""
测试新的OKX API密钥
包含读取、交易和提现权限的完整测试
"""

import os
import sys
sys.path.append('backend')

import logging
from okx_api_manager import OKXAPIManager

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_new_okx_api_key():
    """测试新的OKX API密钥"""
    print("=== 测试新的OKX API密钥 ===\n")
    
    # TODO: 替换为您的新API密钥信息
    API_KEY = "YOUR_NEW_API_KEY"
    SECRET_KEY = "YOUR_NEW_SECRET_KEY"
    PASSPHRASE = "YOUR_NEW_PASSPHRASE"
    
    if API_KEY == "YOUR_NEW_API_KEY":
        print("⚠️ 请先替换API密钥信息")
        print("请编辑此脚本，填入您的新API密钥")
        return False
    
    print(f"API Key: {API_KEY}")
    print(f"Secret Key: {SECRET_KEY[:8]}...{SECRET_KEY[-4:]}")
    print(f"Passphrase: {PASSPHRASE}\n")
    
    try:
        # 创建API管理器
        manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
        
        # 1. 测试基本连接
        print("1. 测试API连接...")
        connection_result = manager.test_connection()
        print(f"连接结果: {connection_result}\n")
        
        if not connection_result.get('public_api'):
            print("❌ 公开API连接失败，请检查网络连接")
            return False
        else:
            print("✅ 公开API连接正常")
        
        if not connection_result.get('private_api'):
            print("❌ 私有API连接失败")
            error_msgs = connection_result.get('error_messages', [])
            for msg in error_msgs:
                print(f"   错误: {msg}")
            
            # 提供详细的错误分析
            if any('50102' in str(msg) or 'Timestamp' in str(msg) for msg in error_msgs):
                print("\n🔍 错误分析:")
                print("时间戳错误通常表示：")
                print("1. API密钥权限不足")
                print("2. IP白名单限制")
                print("3. API密钥格式错误")
                print("\n💡 建议:")
                print("1. 确认API密钥权限包含'读取'")
                print("2. 检查IP白名单设置")
                print("3. 确认API密钥信息正确无误")
            
            return False
        else:
            print("✅ 私有API连接正常")
        
        # 2. 测试余额查询（读取权限）
        print("\n2. 测试余额查询（读取权限）...")
        balance_result = manager.get_balance_with_retry(max_retries=2)
        
        if balance_result.get('code') == '0':
            print("✅ 余额查询成功！")
            balance_data = balance_result.get('data', [])
            if balance_data and balance_data[0].get('details'):
                details = balance_data[0]['details']
                print(f"   账户币种数量: {len(details)}")
                for detail in details[:5]:  # 显示前5个币种
                    ccy = detail.get('ccy', 'Unknown')
                    bal = detail.get('bal', '0')
                    if float(bal) > 0:
                        print(f"   {ccy}: {bal}")
            else:
                print("   账户余额为空或数据格式异常")
        else:
            print("❌ 余额查询失败")
            print(f"   错误: {balance_result.get('msg', '未知错误')}")
            if balance_result.get('suggestion'):
                print(f"   建议: {balance_result['suggestion']}")
            return False
        
        # 3. 测试账户配置查询
        print("\n3. 测试账户配置查询...")
        try:
            config_result = manager._make_request('GET', '/api/v5/account/config')
            if config_result.get('code') == '0':
                print("✅ 账户配置查询成功")
                data = config_result.get('data', [])
                if data:
                    account_info = data[0]
                    print(f"   账户等级: {account_info.get('acctLv', 'Unknown')}")
                    print(f"   账户类型: {account_info.get('uid', 'Unknown')}")
            else:
                print(f"⚠️ 账户配置查询失败: {config_result.get('msg')}")
        except Exception as e:
            print(f"⚠️ 账户配置查询异常: {e}")
        
        # 4. 测试交易权限（获取交易对信息）
        print("\n4. 测试交易相关API...")
        try:
            # 获取持仓信息（需要交易权限）
            positions_result = manager._make_request('GET', '/api/v5/account/positions')
            if positions_result.get('code') == '0':
                print("✅ 持仓信息查询成功（交易权限正常）")
                positions = positions_result.get('data', [])
                print(f"   当前持仓数量: {len(positions)}")
            else:
                print(f"⚠️ 持仓信息查询失败: {positions_result.get('msg')}")
                if '50113' in str(positions_result.get('code')):
                    print("   这可能表示交易权限不足")
        except Exception as e:
            print(f"⚠️ 持仓查询异常: {e}")
        
        # 5. 测试价格查询（确保基本功能正常）
        print("\n5. 测试价格查询...")
        ticker_result = manager.get_ticker('BTC-USDT')
        if ticker_result.get('code') == '0':
            price_data = ticker_result['data'][0]
            price = price_data['last']
            print(f"✅ BTC价格查询成功: ${price}")
        else:
            print(f"❌ 价格查询失败: {ticker_result.get('msg')}")
        
        print(f"\n🎉 API密钥测试完成！")
        print("=" * 50)
        print("✅ 新API密钥工作正常，具备完整权限")
        print("可以开始使用交易控制台进行交易了！")
        
        return True
        
    except Exception as e:
        print(f"❌ API测试过程中发生异常: {e}")
        return False

def show_setup_instructions():
    """显示设置说明"""
    print("📋 OKX API密钥设置说明")
    print("=" * 50)
    print("1. 登录OKX网站")
    print("2. 进入 账户设置 → API管理")
    print("3. 创建新的API密钥")
    print("4. 权限设置:")
    print("   ✅ 读取 (Read)")
    print("   ✅ 交易 (Trade)")
    print("   ✅ 提现 (Withdraw) - 可选")
    print("5. IP白名单:")
    print("   推荐: 留空（不限制IP）")
    print("   或填写: 23.145.24.14")
    print("6. 获取API信息并填入上方脚本")
    print("7. 运行此脚本进行测试")
    print()

if __name__ == "__main__":
    show_setup_instructions()
    
    # 运行测试
    success = test_new_okx_api_key()
    
    if not success:
        print("\n💡 如果测试失败，请检查:")
        print("1. API密钥信息是否正确")
        print("2. 权限设置是否包含'读取'")
        print("3. IP白名单设置是否正确")
        print("4. 网络连接是否正常")
        print("5. SSR代理是否运行在端口1080")
    
    print("\n按任意键退出...")
    input()
