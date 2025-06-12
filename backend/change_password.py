#!/usr/bin/env python3
"""
更改用户111的密码为123456
"""
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from database import SessionLocal, User
from auth import get_password_hash

def change_user_password():
    """更改用户密码"""
    print("🔐 更改用户111密码")
    print("=" * 30)
    
    # 创建数据库会话
    db = SessionLocal()
    
    try:
        # 查找用户111
        user = db.query(User).filter(User.username == '111').first()
        
        if user:
            print(f"📋 找到用户: {user.username}")
            print(f"   用户ID: {user.id}")
            print(f"   邮箱: {user.email}")
            print(f"   当前密码哈希: {user.hashed_password[:20]}...")
            
            # 更新密码为123456
            new_password = '123456'
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            
            print(f"\n✅ 密码更改成功!")
            print(f"   新密码: {new_password}")
            print(f"   新密码哈希: {user.hashed_password[:20]}...")
            
            return True
            
        else:
            print("❌ 用户111未找到")
            
            # 显示所有用户
            users = db.query(User).all()
            print(f"\n📋 数据库中共有 {len(users)} 个用户:")
            for u in users:
                print(f"   - ID: {u.id}, 用户名: {u.username}, 邮箱: {u.email}")
            
            return False
            
    except Exception as e:
        print(f"❌ 密码更改失败: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = change_user_password()
    
    print("\n" + "=" * 30)
    if success:
        print("🎉 密码更改完成!")
        print("\n📝 登录信息:")
        print("   用户名: 111")
        print("   密码: 123456")
        print("\n🌐 现在可以使用新密码登录:")
        print("   http://localhost:3000/login")
    else:
        print("❌ 密码更改失败!")
        print("请检查数据库连接和用户是否存在")
