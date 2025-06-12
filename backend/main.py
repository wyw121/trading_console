from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
from database import create_tables
from routers import auth, exchange, strategies, trades, dashboard

# Create FastAPI app
app = FastAPI(
    title="Trading Console API",
    description="API for cryptocurrency trading strategy management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:8080"],  # Frontend URLs
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
