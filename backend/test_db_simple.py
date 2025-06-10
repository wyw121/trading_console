# 简化的数据库连接测试
import os
import sys

print("Testing database connectivity...")

# 首先尝试PostgreSQL
print("1. Trying PostgreSQL connection...")
try:
    from sqlalchemy import create_engine, text
    
    # PostgreSQL连接字符串
    pg_url = "postgresql://trading_user:trading_pass@localhost:5432/trading_console"
    pg_engine = create_engine(pg_url)
    
    with pg_engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   [OK] PostgreSQL connected: {version[:50]}...")
        
except Exception as e:
    print(f"   [WARNING] PostgreSQL failed: {str(e)[:80]}...")
    
    # 尝试SQLite作为备选
    print("2. Trying SQLite as fallback...")
    try:
        sqlite_url = "sqlite:///./test_trading.db"
        sqlite_engine = create_engine(sqlite_url)
        
        with sqlite_engine.connect() as conn:
            result = conn.execute(text("SELECT sqlite_version()"))
            version = result.fetchone()[0]
            print(f"   [OK] SQLite connected: version {version}")
            
        # 清理测试数据库
        if os.path.exists("test_trading.db"):
            os.remove("test_trading.db")
            print("   [OK] Test database cleaned up")
            
    except Exception as sqlite_e:
        print(f"   [ERROR] SQLite also failed: {sqlite_e}")
        sys.exit(1)

print("Database connectivity test completed successfully!")
