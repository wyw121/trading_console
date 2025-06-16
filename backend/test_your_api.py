"""
简化的OKX连接测试
使用您的测试API密钥
"""
import ccxt
import asyncio
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_okx_with_your_keys():
    """使用您的测试API密钥测试OKX连接"""
    
    # 您的测试API密钥
    config = {
        'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'passphrase': 'vf5Y3UeUFiz6xfF!',
        'sandbox': True,  # 测试环境
        'enableRateLimit': True,
        'timeout': 30000
    }
    
    print("🔗 使用您的测试API密钥测试OKX连接...")
    print("=" * 50)
    
    exchange = None
    try:
        # 创建OKX交易所实例
        print("1️⃣ 创建OKX实例...")
        exchange = ccxt.okx(config)
        print(f"   ✅ OKX实例创建成功，ID: {exchange.id}")
        
        # 测试公共API
        print("2️⃣ 测试公共API...")
        try:
            # 简单的公共API调用
            result = await exchange.public_get_public_time()
            print(f"   ✅ 公共API正常，服务器时间: {result}")
        except Exception as e:
            print(f"   ❌ 公共API失败: {e}")
            return False
        
        # 测试私有API  
        print("3️⃣ 测试私有API...")
        try:
            balance = await exchange.private_get_account_balance()
            print(f"   ✅ 私有API正常，余额响应: {balance.get('code', 'unknown')}")
            return True
        except Exception as e:
            print(f"   ❌ 私有API失败: {e}")
            print(f"   💡 错误可能原因:")
            print(f"      - API密钥权限不足")
            print(f"      - Passphrase错误")
            print(f"      - API密钥过期或无效")
            return False
            
    except Exception as e:
        print(f"❌ 创建连接失败: {e}")
        return False
        
    finally:
        if exchange and hasattr(exchange, 'close'):
            try:
                await exchange.close()
            except:
                pass
                
async def test_network_connectivity():
    """测试网络连接"""
    print("\n🌐 测试网络连接...")
    print("=" * 50)
    
    import aiohttp
    
    urls_to_test = [
        'https://okx.com',
        'https://www.okx.com/api/v5/public/time',
        'https://aws.okx.com'
    ]
    
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
        for url in urls_to_test:
            try:
                async with session.get(url) as response:
                    print(f"   ✅ {url} - 状态码: {response.status}")
            except Exception as e:
                print(f"   ❌ {url} - 失败: {e}")

if __name__ == "__main__":
    print("🧪 OKX API连接诊断")
    print("使用您提供的测试API密钥进行测试")
    print()
    
    # 运行网络测试
    asyncio.run(test_network_connectivity())
    
    # 运行API测试
    success = asyncio.run(test_okx_with_your_keys())
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 测试成功！您的API密钥配置正确")
        print("问题可能出在项目的连接逻辑上")
    else:
        print("❌ 测试失败！请检查API密钥配置")
        
    print("\n📝 建议:")
    print("1. 确认在OKX模拟交易环境中创建的API密钥")
    print("2. 确认API权限至少包含'读取'权限")
    print("3. 检查Passphrase是否正确")
    print("4. 尝试重新生成API密钥")
