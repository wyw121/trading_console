"""
真实API连接交易引擎
只进行真实API连接，不包含任何模拟数据
连接失败时直接返回错误信息
使用简化的OKX修复
"""
import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio
import logging
import requests
from mock_okx_api import mock_exchange_manager
from database import SessionLocal, ExchangeAccount, Strategy, Trade, MarketData
from sqlalchemy.orm import Session
from proxy_config import proxy_config
from simple_ccxt_fix import create_okx_exchange, test_okx_connection, setup_okx_proxy

logger = logging.getLogger(__name__)

class RealExchangeManager:
    """真实交易所管理器 - 只进行真实API连接"""
    
    def __init__(self):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.db_session = None
        logger.info("初始化真实交易所管理器")
      def get_db_session(self) -> Session:
        """获取数据库会话"""
        if not self.db_session:
            self.db_session = SessionLocal()
        return self.db_session
    
    async def create_real_exchange(self, exchange_name: str, config: Dict) -> ccxt.Exchange:
        """创建真实交易所连接 - 使用简化的OKX修复"""
        try:
            logger.info(f"创建真实{exchange_name}交易所连接...")
            
            if exchange_name.lower() in ['okx', 'okex']:
                # 使用简化的OKX修复
                required_keys = ['apiKey', 'secret', 'passphrase']
                missing_keys = [key for key in required_keys if not config.get(key)]
                if missing_keys:
                    raise ValueError(f"OKX缺少必需的API密钥: {missing_keys}")
                
                # 创建带代理的OKX实例
                exchange = create_okx_exchange(config)
                
                # 测试连接
                connection_result = test_okx_connection(exchange)
                if not connection_result['success']:
                    raise Exception(f"OKX连接测试失败: {connection_result['message']}")
                
                logger.info("✅ OKX连接成功")
                return exchange
                
            elif exchange_name.lower() == 'binance':
                required_keys = ['apiKey', 'secret']
                missing_keys = [key for key in required_keys if not config.get(key)]
                if missing_keys:
                    raise ValueError(f"Binance缺少必需的API密钥: {missing_keys}")
                
                # 添加代理配置
                proxy_settings = proxy_config.get_ccxt_proxy_config()
                if proxy_settings:
                    config.update(proxy_settings)
                
                exchange = ccxt.binance(config)
                await self._test_exchange_connection(exchange)
                logger.info(f"成功连接{exchange_name}")
                return exchange
                
            else:
                raise ValueError(f"不支持的交易所: {exchange_name}")
                
        except Exception as e:
            error_msg = f"创建{exchange_name}真实连接失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def _test_exchange_connection(self, exchange: ccxt.Exchange) -> None:
        """测试交易所连接"""
        try:
            logger.info(f"测试交易所连接: {exchange.id}")
            
            # 先测试公共API
            try:
                if hasattr(exchange, 'fetch_time'):
                    server_time = await exchange.fetch_time()
                    logger.info(f"服务器时间: {server_time}")
            except Exception as e:
                logger.warning(f"获取服务器时间失败: {e}")
            
            # 测试市场数据
            try:
                await exchange.load_markets()
                logger.info(f"成功加载市场数据，共{len(exchange.markets)}个交易对")
            except Exception as e:
                logger.warning(f"加载市场数据失败: {e}")
                # 对于私有API，可能不需要市场数据
            
            # 测试私有API (余额)
            try:
                balance = await exchange.fetch_balance()
                logger.info(f"成功获取账户余额")
                
                # 记录非零余额
                total_balances = balance.get('total', {})
                non_zero_balances = {k: v for k, v in total_balances.items() if v > 0}
                if non_zero_balances:
                    logger.info(f"账户余额: {non_zero_balances}")
                else:
                    logger.info("账户余额为空或全部为零")
                    
            except Exception as e:
                error_msg = f"获取账户余额失败: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
            
            logger.info(f"交易所连接测试成功: {exchange.id}")
            
        except Exception as e:
            error_msg = f"交易所连接测试失败: {str(e)}"
            logger.error(error_msg)
            raise Exception(error_msg)
    
    async def add_exchange_account(self, user_id: int, exchange_name: str, 
                                 api_key: str, api_secret: str, 
                                 api_passphrase: str = None, 
                                 is_testnet: bool = False) -> Dict:
        """添加交易所账户 - 只进行真实连接测试"""
        try:
            logger.info(f"为用户{user_id}添加{exchange_name}交易所账户")
            
            # 准备配置
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': is_testnet,
                'enableRateLimit': True,
                'rateLimit': 1000,
            }
            
            if api_passphrase:
                config['passphrase'] = api_passphrase
            
            # 创建真实交易所连接并测试
            exchange = await self.create_real_exchange(exchange_name, config)
            
            # 获取账户信息
            balance = await exchange.fetch_balance()
            markets = exchange.markets
              # 保存连接到内存
            key = f"{user_id}_{exchange_name}_{is_testnet}"
            self.exchanges[key] = exchange
            
            logger.info(f"已保存{exchange_name}交易所连接: {key}")
            
            return {
                "success": True,
                "message": f"成功连接{exchange_name}交易所",
                "data": {
                    "exchange": exchange_name,
                    "testnet": is_testnet,
                    "total_balance_usd": self._calculate_total_balance_usd(balance),
                    "currencies": list(balance.get('total', {}).keys())[:10],  # 只显示前10个币种
                    "available_markets": len(markets)
                }
            }
            
        except Exception as e:
            error_msg = f"添加{exchange_name}交易所账户失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
    
    def _calculate_total_balance_usd(self, balance: Dict) -> float:
        """计算总余额USD价值（简化版本）"""
        try:
            total_balances = balance.get('total', {})
            # 简单估算，实际应该使用实时汇率
            usd_value = 0.0
            for currency, amount in total_balances.items():
                if currency == 'USDT' or currency == 'USD':
                    usd_value += amount
                elif currency == 'BTC' and amount > 0:
                    usd_value += amount * 45000  # 简化估算
                elif currency == 'ETH' and amount > 0:
                    usd_value += amount * 3000   # 简化估算
            return round(usd_value, 2)
        except:
            return 0.0
    
    async def test_connection(self, exchange_name: str, api_key: str, 
                            api_secret: str, api_passphrase: str = None, 
                            is_testnet: bool = False) -> Dict:
        """测试交易所连接 - 纯真实连接测试"""
        try:
            logger.info(f"测试{exchange_name}交易所连接 (testnet: {is_testnet})")
            
            config = {
                'apiKey': api_key,
                'secret': api_secret,
                'sandbox': is_testnet,
                'enableRateLimit': True,
                'rateLimit': 1000,
            }
            
            if api_passphrase:
                config['passphrase'] = api_passphrase
            
            # 创建并测试真实连接
            exchange = await self.create_real_exchange(exchange_name, config)
            
            # 获取基本信息
            balance = await exchange.fetch_balance()
            markets = exchange.markets
              # 获取服务器时间验证连接
            if hasattr(exchange, 'fetch_time'):
                server_time = await exchange.fetch_time()
            else:
                server_time = None
            
            # 安全地关闭连接
            if hasattr(exchange, 'close'):
                try:
                    await exchange.close()
                except:
                    pass
            
            return {
                "success": True,
                "message": f"成功连接到{exchange_name}{'测试网' if is_testnet else '主网'}",
                "data": {
                    "exchange": exchange_name,
                    "testnet": is_testnet,
                    "server_time": server_time,
                    "total_balance_usd": self._calculate_total_balance_usd(balance),
                    "available_markets": len(markets),
                    "currencies": list(balance.get('total', {}).keys())[:5]
                }
            }
            
        except Exception as e:
            error_msg = f"连接{exchange_name}失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,                "message": error_msg,
                "data": None
            }
    
    async def get_real_balance(self, user_id: int, exchange_name: str, 
                              is_testnet: bool = False) -> Dict:
        """获取真实余额信息"""
        try:
            key = f"{user_id}_{exchange_name}_{is_testnet}"
            
            # 如果连接不存在，尝试从数据库重新创建
            if key not in self.exchanges:
                logger.info(f"连接{key}不存在，尝试从数据库重新创建")
                
                # 从数据库获取账户信息
                db = self.get_db_session()
                account = db.query(ExchangeAccount).filter(
                    ExchangeAccount.user_id == user_id,
                    ExchangeAccount.exchange_name == exchange_name,
                    ExchangeAccount.is_testnet == is_testnet
                ).first()
                
                if not account:
                    return {
                        "success": False,
                        "message": "找不到交易所账户，请先添加交易所账户",
                        "data": None
                    }
                
                # 重新创建连接
                config = {
                    'apiKey': account.api_key,
                    'secret': account.api_secret,
                    'sandbox': is_testnet,
                    'enableRateLimit': True,
                    'rateLimit': 1000,
                }                
                if account.api_passphrase:
                    config['passphrase'] = account.api_passphrase
                
                exchange = await self.create_real_exchange(exchange_name, config)
                self.exchanges[key] = exchange
                logger.info(f"重新创建连接成功: {key}")
            
            exchange = self.exchanges[key]
            
            # 使用异步包装器来调用同步的ccxt方法
            import asyncio
            import concurrent.futures
            
            # 在线程池中执行同步的fetch_balance调用
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor() as executor:
                balance = await loop.run_in_executor(executor, exchange.fetch_balance)
            
            return {
                "success": True,
                "message": "成功获取余额信息",
                "data": {
                    "exchange": exchange_name,
                    "testnet": is_testnet,
                    "balances": balance.get('total', {}),
                    "free": balance.get('free', {}),
                    "used": balance.get('used', {}),
                    "total_usd": self._calculate_total_balance_usd(balance)
                }
            }
            
        except Exception as e:
            error_msg = f"获取{exchange_name}余额失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": None
            }
    
    async def get_real_ticker(self, user_id: int, exchange_name: str, 
                             symbol: str, is_testnet: bool = False) -> Dict:
        """获取真实价格信息"""
        try:
            key = f"{user_id}_{exchange_name}_{is_testnet}"
            
            if key not in self.exchanges:
                return {
                    "success": False,
                    "message": "交易所连接不存在，请先添加交易所账户",
                    "data": None
                }
            
            exchange = self.exchanges[key]
            ticker = await exchange.fetch_ticker(symbol)
            
            return {
                "success": True,
                "message": f"成功获取{symbol}价格信息",
                "data": {
                    "symbol": symbol,
                    "exchange": exchange_name,
                    "testnet": is_testnet,
                    "price": ticker.get('last'),
                    "high": ticker.get('high'),
                    "low": ticker.get('low'),
                    "volume": ticker.get('baseVolume'),
                    "timestamp": ticker.get('timestamp')
                }
            }
            
        except Exception as e:
            error_msg = f"获取{symbol}价格失败: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "message": error_msg,
                "data": None            }
    
    async def close_all_connections(self):
        """关闭所有交易所连接"""
        try:
            for key, exchange in self.exchanges.items():
                try:
                    if hasattr(exchange, 'close'):
                        await exchange.close()
                        logger.info(f"关闭连接: {key}")
                except Exception as e:
                    logger.error(f"关闭连接失败 {key}: {e}")
            
            self.exchanges.clear()
            
            if self.db_session:
                self.db_session.close()
                self.db_session = None
                
            logger.info("所有连接已关闭")
            
        except Exception as e:
            logger.error(f"关闭连接时出错: {e}")

# 全局实例
real_exchange_manager = RealExchangeManager()
