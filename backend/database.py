from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://trading_user:trading_password@localhost/trading_console")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exchange_accounts = relationship("ExchangeAccount", back_populates="user")
    strategies = relationship("Strategy", back_populates="user")
    trades = relationship("Trade", back_populates="user")

class ExchangeAccount(Base):
    __tablename__ = "exchange_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange_name = Column(String(50), nullable=False)  # binance, okex, etc.
    api_key = Column(Text, nullable=False)  # encrypted
    api_secret = Column(Text, nullable=False)  # encrypted
    api_passphrase = Column(Text)  # for OKEx, encrypted
    is_testnet = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="exchange_accounts")

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    exchange_account_id = Column(Integer, ForeignKey("exchange_accounts.id"), nullable=False)
    
    name = Column(String(100), nullable=False)
    strategy_type = Column(String(50), nullable=False)  # 5m_boll_ma60, etc.
    symbol = Column(String(20), nullable=False)  # BTC/USDT, etc.
    timeframe = Column(String(10), nullable=False)  # 5m, 15m, 1h, etc.
    
    # Strategy parameters
    entry_amount = Column(Float, nullable=False)
    leverage = Column(Float, default=1.0)
    stop_loss_percent = Column(Float)
    take_profit_percent = Column(Float)
    
    # Bollinger Bands parameters
    bb_period = Column(Integer, default=20)
    bb_deviation = Column(Float, default=2.0)
    
    # Moving Average parameters
    ma_period = Column(Integer, default=60)
    
    # Status
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="strategies")
    exchange_account = relationship("ExchangeAccount")
    trades = relationship("Trade", back_populates="strategy")

class Trade(Base):
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    strategy_id = Column(Integer, ForeignKey("strategies.id"), nullable=False)
    
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    order_type = Column(String(20), nullable=False)  # market, limit
    amount = Column(Float, nullable=False)
    price = Column(Float)
    filled_amount = Column(Float, default=0.0)
    filled_price = Column(Float)
    
    order_id = Column(String(100))  # Exchange order ID
    status = Column(String(20), default="pending")  # pending, filled, cancelled, failed
    
    fee = Column(Float, default=0.0)
    profit_loss = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    filled_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    strategy = relationship("Strategy", back_populates="trades")

class MarketData(Base):
    __tablename__ = "market_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    timeframe = Column(String(10), nullable=False)
    timestamp = Column(DateTime, nullable=False)
    
    open_price = Column(Float, nullable=False)
    high_price = Column(Float, nullable=False)
    low_price = Column(Float, nullable=False)
    close_price = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

# Create tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
