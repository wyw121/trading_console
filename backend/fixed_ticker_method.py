"""
修复后的 get_real_ticker 方法
"""

async def get_real_ticker(self, user_id: int, exchange_name: str, 
                         symbol: str, is_testnet: bool = False) -> Dict:
    """获取真实价格信息"""
    try:
        # 详细调试参数值
        logger.info(f"📊 get_real_ticker 调用参数:")
        logger.info(f"  user_id: {user_id} (type: {type(user_id)})")
        logger.info(f"  exchange_name: {exchange_name} (type: {type(exchange_name)})")
        logger.info(f"  symbol: {symbol} (type: {type(symbol)})")
        logger.info(f"  is_testnet: {is_testnet} (type: {type(is_testnet)})")
        
        # 安全的键生成，防止None值
        user_id_str = str(user_id) if user_id is not None else "unknown"
        exchange_name_str = str(exchange_name) if exchange_name is not None else "unknown"
        is_testnet_str = str(is_testnet) if is_testnet is not None else "False"
        
        logger.info(f"🔑 键组成部分:")
        logger.info(f"  user_id_str: {user_id_str}")
        logger.info(f"  exchange_name_str: {exchange_name_str}")
        logger.info(f"  is_testnet_str: {is_testnet_str}")
        
        key = f"{user_id_str}_{exchange_name_str}_{is_testnet_str}"
        logger.info(f"🔍 查找交易所连接: {key}")
        logger.info(f"🔍 当前存储的连接: {list(self.exchanges.keys())}")
        
        if key not in self.exchanges:
            logger.warning(f"交易所连接{key}不存在")
            return {
                "success": False,
                "message": "交易所连接不存在，请先添加交易所账户",
                "data": None
            }
        
        exchange = self.exchanges[key]
        logger.info(f"🔍 找到交易所实例: {type(exchange)}")
        logger.info(f"🔍 获取价格的交易对: {symbol}")
        
        # 确保 symbol 不为 None 或空
        if not symbol or symbol is None:
            raise ValueError("交易对符号不能为空")
        
        # 安全地调用 fetch_ticker，包装可能的内部错误
        try:
            ticker = exchange.fetch_ticker(symbol)
            
            # 验证返回的数据
            if ticker is None:
                raise ValueError("交易所返回的价格数据为空")
                
            logger.info(f"✅ 成功获取{symbol}的价格信息")
            
            return {
                "success": True,
                "message": "获取价格成功",
                "data": ticker
            }
            
        except Exception as fetch_error:
            # 捕获 CCXT 内部错误，可能包括字符串拼接错误
            logger.error(f"📛 CCXT fetch_ticker 内部错误: {str(fetch_error)}")
            logger.error(f"📛 错误类型: {type(fetch_error)}")
            
            # 如果是 TypeError 且涉及字符串拼接，给出更详细的错误信息
            if isinstance(fetch_error, TypeError) and "NoneType" in str(fetch_error):
                error_msg = f"CCXT库内部字符串拼接错误，可能是市场数据格式异常 - 交易对: {symbol}, 交易所: {exchange_name_str}"
            else:
                error_msg = f"获取价格数据失败: {str(fetch_error)}"
            
            raise ValueError(error_msg) from fetch_error
            
    except Exception as e:
        error_msg = f"获取价格时发生错误: {str(e)}"
        logger.error(error_msg)
        logger.error(f"错误类型: {type(e)}")
        logger.error(f"错误详情: {repr(e)}")
        return {
            "success": False,
            "message": error_msg,
            "data": None
        }
