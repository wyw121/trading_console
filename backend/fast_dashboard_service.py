"""
极简Dashboard服务 - 无阻塞版本
"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import User, Strategy, Trade, ExchangeAccount
import schemas

logger = logging.getLogger(__name__)

class FastDashboardService:
    """极简Dashboard服务，不获取实时余额"""
    
    @staticmethod
    async def get_dashboard_stats_fast(user_id: int, db: Session) -> schemas.DashboardStats:
        """快速获取Dashboard统计信息（不包含实时余额）"""
        try:
            # 快速统计查询
            total_strategies = db.query(Strategy).filter(Strategy.user_id == user_id).count()
            active_strategies = db.query(Strategy).filter(
                Strategy.user_id == user_id,
                Strategy.is_active == True
            ).count()
            
            total_trades = db.query(Trade).filter(Trade.user_id == user_id).count()
            
            total_profit_loss = db.query(func.sum(Trade.profit_loss)).filter(
                Trade.user_id == user_id,
                Trade.status == "filled"
            ).scalar() or 0.0
            
            # 获取交易所账户信息（不调用API）
            account_balances = []
            exchange_accounts = db.query(ExchangeAccount).filter(
                ExchangeAccount.user_id == user_id,
                ExchangeAccount.is_active == True
            ).all()
            
            # 为每个交易所账户添加占位信息
            for account in exchange_accounts:
                account_balances.append(schemas.AccountBalance(
                    exchange=account.exchange_name,
                    currency="点击刷新获取余额",
                    free=0.0,
                    used=0.0,
                    total=0.0
                ))
            
            return schemas.DashboardStats(
                total_strategies=total_strategies,
                active_strategies=active_strategies,
                total_trades=total_trades,
                total_profit_loss=total_profit_loss,
                today_trades=0,
                today_profit_loss=0.0,
                account_balances=account_balances
            )
            
        except Exception as e:
            logger.error(f"获取Dashboard统计失败: {e}")
            # 返回默认值
            return schemas.DashboardStats(
                total_strategies=0,
                active_strategies=0,
                total_trades=0,
                total_profit_loss=0.0,
                today_trades=0,
                today_profit_loss=0.0,
                account_balances=[]
            )
