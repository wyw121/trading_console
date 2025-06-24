from database import engine, Strategy, User
from sqlalchemy.orm import sessionmaker

# 创建数据库会话
Session = sessionmaker(bind=engine)
db = Session()

try:
    # 获取admin用户
    admin_user = db.query(User).filter(User.username == 'admin').first()
    print(f"Admin用户ID: {admin_user.id}")
    
    # 获取所有策略
    all_strategies = db.query(Strategy).all()
    print(f"总策略数: {len(all_strategies)}")
    
    # 将所有策略转移给admin用户
    for strategy in all_strategies:
        if strategy.user_id != admin_user.id:
            print(f"转移策略: {strategy.name} (从用户{strategy.user_id}到{admin_user.id})")
            strategy.user_id = admin_user.id
    
    # 提交更改
    db.commit()
    
    # 验证结果
    admin_strategies = db.query(Strategy).filter(Strategy.user_id == admin_user.id).all()
    print(f"Admin用户现在拥有{len(admin_strategies)}个策略:")
    for strategy in admin_strategies:
        print(f"  - {strategy.name} (活跃: {strategy.is_active})")
        
except Exception as e:
    print(f"错误: {e}")
    db.rollback()
finally:
    db.close()
