"""
OKX Python SDK 简化示例
基于 python-okx 库的实践案例
GitHub: https://github.com/okxapi/python-okx
PyPI: https://pypi.org/project/python-okx/
"""

import okx.Account as Account
import okx.Trade as Trade
import okx.MarketData as MarketData
import okx.PublicData as PublicData
import asyncio
import json
from datetime import datetime

class OKXTradingBot:
    """基于OKX Python SDK的交易机器人"""
    
    def __init__(self, api_key: str, secret_key: str, passphrase: str, is_demo: bool = True):
        """
        初始化OKX交易机器人
        
        Args:
            api_key: API密钥
            secret_key: 密钥
            passphrase: API密码短语
            is_demo: 是否使用模拟交易环境 (True=模拟, False=实盘)
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.flag = "1" if is_demo else "0"  # 1: 模拟交易, 0: 实盘交易
        
        # 初始化各个API模块
        self.account_api = Account.AccountAPI(api_key, secret_key, passphrase, False, self.flag)
        self.trade_api = Trade.TradeAPI(api_key, secret_key, passphrase, False, self.flag)
        self.market_api = MarketData.MarketAPI(flag=self.flag)
        self.public_api = PublicData.PublicAPI(flag=self.flag)
        
        print(f"🚀 OKX交易机器人初始化完成 ({'模拟交易' if is_demo else '实盘交易'})")
    
    def get_system_status(self):
        """获取系统状态"""
        try:
            result = self.public_api.get_system_status()
            print("📊 系统状态:")
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return result
        except Exception as e:
            print(f"❌ 获取系统状态失败: {e}")
            return None
    
    def get_account_config(self):
        """获取账户配置"""
        try:
            result = self.account_api.get_account_config()
            if result['code'] == '0':
                data = result['data'][0]
                acct_lv = data['acctLv']
                pos_mode = data['posMode']
                
                # 账户模式映射
                acct_modes = {
                    '1': '简单模式',
                    '2': '单币种保证金模式', 
                    '3': '跨币种保证金模式',
                    '4': '组合保证金模式'
                }
                
                print("⚙️ 账户配置:")
                print(f"  账户模式: {acct_modes.get(acct_lv, acct_lv)}")
                print(f"  持仓模式: {'双向持仓' if pos_mode == 'long_short_mode' else '净头寸'}")
                print(f"  原始数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
            return result
        except Exception as e:
            print(f"❌ 获取账户配置失败: {e}")
            return None
    
    def get_account_balance(self, currency=None):
        """获取账户余额"""
        try:
            params = {}
            if currency:
                params['ccy'] = currency
                
            result = self.account_api.get_account_balance(**params)
            if result['code'] == '0':
                print("💰 账户余额:")
                for account in result['data']:
                    print(f"  总权益: {account['totalEq']} USD")
                    print("  各币种余额:")
                    for detail in account['details']:
                        if float(detail['eq']) > 0:  # 只显示有余额的币种
                            print(f"    {detail['ccy']}: {detail['eq']} (可用: {detail['availEq']})")
                            
            return result
        except Exception as e:
            print(f"❌ 获取账户余额失败: {e}")
            return None
    
    def get_trading_pairs(self, inst_type="SPOT"):
        """获取交易对信息"""
        try:
            result = self.public_api.get_instruments(instType=inst_type)
            if result['code'] == '0':
                instruments = result['data']
                print(f"📈 {inst_type} 交易对信息:")
                print(f"  总数量: {len(instruments)}")
                
                # 显示前5个交易对的详细信息
                print("  示例交易对:")
                for inst in instruments[:5]:
                    print(f"    {inst['instId']}: 最小下单量={inst['minSz']}, 价格精度={inst['tickSz']}")
                    
                return instruments
            else:
                print(f"❌ 获取交易对失败: {result['msg']}")
                return []
        except Exception as e:
            print(f"❌ 获取交易对失败: {e}")
            return []
    
    def get_ticker(self, symbol="BTC-USDT"):
        """获取行情数据"""
        try:
            result = self.market_api.get_ticker(instId=symbol)
            if result['code'] == '0':
                ticker = result['data'][0]
                print(f"📊 {symbol} 行情:")
                print(f"  最新价: {ticker['last']}")
                print(f"  24h涨跌: {ticker['sodUtc8']} ({float(ticker['sodUtc8'])*100:.2f}%)")
                print(f"  24h最高: {ticker['high24h']}")
                print(f"  24h最低: {ticker['low24h']}")
                print(f"  24h成交量: {ticker['vol24h']}")
                return ticker
            else:
                print(f"❌ 获取行情失败: {result['msg']}")
                return None
        except Exception as e:
            print(f"❌ 获取行情失败: {e}")
            return None
    
    def get_orderbook(self, symbol="BTC-USDT", depth=5):
        """获取订单簿"""
        try:
            result = self.market_api.get_orderbook(instId=symbol, sz=str(depth))
            if result['code'] == '0':
                data = result['data'][0]
                print(f"📋 {symbol} 订单簿 (深度: {depth}):")
                
                print("  卖单 (Ask):")
                for ask in reversed(data['asks'][:depth]):
                    print(f"    价格: {ask[0]}, 数量: {ask[1]}")
                
                print("  买单 (Bid):")
                for bid in data['bids'][:depth]:
                    print(f"    价格: {bid[0]}, 数量: {bid[1]}")
                
                return data
            else:
                print(f"❌ 获取订单簿失败: {result['msg']}")
                return None
        except Exception as e:
            print(f"❌ 获取订单簿失败: {e}")
            return None
    
    def place_limit_order(self, symbol, side, amount, price):
        """下限价单"""
        try:
            result = self.trade_api.place_order(
                instId=symbol,
                tdMode="cash",  # 现货交易模式
                side=side,
                ordType="limit",
                px=str(price),
                sz=str(amount),
                clOrdId=f"limit_{int(datetime.now().timestamp())}"
            )
            
            if result['code'] == '0':
                order_data = result['data'][0]
                if order_data['sCode'] == '0':
                    print(f"✅ 限价单下单成功:")
                    print(f"  订单ID: {order_data['ordId']}")
                    print(f"  客户端订单ID: {order_data['clOrdId']}")
                    print(f"  交易对: {symbol}")
                    print(f"  方向: {side}")
                    print(f"  价格: {price}")
                    print(f"  数量: {amount}")
                    return order_data
                else:
                    print(f"❌ 下单失败: {order_data['sMsg']}")
                    return None
            else:
                print(f"❌ 下单请求失败: {result['msg']}")
                return None
                
        except Exception as e:
            print(f"❌ 下单异常: {e}")
            return None
    
    def place_market_order(self, symbol, side, amount, target_currency="base_ccy"):
        """下市价单"""
        try:
            result = self.trade_api.place_order(
                instId=symbol,
                tdMode="cash",
                side=side,
                ordType="market",
                sz=str(amount),
                tgtCcy=target_currency,  # base_ccy: 以基础货币计价, quote_ccy: 以计价货币计价
                clOrdId=f"market_{int(datetime.now().timestamp())}"
            )
            
            if result['code'] == '0':
                order_data = result['data'][0]
                if order_data['sCode'] == '0':
                    print(f"✅ 市价单下单成功:")
                    print(f"  订单ID: {order_data['ordId']}")
                    print(f"  交易对: {symbol}")
                    print(f"  方向: {side}")
                    print(f"  数量: {amount}")
                    print(f"  计价方式: {target_currency}")
                    return order_data
                else:
                    print(f"❌ 下单失败: {order_data['sMsg']}")
                    return None
            else:
                print(f"❌ 下单请求失败: {result['msg']}")
                return None
                
        except Exception as e:
            print(f"❌ 下单异常: {e}")
            return None
    
    def get_order_info(self, symbol, order_id=None, client_order_id=None):
        """获取订单信息"""
        try:
            params = {'instId': symbol}
            if order_id:
                params['ordId'] = order_id
            elif client_order_id:
                params['clOrdId'] = client_order_id
            else:
                print("❌ 必须提供订单ID或客户端订单ID")
                return None
                
            result = self.trade_api.get_order(**params)
            if result['code'] == '0' and result['data']:
                order = result['data'][0]
                print(f"📋 订单信息:")
                print(f"  订单ID: {order['ordId']}")
                print(f"  交易对: {order['instId']}")
                print(f"  状态: {order['state']}")
                print(f"  方向: {order['side']}")
                print(f"  类型: {order['ordType']}")
                print(f"  价格: {order['px']}")
                print(f"  数量: {order['sz']}")
                print(f"  已成交: {order['accFillSz']}")
                print(f"  平均成交价: {order['avgPx']}")
                print(f"  手续费: {order['fee']} {order['feeCcy']}")
                return order
            else:
                print(f"❌ 获取订单信息失败: {result.get('msg', '订单不存在')}")
                return None
                
        except Exception as e:
            print(f"❌ 获取订单信息异常: {e}")
            return None
    
    def cancel_order(self, symbol, order_id=None, client_order_id=None):
        """撤销订单"""
        try:
            params = {'instId': symbol}
            if order_id:
                params['ordId'] = order_id
            elif client_order_id:
                params['clOrdId'] = client_order_id
            else:
                print("❌ 必须提供订单ID或客户端订单ID")
                return None
                
            result = self.trade_api.cancel_order(**params)
            if result['code'] == '0':
                cancel_data = result['data'][0]
                if cancel_data['sCode'] == '0':
                    print(f"✅ 订单撤销成功:")
                    print(f"  订单ID: {cancel_data['ordId']}")
                    return cancel_data
                else:
                    print(f"❌ 撤销失败: {cancel_data['sMsg']}")
                    return None
            else:
                print(f"❌ 撤销请求失败: {result['msg']}")
                return None
                
        except Exception as e:
            print(f"❌ 撤销订单异常: {e}")
            return None
    
    def get_pending_orders(self, symbol=None):
        """获取当前委托"""
        try:
            params = {}
            if symbol:
                params['instId'] = symbol
                
            result = self.trade_api.get_order_list(**params)
            if result['code'] == '0':
                orders = result['data']
                print(f"📋 当前委托 ({len(orders)} 个):")
                for order in orders:
                    print(f"  {order['ordId']}: {order['instId']} {order['side']} {order['sz']} @ {order['px']} [{order['state']}]")
                return orders
            else:
                print(f"❌ 获取委托失败: {result['msg']}")
                return []
                
        except Exception as e:
            print(f"❌ 获取委托异常: {e}")
            return []
    
    def get_order_history(self, symbol=None, limit=10):
        """获取历史订单"""
        try:
            params = {
                'instType': 'SPOT',
                'limit': str(limit)
            }
            if symbol:
                params['instId'] = symbol
                
            result = self.trade_api.get_orders_history(**params)
            if result['code'] == '0':
                orders = result['data']
                print(f"📜 历史订单 ({len(orders)} 个):")
                for order in orders[:5]:  # 只显示前5个
                    status_emoji = "✅" if order['state'] == 'filled' else "❌" if order['state'] == 'canceled' else "⏳"
                    print(f"  {status_emoji} {order['instId']} {order['side']} {order['sz']} @ {order['avgPx']} [{order['state']}]")
                return orders
            else:
                print(f"❌ 获取历史订单失败: {result['msg']}")
                return []
                
        except Exception as e:
            print(f"❌ 获取历史订单异常: {e}")
            return []

def demo_trading_session():
    """完整的交易演示会话"""
    print("🎯 开始OKX API演示会话")
    print("=" * 50)
    
    # 配置API密钥 (请替换为您的真实API密钥)
    API_KEY = "your_api_key_here"
    SECRET_KEY = "your_secret_key_here"
    PASSPHRASE = "your_passphrase_here"
    IS_DEMO = True  # 使用模拟交易环境
    
    # 初始化交易机器人
    bot = OKXTradingBot(API_KEY, SECRET_KEY, PASSPHRASE, IS_DEMO)
    
    try:
        # 1. 系统检查
        print("\n1️⃣ 系统状态检查")
        bot.get_system_status()
        
        # 2. 账户信息
        print("\n2️⃣ 账户信息查询")
        bot.get_account_config()
        bot.get_account_balance()
        
        # 3. 市场数据
        print("\n3️⃣ 市场数据获取")
        instruments = bot.get_trading_pairs("SPOT")
        bot.get_ticker("BTC-USDT")
        bot.get_orderbook("BTC-USDT", 3)
        
        # 4. 交易操作演示 (仅在有足够余额时)
        print("\n4️⃣ 交易操作演示")
        
        # 获取当前BTC价格
        ticker = bot.get_ticker("BTC-USDT")
        if ticker:
            current_price = float(ticker['last'])
            
            # 下一个低于市价的限价买单
            buy_price = current_price * 0.95  # 低于市价5%
            buy_amount = 0.001  # 购买0.001 BTC
            
            print(f"\n尝试下限价买单: {buy_amount} BTC @ ${buy_price:.2f}")
            order = bot.place_limit_order("BTC-USDT", "buy", buy_amount, buy_price)
            
            if order:
                order_id = order['ordId']
                
                # 查询订单状态
                print(f"\n查询订单状态:")
                bot.get_order_info("BTC-USDT", order_id)
                
                # 撤销订单
                print(f"\n撤销订单:")
                bot.cancel_order("BTC-USDT", order_id)
        
        # 5. 订单历史
        print("\n5️⃣ 订单历史查询")
        bot.get_pending_orders("BTC-USDT")
        bot.get_order_history("BTC-USDT", 5)
        
    except Exception as e:
        print(f"❌ 演示过程中出现错误: {e}")
    
    print("\n🎯 演示会话结束")
    print("=" * 50)

def simple_trading_example():
    """简单交易示例"""
    # API配置
    config = {
        'api_key': 'your_api_key',
        'secret_key': 'your_secret_key', 
        'passphrase': 'your_passphrase',
        'is_demo': True
    }
    
    bot = OKXTradingBot(**config)
    
    # 1. 检查账户
    balance = bot.get_account_balance()
    
    # 2. 获取市场价格
    ticker = bot.get_ticker("BTC-USDT")
    
    # 3. 下单交易
    if ticker:
        current_price = float(ticker['last'])
        
        # 限价买入
        order = bot.place_limit_order(
            symbol="BTC-USDT",
            side="buy", 
            amount=0.001,
            price=current_price * 0.98  # 低于市价2%
        )
        
        if order:
            # 监控订单
            order_info = bot.get_order_info("BTC-USDT", order['ordId'])

if __name__ == "__main__":
    # 运行完整演示
    demo_trading_session()
    
    print("\n" + "="*50)
    print("💡 使用说明:")
    print("1. 请先在OKX官网申请API密钥")
    print("2. 替换代码中的API密钥配置")
    print("3. 建议先在模拟环境测试")
    print("4. 详细文档: https://www.okx.com/docs-v5/")
    print("5. Python SDK: https://github.com/okxapi/python-okx")
