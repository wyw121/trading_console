#!/usr/bin/env python3
"""
更新数据库中的OKX API凭据并测试
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from database import get_db, User, ExchangeAccount
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def update_okx_credentials():
    """更新数据库中的OKX API凭据"""
    
    # 新的API凭据
    new_api_key = "5a0ba67e-8e05-4c8f-a294-9674e40e3ce5"
    new_secret = "11005BB74DB1BD54D11F92CF207E479B"
    new_passphrase = "vf5Y3UeUFiz6xfF!"
    
    try:
        # 获取数据库会话
        db = next(get_db())
        
        # 查找现有的OKX账户
        okx_accounts = db.query(ExchangeAccount).filter(
            ExchangeAccount.exchange_name.in_(['okx', 'OKX', 'okex'])
        ).all()
        
        if okx_accounts:
            print(f"找到 {len(okx_accounts)} 个OKX账户，正在更新...")
            
            for account in okx_accounts:
                print(f"更新账户ID: {account.id}, 用户ID: {account.user_id}")
                
                # 更新API凭据
                account.api_key = new_api_key
                account.api_secret = new_secret
                account.api_passphrase = new_passphrase
                
                print(f"✅ 账户 {account.id} 更新完成")
            
            # 提交更改
            db.commit()
            print("✅ 所有OKX账户凭据已更新到数据库")
            
        else:
            print("⚠️ 数据库中没有找到OKX账户，创建新账户...")
            
            # 查找第一个用户
            user = db.query(User).first()
            if not user:
                print("❌ 数据库中没有用户，请先创建用户")
                return False
            
            # 创建新的OKX账户
            new_account = ExchangeAccount(
                user_id=user.id,
                exchange_name='okx',
                api_key=new_api_key,
                api_secret=new_secret,
                api_passphrase=new_passphrase,
                is_testnet=False
            )
            
            db.add(new_account)
            db.commit()
            db.refresh(new_account)
            
            print(f"✅ 创建新OKX账户，ID: {new_account.id}")
        
        return True
        
    except Exception as e:
        logger.error(f"更新OKX凭据失败: {e}")
        return False
    finally:
        db.close()

def test_updated_credentials():
    """测试更新后的凭据"""
    try:
        from simple_real_trading_engine import real_exchange_manager
        
        print("\n🧪 测试更新后的凭据...")
        
        # 获取数据库会话
        db = next(get_db())
        
        # 查找OKX账户
        okx_account = db.query(ExchangeAccount).filter(
            ExchangeAccount.exchange_name.in_(['okx', 'OKX', 'okex'])
        ).first()
        
        if not okx_account:
            print("❌ 数据库中没有OKX账户")
            return False
        
        print(f"📋 测试账户信息:")
        print(f"   账户ID: {okx_account.id}")
        print(f"   用户ID: {okx_account.user_id}")
        print(f"   交易所: {okx_account.exchange_name}")
        print(f"   API Key: {okx_account.api_key[:8]}...")
        
        # 添加到交易引擎
        result = real_exchange_manager.add_okx_account(
            okx_account.user_id,
            okx_account.api_key,
            okx_account.api_secret,
            okx_account.api_passphrase
        )
        
        if result:
            print("✅ OKX账户已添加到交易引擎")
            
            # 测试连接
            connection_result = real_exchange_manager.test_okx_connection(okx_account.user_id)
            print(f"🔗 连接测试结果: {connection_result}")
            
            # 测试获取余额
            balance_result = real_exchange_manager.get_real_balance(
                okx_account.user_id,
                okx_account.exchange_name,
                False
            )
            print(f"💰 余额测试结果: {balance_result}")
            
            return balance_result.get('success', False)
        else:
            print("❌ 添加OKX账户到交易引擎失败")
            return False
            
    except Exception as e:
        logger.error(f"测试更新后凭据失败: {e}")
        return False
    finally:
        db.close()

if __name__ == "__main__":
    print("🔧 开始更新OKX API凭据...")
    
    # 更新凭据
    if update_okx_credentials():
        print("✅ 数据库更新成功")
        
        # 测试凭据
        if test_updated_credentials():
            print("🎉 测试成功! 新的API凭据工作正常")
        else:
            print("⚠️ 测试失败，请检查API凭据配置")
    else:
        print("❌ 数据库更新失败")
