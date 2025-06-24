#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, ExchangeAccount
from sqlalchemy.orm import Session

def check_okx_accounts():
    """检查OKX账户配置"""
    db: Session = next(get_db())
    
    try:
        # 获取所有交易所账户
        accounts = db.query(ExchangeAccount).all()
        print(f"总共 {len(accounts)} 个交易所账户:")
        
        for account in accounts:
            print(f"\n账户 {account.id}:")
            print(f"  用户ID: {account.user_id}")
            print(f"  交易所: {account.exchange_name}")
            print(f"  测试网: {account.is_testnet}")
            print(f"  激活状态: {account.is_active}")
            
            # 检查API密钥是否存在（不解密）
            print(f"  API Key: {'已设置' if account.api_key else '未设置'}")
            print(f"  API Secret: {'已设置' if account.api_secret else '未设置'}")
            print(f"  Passphrase: {'已设置' if account.api_passphrase else '未设置'}")
                
            print(f"  验证状态: {account.validation_status}")
            if account.validation_error:
                print(f"  验证错误: {account.validation_error}")
                
        # 检查testuser的账户
        print(f"\ntestuser (用户1) 的账户:")
        user1_accounts = db.query(ExchangeAccount).filter(
            ExchangeAccount.user_id == 1
        ).all()
        
        if user1_accounts:
            for account in user1_accounts:
                print(f"  账户 {account.id}: {account.exchange_name} (激活: {account.is_active})")
                if account.api_key and account.api_secret:
                    print(f"    ✅ API密钥已配置")
                else:
                    print(f"    ❌ API密钥未配置")
        else:
            print("  没有找到该用户的账户")
            
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_okx_accounts()
