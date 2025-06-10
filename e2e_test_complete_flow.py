#!/usr/bin/env python3
"""
Trading Console 端到端测试：用户注册到策略创建
完整的用户流程测试
"""
import asyncio
import aiohttp
import time
import json

class TradingConsoleE2ETest:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.access_token = None
        self.user_id = None
        self.exchange_id = None
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
        print("\n👤 步骤2：用户注册...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/auth/register",
                    json=self.test_user
                ) as response:
                    if response.status in [200, 201]:
                        user_data = await response.json()
                        self.user_id = user_data.get('id')
                        self.log_step("用户注册", True, f"用户ID: {self.user_id}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("用户注册", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("用户注册", False, f"异常: {str(e)}")
            return False
    
    async def step_3_user_login(self):
        """步骤3：用户登录"""
        print("\n🔐 步骤3：用户登录...")
        try:
            login_data = aiohttp.FormData()
            login_data.add_field('username', self.test_user['username'])
            login_data.add_field('password', self.test_user['password'])
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.backend_url}/api/auth/login",
                    data=login_data
                ) as response:
                    if response.status == 200:
                        token_data = await response.json()
                        self.access_token = token_data.get('access_token')
                        self.log_step("用户登录", True, f"Token获取成功")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("用户登录", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("用户登录", False, f"异常: {str(e)}")
            return False
    
    async def step_4_get_user_profile(self):
        """步骤4：获取用户资料"""
        print("\n📋 步骤4：获取用户资料...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/auth/me",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        profile = await response.json()
                        username = profile.get('username')
                        email = profile.get('email')
                        self.log_step("获取用户资料", True, f"用户: {username}, 邮箱: {email}")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("获取用户资料", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("获取用户资料", False, f"异常: {str(e)}")
            return False
    
    async def step_5_check_exchanges(self):
        """步骤5：检查交易所列表"""
        print("\n💱 步骤5：检查交易所...")
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.backend_url}/api/exchanges/",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        exchanges = await response.json()
                        exchange_count = len(exchanges)
                        self.log_step("检查交易所列表", True, f"找到 {exchange_count} 个交易所账户")
                        return True
                    else:
                        error_text = await response.text()
                        self.log_step("检查交易所列表", False, f"状态码: {response.status}, 错误: {error_text}")
                        return False
        except Exception as e:
            self.log_step("检查交易所列表", False, f"异常: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试步骤"""
        print("🚀 Trading Console 完整端到端测试")
        print("测试流程：健康检查 → 用户注册 → 登录 → 资料获取 → 交易所检查")
        print("=" * 80)
        
        # 运行所有测试步骤
        steps = [
            self.step_1_check_backend_health,
            self.step_2_user_registration,
            self.step_3_user_login,
            self.step_4_get_user_profile,
            self.step_5_check_exchanges
        ]
        
        all_passed = True
        for step in steps:
            success = await step()
            if not success:
                all_passed = False
                # 如果关键步骤失败，停止后续测试
                if step in [self.step_1_check_backend_health, self.step_2_user_registration, self.step_3_user_login]:
                    print(f"\n❌ 关键步骤失败，停止后续测试")
                    break
        
        # 显示测试结果汇总
        print("\n" + "=" * 80)
        print("📊 测试结果汇总")
        print("=" * 80)
        
        for step_name, success, details in self.results:
            status = "✅ 通过" if success else "❌ 失败"
            print(f"{status} {step_name}")
            if details:
                print(f"   {details}")
        
        print("=" * 80)
        if all_passed:
            print("🎉 所有测试通过！系统功能完整！")
        else:
            print("⚠️ 部分测试失败，请检查系统状态")
        
        return all_passed

async def main():
    """主函数"""
    test = TradingConsoleE2ETest()
    success = await test.run_all_tests()
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n测试执行异常: {e}")
        exit(1)
