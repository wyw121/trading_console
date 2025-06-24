"""
简化的Dashboard服务 - 真实余额版本
"""
import asyncio
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import User, Strategy, Trade, ExchangeAccount
from trading_engine import exchange_manager
import schemas

logger = logging.getLogger(__name__)

class SimpleDashboardService:
    """简化的Dashboard服务，支持真实余额"""
    
    @staticmethod
    async def get_dashboard_stats_safe(user_id: int, db: Session) -> schemas.DashboardStats:
        """获取Dashboard统计信息"""
        try:
            # 获取基础统计（快速查询）
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
            
            # 获取真实余额
            account_balances = []
            
            exchange_accounts = db.query(ExchangeAccount).filter(
                ExchangeAccount.user_id == user_id,
                ExchangeAccount.is_active == True
            ).all()
            
            for account in exchange_accounts:
                try:
                    logger.info(f"Fetching balance for {account.exchange_name}")
                    
                    # 使用5秒超时获取余额
                    balance = await asyncio.wait_for(
                        exchange_manager.get_balance(account),
                        timeout=5.0
                    )
                    
                    # 转换余额格式
                    total_balances = balance.get('total', {})
                    for currency, amount in total_balances.items():
                        if amount > 0.001:  # 只显示有意义余额的币种
                            free_amount = balance.get('free', {}).get(currency, 0)
                            used_amount = balance.get('used', {}).get(currency, 0)
                            
                            account_balances.append(schemas.AccountBalance(
                                exchange=account.exchange_name,
                                currency=currency,
                                free=float(free_amount),
                                used=float(used_amount),
                                total=float(amount)
                            ))
                            
                except asyncio.TimeoutError:
                    logger.warning(f"Timeout fetching balance for {account.exchange_name}")
                    # 添加提示信息
                    account_balances.append(schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency="请求超时",                        free=0.0,
                        used=0.0,
                        total=0.0
                    ))
                    
                except Exception as e:
                    logger.warning(f"Error fetching balance for {account.exchange_name}: {e}")
                    # 添加错误提示
                    account_balances.append(schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency="获取失败",
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
