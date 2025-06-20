"""
快速测试脚本 - 测试OKX API集成
"""

import requests
import json

# 测试数据
test_exchange_data = {
    "exchange_name": "okx",
    "api_key": "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0",
    "api_secret": "CD6A497EEB00AA2DC60B2B0974DD2485",
    "api_passphrase": "vf5Y3UeUFiz6xfF!",
    "is_testnet": False
}

def test_backend_apis():
    """测试后端API"""
    base_url = "http://localhost:8000"
    
    print("🚀 测试Trading Console后端API")
    print("=" * 50)
    
    # 测试1: 健康检查
    print("1️⃣ 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 健康检查成功: {response.json()}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
    
    # 测试2: 根路由
    print("\n2️⃣ 测试根路由...")
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            print(f"✅ 根路由成功: {response.json()}")
        else:
            print(f"❌ 根路由失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 根路由异常: {e}")
    
    # 测试3: API文档
    print("\n3️⃣ 测试API文档...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code == 200:
            print("✅ API文档可访问")
        else:
            print(f"❌ API文档失败: {response.status_code}")
    except Exception as e:
        print(f"❌ API文档异常: {e}")
    
    print("\n📋 后端API测试完成")

def test_okx_integration():
    """测试OKX集成（如果可能的话）"""
    print("\n🔧 测试OKX API集成")
    print("=" * 50)
    
    try:
        from simple_real_trading_engine import real_exchange_manager
        import asyncio
        
        async def test_okx():
            result = await real_exchange_manager.test_connection(
                exchange_name="okx",
                api_key=test_exchange_data["api_key"],
                api_secret=test_exchange_data["api_secret"],
                api_passphrase=test_exchange_data["api_passphrase"],
                is_testnet=False
            )
            
            if result['success']:
                print("✅ OKX API集成测试成功")
                print(f"   消息: {result['message']}")
            else:
                print("❌ OKX API集成测试失败")
                print(f"   错误: {result['message']}")
        
        asyncio.run(test_okx())
        
    except Exception as e:
        print(f"❌ OKX集成测试异常: {e}")

def main():
    """主测试函数"""
    print("🚀 Trading Console 完整测试")
    print("=" * 60)
    
    # 测试后端API
    test_backend_apis()
    
    # 测试OKX集成
    test_okx_integration()
    
    print("\n🎉 测试完成！")
    print("\n💡 可以通过以下URL访问应用:")
    print("   前端: http://localhost:3001")
    print("   后端API文档: http://localhost:8000/docs")
    print("   后端健康检查: http://localhost:8000/health")

if __name__ == "__main__":
    main()
