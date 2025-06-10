from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import asyncio
import logging
from datetime import datetime
from database import SessionLocal, Strategy
from trading_engine import strategy_engine

logger = logging.getLogger(__name__)

class StrategyScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.is_running = False
    
    async def start(self):
        """Start the strategy scheduler"""
        if not self.is_running:
            self.scheduler.start()
            self.is_running = True
            
            # Add strategy monitoring job - check every 30 seconds
            self.scheduler.add_job(
                self.monitor_strategies,
                IntervalTrigger(seconds=30),
                id="strategy_monitor",
                name="Monitor active strategies",
                replace_existing=True
            )
            
            logger.info("Strategy scheduler started")
    
    async def stop(self):
        """Stop the strategy scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Strategy scheduler stopped")
    
    async def monitor_strategies(self):
        """Monitor all active strategies and execute trades if signals are generated"""
        db = SessionLocal()
        try:
            # Get all active strategies
            active_strategies = db.query(Strategy).filter(Strategy.is_active == True).all()
            
            logger.info(f"Monitoring {len(active_strategies)} active strategies")
            
            for strategy in active_strategies:
                try:
                    # Check for trading signal
                    signal = await strategy_engine.check_strategy_signal(strategy, db)
                    
                    if signal:
                        logger.info(f"Signal detected for strategy {strategy.id}: {signal}")
                        
                        # Execute trade
                        trade = await strategy_engine.execute_trade(strategy, signal, db)
                        
                        if trade:
                            logger.info(f"Trade executed: {trade.id}")
                        else:
                            logger.error(f"Failed to execute trade for strategy {strategy.id}")
                
                except Exception as e:
                    logger.error(f"Error monitoring strategy {strategy.id}: {e}")
        
        except Exception as e:
            logger.error(f"Error in strategy monitoring: {e}")
        
        finally:
            db.close()

# Global scheduler instance
scheduler = StrategyScheduler()

# Function to start scheduler (call this from main app)
async def start_scheduler():
    await scheduler.start()

# Function to stop scheduler
async def stop_scheduler():
    await scheduler.stop()
