from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import schemas
from database import get_db, User, Strategy, ExchangeAccount
from auth import verify_token

router = APIRouter(prefix="/strategies", tags=["strategies"])
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

@router.post("", response_model=schemas.StrategyResponse)
async def create_strategy(
    strategy: schemas.StrategyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new trading strategy"""
    # Verify exchange account belongs to user
    exchange_account = db.query(ExchangeAccount).filter(
        ExchangeAccount.id == strategy.exchange_account_id,
        ExchangeAccount.user_id == current_user.id
    ).first()
    
    if not exchange_account:
        raise HTTPException(status_code=404, detail="Exchange account not found")
    
    db_strategy = Strategy(
        user_id=current_user.id,
        exchange_account_id=strategy.exchange_account_id,
        name=strategy.name,
        strategy_type=strategy.strategy_type,
        symbol=strategy.symbol,
        timeframe=strategy.timeframe,
        entry_amount=strategy.entry_amount,
        leverage=strategy.leverage,
        stop_loss_percent=strategy.stop_loss_percent,
        take_profit_percent=strategy.take_profit_percent,
        bb_period=strategy.bb_period,
        bb_deviation=strategy.bb_deviation,
        ma_period=strategy.ma_period
    )
    
    db.add(db_strategy)
    db.commit()
    db.refresh(db_strategy)
    return db_strategy

@router.get("", response_model=List[schemas.StrategyResponse])
async def get_strategies(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's trading strategies"""
    strategies = db.query(Strategy).filter(Strategy.user_id == current_user.id).all()
    return strategies

@router.get("/{strategy_id}", response_model=schemas.StrategyResponse)
async def get_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    return strategy

@router.put("/{strategy_id}", response_model=schemas.StrategyResponse)
async def update_strategy(
    strategy_id: int,
    strategy_update: schemas.StrategyUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a trading strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    update_data = strategy_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(strategy, field, value)
    
    db.commit()
    db.refresh(strategy)
    return strategy

@router.delete("/{strategy_id}")
async def delete_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a trading strategy"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    db.delete(strategy)
    db.commit()
    return {"message": "Strategy deleted successfully"}

@router.post("/{strategy_id}/toggle")
async def toggle_strategy(
    strategy_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Toggle strategy active status"""
    strategy = db.query(Strategy).filter(
        Strategy.id == strategy_id,
        Strategy.user_id == current_user.id
    ).first()
    
    if not strategy:
        raise HTTPException(status_code=404, detail="Strategy not found")
    
    strategy.is_active = not strategy.is_active
    db.commit()
    db.refresh(strategy)
    
    return {"message": f"Strategy {'activated' if strategy.is_active else 'deactivated'}", "is_active": strategy.is_active}
