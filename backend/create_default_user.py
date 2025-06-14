#!/usr/bin/env python3
"""
创建默认用户脚本
"""
from database import SessionLocal, User
from auth import get_password_hash

def create_default_user():
    """创建默认用户"""
    db = SessionLocal()
    
    try:
        # 检查是否已有用户
        existing_user = db.query(User).filter(User.username == "admin").first()
        if existing_user:
            print("默认用户已存在")
            return
        
        # 创建默认用户
        hashed_password = get_password_hash("admin123")
        default_user = User(
            username="admin",
            email="admin@example.com",
            hashed_password=hashed_password
        )
        
        db.add(default_user)
        db.commit()
        print("默认用户创建成功:")
        print("用户名: admin")
        print("密码: admin123")
        
    except Exception as e:
        print(f"创建用户失败: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_default_user()
