"""
OKX API 完整修复脚本
整合SSR代理配置和修复后的CCXT
完美解决OKX API访问问题
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, Any, Optional

# 导入我们的模块
from ssr_proxy_config import SSRProxyConfig, create_ssr_session, configure_ccxt_proxy, test_ssr_connection
from fixed_ccxt import FixedOKXExchange, create_okx_exchange

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class OKXAPIManager:
    """OKX API管理器 - 集成SSR代理和修复的CCXT"""
    
    def __init__(self, 
                 api_key: str,
                 api_secret: str, 
                 api_passphrase: str,
                 proxy_host: str = "127.0.0.1",
                 proxy_port: int = 1080,
                 is_sandbox: bool = False):
        """
        初始化OKX API管理器
        
        Args:
            api_key: OKX API密钥
            api_secret: OKX API密码
            api_passphrase: OKX API口令
            proxy_host: 代理服务器地址
            proxy_port: 代理服务器端口
            is_sandbox: 是否使用沙盒环境
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_passphrase = api_passphrase
        self.is_sandbox = is_sandbox
        
        # 初始化代理配置
        self.proxy_config = SSRProxyConfig(proxy_host, proxy_port, "socks5")
        
        # 交易所实例
        self.exchange: Optional[FixedOKXExchange] = None
        
        logger.info("🚀 OKX API管理器已初始化")
    
    def test_proxy_connection(self) -> bool:
        """测试代理连接"""
        logger.info("🔍 测试SSR代理连接...")
        return test_ssr_connection(self.proxy_config)
    
    def create_exchange(self) -> FixedOKXExchange:
        """创建配置了代理的OKX交易所实例"""
        try:
            logger.info("🔧 创建OKX交易所实例...")
            
            # API配置
            api_config = {
                'apiKey': self.api_key,
                'secret': self.api_secret,
                'passphrase': self.api_passphrase,
                'sandbox': self.is_sandbox,
                'enableRateLimit': True,
                'rateLimit': 100,
                'timeout': 30000,
                'verbose': False,
                'options': {
                    'defaultType': 'spot',
                }
            }
            
            # 设置代理环境变量
            self.proxy_config.set_environment_vars()
            
            # 创建交易所实例
            self.exchange = FixedOKXExchange(api_config)
            
            # 配置代理
            configure_ccxt_proxy(self.exchange, self.proxy_config)
            
            logger.info("✅ OKX交易所实例创建成功")
            return self.exchange
            
        except Exception as e:
            logger.error(f"❌ 创建OKX交易所实例失败: {e}")
            raise
    
    def test_public_api(self) -> bool:
        """测试公共API"""
        try:
            if not self.exchange:
                self.create_exchange()
            
            logger.info("📊 测试公共API...")
            
            # 测试获取服务器时间
            server_time = self.exchange.fetch_time()
            logger.info(f"✅ 服务器时间: {datetime.fromtimestamp(server_time/1000)}")
            
            # 测试加载市场数据
            markets = self.exchange.load_markets()
            logger.info(f"✅ 成功加载 {len(markets)} 个交易对")
            
            # 测试获取ticker
            if 'BTC/USDT' in markets:
                ticker = self.exchange.fetch_ticker('BTC/USDT')
                logger.info(f"✅ BTC/USDT 价格: {ticker['last']}")
            
            logger.info("🎉 公共API测试成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 公共API测试失败: {e}")
            return False
    
    def test_private_api(self) -> bool:
        """测试私有API"""
        try:
            if not self.exchange:
                self.create_exchange()
            
            logger.info("🔐 测试私有API...")
            
            # 测试获取账户余额
            balance = self.exchange.fetch_balance()
            logger.info("✅ 成功获取账户余额")
            
            # 安全显示余额信息
            total_balance = balance.get('total', {})
            if total_balance:
                currency_count = len([k for k, v in total_balance.items() if v and v > 0])
                logger.info(f"📊 拥有余额的货币数量: {currency_count}")
                
                # 显示主要货币（不显示具体数额）
                currencies = [k for k, v in total_balance.items() if v and v > 0][:5]
                if currencies:
                    logger.info(f"📊 主要货币: {currencies}")
            else:
                logger.info("📊 账户余额为空")
            
            logger.info("🎉 私有API测试成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 私有API测试失败: {e}")
            
            # 详细错误分析
            error_msg = str(e).lower()
            if 'password' in error_msg or 'passphrase' in error_msg:
                logger.error("   可能原因: API配置缺少passphrase参数")
            elif 'signature' in error_msg:
                logger.error("   可能原因: API签名验证失败，请检查API密钥和secret")
            elif 'permission' in error_msg or 'unauthorized' in error_msg:
                logger.error("   可能原因: API权限不足，请检查API权限设置")
            elif 'invalid' in error_msg:
                logger.error("   可能原因: API密钥无效或已过期")
            
            return False
    
    def run_full_test(self) -> bool:
        """运行完整测试"""
        logger.info("🚀 开始OKX API完整测试")
        logger.info("=" * 60)
        
        # 步骤1: 测试代理连接
        if not self.test_proxy_connection():
            logger.error("❌ 代理连接失败，请检查SSR客户端是否运行")
            return False
        
        # 步骤2: 创建交易所实例
        try:
            self.create_exchange()
        except Exception as e:
            logger.error(f"❌ 创建交易所失败: {e}")
            return False
        
        # 步骤3: 测试公共API
        public_success = self.test_public_api()
        
        # 步骤4: 测试私有API
        private_success = self.test_private_api()
        
        # 结果总结
        logger.info("\n📋 测试结果总结")
        logger.info("=" * 60)
        logger.info(f"✅ 代理连接: 成功")
        logger.info(f"✅ 公共API: {'成功' if public_success else '失败'}")
        logger.info(f"✅ 私有API: {'成功' if private_success else '失败'}")
        
        overall_success = public_success and private_success
        
        if overall_success:
            logger.info("\n🎉 OKX API完整测试成功！")
            logger.info("💡 您的系统现在可以正常访问OKX API了")
        else:
            logger.info("\n⚠️ 部分功能存在问题")
        
        return overall_success
    
    def get_exchange(self) -> Optional[FixedOKXExchange]:
        """获取交易所实例"""
        if not self.exchange:
            self.create_exchange()
        return self.exchange


def main():
    """主函数"""
    print("🚀 OKX API 完整修复测试")
    print("=" * 60)
    print(f"时间: {datetime.now()}")
    print("功能: SSR代理 + 修复CCXT + 完整API测试")
    print("=" * 60)
    
    # 您的API配置
    api_config = {
        'api_key': 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0',
        'api_secret': 'CD6A497EEB00AA2DC60B2B0974DD2485',
        'api_passphrase': 'vf5Y3UeUFiz6xfF!',
        'is_sandbox': False  # 使用真实环境，因为您的密钥是只读权限
    }
    
    # 创建API管理器
    okx_manager = OKXAPIManager(**api_config)
    
    # 运行完整测试
    success = okx_manager.run_full_test()
    
    if success:
        print("\n🎯 使用方法:")
        print("从现在开始，您可以在项目中这样使用:")
        print("```python")
        print("from okx_api_complete_fix import OKXAPIManager")
        print("manager = OKXAPIManager(api_key, api_secret, api_passphrase)")
        print("exchange = manager.get_exchange()")
        print("markets = exchange.load_markets()")
        print("balance = exchange.fetch_balance()")
        print("```")
    
    print("\n📋 测试完成")


if __name__ == "__main__":
    main()
