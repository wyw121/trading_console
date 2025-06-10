#!/usr/bin/env python3

import sys
print(f"Python version: {sys.version}")
print(f"Current working directory: {sys.path[0]}")

try:
    from fastapi import FastAPI
    print("[OK] FastAPI imported successfully")
    
    app = FastAPI(title="Test API")
    print("[OK] FastAPI app created successfully")
    
    @app.get("/")
    def read_root():
        return {"message": "Hello World"}
    
    print("[OK] Route defined successfully")
    print("[OK] App object created and ready")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
