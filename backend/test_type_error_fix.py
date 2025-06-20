#!/usr/bin/env python3
"""测试修复后的 TypeError 问题"""

import requests
import json
import time

def test_fixed_ticker_api():
    """测试修复后的价格获取API"""
    base_url = "http://localhost:8000"
    
    # 1. 健康检查
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ 后端健康状态: {health_response.status_code}")
    except Exception as e:
        print(f"❌ 后端连接失败: {e}")
        return
    
    # 2. 用户登录
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    
    try:
        # 注册用户（如果不存在）
        requests.post(f"{base_url}/api/auth/register", json=login_data)
        
        # 登录
        login_response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        
        if login_response.status_code != 200:
            print(f"❌ 登录失败: {login_response.status_code}")
            return
            
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ 用户登录成功")
        
        # 3. 获取交易所账户列表
        accounts_response = requests.get(f"{base_url}/api/exchanges/", headers=headers)
        print(f"📋 交易所账户获取: {accounts_response.status_code}")
        
        if accounts_response.status_code == 200:
            accounts = accounts_response.json()
            print(f"📊 账户数量: {len(accounts)}")
            
            if accounts:
                # 4. 测试价格获取 - 关键测试点
                for account in accounts[:2]:  # 只测试前2个账户
                    account_id = account["id"]
                    print(f"\n🎯 测试账户 {account_id} ({account.get('exchange_name', 'unknown')})")
                    
                    # 测试BTC/USDT价格获取
                    ticker_response = requests.get(
                        f"{base_url}/api/exchanges/accounts/{account_id}/ticker/BTCUSDT", 
                        headers=headers,
                        timeout=30
                    )
                    
                    print(f"📈 价格获取状态码: {ticker_response.status_code}")
                    
                    if ticker_response.status_code == 400:
                        # 如果还是400，检查错误信息
                        try:
                            error_data = ticker_response.json()
                            error_detail = error_data.get('detail', 'Unknown error')
                            print(f"📛 错误详情: {error_detail}")
                            
                            # 检查是否还是TypeError
                            if "unsupported operand type(s) for +: 'NoneType' and 'str'" in error_detail:
                                print("❌ 仍然存在TypeError问题！")
                            else:
                                print("✅ TypeError已修复，现在是其他错误")
                                
                        except:
                            print("⚠️ 无法解析错误响应")
                            
                    elif ticker_response.status_code == 200:
                        print("🎉 价格获取成功！")
                        
                    elif ticker_response.status_code == 404:
                        print("⚠️ 账户未找到（正常）")
                        
                    elif ticker_response.status_code == 401:
                        print("⚠️ 需要认证（正常）")
                        
                    else:
                        print(f"ℹ️ 其他状态码: {ticker_response.status_code}")
                        
            else:
                print("⚠️ 没有交易所账户，无法测试价格获取")
                
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")

if __name__ == "__main__":
    print("🧪 开始测试修复后的TypeError问题...")
    test_fixed_ticker_api()
    print("🔚 测试完成")
