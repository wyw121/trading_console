"""
最简化的FastAPI测试服务器
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 创建FastAPI应用
app = FastAPI(
    title="Trading Console API - Test",
    description="API for cryptocurrency trading strategy management (Test Mode)",
    version="1.0.0-test"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Trading Console API is running", 
        "status": "ok",
        "mode": "test"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "environment": "test"
    }

@app.get("/api/test")
async def api_test():
    return {
        "message": "API endpoint working", 
        "data": {"test": True}
    }
