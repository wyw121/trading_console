from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import schemas
from database import get_db, User, ExchangeAccount
from auth import verify_token

router = APIRouter(prefix="/exchange", tags=["exchange"])
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

@router.post("/accounts", response_model=schemas.ExchangeAccountResponse)
async def create_exchange_account(
    account: schemas.ExchangeAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new exchange account"""
    # TODO: Encrypt API keys before storing
    db_account = ExchangeAccount(
        user_id=current_user.id,
        exchange_name=account.exchange_name,
        api_key=account.api_key,  # TODO: encrypt
        api_secret=account.api_secret,  # TODO: encrypt
        api_passphrase=account.api_passphrase,  # TODO: encrypt
        is_testnet=account.is_testnet
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    # Mask sensitive data in response
    response = schemas.ExchangeAccountResponse.from_orm(db_account)
    response.api_key = f"{response.api_key[:8]}..." if len(response.api_key) > 8 else "***"
    return response

@router.get("/accounts", response_model=List[schemas.ExchangeAccountResponse])
async def get_exchange_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's exchange accounts"""
    accounts = db.query(ExchangeAccount).filter(ExchangeAccount.user_id == current_user.id).all()
    
    # Mask sensitive data in response
    masked_accounts = []
    for account in accounts:
        response = schemas.ExchangeAccountResponse.from_orm(account)
        response.api_key = f"{response.api_key[:8]}..." if len(response.api_key) > 8 else "***"
        masked_accounts.append(response)
    
    return masked_accounts

@router.delete("/accounts/{account_id}")
async def delete_exchange_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete an exchange account"""
    account = db.query(ExchangeAccount).filter(
        ExchangeAccount.id == account_id,
        ExchangeAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Exchange account not found")
    
    db.delete(account)
    db.commit()
    return {"message": "Exchange account deleted successfully"}

@router.get("/accounts/{account_id}/balance")
async def get_account_balance(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get account balance from exchange"""
    account = db.query(ExchangeAccount).filter(
        ExchangeAccount.id == account_id,
        ExchangeAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Exchange account not found")
    
    try:
        from trading_engine import exchange_manager
        balance = await exchange_manager.get_balance(account)
        return balance
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching balance: {str(e)}")

@router.get("/accounts/{account_id}/ticker/{symbol}")
async def get_ticker(
    account_id: int,
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get ticker data for a symbol"""
    account = db.query(ExchangeAccount).filter(
        ExchangeAccount.id == account_id,
        ExchangeAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Exchange account not found")
    
    try:
        from trading_engine import exchange_manager
        ticker = await exchange_manager.get_ticker(account, symbol)
        return ticker
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error fetching ticker: {str(e)}")
