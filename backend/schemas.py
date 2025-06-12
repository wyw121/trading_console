from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User models
class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Auth models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Exchange Account models
class ExchangeAccountBase(BaseModel):
    exchange_name: str
    api_key: str
    api_secret: str
    api_passphrase: Optional[str] = None
    is_testnet: bool = False

class ExchangeAccountCreate(ExchangeAccountBase):
    pass

class ExchangeAccountResponse(BaseModel):
    id: int
    exchange_name: str
    api_key: str  # Will be masked in response
    is_testnet: bool
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Strategy models
class StrategyBase(BaseModel):
    name: str
    strategy_type: str
    symbol: str
    timeframe: str
    entry_amount: float
    leverage: float = 1.0
    stop_loss_percent: Optional[float] = None
    take_profit_percent: Optional[float] = None
    bb_period: int = 20
    bb_deviation: float = 2.0
    ma_period: int = 60

class StrategyCreate(StrategyBase):
    exchange_account_id: int

class StrategyUpdate(BaseModel):
    name: Optional[str] = None
    entry_amount: Optional[float] = None
    leverage: Optional[float] = None
    stop_loss_percent: Optional[float] = None
    take_profit_percent: Optional[float] = None
    bb_period: Optional[int] = None
    bb_deviation: Optional[float] = None
    ma_period: Optional[int] = None
    is_active: Optional[bool] = None

class StrategyResponse(StrategyBase):
    id: int
    exchange_account_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Trade models
class TradeBase(BaseModel):
    symbol: str
    side: str
    order_type: str
    amount: float
    price: Optional[float] = None

class TradeCreate(TradeBase):
    strategy_id: int

class TradeResponse(TradeBase):
    id: int
    user_id: int
    strategy_id: int
    filled_amount: float
    filled_price: Optional[float] = None
    order_id: Optional[str] = None
    status: str
    fee: float
    profit_loss: float
    created_at: datetime
    filled_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# Dashboard models
class AccountBalance(BaseModel):
    exchange: str
    currency: str
    free: float
    used: float
    total: float

class DashboardStats(BaseModel):
    total_strategies: int
    active_strategies: int
    total_trades: int
    total_profit_loss: float
    today_trades: int
    today_profit_loss: float
    account_balances: List[AccountBalance] = []

# Market Data models
class MarketDataResponse(BaseModel):
    symbol: str
    timeframe: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    
    class Config:
        from_attributes = True

# Balance models
class BalanceResponse(BaseModel):
    currency: str
    free: float
    used: float
    total: float

class ExchangeBalanceResponse(BaseModel):
    exchange: str
    balances: List[BalanceResponse]
    timestamp: datetime

class ExchangeConnectionTest(BaseModel):
    exchange: str
    api_key: str
    secret_key: str
    passphrase: Optional[str] = None
    is_testnet: bool = False
