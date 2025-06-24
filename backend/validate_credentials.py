#!/usr/bin/env python3
"""
OKX API凭据详细验证
逐一验证每个字段的正确性
"""
import re

def validate_okx_credentials():
    """验证OKX API凭据格式"""
    
    print("🔍 验证OKX API凭据格式")
    print("=" * 50)
    
    # 你提供的凭据
    api_key = "5a0ba67e-8e05-4c8f-a294-9674e40e3ce5"
    secret = "11005BB74DB1BD54D11F92CF207E479B"
    passphrase = "vf5Y3UeUFiz6xfF!"
    
    print(f"API Key: {api_key}")
    print(f"Secret: {secret}")
    print(f"Passphrase: {passphrase}")
    print()
    
    # 1. API Key格式验证
    print("1️⃣ API Key格式验证:")
    api_key_pattern = r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
    if re.match(api_key_pattern, api_key):
        print(f"✅ API Key格式正确: {api_key}")
    else:
        print(f"❌ API Key格式异常: {api_key}")
        print("   标准格式: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx")
    
    # 2. Secret Key格式验证
    print("\n2️⃣ Secret Key格式验证:")
    secret_pattern = r'^[A-F0-9]{32}$'
    if re.match(secret_pattern, secret):
        print(f"✅ Secret Key格式正确: {secret}")
    else:
        print(f"❌ Secret Key格式异常: {secret}")
        print(f"   长度: {len(secret)} (期望32)")
        print("   包含字符:", set(secret))
        print("   标准格式: 32位大写十六进制字符")
    
    # 3. Passphrase验证
    print("\n3️⃣ Passphrase验证:")
    print(f"✅ Passphrase: {passphrase}")
    print(f"   长度: {len(passphrase)}")
    print(f"   包含特殊字符: {'是' if any(c in '!@#$%^&*' for c in passphrase) else '否'}")
    
    # 4. 生成测试签名
    print("\n4️⃣ 生成测试签名:")
    try:
        import hmac
        import hashlib
        import base64
        import time
        
        timestamp = str(int(time.time() * 1000))
        method = 'GET'
        path = '/api/v5/account/balance'
        body = ''
        
        message = timestamp + method + path + body
        signature = base64.b64encode(
            hmac.new(secret.encode('utf-8'), 
                    message.encode('utf-8'), 
                    hashlib.sha256).digest()
        ).decode('utf-8')
        
        print(f"✅ 签名生成成功")
        print(f"   时间戳: {timestamp}")
        print(f"   消息: {message}")
        print(f"   签名: {signature[:20]}...")
        
    except Exception as e:
        print(f"❌ 签名生成失败: {e}")
    
    # 5. 建议的检查项目
    print("\n5️⃣ 请在OKX网站检查以下设置:")
    print("=" * 50)
    print("1. 登录 OKX 网站 -> API管理")
    print("2. 找到API Key: 5a0ba67e-8e05-4c8f-a294-9674e40e3ce5")
    print("3. 检查状态是否为'正常'")
    print("4. 检查权限是否包含:")
    print("   ✓ 读取 (必须)")
    print("   ✓ 交易 (可选)")
    print("   ✓ 提现 (可选)")
    print("5. 检查IP白名单:")
    print("   ✓ 23.145.24.14 (当前IP)")
    print("   ✓ 或者设为空(允许所有IP)")
    print("6. 检查API密钥是否已过期")
    print("7. 检查是否有其他安全限制")
    
    print("\n💡 常见问题排查:")
    print("- 如果凭据格式都正确，但仍然401/50102错误")
    print("- 最可能的原因是权限配置问题")
    print("- 建议在OKX网站重新生成API密钥")
    print("- 确保勾选'读取'权限")
    print("- 暂时不设IP白名单进行测试")

if __name__ == "__main__":
    validate_okx_credentials()
