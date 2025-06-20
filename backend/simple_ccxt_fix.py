"""
简化版OKX修复模块 - 用于Trading Console
避免复杂的继承和缩进问题
"""

import ccxt
import os
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def setup_okx_proxy():
    """设置OKX代理配置"""
    proxy_url = 'socks5h://127.0.0.1:1080'
    
    # 设置环境变量
    os.environ['HTTP_PROXY'] = proxy_url
    os.environ['HTTPS_PROXY'] = proxy_url
    os.environ['http_proxy'] = proxy_url
    os.environ['https_proxy'] = proxy_url
    
    return {
        'http': proxy_url,
        'https': proxy_url
    }

def create_okx_exchange(config: Dict[str, Any]) -> ccxt.Exchange:
    """
    创建配置了代理的OKX交易所实例
    
    Args:
        config: 交易所配置
        
    Returns:
        配置了代理的OKX交易所实例
    """
    # 设置代理
    proxy_config = setup_okx_proxy()
    
    # 创建交易所
    exchange = ccxt.okx(config)
    
    # 配置代理
    if hasattr(exchange, 'session') and exchange.session:
        exchange.session.proxies = proxy_config
    elif hasattr(exchange, 'proxies'):
        exchange.proxies = proxy_config
    
    logger.info("✅ OKX交易所实例创建完成（带代理）")
    return exchange

def test_okx_connection(exchange: ccxt.Exchange) -> Dict[str, Any]:
    """
    测试OKX连接
    
    Args:
        exchange: OKX交易所实例
        
    Returns:
        测试结果
    """
    result = {
        'success': False,
        'message': '',
        'details': {}
    }
    
    try:
        # 测试服务器时间
        server_time = exchange.fetch_time()
        result['details']['server_time'] = server_time
        
        # 测试ticker (使用简单方法)
        try:
            ticker = exchange.fetch_ticker('BTC/USDT')
            result['details']['ticker_test'] = f"BTC/USDT: {ticker.get('last', 'N/A')}"
        except Exception as e:
            result['details']['ticker_test'] = f"失败: {str(e)}"
        
        result['success'] = True
        result['message'] = 'OKX连接测试成功'
        
    except Exception as e:
        result['message'] = f'连接测试失败: {str(e)}'
        logger.error(f"❌ OKX连接测试失败: {e}")
    
    return result

# 为了保持向后兼容性，提供这些函数
FixedOKXExchange = ccxt.okx
create_okx_exchange_fixed = create_okx_exchange
test_exchange_connection = test_okx_connection
