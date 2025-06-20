"""
测试OKX API认证和余额获取
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from okx_api_manager import OKXAPIManager
import logging

# 设置日志级别
logging.basicConfig(level=logging.DEBUG)

def test_okx_api_auth():
    """测试OKX API认证"""
    print("🔐 测试OKX API认证和余额获取...")
    
    # 使用预设的测试API密钥
    api_key = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
    secret = "CD6A497EEB00AA2DC60B2B0974DD2485"
    passphrase = "vf5Y3UeUFiz6xfF!"
    
    try:
        # 创建API管理器
        manager = OKXAPIManager(api_key, secret, passphrase)
        
        # 1. 调试API凭据
        print("\n1️⃣ 调试API凭据:")
        debug_result = manager.debug_api_credentials()
        for key, value in debug_result.items():
            print(f"  {key}: {value}")
        
        # 2. 测试公开API
        print("\n2️⃣ 测试公开API (服务器时间):")
        time_result = manager.get_server_time()
        print(f"  结果: {time_result}")
        
        # 3. 测试私有API (余额)
        print("\n3️⃣ 测试私有API (余额):")
        balance_result = manager.get_balance()
        print(f"  结果: {balance_result}")
        
        # 4. 完整连接测试
        print("\n4️⃣ 完整连接测试:")
        connection_result = manager.test_connection()
        print(f"  结果: {connection_result}")
        
        # 分析结果
        print("\n📊 结果分析:")
        if time_result.get('code') == '0':
            print("  ✅ 公开API正常")
        else:
            print(f"  ❌ 公开API失败: {time_result.get('msg', '未知错误')}")
        
        if balance_result.get('code') == '0':
            print("  ✅ 私有API正常")
        elif balance_result.get('code') == '401':
            print("  ❌ 私有API认证失败 (401)")
            print("  💡 可能原因:")
            print("    - API密钥无效或已过期")
            print("    - API密钥没有读取余额的权限")
            print("    - IP地址未加入白名单")
            print("    - 签名算法错误")
        else:
            print(f"  ❌ 私有API失败: {balance_result.get('msg', '未知错误')}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")

def test_signature_algorithm():
    """测试签名算法"""
    print("\n🔐 测试签名算法...")
    
    # 使用OKX官方文档的示例数据进行测试
    api_key = "test-api-key"
    secret = "test-secret"
    passphrase = "test-passphrase"
    
    manager = OKXAPIManager(api_key, secret, passphrase, use_proxy=False)
    
    # 测试签名生成
    timestamp = "2023-01-01T00:00:00.000Z"
    method = "GET"
    request_path = "/api/v5/account/balance"
    body = ""
    
    signature = manager._create_signature(timestamp, method, request_path, body)
    print(f"测试签名: {signature}")
    
    # 验证签名格式
    import base64
    try:
        base64.b64decode(signature)
        print("✅ 签名格式正确 (Base64)")
    except:
        print("❌ 签名格式错误")

if __name__ == "__main__":
    test_okx_api_auth()
    test_signature_algorithm()
