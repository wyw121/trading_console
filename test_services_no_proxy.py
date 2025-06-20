import requests
import os

def test_services_no_proxy():
    print("🔍 测试交易控制台服务状态（绕过代理）...")
    
    # 临时移除代理设置
    old_proxies = {
        'HTTP_PROXY': os.environ.get('HTTP_PROXY'),
        'HTTPS_PROXY': os.environ.get('HTTPS_PROXY'),
        'http_proxy': os.environ.get('http_proxy'),
        'https_proxy': os.environ.get('https_proxy'),
    }
    
    # 清除代理环境变量
    for key in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        if key in os.environ:
            del os.environ[key]
    
    try:
        # 测试后端
        print("\n📡 测试后端服务...")
        session = requests.Session()
        session.proxies = {}  # 明确不使用代理
        
        response = session.get('http://localhost:8000/health', timeout=5)
        print(f"✅ 后端健康检查: {response.status_code} - {response.json()}")
        
        # 测试API端点
        response = session.get('http://localhost:8000/api/exchanges/supported', timeout=5)
        print(f"✅ 交易所API: {response.status_code} - 返回 {len(response.json())} 个交易所")
        
        # 测试API健康检查
        response = session.get('http://localhost:8000/api/health', timeout=5)
        print(f"✅ API健康检查: {response.status_code} - {response.json()}")
        
        # 测试前端
        print("\n🌐 测试前端服务...")
        response = session.get('http://localhost:3000', timeout=5)
        print(f"✅ 前端页面: {response.status_code} - HTML长度: {len(response.text)}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 恢复代理设置
        for key, value in old_proxies.items():
            if value:
                os.environ[key] = value
        print("\n🔧 代理设置已恢复")
    
    print("\n🎯 服务测试完成!")

if __name__ == "__main__":
    test_services_no_proxy()
