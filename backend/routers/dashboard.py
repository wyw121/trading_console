from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import schemas
from database import get_db, User
from auth import verify_token
from simple_dashboard_service import SimpleDashboardService

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
    """获取Dashboard统计信息（简化版本）"""
    try:
        return await SimpleDashboardService.get_dashboard_stats_safe(current_user.id, db)
    except Exception as e:
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