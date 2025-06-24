#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import get_db, User
from sqlalchemy.orm import Session

def check_users():
    """检查用户配置"""
    db: Session = next(get_db())
    
    try:
        # 获取testuser
        testuser = db.query(User).filter(User.username == 'testuser').first()
        if testuser:
            print(f"testuser的ID: {testuser.id}")
            print(f"testuser的邮箱: {testuser.email}")
        else:
            print("没有找到testuser")
            
        # 获取所有用户
        users = db.query(User).all()
        print(f"\n所有用户:")
        for user in users:
            print(f"  用户ID {user.id}: {user.username} ({user.email})")
            
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_users()
