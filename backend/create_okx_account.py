#!/usr/bin/env python3
"""
创建OKX测试账户
"""
import sys
import os
sys.path.append('.')

from database import SessionLocal, User, ExchangeAccount
from auth import get_password_hash

def create_okx_account():
    """创建OKX测试账户"""
    print("🔧 创建OKX测试账户")
    print("=" * 50)
    
    # 获取数据库会话
    db = SessionLocal()
    
    try:
        # 查找用户
        user = db.query(User).filter(User.username == "admin").first()
        if not user:
            print("❌ 用户admin不存在")
            return
        
        print(f"✅ 找到用户: {user.username} (ID: {user.id})")
        
        # 检查是否已存在OKX账户
        existing_account = db.query(ExchangeAccount).filter(
            ExchangeAccount.user_id == user.id,
            ExchangeAccount.exchange_name == "okex"
        ).first()
        
        if existing_account:
            print(f"ℹ️ 用户已存在OKX账户 (ID: {existing_account.id})")
            print("删除现有账户并重新创建...")
            db.delete(existing_account)
            db.commit()
        
        # 创建新的OKX账户
        api_key = "36815315-d6cd-4333-833e-b7e5ddffa9cb"
        api_secret = "AB482B3DF5D08DDFAEA0E09B37062AB5"
        passphrase = "TradingConsole2025!"        
        exchange_account = ExchangeAccount(
            user_id=user.id,
            exchange_name="okex",  # OKX的CCXT标识符
            api_key=api_key,
            api_secret=api_secret,
            api_passphrase=passphrase,
            is_testnet=False,
            is_active=True,
            permissions='["读取", "交易", "提现"]',
            ip_whitelist=""
        )
        
        db.add(exchange_account)
        db.commit()
        
        print(f"✅ OKX账户创建成功!")
        print(f"   账户ID: {exchange_account.id}")
        print(f"   交易所: {exchange_account.exchange_name}")
        print(f"   API Key: {api_key[:10]}...")
        print(f"   测试网: {exchange_account.is_testnet}")
        print(f"   权限: {exchange_account.permissions}")
        
    except Exception as e:
        print(f"❌ 创建账户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_okx_account()
