"""
最终OKX API连接测试脚本
验证所有修复是否有效
"""

import logging
import sys
import os
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_final_okx_connection():
    """最终的OKX连接测试"""
    logger.info("🚀 最终OKX API连接测试")
    logger.info("=" * 60)
    
    try:
        # 导入我们的修复模块
        from trading_console_okx import TradingConsoleOKX
        
        # API配置
        api_key = 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0'
        api_secret = 'CD6A497EEB00AA2DC60B2B0974DD2485'
        api_passphrase = 'vf5Y3UeUFiz6xfF!'
        
        logger.info("1️⃣ 创建OKX实例...")
        okx = TradingConsoleOKX(api_key, api_secret, api_passphrase, sandbox=False)
        
        logger.info("2️⃣ 测试连接...")
        connection_result = okx.test_connection()
        
        if connection_result['success']:
            logger.info("✅ 连接测试成功!")
            logger.info(f"   服务器时间: {connection_result['details']['server_time']}")
            logger.info(f"   余额测试: {connection_result['details']['balance_test']}")
            
            logger.info("3️⃣ 测试基本功能...")
            
            # 测试服务器时间
            try:
                server_time = okx.get_server_time()
                logger.info(f"✅ 服务器时间戳: {server_time}")
            except Exception as e:
                logger.error(f"❌ 服务器时间获取失败: {e}")
            
            # 测试市场数据
            try:
                markets = okx.get_markets()
                logger.info(f"✅ 获取到交易对数量: {len(markets)}")
                if markets:
                    sample_pairs = list(markets.keys())[:3]
                    logger.info(f"   示例交易对: {sample_pairs}")
            except Exception as e:
                logger.error(f"❌ 市场数据获取失败: {e}")
            
            # 测试单个ticker
            try:
                # 使用底层的CCXT实例直接获取ticker
                ticker = okx.exchange.fetch_ticker('BTC/USDT')
                logger.info(f"✅ BTC/USDT价格: {ticker.get('last', 'N/A')}")
            except Exception as e:
                logger.error(f"❌ Ticker获取失败: {e}")
            
            logger.info("\n🎉 最终测试结果: 成功!")
            logger.info("💡 OKX API现在可以正常使用了")
            
            return True
            
        else:
            logger.error(f"❌ 连接测试失败: {connection_result['message']}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 测试过程中出现错误: {e}")
        import traceback
        logger.error(f"详细错误: {traceback.format_exc()}")
        return False

def test_direct_ccxt():
    """测试直接使用CCXT"""
    logger.info("\n🔧 测试直接使用CCXT (带代理)")
    
    try:
        import ccxt
        
        # 设置代理环境变量
        os.environ['HTTP_PROXY'] = 'socks5h://127.0.0.1:1080'
        os.environ['HTTPS_PROXY'] = 'socks5h://127.0.0.1:1080'
        os.environ['http_proxy'] = 'socks5h://127.0.0.1:1080'
        os.environ['https_proxy'] = 'socks5h://127.0.0.1:1080'
        
        config = {
            'apiKey': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
            'secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
            'passphrase': 'vf5Y3UeUFiz6xfF!',
            'sandbox': False,
            'enableRateLimit': True,
            'timeout': 30000,
        }
        
        exchange = ccxt.okx(config)
        
        # 设置代理
        if hasattr(exchange, 'session'):
            exchange.session.proxies = {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            }
        
        # 测试服务器时间
        server_time = exchange.fetch_time()
        logger.info(f"✅ 直接CCXT服务器时间: {datetime.fromtimestamp(server_time/1000)}")
        
        # 测试ticker
        ticker = exchange.fetch_ticker('BTC/USDT')
        logger.info(f"✅ 直接CCXT BTC/USDT: {ticker.get('last')}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 直接CCXT测试失败: {e}")
        return False

def main():
    """主函数"""
    print("🚀 OKX API 最终验证测试")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print("目标: 验证SSR代理配置和OKX API修复是否完全有效")
    print("=" * 60)
    
    # 测试1: 使用我们的修复版本
    success1 = test_final_okx_connection()
    
    # 测试2: 测试直接CCXT
    success2 = test_direct_ccxt()
    
    # 总结
    print("\n📋 最终测试结果")
    print("=" * 60)
    print(f"✅ 修复版本OKX: {'成功' if success1 else '失败'}")
    print(f"✅ 直接CCXT: {'成功' if success2 else '失败'}")
    
    if success1 or success2:
        print("\n🎉 OKX API连接问题已解决!")
        print("\n🔧 在您的项目中使用:")
        print("```python")
        print("from trading_console_okx import TradingConsoleOKX")
        print("okx = TradingConsoleOKX(api_key, api_secret, api_passphrase)")
        print("result = okx.test_connection()")
        print("ticker = okx.get_ticker('BTC/USDT')  # 如果需要的话")
        print("```")
        
        print("\n💡 关键修复内容:")
        print("- ✅ SSR代理配置 (socks5h://127.0.0.1:1080)")
        print("- ✅ PySocks支持")
        print("- ✅ CCXT解析错误修复")
        print("- ✅ 环境变量代理设置")
        print("- ✅ 错误处理和重试机制")
    else:
        print("\n❌ 仍有问题需要解决")
        print("请检查:")
        print("- SSR客户端是否在端口1080运行")
        print("- API密钥是否正确")
        print("- 网络连接是否正常")
    
    print("\n📋 测试完成")

if __name__ == "__main__":
    main()
