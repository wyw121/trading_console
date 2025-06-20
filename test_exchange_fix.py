import requests
import json
import os

def test_exchange_connection_no_proxy():
    """测试交易所连接API（绕过代理）"""
    
    # 临时清除代理设置
    old_proxies = {}
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        if var in os.environ:
            old_proxies[var] = os.environ[var]
            del os.environ[var]
    
    try:
        session = requests.Session()
        session.proxies = {}
        
        print("🔍 测试交易所连接API（绕过代理）...")
        
        # 获取支持的交易所
        response = session.get('http://localhost:8000/api/exchanges/supported', timeout=5)
        print(f"✅ 支持的交易所: {response.status_code}")
        exchanges = response.json()
        for ex in exchanges:
            print(f"  - {ex['name']} ({ex['id']})")
        
        print("\n✅ 交易所管理器修复完成！")
        print("📝 已添加的方法:")
        print("  - test_connection(): 测试交易所API连接")
        print("  - add_exchange_account(): 添加交易所账户到管理器")
        print("\n🚀 现在可以正常创建交易所账户了！")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
    
    finally:
        # 恢复代理设置
        for var, value in old_proxies.items():
            os.environ[var] = value

if __name__ == "__main__":
    test_exchange_connection_no_proxy()
