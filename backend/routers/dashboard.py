from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import logging
import schemas
from database import get_db, User
from auth import verify_token
from simple_dashboard_service import SimpleDashboardService
from fast_dashboard_service import FastDashboardService
from hybrid_dashboard_service import HybridDashboardService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])
security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    username = verify_token(credentials.credentials)
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取Dashboard统计信息（混合版本）"""
    try:
        return await HybridDashboardService.get_dashboard_stats_hybrid(current_user.id, db)
    except Exception as e:
        logger.error(f"获取Dashboard统计失败: {e}")
        # 即使出错也返回基础数据
        return schemas.DashboardStats(
            total_strategies=0,
            active_strategies=0,
            total_trades=0,
            total_profit_loss=0.0,
            today_trades=0,
            today_profit_loss=0.0,
            account_balances=[]
        )

@router.get("/refresh-balances")
async def refresh_balances(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """手动刷新账户余额（异步版本）"""
    try:
        return await HybridDashboardService.refresh_balances_async(current_user.id, db)
    except Exception as e:
        logger.error(f"刷新余额失败: {e}")
        raise HTTPException(
            status_code=500,
            detail="刷新余额失败，请稍后重试"
        )