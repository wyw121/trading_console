import requests
import time

def test_services():
    print("🔍 测试交易控制台服务状态...")
    
    # 测试后端
    try:
        print("\n📡 测试后端服务...")
        response = requests.get('http://localhost:8000/health', timeout=5)
        print(f"✅ 后端健康检查: {response.status_code} - {response.json()}")
        
        # 测试API端点
        response = requests.get('http://localhost:8000/api/exchanges/supported', timeout=5)
        print(f"✅ 交易所API: {response.status_code} - 返回 {len(response.json())} 个交易所")
        
        # 测试API健康检查
        response = requests.get('http://localhost:8000/api/health', timeout=5)
        print(f"✅ API健康检查: {response.status_code} - {response.json()}")
        
    except Exception as e:
        print(f"❌ 后端测试失败: {e}")
    
    # 测试前端
    try:
        print("\n🌐 测试前端服务...")
        response = requests.get('http://localhost:3000', timeout=5)
        print(f"✅ 前端页面: {response.status_code} - HTML长度: {len(response.text)}")
        
    except Exception as e:
        print(f"❌ 前端测试失败: {e}")
    
    print("\n🎯 服务测试完成!")

if __name__ == "__main__":
    test_services()
