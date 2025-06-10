print("Starting import test...")

try:
    print("1. Testing FastAPI import...")
    from fastapi import FastAPI
    print("   [OK] FastAPI imported")
    
    print("2. Testing database import...")
    from database import create_tables
    print("   [OK] Database imported")
    
    print("3. Testing router imports...")
    from routers import auth
    print("   [OK] Auth router imported")
    
    from routers import exchange
    print("   [OK] Exchange router imported")
    
    from routers import strategies
    print("   [OK] Strategies router imported")
    
    from routers import trades
    print("   [OK] Trades router imported")
    
    from routers import dashboard
    print("   [OK] Dashboard router imported")
    
    print("4. Testing main import...")
    from main import app
    print("   [OK] Main app imported successfully")
    
    print("All imports successful!")
    
except Exception as e:
    print(f"[ERROR] Import failed: {e}")
    import traceback
    traceback.print_exc()
