from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import schemas
from database import get_db, User, Trade, Strategy, ExchangeAccount
from auth import verify_token

router = APIRouter(prefix="/trades", tags=["trades"])
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

@router.get("", response_model=List[schemas.TradeResponse])
async def get_trades(
    strategy_id: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's trades, optionally filtered by strategy"""
    query = db.query(Trade).filter(Trade.user_id == current_user.id)
    
    if strategy_id:
        query = query.filter(Trade.strategy_id == strategy_id)
    
    trades = query.order_by(Trade.created_at.desc()).all()
    return trades

@router.get("/{trade_id}", response_model=schemas.TradeResponse)
async def get_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific trade"""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == current_user.id
    ).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    return trade

@router.post("/{trade_id}/cancel")
async def cancel_trade(
    trade_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a pending trade"""
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == current_user.id
    ).first()
    
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    if trade.status != "pending":
        raise HTTPException(status_code=400, detail="Can only cancel pending trades")
    
    # TODO: Cancel order on exchange if order_id exists
    trade.status = "cancelled"
    db.commit()
    
    return {"message": "Trade cancelled successfully"}
