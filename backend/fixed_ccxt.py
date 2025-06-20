"""
修复的CCXT OKX交易所实现
解决原始CCXT库中的解析错误问题

使用方法:
from fixed_ccxt import FixedOKXExchange
exchange = FixedOKXExchange(config)
"""

import ccxt
import os
from typing import Dict, List, Optional, Any

class FixedOKXExchange(ccxt.okx):
    """
    修复后的OKX交易所类
    主要修复了parse_market方法中的NoneType错误
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化修复后的OKX交易所
        
        Args:
            config: 交易所配置字典
        """
        super().__init__(config or {})
        
        # 自动设置代理（如果环境变量中有配置）
        self._setup_proxy()
    
    def _setup_proxy(self):
        """设置代理配置"""
        proxy_config = {}
        
        # 从环境变量获取代理配置
        http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        
        if http_proxy:
            proxy_config['http'] = http_proxy
        if https_proxy:
            proxy_config['https'] = https_proxy
        
        # 设置代理
        if proxy_config:
            if hasattr(self, 'session') and self.session:
                self.session.proxies = proxy_config
            elif hasattr(self, 'proxies'):
                self.proxies = proxy_config
            
            print(f"✅ 代理已设置: {https_proxy or http_proxy}")
    
    def parse_market(self, market: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        重写parse_market方法以修复NoneType错误
        
        Args:
            market: 原始市场数据
            
        Returns:
            解析后的市场数据，如果解析失败返回None
        """
        try:
            # 获取基础数据
            id = market.get('instId')
            base_id = market.get('baseCcy')
            quote_id = market.get('quoteCcy')
            
            # 使用safe_currency_code转换货币代码
            base = self.safe_currency_code(base_id)
            quote = self.safe_currency_code(quote_id)
            
            # 修复：确保base和quote不为None
            if not base or not quote:
                print(f"⚠️ 跳过无效交易对 {id}: base={base}, quote={quote}")
                return None
            
            # 构建交易对符号
            symbol = f"{base}/{quote}"
            
            # 获取结算货币
            settle_id = market.get('settleCcy')
            settle = self.safe_currency_code(settle_id) if settle_id else None
            
            # 获取期权类型
            option = market.get('optType')
            
            # 获取交易对类型
            type_id = market.get('instType')
            type_mappings = {
                'SPOT': 'spot',
                'FUTURES': 'future',
                'SWAP': 'swap',
                'OPTION': 'option',
            }
            type = self.safe_string(type_mappings, type_id, type_id)
            
            # 确定交易对特性
            contract = type in ['future', 'swap', 'option']
            spot = type == 'spot'
            future = type == 'future'
            swap = type == 'swap'
            option_type = type == 'option'
            
            # 获取活跃状态
            active = market.get('state') == 'live'
            
            # 合约规模
            contract_size = None
            if contract:
                contract_size = self.safe_number(market, 'ctVal')
            
            # 精度设置
            precision = {
                'amount': self.safe_number(market, 'lotSz'),
                'price': self.safe_number(market, 'tickSz'),
            }
            
            # 最小/最大限制
            min_amount = self.safe_number(market, 'minSz')
            
            limits = {
                'amount': {
                    'min': min_amount,
                    'max': None,
                },
                'price': {
                    'min': None,
                    'max': None,
                },
                'cost': {
                    'min': None,
                    'max': None,
                },
            }
            
            # 手续费
            fees = self.safe_value(self.fees, type, {})
            
            # 构建结果
            result = {
                'id': id,
                'symbol': symbol,
                'base': base,
                'quote': quote,
                'settle': settle,
                'baseId': base_id,
                'quoteId': quote_id,
                'settleId': settle_id,
                'type': type,
                'spot': spot,
                'margin': False,
                'swap': swap,
                'future': future,
                'option': option_type,
                'active': active,
                'contract': contract,
                'linear': None,
                'inverse': None,
                'taker': self.safe_number(fees, 'taker'),
                'maker': self.safe_number(fees, 'maker'),
                'contractSize': contract_size,
                'expiry': None,
                'expiryDatetime': None,
                'strike': None,
                'optionType': option,
                'precision': precision,
                'limits': limits,
                'info': market,
            }
            
            return result
            
        except Exception as e:
            print(f"❌ 解析交易对失败 {market.get('instId', 'Unknown')}: {e}")
            return None
      def parse_markets(self, markets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        重写parse_markets方法以处理None值
        
        Args:
            markets: 原始市场数据列表
            
        Returns:
            解析后的市场数据列表
        """
        if markets is None:
            print("⚠️ 市场数据为None，返回空列表")
            return []
        
        if not isinstance(markets, list):
            print(f"⚠️ 市场数据不是列表类型: {type(markets)}")
            return []
        
        result = []
        failed_count = 0
        
        for i in range(len(markets)):
            try:
                parsed_market = self.parse_market(markets[i])
                if parsed_market is not None:
                    result.append(parsed_market)
                else:
                    failed_count += 1
            except Exception as e:
                print(f"❌ 解析第{i}个交易对时出错: {e}")
                failed_count += 1
        
        if failed_count > 0:
            print(f"⚠️ {failed_count} 个交易对解析失败，成功解析 {len(result)} 个")
        
        return result
        
        return result
      def load_markets(self, reload: bool = False, params: Dict = None) -> Dict[str, Any]:
        """
        重写load_markets方法以使用修复后的解析器
        
        Args:
            reload: 是否重新加载
            params: 额外参数
            
        Returns:
            交易对字典
        """
        if not reload and self.markets:
            return self.markets
        
        try:
            print("🔄 正在加载交易对数据...")
            
            # 直接调用父类的fetch_markets方法
            markets_data = self.fetch_markets(params)
            
            if not markets_data:
                print("⚠️ 未获取到交易对数据")
                return {}
            
            # 使用我们修复的解析方法
            parsed_markets = []
            for market in markets_data:
                parsed_market = self.parse_market(market)
                if parsed_market:
                    parsed_markets.append(parsed_market)
            
            # 转换为字典格式
            markets_dict = {}
            for market in parsed_markets:
                markets_dict[market['symbol']] = market
            
            # 存储到实例变量
            self.markets = markets_dict
            self.markets_by_id = {}
            for market in parsed_markets:
                self.markets_by_id[market['id']] = market
            
            print(f"✅ 成功加载 {len(markets_dict)} 个交易对")
            return markets_dict
            
        except Exception as e:
            print(f"❌ 加载交易对失败: {e}")
            import traceback
            print(f"详细错误: {traceback.format_exc()}")
            
            # 尝试返回空字典而不是抛出异常
            return {}
    
    def fetch_ticker(self, symbol: str, params: Dict = None) -> Dict[str, Any]:
        """
        获取ticker数据（添加错误处理）
        
        Args:
            symbol: 交易对符号
            params: 额外参数
            
        Returns:
            ticker数据
        """
        try:
            return super().fetch_ticker(symbol, params)
        except Exception as e:
            print(f"❌ 获取 {symbol} ticker失败: {e}")
            raise
    
    def fetch_balance(self, params: Dict = None) -> Dict[str, Any]:
        """
        获取账户余额（添加错误处理）
        
        Args:
            params: 额外参数
            
        Returns:
            余额数据
        """
        try:
            return super().fetch_balance(params)
        except Exception as e:
            if 'password' in str(e).lower():
                raise ValueError("API配置缺少passphrase参数")
            elif 'signature' in str(e).lower():
                raise ValueError("API签名验证失败，请检查API密钥和secret")
            elif 'permission' in str(e).lower():
                raise ValueError("API权限不足，请检查API权限设置")
            else:
                print(f"❌ 获取账户余额失败: {e}")
                raise


def create_okx_exchange(config: Dict[str, Any]) -> FixedOKXExchange:
    """
    创建修复后的OKX交易所实例
    
    Args:
        config: 交易所配置
        
    Returns:
        FixedOKXExchange实例
    """
    # 确保基础配置
    default_config = {
        'sandbox': False,
        'enableRateLimit': True,
        'rateLimit': 100,
        'timeout': 30000,
        'verbose': False,
        'options': {
            'defaultType': 'spot',
        }
    }
    
    # 合并配置
    final_config = {**default_config, **config}
    
    return FixedOKXExchange(final_config)


def test_exchange_connection(exchange: FixedOKXExchange) -> bool:
    """
    测试交易所连接
    
    Args:
        exchange: 交易所实例
        
    Returns:
        连接是否成功
    """
    try:
        print("🔍 测试交易所连接...")
        
        # 测试公共API
        server_time = exchange.fetch_time()
        print(f"✅ 服务器时间: {server_time}")
        
        # 测试加载市场
        markets = exchange.load_markets()
        print(f"✅ 加载 {len(markets)} 个交易对")
        
        # 测试ticker
        if 'BTC/USDT' in markets:
            ticker = exchange.fetch_ticker('BTC/USDT')
            print(f"✅ BTC/USDT: {ticker['last']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 连接测试失败: {e}")
        return False


# 导出主要类和函数
__all__ = ['FixedOKXExchange', 'create_okx_exchange', 'test_exchange_connection']
