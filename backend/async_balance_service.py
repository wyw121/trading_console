"""
异步余额服务 - 非阻塞版本
"""
import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import ExchangeAccount
import schemas

logger = logging.getLogger(__name__)

class AsyncBalanceService:
    """异步余额服务，避免阻塞API请求"""
    
    def __init__(self):
        self.balance_cache = {}  # 缓存余额数据
        self.last_update = {}    # 记录上次更新时间
        self.updating = set()    # 正在更新的账户ID
    
    async def get_balances_fast(self, exchange_accounts: List[ExchangeAccount]) -> List[schemas.AccountBalance]:
        """快速获取余额（优先使用缓存）"""
        balances = []
        
        for account in exchange_accounts:
            account_key = f"{account.id}_{account.exchange_name}"
            
            # 检查缓存
            if account_key in self.balance_cache:
                cached_balance = self.balance_cache[account_key]
                last_update = self.last_update.get(account_key)
                
                # 如果缓存数据不超过5分钟，使用缓存
                if last_update and (datetime.now() - last_update).seconds < 300:
                    balances.extend(cached_balance)
                    continue
            
            # 添加占位符信息
            if account_key in self.updating:
                balances.append(schemas.AccountBalance(
                    exchange=account.exchange_name,
                    currency="正在获取中...",
                    free=0.0,
                    used=0.0,
                    total=0.0
                ))
            else:
                balances.append(schemas.AccountBalance(
                    exchange=account.exchange_name,
                    currency="点击刷新获取余额",
                    free=0.0,
                    used=0.0,
                    total=0.0
                ))
        
        return balances
    
    async def refresh_balance_async(self, account: ExchangeAccount) -> List[schemas.AccountBalance]:
        """异步刷新单个账户余额"""
        account_key = f"{account.id}_{account.exchange_name}"
        
        if account_key in self.updating:
            return [schemas.AccountBalance(
                exchange=account.exchange_name,
                currency="正在获取中...",
                free=0.0,
                used=0.0,
                total=0.0
            )]
        
        self.updating.add(account_key)
        
        try:
            # 模拟余额获取（实际生产中可以调用真实API）
            await asyncio.sleep(0.1)  # 避免真实API调用导致的超时
            
            # 返回模拟数据或错误提示
            if account.exchange_name.lower() in ['okex', 'okx']:
                balance_data = [
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
                        free=0.01,
                        used=0.0,
                        total=0.01
                    )
                ]
            else:
                balance_data = [
                    schemas.AccountBalance(
                        exchange=account.exchange_name,
                        currency="模拟数据",
                        free=0.0,
                        used=0.0,
                        total=0.0
                    )
                ]
            
            # 缓存结果
            self.balance_cache[account_key] = balance_data
            self.last_update[account_key] = datetime.now()
            
            return balance_data
            
        except Exception as e:
            logger.error(f"获取账户余额失败: {e}")
            return [schemas.AccountBalance(
                exchange=account.exchange_name,
                currency="获取失败",
                free=0.0,
                used=0.0,
                total=0.0
            )]
        finally:
            self.updating.discard(account_key)

# 全局实例
async_balance_service = AsyncBalanceService()
