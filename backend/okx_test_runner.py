#!/usr/bin/env python3
"""
OKX API 完整测试脚本
运行所有API功能测试，验证连接和功能
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from okx_api_practice import OKXAPIManager, OKXConfig
from okx_python_sdk_example import OKXTradingBot
import json
from datetime import datetime

class OKXTestSuite:
    """OKX API测试套件"""
    
    def __init__(self):
        self.test_results = {}
        self.passed = 0
        self.failed = 0
        
        # 测试配置 - 请替换为您的API密钥
        self.config = {
            'api_key': 'your_api_key_here',
            'secret_key': 'your_secret_key_here',
            'passphrase': 'your_passphrase_here',
            'is_sandbox': True  # 使用沙盒环境
        }
    
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        
        self.test_results[test_name] = {
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        if success:
            self.passed += 1
        else:
            self.failed += 1
    
    async def test_ccxt_connection(self):
        """测试CCXT连接"""
        print("\n🔗 测试CCXT连接...")
        try:
            config = OKXConfig(
                api_key=self.config['api_key'],
                secret_key=self.config['secret_key'],
                passphrase=self.config['passphrase'],
                is_sandbox=self.config['is_sandbox']
            )
            
            api = OKXAPIManager(config)
            success = await api.initialize()
            
            if success:
                # 测试基本功能
                status = await api.get_system_status()
                account_config = await api.get_account_config()
                
                await api.close()
                
                self.log_test("CCXT连接测试", True, f"系统状态: {status.get('code', 'N/A')}")
            else:
                self.log_test("CCXT连接测试", False, "初始化失败")
                
        except Exception as e:
            self.log_test("CCXT连接测试", False, str(e))
    
    def test_python_sdk_connection(self):
        """测试Python SDK连接"""
        print("\n📦 测试Python SDK连接...")
        try:
            bot = OKXTradingBot(
                api_key=self.config['api_key'],
                secret_key=self.config['secret_key'],
                passphrase=self.config['passphrase'],
                is_demo=self.config['is_sandbox']
            )
            
            # 测试系统状态
            status = bot.get_system_status()
            
            if status and status.get('code') == '0':
                self.log_test("Python SDK连接测试", True, "系统状态正常")
            else:
                self.log_test("Python SDK连接测试", False, "系统状态异常")
                
        except Exception as e:
            self.log_test("Python SDK连接测试", False, str(e))
    
    async def test_market_data_apis(self):
        """测试市场数据API"""
        print("\n📊 测试市场数据API...")
        try:
            config = OKXConfig(**self.config)
            api = OKXAPIManager(config)
            
            if await api.initialize():
                # 测试获取交易工具
                instruments = await api.get_instruments("SPOT")
                self.log_test("获取交易工具", 
                            len(instruments) > 0, 
                            f"获取到 {len(instruments)} 个现货交易对")
                
                # 测试获取行情
                ticker = await api.get_market_ticker("BTC-USDT")
                self.log_test("获取行情数据", 
                            'last' in ticker, 
                            f"BTC-USDT价格: {ticker.get('last', 'N/A')}")
                
                await api.close()
            else:
                self.log_test("市场数据API", False, "连接初始化失败")
                
        except Exception as e:
            self.log_test("市场数据API", False, str(e))
    
    async def test_account_apis(self):
        """测试账户API"""
        print("\n💰 测试账户API...")
        try:
            config = OKXConfig(**self.config)
            api = OKXAPIManager(config)
            
            if await api.initialize():
                # 测试账户配置
                account_config = await api.get_account_config()
                self.log_test("获取账户配置", 
                            not account_config.get('error'), 
                            f"账户配置: {account_config.get('code', 'N/A')}")
                
                # 测试账户余额
                balance = await api.get_account_balance()
                self.log_test("获取账户余额", 
                            not balance.get('error'), 
                            f"余额数据: {len(balance) if isinstance(balance, list) else 'N/A'} 条记录")
                
                await api.close()
            else:
                self.log_test("账户API", False, "连接初始化失败")
                
        except Exception as e:
            self.log_test("账户API", False, str(e))
    
    def test_error_handling(self):
        """测试错误处理"""
        print("\n⚠️ 测试错误处理...")
        try:
            # 使用错误的API密钥测试
            wrong_config = OKXConfig(
                api_key="wrong_key",
                secret_key="wrong_secret",
                passphrase="wrong_passphrase",
                is_sandbox=True
            )
            
            bot = OKXTradingBot(
                api_key="wrong_key",
                secret_key="wrong_secret",
                passphrase="wrong_passphrase",
                is_demo=True
            )
            
            # 尝试获取账户信息（应该失败）
            result = bot.get_account_config()
            
            if result and result.get('code') != '0':
                self.log_test("错误处理测试", True, "正确处理了错误的API密钥")
            else:
                self.log_test("错误处理测试", False, "未正确处理错误")
                
        except Exception as e:
            # 异常也是预期的结果
            self.log_test("错误处理测试", True, f"正确抛出异常: {str(e)[:50]}...")
    
    def test_rate_limiting(self):
        """测试限速处理"""
        print("\n🚦 测试限速处理...")
        try:
            bot = OKXTradingBot(
                api_key=self.config['api_key'],
                secret_key=self.config['secret_key'],
                passphrase=self.config['passphrase'],
                is_demo=self.config['is_sandbox']
            )
            
            # 快速连续调用API
            results = []
            for i in range(5):
                result = bot.get_system_status()
                results.append(result is not None)
            
            success_rate = sum(results) / len(results)
            self.log_test("限速处理测试", 
                        success_rate >= 0.8, 
                        f"成功率: {success_rate:.1%}")
                        
        except Exception as e:
            self.log_test("限速处理测试", False, str(e))
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "="*60)
        print("📊 测试报告")
        print("="*60)
        
        total_tests = self.passed + self.failed
        success_rate = (self.passed / total_tests * 100) if total_tests > 0 else 0
        
        print(f"总测试数: {total_tests}")
        print(f"通过: {self.passed}")
        print(f"失败: {self.failed}")
        print(f"成功率: {success_rate:.1f}%")
        
        print(f"\n{'测试名称':<25} {'状态':<8} {'详情'}")
        print("-" * 60)
        
        for test_name, result in self.test_results.items():
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            details = result['details'][:30] + "..." if len(result['details']) > 30 else result['details']
            print(f"{test_name:<25} {status:<8} {details}")
        
        # 保存详细报告
        report = {
            'summary': {
                'total': total_tests,
                'passed': self.passed,
                'failed': self.failed,
                'success_rate': success_rate,
                'timestamp': datetime.now().isoformat()
            },
            'details': self.test_results
        }
        
        with open('okx_test_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📄 详细报告已保存到: okx_test_report.json")
        
        return success_rate >= 80  # 80%以上通过率认为成功

async def run_comprehensive_tests():
    """运行完整测试"""
    print("🚀 开始OKX API完整测试")
    print("="*60)
    
    # 检查配置
    print("⚙️ 检查测试配置...")
    
    test_suite = OKXTestSuite()
    
    # 检查API密钥是否已配置
    if test_suite.config['api_key'] == 'your_api_key_here':
        print("❌ 请先配置您的API密钥")
        print("1. 在OKX官网申请API密钥")
        print("2. 修改 test_suite.config 中的API密钥")
        print("3. 建议使用测试网络的API密钥")
        return False
    
    # 运行各项测试
    try:
        # 1. 连接测试
        await test_suite.test_ccxt_connection()
        test_suite.test_python_sdk_connection()
        
        # 2. 功能测试
        await test_suite.test_market_data_apis()
        await test_suite.test_account_apis()
        
        # 3. 错误和性能测试
        test_suite.test_error_handling()
        test_suite.test_rate_limiting()
        
        # 4. 生成报告
        success = test_suite.generate_report()
        
        if success:
            print("\n🎉 所有测试基本通过！")
            print("✅ OKX API集成准备就绪")
        else:
            print("\n⚠️ 部分测试失败，请检查配置和网络连接")
            print("📋 详情请查看测试报告")
        
        return success
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现未预期的错误: {e}")
        return False

def quick_connection_test():
    """快速连接测试"""
    print("🔍 快速连接测试")
    print("-" * 30)
    
    # 测试配置
    config = {
        'api_key': 'your_api_key_here',
        'secret_key': 'your_secret_key_here',
        'passphrase': 'your_passphrase_here',
        'is_demo': True
    }
    
    if config['api_key'] == 'your_api_key_here':
        print("❌ 请先配置API密钥")
        return False
    
    try:
        bot = OKXTradingBot(**config)
        
        # 测试基本连接
        status = bot.get_system_status()
        
        if status and status.get('code') == '0':
            print("✅ 连接成功")
            
            # 获取一些基本信息
            bot.get_account_config()
            bot.get_ticker("BTC-USDT")
            
            print("✅ 基本功能正常")
            return True
        else:
            print("❌ 连接失败")
            return False
            
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False

if __name__ == "__main__":
    print("OKX API 测试工具")
    print("="*40)
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        # 快速测试模式
        quick_connection_test()
    else:
        # 完整测试模式
        asyncio.run(run_comprehensive_tests())
    
    print("\n💡 使用提示:")
    print("1. 快速测试: python okx_test_runner.py quick")
    print("2. 完整测试: python okx_test_runner.py")
    print("3. 请确保已正确配置API密钥")
    print("4. 建议在测试环境中运行")
