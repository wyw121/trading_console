import requests
import json
import time
import sys

def main():
    print("=" * 60)
    print("🚀 Trading Console 端到端测试")
    print("测试流程: 注册 → 登录 → 用户资料 → 交易所配置 → 策略创建")
    print("=" * 60)
    
    backend_url = "http://localhost:8000"
    auth_token = None
    user_id = None
    exchange_account_id = None
    strategy_id = None
    
    # 生成唯一的测试用户
    timestamp = int(time.time())
    test_user = {
        "username": f"testuser_{timestamp}",
        "email": f"test_{timestamp}@example.com", 
        "password": "SecurePass123!"
    }
    
    print(f"📝 测试用户: {test_user['username']}")
    print()
    
    # 测试步骤计数
    step = 1
    
    try:
        # 步骤1: 检查后端健康状态
        print(f"步骤 {step}: 检查后端服务...")
        response = requests.get(f"{backend_url}/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ 后端服务正常: {health_data}")
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
        step += 1
          # 步骤2: 用户注册
        print(f"\n步骤 {step}: 用户注册...")
        print(f"   正在注册用户: {test_user['username']}")
        response = requests.post(
            f"{backend_url}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            register_data = response.json()
            auth_token = register_data.get("access_token")
            user_id = register_data.get("user_id")
            print(f"✅ 用户注册成功")
            print(f"   访问令牌: {auth_token[:20]}...")
            if user_id:
                print(f"   用户ID: {user_id}")
        else:
            print(f"❌ 用户注册失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
          # 步骤3: 用户登录
        print(f"\n步骤 {step}: 用户登录验证...")
        login_data = {
            "username": test_user["username"],
            "password": test_user["password"]
        }
        response = requests.post(
            f"{backend_url}/api/auth/login",
            data=login_data,  # OAuth2 expects form data
            timeout=10
        )
        
        if response.status_code == 200:
            login_response = response.json()
            auth_token = login_response.get("access_token")  # 更新token
            print(f"✅ 用户登录成功")
            print(f"   新访问令牌: {auth_token[:20]}...")
        else:
            print(f"❌ 用户登录失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
        
        # 步骤4: 获取用户资料
        print(f"\n步骤 {step}: 获取用户资料...")
        headers = {
            "Authorization": f"Bearer {auth_token}",
            "Content-Type": "application/json"
        }
        response = requests.get(
            f"{backend_url}/api/auth/me",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            user_id = user_data.get("id")
            print(f"✅ 用户资料获取成功")
            print(f"   用户ID: {user_data.get('id')}")
            print(f"   用户名: {user_data.get('username')}")
            print(f"   邮箱: {user_data.get('email')}")
            print(f"   注册时间: {user_data.get('created_at', 'N/A')}")
        else:
            print(f"❌ 获取用户资料失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
        
        # 步骤5: 添加交易所账户
        print(f"\n步骤 {step}: 添加交易所账户...")
        exchange_data = {
            "exchange_name": "binance",
            "api_key": "test_api_key_for_e2e_testing",
            "api_secret": "test_api_secret_for_e2e_testing",            "api_passphrase": None,
            "is_testnet": True
        }
        
        response = requests.post(
            f"{backend_url}/api/exchanges/",
            json=exchange_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            exchange_response = response.json()
            exchange_account_id = exchange_response.get("id")
            print(f"✅ 交易所账户添加成功")
            print(f"   账户ID: {exchange_account_id}")
            print(f"   交易所: {exchange_response.get('exchange_name')}")
            print(f"   测试网络: {exchange_response.get('is_testnet')}")
        else:
            print(f"❌ 添加交易所账户失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
          # 步骤6: 查看交易所账户列表
        print(f"\n步骤 {step}: 查看交易所账户列表...")
        response = requests.get(
            f"{backend_url}/api/exchanges/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            exchanges_list = response.json()
            print(f"✅ 获取交易所账户列表成功")
            print(f"   账户数量: {len(exchanges_list)}")
            for exchange in exchanges_list:
                print(f"   - {exchange.get('exchange_name')} (ID: {exchange.get('id')})")
        else:
            print(f"❌ 获取交易所账户列表失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
        
        # 步骤7: 创建交易策略
        print(f"\n步骤 {step}: 创建交易策略...")
        strategy_data = {
            "name": f"E2E测试策略_{timestamp}",
            "strategy_type": "5m_boll_ma60",
            "symbol": "BTC/USDT",
            "timeframe": "5m",
            "entry_amount": 100.0,
            "leverage": 1.0,
            "stop_loss_percent": 2.0,
            "take_profit_percent": 3.0,
            "bb_period": 20,
            "bb_deviation": 2.0,            "ma_period": 60,
            "exchange_account_id": exchange_account_id
        }
        
        response = requests.post(
            f"{backend_url}/api/strategies/",
            json=strategy_data,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            strategy_response = response.json()
            strategy_id = strategy_response.get("id")
            print(f"✅ 交易策略创建成功")
            print(f"   策略ID: {strategy_id}")
            print(f"   策略名称: {strategy_response.get('name')}")
            print(f"   策略类型: {strategy_response.get('strategy_type')}")
            print(f"   交易对: {strategy_response.get('symbol')}")
            print(f"   时间框架: {strategy_response.get('timeframe')}")
            print(f"   投入金额: {strategy_response.get('entry_amount')} USDT")
            print(f"   杠杆倍数: {strategy_response.get('leverage')}x")
        else:
            print(f"❌ 创建交易策略失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
        
        # 步骤8: 查看策略列表
        print(f"\n步骤 {step}: 查看策略列表...")
        response = requests.get(
            f"{backend_url}/strategies/",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            strategies_list = response.json()
            print(f"✅ 获取策略列表成功")
            print(f"   策略数量: {len(strategies_list)}")
            for strategy in strategies_list:
                status = "激活" if strategy.get('is_active') else "暂停"
                print(f"   - {strategy.get('name')} ({strategy.get('strategy_type')}) - {status}")
        else:
            print(f"❌ 获取策略列表失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
        
        # 步骤9: 查看策略详情
        print(f"\n步骤 {step}: 查看策略详情...")
        response = requests.get(
            f"{backend_url}/strategies/{strategy_id}",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            strategy_details = response.json()
            print(f"✅ 获取策略详情成功")
            print(f"   创建时间: {strategy_details.get('created_at')}")
            print(f"   更新时间: {strategy_details.get('updated_at')}")
            print(f"   关联交易所账户: {strategy_details.get('exchange_account_id')}")
            print(f"   当前状态: {'激活' if strategy_details.get('is_active') else '暂停'}")
        else:
            print(f"❌ 获取策略详情失败: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        step += 1
        
        print("\n" + "=" * 60)
        print("🧹 清理测试数据...")
        
        # 清理策略
        if strategy_id:
            try:
                response = requests.delete(
                    f"{backend_url}/strategies/{strategy_id}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ 测试策略已删除")
                else:
                    print(f"⚠️ 删除测试策略失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 删除测试策略时出错: {e}")
          # 清理交易所账户
        if exchange_account_id:
            try:
                response = requests.delete(
                    f"{backend_url}/api/exchanges/{exchange_account_id}",
                    headers=headers,
                    timeout=10
                )
                if response.status_code == 200:
                    print("✅ 测试交易所账户已删除")
                else:
                    print(f"⚠️ 删除测试交易所账户失败: {response.status_code}")
            except Exception as e:
                print(f"⚠️ 删除测试交易所账户时出错: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 端到端测试完成！")
        print("=" * 60)
        print(f"✅ 所有 {step-1} 个测试步骤全部通过")
        print(f"🚀 从用户注册到策略制定的完整流程验证成功！")
        print()
        print("📱 您可以继续测试:")
        print(f"   • 前端界面: http://localhost:5173")
        print(f"   • 后端API: http://localhost:8000")
        print(f"   • API文档: http://localhost:8000/docs")
        print()
        print("🌟 您的交易控制台已准备就绪！")
        
        return True
        
    except requests.exceptions.ConnectionError:
        print(f"❌ 无法连接到后端服务 {backend_url}")
        print("请确保后端服务正在运行:")
        print("  cd backend && python -m uvicorn main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print("❌ 请求超时，请检查服务状态")
        return False
    except Exception as e:
        print(f"❌ 测试执行异常: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
