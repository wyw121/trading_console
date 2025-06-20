from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
import logging
import schemas
from database import get_db, User, ExchangeAccount
from auth import verify_token
from simple_real_trading_engine import real_exchange_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exchanges", tags=["exchange"])
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

@router.post("/", response_model=schemas.ExchangeAccountResponse)
async def create_exchange_account(
    account: schemas.ExchangeAccountCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new exchange account with real API verification"""
    try:
        # 首先验证真实API连接
        connection_result = real_exchange_manager.test_connection(
            exchange_name=account.exchange_name,
            api_key=account.api_key,
            api_secret=account.api_secret,
            api_passphrase=account.api_passphrase,
            is_testnet=account.is_testnet
        )
        
        if not connection_result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"API连接验证失败: {connection_result['message']}"
            )
        
        # 连接验证成功，保存到数据库
        # TODO: 在实际生产环境中需要加密API密钥
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
        
        # 将连接添加到管理器
        add_result = real_exchange_manager.add_exchange_account(
            user_id=current_user.id,
            exchange_name=account.exchange_name,
            api_key=account.api_key,
            api_secret=account.api_secret,
            api_passphrase=account.api_passphrase,
            is_testnet=account.is_testnet
        )
        
        # 在响应中隐藏敏感信息
        response = schemas.ExchangeAccountResponse.from_orm(db_account)
        response.api_key = f"{response.api_key[:8]}..." if len(response.api_key) > 8 else "***"
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"创建交易所账户失败: {str(e)}"
        )

@router.get("/", response_model=List[schemas.ExchangeAccountResponse])
async def get_exchange_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):    """Get user's exchange accounts"""
    accounts = db.query(ExchangeAccount).filter(ExchangeAccount.user_id == current_user.id).all()
    
    # 尝试恢复交易所连接（如果不存在的话）
    try:
        real_exchange_manager.restore_exchange_connections(current_user.id, accounts)
    except Exception as e:
        # 连接恢复失败不影响账户列表返回
        logger.warning(f"恢复交易所连接时出错: {str(e)}")
    
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
    """Get real account balance from exchange"""
    account = db.query(ExchangeAccount).filter(
        ExchangeAccount.id == account_id,
        ExchangeAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Exchange account not found")
    
    try:        # 使用真实API获取余额
        result = real_exchange_manager.get_real_balance(
            user_id=current_user.id,
            exchange_name=account.exchange_name,
            is_testnet=account.is_testnet
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"获取余额失败: {result['message']}"
            )
        
        return {
            "success": True,
            "message": result["message"],
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取余额时发生错误: {str(e)}")

@router.get("/accounts/{account_id}/ticker/{symbol}")
async def get_ticker(
    account_id: int,
    symbol: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get real ticker data for a symbol"""
    account = db.query(ExchangeAccount).filter(
        ExchangeAccount.id == account_id,
        ExchangeAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail="Exchange account not found")
    
    try:        # 使用真实API获取价格
        result = real_exchange_manager.get_real_ticker(
            user_id=current_user.id,
            exchange_name=account.exchange_name,
            symbol=symbol,
            is_testnet=account.is_testnet
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400,
                detail=f"获取价格失败: {result['message']}"
            )
        
        return {
            "success": True,
            "message": result["message"],
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取价格时发生错误: {str(e)}")

@router.post("/test_connection")
async def test_connection(connection_test: schemas.ExchangeConnectionTest):
    """Test exchange connection"""
    try:
        from trading_engine import exchange_manager
        result = await exchange_manager.test_connection(
            exchange=connection_test.exchange,
            api_key=connection_test.api_key,
            secret_key=connection_test.secret_key,
            passphrase=connection_test.passphrase,
            is_testnet=connection_test.is_testnet
        )
        return {"success": True, "message": "Connection successful", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Connection failed: {str(e)}")

@router.get("/supported")
async def get_supported_exchanges():
    """Get list of supported exchanges"""
    return [
        {
            "id": "okx",
            "name": "OKX",
            "description": "OKX exchange",
            "supported_features": ["spot_trading", "futures_trading", "testnet"],
            "logo": "okx_logo.png"
        },
        {
            "id": "binance",
            "name": "Binance",
            "description": "Binance exchange",
            "supported_features": ["spot_trading", "futures_trading", "testnet"],
            "logo": "binance_logo.png"
        }
    ]

@router.post("/test-connection")
async def test_real_api_connection(
    connection_data: schemas.ExchangeConnectionTest,
    current_user: User = Depends(get_current_user)
):
    """测试真实API连接 - 不使用任何模拟数据"""
    try:
        result = real_exchange_manager.test_connection(
            exchange_name=connection_data.exchange_name,
            api_key=connection_data.api_key,
            api_secret=connection_data.api_secret,
            api_passphrase=connection_data.api_passphrase,
            is_testnet=connection_data.is_testnet
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=400, 
                detail=f"API连接失败: {result['message']}"
            )
        
        return {
            "success": True,
            "message": result["message"],
            "connection_type": "real",
            "data": result["data"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"连接测试失败: {str(e)}"
        )
