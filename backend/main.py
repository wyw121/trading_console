from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from dotenv import load_dotenv
from database import create_tables
from routers import auth, exchange, strategies, trades, dashboard

# 加载环境变量（包括SSR代理配置）
load_dotenv()

# 设置代理环境变量（确保所有HTTP请求都通过SSR代理）
if os.getenv('HTTP_PROXY'):
    os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
    os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
    os.environ['http_proxy'] = os.getenv('http_proxy')
    os.environ['https_proxy'] = os.getenv('https_proxy')
    print(f"✅ 代理配置已加载: {os.getenv('HTTPS_PROXY')}")

# Create FastAPI app
app = FastAPI(
    title="Trading Console API",
    description="API for cryptocurrency trading strategy management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://localhost:8080"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(auth.router, prefix="/api")
app.include_router(exchange.router, prefix="/api")
app.include_router(strategies.router, prefix="/api")
app.include_router(trades.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Trading Console API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/health")
async def api_health_check():
    return {"status": "healthy", "api": "v1"}

# Initialize database and scheduler
@app.on_event("startup")
async def startup_event():
    create_tables()
    # Temporarily disable scheduler
    # from scheduler import start_scheduler
    # await start_scheduler()

@app.on_event("shutdown")
async def shutdown_event():
    # Temporarily disable scheduler
    # from scheduler import stop_scheduler
    # await stop_scheduler()
    pass

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
