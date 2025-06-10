"""
简化的FastAPI启动脚本，用于开发测试
使用SQLite数据库，避免PostgreSQL依赖
"""
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

# 设置SQLite数据库
DATABASE_URL = "sqlite:///./trading_console_dev.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title="Trading Console API - Development",
    description="API for cryptocurrency trading strategy management (Development Mode)",
    version="1.0.0-dev"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 基础路由
@app.get("/")
async def root():
    return {
        "message": "Trading Console API is running", 
        "status": "ok",
        "mode": "development",
        "database": "SQLite"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "environment": "development",
        "database": "SQLite",
        "database_url": DATABASE_URL
    }

@app.get("/api/test")
async def api_test():
    return {
        "message": "API endpoint working", 
        "data": {"test": True},
        "timestamp": "2025-06-10"
    }

# 依赖注入函数
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 Starting Trading Console API Server...")
    print(f"📊 Database: {DATABASE_URL}")
    print("🌐 Server will be available at: http://localhost:8000")
    print("📖 API Documentation: http://localhost:8000/docs")
    
    uvicorn.run(
        "dev_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
