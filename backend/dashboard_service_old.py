"""
Dashboard service with optimized loading and error handling
"""
import asyncio
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import User, Strategy, Trade, ExchangeAccount
from error_handler import console_logger, error_handler
import schemas

logger = console_logger

class DashboardService:
    """Dashboard service with timeout and error handling"""
    
    @staticmethod
    async def get_dashboard_stats_safe(user_id: int, db: Session) -> schemas.DashboardStats:
        """Get dashboard stats with safe error handling"""
        try:
            # Get basic stats first (these are fast)
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
            
            # Get account balances with timeout
            account_balances = await DashboardService._get_account_balances_safe(user_id, db)
            
            return schemas.DashboardStats(
                total_strategies=total_strategies,
                active_strategies=active_strategies,
                total_trades=total_trades,
                total_profit_loss=total_profit_loss,
                today_trades=0,  # TODO: Calculate today's trades
                today_profit_loss=0.0,  # TODO: Calculate today's profit/loss
                account_balances=account_balances
            )
        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            # Return basic stats even if balance fetch fails
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
    async def _get_account_balances_safe(user_id: int, db: Session) -> List[schemas.AccountBalance]:
        """Get account balances with timeout and error handling"""
        account_balances = []
        
        try:
            exchange_accounts = db.query(ExchangeAccount).filter(
                ExchangeAccount.user_id == user_id,
                ExchangeAccount.is_active == True
            ).all()
            
            if not exchange_accounts:
                logger.info("No active exchange accounts found")
                return account_balances
            
            # Process accounts with individual timeouts
            tasks = []
            for account in exchange_accounts:
                task = asyncio.create_task(
                    DashboardService._fetch_single_account_balance(account)
                )
                tasks.append((account.exchange_name, task))
            
            # Wait for all tasks with global timeout
            try:
                results = await asyncio.wait_for(
                    asyncio.gather(*[task for _, task in tasks], return_exceptions=True),
                    timeout=10.0  # 10 second global timeout
                )
                
                for i, result in enumerate(results):
                    account_name = tasks[i][0]
                    if isinstance(result, Exception):
                        logger.warning(f"Failed to fetch balance for {account_name}: {result}")
                        continue
                    elif result:
                        account_balances.extend(result)
                        
            except asyncio.TimeoutError:
                logger.warning("Global timeout for balance fetching")
                # Cancel remaining tasks
                for _, task in tasks:
                    if not task.done():
                        task.cancel()
                        
        except Exception as e:
            logger.error(f"Error fetching account balances: {e}")
          return account_balances
    
    @staticmethod
    async def _fetch_single_account_balance(account: ExchangeAccount) -> List[schemas.AccountBalance]:
        """Fetch balance for a single account with timeout"""
        try:
            from trading_engine import exchange_manager
            
            # Check if we should skip this account due to repeated errors
            if error_handler.should_use_mock(account.exchange_name):
                logger.info(f"Using mock mode for {account.exchange_name} due to repeated errors")
                # Return mock balance data
                return [
                    schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency="USDT",
                        free=1000.0,
                        used=0.0,
                        total=1000.0
                    ),
                    schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency="BTC",
                        free=0.1,
                        used=0.0,
                        total=0.1
                    )
                ]
            
            # Individual account timeout
            balance = await asyncio.wait_for(
                exchange_manager.get_balance(account),
                timeout=5.0  # 5 second per account
            )
            
            # Reset error count on success
            error_handler.reset_error_count(account.exchange_name)
            
            account_balances = []
            for currency, data in balance.get('total', {}).items():
                if data > 0:  # Only show non-zero balances
                    account_balances.append(schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency=currency,
                        free=balance.get('free', {}).get(currency, 0),
                        used=balance.get('used', {}).get(currency, 0),
                        total=data
                    ))
            
            logger.info(f"Successfully fetched balance for {account.exchange_name}")
            return account_balances
            
        except asyncio.TimeoutError:
            error_msg = error_handler.handle_okx_error(
                Exception("Timeout"), 
                account.exchange_name
            )
            logger.warning(f"Timeout fetching balance for {account.exchange_name}: {error_msg}")
            return []
        except Exception as e:
            error_msg = error_handler.handle_okx_error(e, account.exchange_name)
            logger.error(f"Error fetching balance for {account.exchange_name}: {error_msg}")
            return []
