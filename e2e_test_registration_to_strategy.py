# -*- coding: utf-8 -*-
"""
Trading Console E2E Test: Complete flow from user registration to strategy creation
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime
import sys
import os

class TradingConsoleE2ETest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:5173"
        self.auth_token = None
        self.user_id = None
        self.exchange_account_id = None
        self.strategy_id = None
        self.test_user = {
            "username": f"e2e_user_{int(time.time())}",
            "email": f"e2e_{int(time.time())}@example.com",
            "password": "SecurePassword123!"
        }
        self.results = []
        
    def log_step(self, step_name, success, details=""):
        """记录测试步骤结果"""
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{status} {step_name}")
        if details:
            print(f"   {details}")
        self.results.append((step_name, success, details))
        
    async def step_1_check_backend_health(self):
        """步骤1：检查后端服务健康状态"""
        print("\n🔍 步骤1：检查后端服务状态...")
          try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.backend_url}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        self.log_step("后端健康检查", True, f"服务状态: {data.get('status', '未知')}")
                        return True
                    else:
                        self.log_step("后端健康检查", False, f"HTTP状态码: {response.status}")
                        return False
        except Exception as e:
            self.log_step("后端健康检查", False, f"连接错误: {str(e)}")
            return False
    
    async def step_2_user_registration(self):
        """步骤2：用户注册"""
        print("\n🔍 步骤2：测试用户注册...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/auth/register",
                    json=self.test_user,
                    headers={"Content-Type": "application/json"}
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data.get("access_token")
                        self.user_id = data.get("user_id")
                        self.log_step("用户注册", True, f"用户: {self.test_user['username']}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("用户注册", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("用户注册", False, f"请求异常: {str(e)}")
            return False
    
    async def step_3_user_login(self):
        """步骤3：用户登录验证"""
        print("\n🔍 步骤3：测试用户登录...")
        
        try:
            async with aiohttp.ClientSession() as session:
                # 准备登录数据
                form_data = aiohttp.FormData()
                form_data.add_field('username', self.test_user['username'])
                form_data.add_field('password', self.test_user['password'])
                
                async with session.post(
                    f"{self.backend_url}/api/auth/login",
                    data=form_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.auth_token = data.get("access_token")
                        self.log_step("用户登录", True, "登录成功，获取到新的token")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("用户登录", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("用户登录", False, f"请求异常: {str(e)}")
            return False
    
    async def step_4_get_user_profile(self):
        """步骤4：获取用户资料"""
        print("\n🔍 步骤4：获取用户资料...")
        
        if not self.auth_token:
            self.log_step("获取用户资料", False, "缺少认证token")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/auth/me",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.user_id = data.get("id")
                        self.log_step("获取用户资料", True, f"用户ID: {self.user_id}, 邮箱: {data.get('email')}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("获取用户资料", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("获取用户资料", False, f"请求异常: {str(e)}")
            return False
    
    async def step_5_add_exchange_account(self):
        """步骤5：添加交易所账户"""
        print("\n🔍 步骤5：添加交易所账户...")
        
        if not self.auth_token:
            self.log_step("添加交易所账户", False, "缺少认证token")
            return False
        
        try:
            # 使用测试API密钥
            exchange_data = {
                "exchange_name": "binance",
                "api_key": "test_api_key_for_e2e_testing",
                "api_secret": "test_api_secret_for_e2e_testing",
                "api_passphrase": None,
                "is_testnet": True
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/exchanges/",
                    json=exchange_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.exchange_account_id = data.get("id")
                        self.log_step("添加交易所账户", True, f"账户ID: {self.exchange_account_id}, 交易所: {data.get('exchange_name')}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("添加交易所账户", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("添加交易所账户", False, f"请求异常: {str(e)}")
            return False
    
    async def step_6_list_exchange_accounts(self):
        """步骤6：查看交易所账户列表"""
        print("\n🔍 步骤6：查看交易所账户列表...")
        
        if not self.auth_token:
            self.log_step("查看交易所账户列表", False, "缺少认证token")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/exchanges/",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        account_count = len(data)
                        self.log_step("查看交易所账户列表", True, f"找到 {account_count} 个交易所账户")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("查看交易所账户列表", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("查看交易所账户列表", False, f"请求异常: {str(e)}")
            return False
    
    async def step_7_create_strategy(self):
        """步骤7：创建交易策略"""
        print("\n🔍 步骤7：创建交易策略...")
        
        if not self.auth_token or not self.exchange_account_id:
            self.log_step("创建交易策略", False, "缺少认证token或交易所账户ID")
            return False
        
        try:
            strategy_data = {
                "name": f"E2E测试策略_{int(time.time())}",
                "strategy_type": "5m_boll_ma60",
                "symbol": "BTC/USDT",
                "timeframe": "5m",
                "entry_amount": 100.0,
                "leverage": 1.0,
                "stop_loss_percent": 2.0,
                "take_profit_percent": 3.0,
                "bb_period": 20,
                "bb_deviation": 2.0,
                "ma_period": 60,
                "exchange_account_id": self.exchange_account_id
            }
            
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/strategies/",
                    json=strategy_data,
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        self.strategy_id = data.get("id")
                        strategy_name = data.get("name")
                        self.log_step("创建交易策略", True, f"策略ID: {self.strategy_id}, 名称: {strategy_name}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("创建交易策略", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("创建交易策略", False, f"请求异常: {str(e)}")
            return False
    
    async def step_8_list_strategies(self):
        """步骤8：查看策略列表"""
        print("\n🔍 步骤8：查看策略列表...")
        
        if not self.auth_token:
            self.log_step("查看策略列表", False, "缺少认证token")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/strategies/",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        strategy_count = len(data)
                        self.log_step("查看策略列表", True, f"找到 {strategy_count} 个交易策略")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("查看策略列表", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("查看策略列表", False, f"请求异常: {str(e)}")
            return False
    
    async def step_9_get_strategy_details(self):
        """步骤9：查看策略详情"""
        print("\n🔍 步骤9：查看策略详情...")
        
        if not self.auth_token or not self.strategy_id:
            self.log_step("查看策略详情", False, "缺少认证token或策略ID")
            return False
        
        try:
            headers = {
                "Authorization": f"Bearer {self.auth_token}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/strategies/{self.strategy_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        is_active = data.get("is_active", False)
                        symbol = data.get("symbol", "未知")
                        self.log_step("查看策略详情", True, f"策略状态: {'激活' if is_active else '暂停'}, 交易对: {symbol}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("查看策略详情", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("查看策略详情", False, f"请求异常: {str(e)}")
            return False
    
    async def step_10_check_frontend_accessibility(self):
        """步骤10：检查前端可访问性"""
        print("\n🔍 步骤10：检查前端服务...")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.frontend_url) as response:
                    if response.status == 200:
                        self.log_step("前端服务检查", True, f"前端应用正常运行在 {self.frontend_url}")
                        return True
                    else:
                        self.log_step("前端服务检查", False, f"HTTP状态码: {response.status}")
                        return False
        except Exception as e:
            self.log_step("前端服务检查", False, f"连接错误: {str(e)} (前端可能未启动)")
            return False
    
    async def cleanup_test_data(self):
        """清理测试数据"""
        print("\n🧹 清理测试数据...")
        
        if not self.auth_token:
            print("   ⚠️ 无法清理：缺少认证token")
            return
        
        headers = {
            "Authorization": f"Bearer {self.auth_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            # 删除测试策略
            if self.strategy_id:
                try:
                    async with session.delete(
                        f"{self.backend_url}/strategies/{self.strategy_id}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            print("   ✅ 测试策略已删除")
                        else:
                            print(f"   ⚠️ 删除测试策略失败 (状态码: {response.status})")
                except Exception as e:
                    print(f"   ⚠️ 删除测试策略时出错: {e}")
            
            # 删除测试交易所账户
            if self.exchange_account_id:
                try:
                    async with session.delete(
                        f"{self.backend_url}/exchanges/{self.exchange_account_id}",
                        headers=headers
                    ) as response:
                        if response.status == 200:
                            print("   ✅ 测试交易所账户已删除")
                        else:
                            print(f"   ⚠️ 删除测试交易所账户失败 (状态码: {response.status})")
                except Exception as e:
                    print(f"   ⚠️ 删除测试交易所账户时出错: {e}")
    
    async def run_complete_e2e_test(self):
        """运行完整的端到端测试"""
        print("🚀 Trading Console 端到端测试")
        print("测试流程：用户注册 → 登录 → 配置交易所 → 创建策略")
        print("=" * 80)
        
        start_time = datetime.now()
        
        # 定义测试步骤
        test_steps = [
            ("检查后端服务", self.step_1_check_backend_health),
            ("用户注册", self.step_2_user_registration),
            ("用户登录", self.step_3_user_login),
            ("获取用户资料", self.step_4_get_user_profile),
            ("添加交易所账户", self.step_5_add_exchange_account),
            ("查看交易所账户列表", self.step_6_list_exchange_accounts),
            ("创建交易策略", self.step_7_create_strategy),
            ("查看策略列表", self.step_8_list_strategies),
            ("查看策略详情", self.step_9_get_strategy_details),
            ("检查前端服务", self.step_10_check_frontend_accessibility),
        ]
        
        # 执行测试步骤
        for step_name, step_func in test_steps:
            try:
                success = await step_func()
                if not success:
                    print(f"\n❌ 测试在步骤 '{step_name}' 失败，停止执行")
                    break
            except Exception as e:
                print(f"\n💥 步骤 '{step_name}' 出现异常: {e}")
                self.log_step(step_name, False, f"异常: {str(e)}")
                break
        
        # 清理测试数据
        await self.cleanup_test_data()
        
        # 生成测试报告
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "=" * 80)
        print("📊 端到端测试结果汇总")
        print("=" * 80)
        
        passed = 0
        total = 0
        
        for step_name, success, details in self.results:
            total += 1
            if success:
                passed += 1
                print(f"✅ {step_name}")
            else:
                print(f"❌ {step_name} - {details}")
        
        success_rate = (passed / total * 100) if total > 0 else 0
        
        print("=" * 80)
        print(f"📈 测试结果: {passed}/{total} 步骤通过 ({success_rate:.1f}%)")
        print(f"⏱️ 测试耗时: {duration:.2f} 秒")
        print(f"👤 测试用户: {self.test_user['username']}")
        
        if passed == total:
            print("\n🎉 恭喜！从用户注册到策略制定的完整流程测试成功！")
            print("✨ 您的交易控制台已经准备就绪，可以正常使用")
            print(f"\n🌐 访问地址:")
            print(f"   • 前端界面: {self.frontend_url}")
            print(f"   • 后端API: {self.backend_url}")
            print(f"   • API文档: {self.backend_url}/docs")
        else:
            print("\n⚠️ 部分测试失败，请检查相关服务和配置")
            print("💡 建议检查:")
            print("   1. 后端服务是否正常运行")
            print("   2. 数据库连接是否正常")
            print("   3. 前端服务是否启动")
            print("   4. API路由是否正确配置")
        
        return passed == total

async def main():
    """主测试函数"""
    try:
        tester = TradingConsoleE2ETest()
        success = await tester.run_complete_e2e_test()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")
        return 1
    except Exception as e:
        print(f"\n\n💥 测试执行异常: {e}")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"启动测试失败: {e}")
        sys.exit(1)
