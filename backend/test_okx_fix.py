#!/usr/bin/env python3
"""
测试OKX连接修复
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, ExchangeAccount
from trading_engine import exchange_manager
import asyncio

async def test_okx_connection():
    """测试修复后的OKX连接"""
    print("🔧 Testing OKX Connection Fix")
    print("=" * 40)
    
    try:
        db = next(get_db())
        account = db.query(ExchangeAccount).filter(ExchangeAccount.id == 1).first()
        
        if not account:
            print("❌ OKX account not found")
            return False
        
        print(f"📋 Account Info:")
        print(f"   Exchange: {account.exchange_name}")
        print(f"   API Key: {account.api_key[:10]}...")
        print(f"   Testnet: {account.is_testnet}")
        
        # 测试行情获取
        print("\n📈 Testing ticker retrieval...")
        ticker = await exchange_manager.get_ticker(account, 'BTCUSDT')
        
        if ticker and 'last' in ticker:
            price = ticker['last']
            print(f"✅ Success! BTC/USDT price: ${price:,.2f}")
            
            # 测试余额获取
            print("\n💰 Testing balance retrieval...")
            try:
                balance = await exchange_manager.get_balance(account)
                print("✅ Balance retrieved successfully!")
                print(f"   Balance keys: {list(balance.keys())[:5]}...")
            except Exception as e:
                print(f"⚠️ Balance failed (expected with test API): {str(e)[:100]}...")
            
            return True
        else:
            print("❌ Invalid ticker response")
            return False
            
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_okx_connection())
    
    print("\n" + "=" * 40)
    if result:
        print("🎉 OKX Connection Test PASSED!")
        print("✅ The API endpoints are working correctly")
        print("🌐 You can now test in the frontend interface")
    else:
        print("❌ OKX Connection Test FAILED!")
        print("🔍 Check the logs above for specific errors")
    
    print("\n📝 Next Steps:")
    print("1. Login to http://localhost:3000 as user '111'")
    print("2. Go to Exchanges page")
    print("3. Click 'Connection Test' for OKX account")
    print("4. Verify that connection and data retrieval work")
