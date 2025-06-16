"""
OKX API连接测试脚本
用于测试API密钥配置是否正确
"""
import asyncio
import ccxt
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_okx_connection():
    """测试OKX API连接"""
    
    # ⚠️ 警告：这些是示例密钥，请使用您自己的API密钥
    # 请在OKX官网重新生成新的API密钥
    API_CONFIG = {
        'apiKey': 'your_new_api_key_here',  # 请替换
        'secret': 'your_new_secret_here',   # 请替换  
        'passphrase': 'your_new_passphrase_here',  # 请替换
        'sandbox': True,  # 使用测试环境
        'enableRateLimit': True,
        'rateLimit': 100,
        'timeout': 30000,
    }
    
    print("🔐 OKX API连接测试")
    print("=" * 50)
    
    try:
        # 1. 创建交易所实例
        print("1️⃣ 创建OKX交易所实例...")
        exchange = ccxt.okx(API_CONFIG)
        
        # 2. 测试公共API - 获取系统状态
        print("2️⃣ 测试公共API - 获取系统状态...")
        try:
            status = await exchange.public_get_system_status()
            print(f"   ✅ 系统状态: {status}")
        except Exception as e:
            print(f"   ❌ 公共API失败: {e}")
            return
        
        # 3. 测试私有API - 获取账户配置
        print("3️⃣ 测试私有API - 获取账户配置...")
        try:
            config = await exchange.private_get_account_config()
            print(f"   ✅ 账户配置: {config}")
        except Exception as e:
            print(f"   ❌ 私有API失败: {e}")
            print(f"   💡 可能的原因:")
            print(f"      - API密钥错误")
            print(f"      - API权限不足") 
            print(f"      - IP地址不在白名单")
            print(f"      - Passphrase错误")
            return
        
        # 4. 测试获取交易工具
        print("4️⃣ 测试获取交易工具...")
        try:
            instruments = await exchange.public_get_public_instruments({'instType': 'SPOT'})
            count = len(instruments.get('data', []))
            print(f"   ✅ 获取到 {count} 个现货交易对")
        except Exception as e:
            print(f"   ❌ 获取交易工具失败: {e}")
        
        # 5. 测试获取余额（如果有权限）
        print("5️⃣ 测试获取账户余额...")
        try:
            balance = await exchange.private_get_account_balance()
            print(f"   ✅ 账户余额: {balance}")
        except Exception as e:
            print(f"   ❌ 获取余额失败: {e}")
        
        # 6. 测试获取行情
        print("6️⃣ 测试获取BTC-USDT行情...")
        try:
            ticker = await exchange.public_get_market_ticker({'instId': 'BTC-USDT'})
            if ticker.get('code') == '0' and ticker.get('data'):
                price = ticker['data'][0]['last']
                print(f"   ✅ BTC-USDT当前价格: ${price}")
            else:
                print(f"   ❌ 获取行情失败: {ticker}")
        except Exception as e:
            print(f"   ❌ 获取行情失败: {e}")
        
        print("\n✅ API连接测试完成！")
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        print("\n🔧 故障排除建议:")
        print("1. 检查API密钥是否正确")
        print("2. 确认Passphrase是否正确")
        print("3. 检查API权限设置")
        print("4. 确认IP地址是否在白名单")        print("5. 尝试在OKX官网重新生成API密钥")
        
    finally:
        if 'exchange' in locals() and hasattr(exchange, 'close'):
            await exchange.close()

async def test_api_with_ccxt_only():
    """仅使用CCXT测试，不依赖项目代码"""
    print("\n🧪 纯CCXT API测试")
    print("=" * 50)
    
    # 请在这里填入您的新API密钥
    config = {
        'apiKey': '',  # 在这里填入您的新API Key
        'secret': '',  # 在这里填入您的新Secret Key  
        'passphrase': '',  # 在这里填入您的新Passphrase
        'sandbox': True,  # 测试环境
        'enableRateLimit': True,
    }
    
    if not config['apiKey']:
        print("❌ 请先在代码中填入您的API密钥配置")
        return
    
    try:
        exchange = ccxt.okx(config)
        
        # 简单的连接测试
        markets = await exchange.load_markets()
        print(f"✅ 成功加载 {len(markets)} 个交易市场")
        
        # 获取余额
        balance = await exchange.fetch_balance()
        print(f"✅ 成功获取账户余额")
        
        # 显示非零余额
        total_balances = balance.get('total', {})
        non_zero = {k: v for k, v in total_balances.items() if v > 0}
        if non_zero:
            print(f"💰 非零余额: {non_zero}")
        else:
            print("💰 账户余额为空（这在测试环境中是正常的）")
            
    except Exception as e:
        print(f"❌ CCXT测试失败: {e}")
    finally:        if 'exchange' in locals() and hasattr(exchange, 'close'):
            await exchange.close()

if __name__ == "__main__":
    print("🚨 安全提醒：请立即在OKX官网删除您之前暴露的API密钥！")
    print("📝 然后重新生成新的API密钥用于测试")
    print()
    
    # 运行测试
    asyncio.run(test_okx_connection())
    asyncio.run(test_api_with_ccxt_only())
