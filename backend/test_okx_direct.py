#!/usr/bin/env python3
"""
Direct OKX API test to diagnose connection issues
"""
import ccxt
import asyncio
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_okx_connection():
    """Test OKX connection directly"""
    
    # 你的API配置
    config = {
        'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'passphrase': 'vf5Y3UeUFiz6xfF!',
        'sandbox': False,  # 主网
        'enableRateLimit': True,
        'timeout': 30000,
        'options': {
            'defaultType': 'spot',
        }
    }
    
    try:
        # 创建交易所实例
        logger.info("Creating OKX exchange instance...")
        exchange = ccxt.okex(config)
        
        # 1. 测试公共API - 获取交易对信息
        logger.info("Testing public API - markets...")
        markets = await exchange.load_markets()
        logger.info(f"Loaded {len(markets)} markets")
        
        # 2. 测试公共API - 获取ticker
        logger.info("Testing public API - ticker...")
        ticker = await exchange.fetch_ticker('BTC/USDT')
        logger.info(f"BTC/USDT ticker: {ticker['last']}")
        
        # 3. 测试私有API - 获取余额
        logger.info("Testing private API - balance...")
        balance = await exchange.fetch_balance()
        logger.info(f"Balance keys: {list(balance.keys())}")
        
        # 4. 测试账户信息
        logger.info("Testing account info...")
        if hasattr(exchange, 'fetch_account'):
            account = await exchange.fetch_account()
            logger.info(f"Account info: {account}")
        
        logger.info("✅ All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        logger.error(f"Error type: {type(e)}")
        
        # 详细错误信息
        if hasattr(e, 'response'):
            logger.error(f"Response: {e.response}")
        
        return False
    
    finally:
        if 'exchange' in locals():
            await exchange.close()
    
    return True

if __name__ == "__main__":
    asyncio.run(test_okx_connection())
