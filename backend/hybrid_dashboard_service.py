"""
混合Dashboard服务 - 快速加载 + 异步刷新
"""
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import User, Strategy, Trade, ExchangeAccount
from async_balance_service import async_balance_service
import schemas

logger = logging.getLogger(__name__)

class HybridDashboardService:
    """混合Dashboard服务"""
    
    @staticmethod
    async def get_dashboard_stats_hybrid(user_id: int, db: Session) -> schemas.DashboardStats:
        """混合获取Dashboard统计信息"""
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
            
            # 获取交易所账户
            exchange_accounts = db.query(ExchangeAccount).filter(
                ExchangeAccount.user_id == user_id,
                ExchangeAccount.is_active == True
            ).all()
            
            # 使用异步余额服务快速获取余额
            account_balances = await async_balance_service.get_balances_fast(exchange_accounts)
            
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
            return schemas.DashboardStats(
                total_strategies=0,
                active_strategies=0,
                total_trades=0,
                total_profit_loss=0.0,
                today_trades=0,
                today_profit_loss=0.0,
                account_balances=[]
            )
    
    @staticmethod
    async def refresh_balances_async(user_id: int, db: Session) -> schemas.DashboardStats:
        """异步刷新账户余额"""
        try:
            # 基础统计
            stats = await HybridDashboardService.get_dashboard_stats_hybrid(user_id, db)
            
            # 获取交易所账户
            exchange_accounts = db.query(ExchangeAccount).filter(
                ExchangeAccount.user_id == user_id,
                ExchangeAccount.is_active == True
            ).all()
            
            # 异步刷新每个账户的余额
            all_balances = []
            for account in exchange_accounts:
                try:
                    balances = await async_balance_service.refresh_balance_async(account)
                    all_balances.extend(balances)
                except Exception as e:
                    logger.warning(f"刷新账户 {account.id} 余额失败: {e}")
                    all_balances.append(schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency="刷新失败",
                        free=0.0,
                        used=0.0,
                        total=0.0
                    ))
            
            # 更新统计数据
            stats.account_balances = all_balances
            return stats
            
        except Exception as e:
            logger.error(f"异步刷新余额失败: {e}")
            # 返回基础统计
            return await HybridDashboardService.get_dashboard_stats_hybrid(user_id, db)
