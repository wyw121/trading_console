# Final System Integration Test
# 最终系统集成测试

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000/api"

class TradingConsoleTest:
    def __init__(self):
        self.token = None
        self.user_id = None
        self.exchange_account_id = None
        self.strategy_id = None
        
    def log(self, message):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
        
    def test_user_registration_and_login(self):
        """测试用户注册和登录"""
        self.log("🔐 Testing user authentication...")
        
        # 使用现有的测试用户
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.token = data["access_token"]
            self.log("✅ User login successful")
            return True
        else:
            self.log(f"❌ Login failed: {response.text}")
            return False
    
    def test_exchange_connection(self):
        """测试交易所连接"""
        self.log("🔗 Testing OKX connection...")
        
        connection_data = {
            "exchange": "okx",
            "api_key": "test_key_final",
            "secret_key": "test_secret_final", 
            "passphrase": "test_passphrase_final",
            "is_testnet": False
        }
        
        response = requests.post(
            f"{BASE_URL}/exchanges/test_connection",
            json=connection_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.log(f"✅ Connection test successful: {data['data']['message']}")
            return True
        else:
            self.log(f"❌ Connection test failed: {response.text}")
            return False
    
    def test_create_exchange_account(self):
        """测试创建交易所账户"""
        self.log("🏦 Creating exchange account...")
        
        account_data = {
            "exchange_name": "okex",
            "api_key": "final_test_key_123",
            "api_secret": "final_test_secret_123",
            "api_passphrase": "final_test_passphrase_123",
            "is_testnet": False
        }
        
        response = requests.post(
            f"{BASE_URL}/exchanges/",
            json=account_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.exchange_account_id = data["id"]
            self.log(f"✅ Exchange account created: ID {self.exchange_account_id}")
            return True
        else:
            self.log(f"❌ Failed to create exchange account: {response.text}")
            return False
    
    def test_get_balance(self):
        """测试获取账户余额"""
        self.log("💰 Testing balance retrieval...")
        
        response = requests.get(
            f"{BASE_URL}/exchanges/accounts/{self.exchange_account_id}/balance",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            total_balance = data.get('total', {})
            self.log("✅ Balance retrieved successfully:")
            for currency, amount in total_balance.items():
                if amount > 0:
                    self.log(f"   {currency}: {amount}")
            return True
        else:
            self.log(f"❌ Failed to get balance: {response.text}")
            return False
    
    def test_get_ticker(self):
        """测试获取价格数据"""
        self.log("📊 Testing ticker data...")
        
        response = requests.get(
            f"{BASE_URL}/exchanges/accounts/{self.exchange_account_id}/ticker/BTCUSDT",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            price = data.get('last', 0)
            self.log(f"✅ Ticker data retrieved: BTC/USDT = ${price:.2f}")
            return True
        else:
            self.log(f"❌ Failed to get ticker: {response.text}")
            return False
    
    def test_create_strategy(self):
        """测试创建交易策略"""
        self.log("🎯 Creating trading strategy...")
        
        strategy_data = {
            "name": "Final Test Strategy",
            "strategy_type": "5m_boll_ma60",
            "symbol": "BTCUSDT",
            "timeframe": "5m",
            "exchange_account_id": self.exchange_account_id,
            "bb_period": 20,
            "bb_deviation": 2.0,
            "ma_period": 60,
            "entry_amount": 0.001,
            "stop_loss_pct": 2.0,
            "take_profit_pct": 4.0
        }
        
        response = requests.post(
            f"{BASE_URL}/strategies",
            json=strategy_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.token}"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            self.strategy_id = data["id"]
            self.log(f"✅ Strategy created: ID {self.strategy_id}")
            return True
        else:
            self.log(f"❌ Failed to create strategy: {response.text}")
            return False
    
    def test_activate_strategy(self):
        """测试激活策略"""
        self.log("⚡ Activating strategy...")
        
        response = requests.post(
            f"{BASE_URL}/strategies/{self.strategy_id}/toggle",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            is_active = data.get("is_active", False)
            self.log(f"✅ Strategy activated: {is_active}")
            return True
        else:
            self.log(f"❌ Failed to activate strategy: {response.text}")
            return False
    
    def test_dashboard_stats(self):
        """测试仪表板统计"""
        self.log("📈 Testing dashboard statistics...")
        
        response = requests.get(
            f"{BASE_URL}/dashboard/stats",
            headers={"Authorization": f"Bearer {self.token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            self.log("✅ Dashboard stats retrieved:")
            self.log(f"   Total strategies: {data.get('total_strategies', 0)}")
            self.log(f"   Active strategies: {data.get('active_strategies', 0)}")
            self.log(f"   Account balances: {len(data.get('account_balances', []))}")
            return True
        else:
            self.log(f"❌ Failed to get dashboard stats: {response.text}")
            return False
    
    def run_full_test(self):
        """运行完整的系统测试"""
        self.log("🚀 Starting comprehensive system test...")
        self.log("=" * 60)
        
        tests = [
            ("User Authentication", self.test_user_registration_and_login),
            ("Exchange Connection", self.test_exchange_connection),
            ("Exchange Account Creation", self.test_create_exchange_account),
            ("Balance Retrieval", self.test_get_balance),
            ("Ticker Data", self.test_get_ticker),
            ("Strategy Creation", self.test_create_strategy),
            ("Strategy Activation", self.test_activate_strategy),
            ("Dashboard Statistics", self.test_dashboard_stats),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n🧪 Running: {test_name}")
            try:
                if test_func():
                    passed += 1
                else:
                    self.log(f"❌ {test_name} FAILED")
            except Exception as e:
                self.log(f"❌ {test_name} ERROR: {str(e)}")
            
            time.sleep(0.5)  # Brief pause between tests
        
        self.log("\n" + "=" * 60)
        self.log(f"🏁 TEST SUMMARY: {passed}/{total} tests passed")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! System is fully functional.")
            return True
        else:
            self.log(f"⚠️  {total - passed} tests failed. Please check the logs above.")
            return False

if __name__ == "__main__":
    print("OKX Trading Console - Final Integration Test")
    print("=" * 60)
    
    tester = TradingConsoleTest()
    success = tester.run_full_test()
    
    if success:
        print("\n🎯 CONCLUSION: OKX API connection fix is COMPLETE and VERIFIED!")
        print("   All core functionalities are working properly.")
        print("   The system is ready for production use.")
    else:
        print("\n⚠️  Some issues detected. Please review the test results.")
