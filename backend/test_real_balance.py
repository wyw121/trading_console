#!/usr/bin/env python3
"""
测试真实OKX余额获取
"""
import asyncio
import sys
import os
sys.path.append('.')

from database import SessionLocal, User, ExchangeAccount
from trading_engine import exchange_manager

async def test_real_balance():
    """测试真实余额获取"""
    print("🔧 测试真实OKX余额获取")
    print("=" * 50)
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 查找用户和交易所账户
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("❌ 用户admin不存在")
            return
        
        exchange_account = db.query(ExchangeAccount).filter(
            ExchangeAccount.user_id == user.id,
            ExchangeAccount.exchange_name == "okex"
        ).first()
        
        if not exchange_account:
            print("❌ 未找到OKX账户")
            return
        
        print(f"✅ 找到OKX账户: ID {exchange_account.id}")
        print(f"   API Key: {exchange_account.api_key[:10]}...")
        print(f"   测试网: {exchange_account.is_testnet}")
        print("")
        
        # 获取余额
        print("🔍 正在获取余额...")
        balance = await exchange_manager.get_balance(exchange_account)
        
        print("✅ 余额获取成功!")
        print(f"总余额数据: {len(balance.get('total', {}))} 种币")
        
        # 显示有余额的币种
        total_balances = balance.get('total', {})
        for currency, amount in total_balances.items():
            if amount > 0:
                print(f"   {currency}: {amount}")
        
        print("")
        print("完整余额数据:")
        print(balance)
        
    except Exception as e:
        print(f"❌ 获取余额失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_real_balance())
