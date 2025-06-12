#!/usr/bin/env python3
"""
快速诊断和修复脚本
"""
import requests
import json
import time

def main():
    print("🔧 交易所API快速诊断和修复")
    print("=" * 50)
    
    backend_url = "http://localhost:8000"
    
    # 1. 健康检查
    print("\n1. 🏥 服务器健康检查...")
    try:
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            print("   ✅ 后端服务器正常")
        else:
            print(f"   ❌ 后端服务器异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 无法连接后端服务器: {e}")
        return False
    
    # 2. 用户登录测试
    print("\n2. 🔐 测试用户登录...")
    
    # 使用修改后的密码123456
    login_data = {
        "username": "111",
        "password": "123456"
    }
    
    try:
        response = requests.post(f"{backend_url}/api/auth/login", data=login_data, timeout=10)
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("   ✅ 用户111登录成功 (密码: 123456)")
        else:
            print(f"   ❌ 登录失败 ({response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 登录请求失败: {e}")
        return False
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. 检查交易所账户
    print("\n3. 🏦 检查交易所账户...")
    try:
        response = requests.get(f"{backend_url}/api/exchanges/", headers=headers, timeout=10)
        if response.status_code == 200:
            accounts = response.json()
            okx_accounts = [acc for acc in accounts if acc["exchange_name"] == "okex"]
            print(f"   ✅ 找到 {len(accounts)} 个交易所账户")
            print(f"   📊 其中 {len(okx_accounts)} 个OKX账户")
            
            if okx_accounts:
                account = okx_accounts[0]
                account_id = account["id"]
                print(f"   🎯 使用OKX账户ID: {account_id}")
                
                # 4. 测试Mock交易所连接
                print("\n4. 🎭 测试Mock交易所功能...")
                
                # 测试ticker
                print("   📈 测试行情数据...")
                response = requests.get(
                    f"{backend_url}/api/exchanges/accounts/{account_id}/ticker/BTCUSDT", 
                    headers=headers, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    ticker = response.json()
                    price = ticker.get("last", "N/A")
                    print(f"   ✅ 行情数据获取成功! BTC/USDT: ${price}")
                    
                    # 测试余额
                    print("   💰 测试余额查询...")
                    response = requests.get(
                        f"{backend_url}/api/exchanges/accounts/{account_id}/balance", 
                        headers=headers, 
                        timeout=15
                    )
                    
                    if response.status_code == 200:
                        balance = response.json()
                        print("   ✅ 余额查询成功!")
                        
                        # 显示部分余额信息
                        if "USDT" in balance:
                            usdt_balance = balance["USDT"].get("total", 0)
                            print(f"   💵 USDT余额: {usdt_balance}")
                        
                        return True
                    else:
                        error_detail = response.json().get("detail", "Unknown error") if response.headers.get('content-type', '').startswith('application/json') else response.text
                        print(f"   ⚠️ 余额查询失败: {error_detail}")
                        return False
                        
                else:
                    error_detail = response.json().get("detail", "Unknown error") if response.headers.get('content-type', '').startswith('application/json') else response.text
                    print(f"   ❌ 行情数据获取失败: {error_detail}")
                    return False
            else:
                print("   ⚠️ 没有找到OKX账户，需要先创建")
                return False
        else:
            print(f"   ❌ 获取账户列表失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("开始快速诊断...")
    
    success = main()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 快速诊断完成 - 系统正常!")
        print("")
        print("📝 测试结果:")
        print("   ✅ 后端服务器运行正常")
        print("   ✅ 用户认证系统正常")
        print("   ✅ OKX Mock交易所正常")
        print("   ✅ 行情数据和余额查询正常")
        print("")
        print("🌐 现在可以正常使用前端界面:")
        print("   登录: http://localhost:3000/login")
        print("   用户名: 111")
        print("   密码: 123456")
    else:
        print("❌ 快速诊断发现问题!")
        print("")
        print("🔍 请检查:")
        print("   1. 后端服务器是否正在运行")
        print("   2. 用户认证是否正常")
        print("   3. 数据库连接是否正常")
        print("   4. trading_engine.py是否有语法错误")
