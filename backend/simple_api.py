"""
最简单的FastAPI服务器
用于快速启动测试
"""
from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from pydantic import BaseModel
from typing import Dict, Optional, List
import asyncio
from real_okx_connection import real_okx_connection
from auth import verify_password, get_password_hash, create_access_token, verify_token
import sqlite3
import os
from datetime import timedelta

# 创建FastAPI应用
app = FastAPI(title="Trading Console API")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加HTTP Bearer认证
security = HTTPBearer()

# 数据库文件路径
DB_FILE = "trading_console_simple.db"

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # 创建用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 创建默认测试用户
    test_password_hash = get_password_hash("123456")
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, email, password_hash)
        VALUES (?, ?, ?)
    ''', ("testuser", "test@example.com", test_password_hash))
    
    conn.commit()
    conn.close()

# 初始化数据库
init_db()

# 定义请求模型
class APICredentials(BaseModel):
    api_key: str
    secret: str
    passphrase: str
    is_testnet: bool = False

class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class User(BaseModel):
    id: int
    username: str
    email: str

def get_user_by_username(username: str):
    """根据用户名获取用户"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "id": result[0],
            "username": result[1],
            "email": result[2],
            "password_hash": result[3]
        }
    return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """获取当前用户"""
    username = verify_token(credentials.credentials)
    if not username:
        raise HTTPException(status_code=401, detail="无效的令牌")
    
    user = get_user_by_username(username)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return user

@app.get("/")
async def root():
    """API 根路径"""
    return {"message": "交易控制台API正在运行"}

@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """用户登录"""
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/register")
async def register(user_data: UserRegister):
    """用户注册"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (user_data.username,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="用户名已存在")
        
        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM users WHERE email = ?", (user_data.email,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="邮箱已存在")
        
        # 创建新用户
        password_hash = get_password_hash(user_data.password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (user_data.username, user_data.email, password_hash))
        
        conn.commit()
        return {"message": "注册成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")
    finally:
        conn.close()

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """获取当前用户信息"""
    return {
        "id": current_user["id"],
        "username": current_user["username"],
        "email": current_user["email"]
    }

@app.get("/exchanges")
async def get_exchanges():
    """获取支持的交易所列表"""
    return [
        {"id": "okx", "name": "OKX", "logo": "okx_logo.png", "status": "active"},
        {"id": "binance", "name": "Binance", "logo": "binance_logo.png", "status": "coming_soon"},
    ]

@app.get("/dashboard")
async def get_dashboard():
    """获取仪表板数据"""
    return {
        "total_balance": 1500.0,
        "today_trades": 5,
        "today_profit_loss": 25.50,
        "active_strategies": 2
    }

@app.post("/test_connection")
async def test_connection(credentials: APICredentials):
    """
    测试真实 OKX API 连接 - 无模拟回退
    测试交易所API连接并返回结果
    """
    try:
        # 调用真实连接测试，不使用模拟
        success, message, data = await real_okx_connection.test_real_connection(
            credentials.api_key,
            credentials.secret,
            credentials.passphrase,
            credentials.is_testnet
        )
        
        if not success:
            # 如果连接失败，直接返回失败信息
            raise HTTPException(status_code=400, detail=message)
            
        # 连接成功，返回详细信息
        return {
            "success": True,
            "message": message,
            "connection_type": "real",  # 只返回真实连接类型
            "data": data
        }
        
    except Exception as e:
        # 捕获所有异常，返回错误信息
        raise HTTPException(status_code=400, detail=f"API连接测试失败: {str(e)}")

@app.post("/register")
async def register(user: UserRegister):
    """用户注册"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # 检查用户是否已存在
        existing_user = get_user_by_username(user.username)
        if existing_user:
            raise HTTPException(status_code=400, detail="用户名已被占用")
        
        # 插入新用户
        password_hash = get_password_hash(user.password)
        cursor.execute('''
            INSERT INTO users (username, email, password_hash)
            VALUES (?, ?, ?)
        ''', (user.username, user.email, password_hash))
        
        conn.commit()
        conn.close()
        
        return {"message": "注册成功"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"注册失败: {str(e)}")

@app.post("/login")
async def login(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """用户登录"""
    try:
        user = get_user_by_username(credentials.username)
        if not user or not verify_password(credentials.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="用户名或密码错误")
        
        # 生成访问令牌
        access_token = create_access_token(user["username"])
        
        return {"access_token": access_token, "token_type": "bearer"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user

if __name__ == "__main__":
    print("🚀 启动简化版交易控制台API...")
    print("地址: http://localhost:8000")
    print("文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
