#!/usfrom database import get_db, ExchangeAccount
from sqlalchemy.orm import Sessionin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, ExchangeAccount
from sqlalchemy.orm import Session
# from encryption import decrypt_api_key

def check_okx_accounts():
    """检查OKX账户配置"""
    db: Session = next(get_db())
    
    try:        # 获取所有交易所账户
        accounts = db.query(ExchangeAccount).all()
        print(f"总共 {len(accounts)} 个交易所账户:")
        
        for account in accounts:
            print(f"\n账户 {account.id}:")
            print(f"  用户ID: {account.user_id}")
            print(f"  交易所: {account.exchange_name}")
            print(f"  测试网: {account.is_testnet}")
            print(f"  激活状态: {account.is_active}")
            
            # 检查API密钥是否存在
            if account.api_key:
                try:
                    decrypted_key = decrypt_api_key(account.api_key)
                    key_length = len(decrypted_key) if decrypted_key else 0
                    print(f"  API Key: 已设置 (长度: {key_length})")
                except Exception as e:
                    print(f"  API Key: 解密失败 - {e}")
            else:
                print(f"  API Key: 未设置")
                
            if account.api_secret:
                try:
                    decrypted_secret = decrypt_api_key(account.api_secret)
                    secret_length = len(decrypted_secret) if decrypted_secret else 0
                    print(f"  API Secret: 已设置 (长度: {secret_length})")
                except Exception as e:
                    print(f"  API Secret: 解密失败 - {e}")
            else:
                print(f"  API Secret: 未设置")
                
            if account.api_passphrase:
                try:
                    decrypted_passphrase = decrypt_api_key(account.api_passphrase)
                    passphrase_length = len(decrypted_passphrase) if decrypted_passphrase else 0
                    print(f"  Passphrase: 已设置 (长度: {passphrase_length})")
                except Exception as e:
                    print(f"  Passphrase: 解密失败 - {e}")
            else:
                print(f"  Passphrase: 未设置")
                
            print(f"  验证状态: {account.validation_status}")
            if account.validation_error:
                print(f"  验证错误: {account.validation_error}")
                  # 检查用户1的账户
        print(f"\n用户1的账户:")
        user1_accounts = db.query(ExchangeAccount).filter(
            ExchangeAccount.user_id == 1
        ).all()
        
        for account in user1_accounts:
            print(f"  账户 {account.id}: {account.exchange_name} (激活: {account.is_active})")
            
    except Exception as e:
        print(f"检查失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_okx_accounts()
