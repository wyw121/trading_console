"""
测试简化的交易引擎类
"""
import logging

logger = logging.getLogger(__name__)

class SimpleRealExchangeManager:
    """简化的真实交易所管理器"""
    
    def __init__(self):
        self.exchanges = {}
        logger.info("初始化简化真实交易所管理器")
    
    def test_method(self):
        return "测试成功"

# 创建全局实例
real_exchange_manager = SimpleRealExchangeManager()

if __name__ == "__main__":
    print("Direct run:", real_exchange_manager.test_method())
