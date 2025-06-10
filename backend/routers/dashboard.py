from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
import schemas
from database import get_db, User, Strategy, Trade, ExchangeAccount
from auth import verify_token

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
    """Get dashboard statistics"""
    # Get strategy stats
    total_strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).count()
    active_strategies = db.query(Strategy).filter(
        Strategy.user_id == current_user.id,
        Strategy.is_active == True
    ).count()
    
    # Get trade stats
    total_trades = db.query(Trade).filter(Trade.user_id == current_user.id).count()
    
    # Calculate total P&L
    total_profit_loss = db.query(func.sum(Trade.profit_loss)).filter(
        Trade.user_id == current_user.id,
        Trade.status == "filled"
    ).scalar() or 0.0
    
    # Get account balances (placeholder - in real implementation, fetch from exchanges)
    account_balances = []
    exchange_accounts = db.query(ExchangeAccount).filter(
        ExchangeAccount.user_id == current_user.id,
        ExchangeAccount.is_active == True
    ).all()
    
    for account in exchange_accounts:
        try:
            from trading_engine import exchange_manager
            balance = await exchange_manager.get_balance(account)
            
            for currency, data in balance.get('total', {}).items():
                if data > 0:  # Only show non-zero balances
                    account_balances.append(schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency=currency,
                        free=balance.get('free', {}).get(currency, 0),
                        used=balance.get('used', {}).get(currency, 0),
                        total=data
                    ))
        except Exception:
            # If we can't fetch balance, skip this account
            pass
    
    return schemas.DashboardStats(
        total_strategies=total_strategies,
        active_strategies=active_strategies,
        total_trades=total_trades,
        total_profit_loss=total_profit_loss,
        account_balances=account_balances
    )
