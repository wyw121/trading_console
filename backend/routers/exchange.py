from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import logging
import json
import schemas
from database import get_db, User, ExchangeAccount
from auth import verify_token
from simple_real_trading_engine import real_exchange_manager
from okx_compliance_manager import okx_compliance
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/exchanges", tags=["exchange"])
security = HTTPBearer()

# 添加数据转换辅助函数
def parse_permissions(permissions_str: str) -> List[str]:
    """解析权限字符串为列表"""
    if not permissions_str:
        return []
    try:
        return json.loads(permissions_str)
    except json.JSONDecodeError:
        return []

def parse_ip_whitelist(ip_whitelist_str: str) -> List[str]:
    """解析IP白名单字符串为列表"""
    if not ip_whitelist_str:
        return []
    return [ip.strip() for ip in ip_whitelist_str.split(",") if ip.strip()]

def serialize_permissions(permissions: List[str]) -> str:
    """将权限列表序列化为JSON字符串"""
    return json.dumps(permissions) if permissions else None

def serialize_ip_whitelist(ip_list: List[str]) -> str:
    """将IP列表序列化为逗号分隔的字符串"""
    return ",".join(ip_list) if ip_list else None

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
        # 如果是OKX交易所，进行OKX合规性检查
        if account.exchange_name.lower() in ['okx', 'okex']:
            validation_result = await okx_compliance.validate_api_credentials(
                api_key=account.api_key,
                api_secret=account.api_secret,
                passphrase=account.api_passphrase,
                is_testnet=account.is_testnet
            )
            
            if not validation_result.is_valid:
                raise HTTPException(
                    status_code=400,
                    detail=f"OKX API验证失败: {validation_result.error_message}"
                )
        
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
        # 处理权限和IP白名单数据
        permissions_json = json.dumps(account.permissions) if account.permissions else None
        ip_whitelist_str = ",".join(account.ip_whitelist) if account.ip_whitelist else None
        
        # TODO: 在实际生产环境中需要加密API密钥
        db_account = ExchangeAccount(
            user_id=current_user.id,
            exchange_name=account.exchange_name,
            api_key=account.api_key,  # TODO: encrypt
            api_secret=account.api_secret,  # TODO: encrypt
            api_passphrase=account.api_passphrase,  # TODO: encrypt
            is_testnet=account.is_testnet,
            permissions=permissions_json,
            ip_whitelist=ip_whitelist_str,
            validation_status="pending"
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
          # 在响应中隐藏敏感信息并转换数据格式
        response_data = {
            "id": db_account.id,
            "exchange_name": db_account.exchange_name,
            "api_key": f"{db_account.api_key[:8]}..." if len(db_account.api_key) > 8 else "***",
            "is_testnet": db_account.is_testnet,
            "is_active": db_account.is_active,
            "created_at": db_account.created_at,
            "permissions": parse_permissions(db_account.permissions),
            "ip_whitelist": parse_ip_whitelist(db_account.ip_whitelist),
            "validation_status": db_account.validation_status,
            "validation_error": db_account.validation_error,
            "last_validation": db_account.last_validation,
            "rate_limit_remaining": db_account.rate_limit_remaining,
            "rate_limit_reset": db_account.rate_limit_reset
        }
        
        return response_data
        
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
):
    """Get user's exchange accounts"""
    accounts = db.query(ExchangeAccount).filter(ExchangeAccount.user_id == current_user.id).all()
    
    # 尝试恢复交易所连接（如果不存在的话）
    try:
        real_exchange_manager.restore_exchange_connections(current_user.id, accounts)
    except Exception as e:
        # 连接恢复失败不影响账户列表返回
        logger.warning(f"恢复交易所连接时出错: {str(e)}")
      # Mask sensitive data in response and convert data types
    masked_accounts = []
    for account in accounts:
        account_data = {
            "id": account.id,
            "exchange_name": account.exchange_name,
            "api_key": f"{account.api_key[:8]}..." if len(account.api_key) > 8 else "***",
            "is_testnet": account.is_testnet,
            "is_active": account.is_active,
            "created_at": account.created_at,
            "permissions": parse_permissions(account.permissions),
            "ip_whitelist": parse_ip_whitelist(account.ip_whitelist),
            "validation_status": account.validation_status,
            "validation_error": account.validation_error,
            "last_validation": account.last_validation,
            "rate_limit_remaining": account.rate_limit_remaining,
            "rate_limit_reset": account.rate_limit_reset
        }
        masked_accounts.append(account_data)
    
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
    
    try:
        # 使用真实API获取余额
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
    
    try:
        # 使用真实API获取价格
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

@router.post("/validate-permissions")
async def validate_exchange_permissions(
    request_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """验证交易所账户权限并更新状态"""
    try:
        account_id = request_data.get("account_id")
        if not account_id:
            raise HTTPException(status_code=400, detail="account_id is required")
        
        # 获取账户信息
        account = db.query(ExchangeAccount).filter(
            ExchangeAccount.id == account_id,
            ExchangeAccount.user_id == current_user.id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Exchange account not found")
        
        # 如果是OKX账户，进行详细验证
        if account.exchange_name.lower() in ['okx', 'okex']:
            validation_result = await okx_compliance.validate_api_credentials(
                api_key=account.api_key,
                api_secret=account.api_secret,
                passphrase=account.api_passphrase,
                is_testnet=account.is_testnet
            )
            
            # 更新验证状态
            okx_compliance.update_validation_status(db, account, validation_result)
            
            return {
                "success": validation_result.is_valid,
                "permissions": validation_result.permissions,
                "ip_address": validation_result.ip_address,
                "error_message": validation_result.error_message,
                "rate_limit_info": validation_result.rate_limit_info
            }
        else:
            # 对于其他交易所，使用基本验证
            connection_result = real_exchange_manager.test_connection(
                exchange_name=account.exchange_name,
                api_key=account.api_key,
                api_secret=account.api_secret,
                api_passphrase=account.api_passphrase,
                is_testnet=account.is_testnet
            )
            
            return {
                "success": connection_result["success"],
                "message": connection_result["message"]
            }
    
    except Exception as e:
        logger.error(f"权限验证失败: {e}")
        raise HTTPException(status_code=500, detail=f"权限验证失败: {str(e)}")

@router.get("/accounts/{account_id}/permissions")
async def get_account_permissions(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取账户权限信息"""
    try:
        account = db.query(ExchangeAccount).filter(
            ExchangeAccount.id == account_id,
            ExchangeAccount.user_id == current_user.id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Exchange account not found")
        
        permissions = []
        if account.permissions:
            try:
                permissions = json.loads(account.permissions)
            except:
                permissions = []
        
        return {
            "account_id": account_id,
            "permissions": permissions,
            "ip_whitelist": account.ip_whitelist,
            "validation_status": account.validation_status,
            "validation_error": account.validation_error,
            "last_validation": account.last_validation,
            "rate_limit_remaining": account.rate_limit_remaining,
            "rate_limit_reset": account.rate_limit_reset
        }
    
    except Exception as e:
        logger.error(f"获取权限信息失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取权限信息失败: {str(e)}")

@router.put("/accounts/{account_id}/ip-whitelist")
async def update_ip_whitelist(
    account_id: int,
    whitelist_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新IP白名单"""
    try:
        account = db.query(ExchangeAccount).filter(
            ExchangeAccount.id == account_id,
            ExchangeAccount.user_id == current_user.id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Exchange account not found")
        
        ip_list = whitelist_data.get("ip_whitelist", [])
        
        # 验证IP格式
        import ipaddress
        for ip in ip_list:
            try:
                ipaddress.ip_address(ip.strip())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"无效的IP格式: {ip}")
        
        # 更新IP白名单
        account.ip_whitelist = serialize_ip_whitelist(ip_list)
        account.updated_at = datetime.utcnow()
        
        db.commit()
        
        return {
            "success": True, 
            "ip_whitelist": ip_list,
            "message": "IP白名单更新成功"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新IP白名单失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新IP白名单失败: {str(e)}")

@router.get("/current-ip")
async def get_current_ip_global(
    current_user: User = Depends(get_current_user)
):
    """获取当前IP地址（全局端点，用于前端显示和添加到白名单）"""
    try:
        import requests
        
        # 尝试从多个服务获取IP
        ip_services = [
            "https://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "https://ipinfo.io/json"
        ]
        
        current_ip = None
        for service in ip_services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # 不同服务返回的字段名不同
                    current_ip = data.get('ip') or data.get('origin') or data.get('query')
                    if current_ip:
                        break
            except:
                continue
        
        if not current_ip:
            # 备用方法
            current_ip = await okx_compliance._get_current_ip()
        
        return {"ip": current_ip}
    
    except Exception as e:
        logger.error(f"获取当前IP失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取当前IP失败: {str(e)}")

@router.put("/accounts/{account_id}/permissions")
async def update_account_permissions(
    account_id: int,
    permissions_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新账户权限"""
    try:
        account = db.query(ExchangeAccount).filter(
            ExchangeAccount.id == account_id,
            ExchangeAccount.user_id == current_user.id
        ).first()
        
        if not account:
            raise HTTPException(status_code=404, detail="Exchange account not found")
        
        permissions = permissions_data.get("permissions", [])
        
        # 验证权限有效性
        valid_permissions = ["read", "trade", "withdraw"]
        for perm in permissions:
            if perm not in valid_permissions:
                raise HTTPException(status_code=400, detail=f"Invalid permission: {perm}")
        
        # 更新权限
        account.permissions = serialize_permissions(permissions)
        account.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(account)
        
        return {
            "success": True,
            "permissions": permissions,
            "message": "权限更新成功"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新权限失败: {e}")
        raise HTTPException(status_code=500, detail=f"更新权限失败: {str(e)}")
