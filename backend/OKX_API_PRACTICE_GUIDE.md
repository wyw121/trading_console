# OKX API 官方文档实践指南

## 📖 概述

本指南基于OKX官方API文档 (https://www.okx.com/docs-v5/) 提供完整的实践案例，包括：

- 认证与连接
- 市场数据获取  
- 账户管理
- 订单管理
- 最佳实践
- 错误处理

## 🔐 认证配置

### 1. API密钥申请

1. 登录OKX官网
2. 进入【交易】- 【模拟交易】创建测试API密钥
3. 点击【个人资料】- 【模拟交易API】
4. 创建API密钥，需要以下信息：
   - API Key
   - Secret Key  
   - Passphrase
   - 权限设置（建议先只开启只读权限测试）

### 2. 安全建议

- **测试环境优先**：先在沙盒环境测试所有功能
- **权限最小化**：只授予必要的API权限
- **密钥安全**：使用环境变量存储API密钥
- **IP白名单**：设置API访问IP白名单
- **定期轮换**：定期更换API密钥

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install ccxt pandas numpy python-okx
```

### 2. 基础连接测试

```python
import ccxt
import asyncio

async def test_connection():
    config = {
        'apiKey': 'your_api_key',
        'secret': 'your_secret_key', 
        'passphrase': 'your_passphrase',
        'sandbox': True,  # 沙盒环境
        'enableRateLimit': True
    }
    
    exchange = ccxt.okx(config)
    
    try:
        # 测试公共API
        markets = await exchange.load_markets()
        print(f"支持的交易对数量: {len(markets)}")
        
        # 测试私有API
        balance = await exchange.fetch_balance()
        print(f"账户余额: {balance}")
        
    except Exception as e:
        print(f"连接失败: {e}")
    finally:
        await exchange.close()

# 运行测试
asyncio.run(test_connection())
```

## 📊 市场数据 API

### 1. 获取交易工具配置

```python
# 获取现货交易对
instruments = await exchange.public_get_public_instruments({
    'instType': 'SPOT'
})

# 获取合约交易对  
futures = await exchange.public_get_public_instruments({
    'instType': 'FUTURES'
})
```

### 2. 获取行情数据

```python
# 获取单个交易对行情
ticker = await exchange.public_get_market_ticker({
    'instId': 'BTC-USDT'
})

# 获取所有现货行情
all_tickers = await exchange.public_get_market_tickers({
    'instType': 'SPOT'
})
```

### 3. 获取深度数据

```python
# 获取订单簿
orderbook = await exchange.public_get_market_books({
    'instId': 'BTC-USDT',
    'sz': '20'  # 深度档位
})

# 实时深度 (WebSocket)
```

### 4. K线数据

```python
# 获取K线数据
candles = await exchange.public_get_market_candles({
    'instId': 'BTC-USDT',
    'bar': '1H',  # 1小时K线
    'limit': '100'
})
```

## 💰 账户管理 API

### 1. 账户配置

```python
# 获取账户配置
config = await exchange.private_get_account_config()

# 账户模式说明:
# 1: 简单模式
# 2: 单币种保证金模式  
# 3: 跨币种保证金模式
# 4: 组合保证金模式
```

### 2. 账户余额

```python
# 获取所有币种余额
balance = await exchange.private_get_account_balance()

# 获取指定币种余额
btc_balance = await exchange.private_get_account_balance({
    'ccy': 'BTC'
})
```

### 3. 持仓信息

```python
# 获取所有持仓
positions = await exchange.private_get_account_positions()

# 获取指定产品持仓
swap_positions = await exchange.private_get_account_positions({
    'instType': 'SWAP'
})
```

### 4. 最大可用余额

```python
# 获取最大可买/卖数量
max_size = await exchange.private_get_account_max_avail_size({
    'instId': 'BTC-USDT',
    'tdMode': 'cash'
})
```

## 📋 订单管理 API

### 1. 下单

```python
async def place_spot_order():
    """现货下单示例"""
    order_params = {
        'instId': 'BTC-USDT',
        'tdMode': 'cash',      # 现货模式
        'side': 'buy',         # buy/sell
        'ordType': 'limit',    # limit/market
        'px': '50000',         # 价格
        'sz': '0.01',          # 数量
        'clOrdId': f'order_{int(time.time())}'  # 客户端订单ID
    }
    
    result = await exchange.private_post_trade_order(order_params)
    return result

# 市价单
market_order = {
    'instId': 'BTC-USDT',
    'tdMode': 'cash',
    'side': 'buy',
    'ordType': 'market',
    'sz': '100',           # 市价买入100 USDT
    'tgtCcy': 'quote_ccy'  # 以计价货币为单位
}
```

### 2. 订单查询

```python
# 查询单个订单
order_info = await exchange.private_get_trade_order({
    'instId': 'BTC-USDT',
    'ordId': 'order_id'
})

# 查询当前委托
pending_orders = await exchange.private_get_trade_orders_pending()

# 查询历史订单
order_history = await exchange.private_get_trade_orders_history({
    'instType': 'SPOT',
    'limit': '100'
})
```

### 3. 订单修改

```python
# 修改订单
amend_result = await exchange.private_post_trade_amend_order({
    'instId': 'BTC-USDT',
    'ordId': 'order_id',
    'newSz': '0.02',      # 新数量
    'newPx': '51000'      # 新价格
})
```

### 4. 撤销订单

```python
# 撤销单个订单
cancel_result = await exchange.private_post_trade_cancel_order({
    'instId': 'BTC-USDT',
    'ordId': 'order_id'
})

# 批量撤销
batch_cancel = await exchange.private_post_trade_cancel_batch_orders([
    {'instId': 'BTC-USDT', 'ordId': 'order_id_1'},
    {'instId': 'ETH-USDT', 'ordId': 'order_id_2'}
])
```

## 📈 交易策略实现

### 1. 简单网格策略

```python
class GridTradingStrategy:
    def __init__(self, exchange, symbol, grid_size=0.01, grid_num=10):
        self.exchange = exchange
        self.symbol = symbol
        self.grid_size = grid_size  # 网格间距
        self.grid_num = grid_num    # 网格数量
        self.orders = {}
        
    async def initialize(self):
        """初始化网格"""
        # 获取当前价格
        ticker = await self.exchange.public_get_market_ticker({
            'instId': self.symbol
        })
        current_price = float(ticker['data'][0]['last'])
        
        # 计算网格价格
        base_price = current_price * (1 - self.grid_size * self.grid_num / 2)
        
        for i in range(self.grid_num):
            buy_price = base_price * (1 + self.grid_size * i)
            sell_price = base_price * (1 + self.grid_size * (i + 1))
            
            # 下买单
            await self.place_grid_order('buy', buy_price)
            # 下卖单  
            await self.place_grid_order('sell', sell_price)
    
    async def place_grid_order(self, side, price):
        """下网格订单"""
        try:
            order_params = {
                'instId': self.symbol,
                'tdMode': 'cash',
                'side': side,
                'ordType': 'limit',
                'px': str(price),
                'sz': '0.01',
                'clOrdId': f'grid_{side}_{int(price)}'
            }
            
            result = await self.exchange.private_post_trade_order(order_params)
            if result['code'] == '0':
                order_id = result['data'][0]['ordId']
                self.orders[order_id] = {
                    'side': side,
                    'price': price,
                    'status': 'pending'
                }
                
        except Exception as e:
            print(f"下单失败: {e}")
```

### 2. 移动平均策略

```python
class MovingAverageStrategy:
    def __init__(self, exchange, symbol, short_period=5, long_period=20):
        self.exchange = exchange
        self.symbol = symbol
        self.short_period = short_period
        self.long_period = long_period
        self.position = 0
        
    async def get_ma_signal(self):
        """获取移动平均信号"""
        # 获取K线数据
        candles = await self.exchange.public_get_market_candles({
            'instId': self.symbol,
            'bar': '1H',
            'limit': str(self.long_period + 10)
        })
        
        prices = [float(candle[4]) for candle in candles['data']]  # 收盘价
        
        if len(prices) < self.long_period:
            return None
            
        # 计算移动平均
        short_ma = sum(prices[:self.short_period]) / self.short_period
        long_ma = sum(prices[:self.long_period]) / self.long_period
        
        # 生成信号
        if short_ma > long_ma and self.position <= 0:
            return 'buy'
        elif short_ma < long_ma and self.position >= 0:
            return 'sell'
        
        return None
    
    async def execute_signal(self, signal):
        """执行交易信号"""
        if signal == 'buy':
            await self.place_order('buy', '0.01')
            self.position = 1
        elif signal == 'sell':
            await self.place_order('sell', '0.01')  
            self.position = -1
```

## 🔄 WebSocket 实时数据

### 1. 公共数据订阅

```python
import websockets
import json

async def subscribe_public_data():
    """订阅公共数据"""
    uri = "wss://ws.okx.com:8443/ws/v5/public"
    
    async with websockets.connect(uri) as websocket:
        # 订阅行情数据
        subscribe_msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "tickers",
                    "instId": "BTC-USDT"
                }
            ]
        }
        
        await websocket.send(json.dumps(subscribe_msg))
        
        # 接收数据
        async for message in websocket:
            data = json.loads(message)
            if data.get('data'):
                print(f"收到行情数据: {data}")
```

### 2. 私有数据订阅

```python
async def subscribe_private_data():
    """订阅私有数据"""
    uri = "wss://ws.okx.com:8443/ws/v5/private"
    
    async with websockets.connect(uri) as websocket:
        # 登录
        login_msg = {
            "op": "login",
            "args": [
                {
                    "apiKey": "your_api_key",
                    "passphrase": "your_passphrase", 
                    "timestamp": str(int(time.time())),
                    "sign": "your_signature"
                }
            ]
        }
        
        await websocket.send(json.dumps(login_msg))
        
        # 订阅账户数据
        subscribe_msg = {
            "op": "subscribe",
            "args": [
                {
                    "channel": "account"
                },
                {
                    "channel": "orders",
                    "instType": "SPOT"
                }
            ]
        }
        
        await websocket.send(json.dumps(subscribe_msg))
```

## ⚠️ 限速和错误处理

### 1. API限速规则

- REST API: 每2秒最多20次请求
- WebSocket: 每秒最多20次操作
- 下单API: 每2秒最多60次请求
- 超出限制会返回429错误

### 2. 错误处理最佳实践

```python
async def safe_api_call(api_func, *args, **kwargs):
    """安全的API调用"""
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            result = await api_func(*args, **kwargs)
            
            # 检查API响应
            if result.get('code') != '0':
                error_msg = result.get('msg', '未知错误')
                
                # 特殊错误处理
                if result.get('code') == '50001':  # 余额不足
                    raise InsufficientBalanceError(error_msg)
                elif result.get('code') == '50004':  # 订单不存在
                    raise OrderNotFoundError(error_msg)
                else:
                    raise APIError(f"API错误 {result.get('code')}: {error_msg}")
                    
            return result
            
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries - 1:
                await asyncio.sleep(retry_delay * (2 ** attempt))
                continue
            raise e
        except Exception as e:
            if attempt < max_retries - 1 and "rate limit" in str(e).lower():
                await asyncio.sleep(retry_delay * (2 ** attempt))
                continue
            raise e
```

### 3. 常见错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 50001 | 余额不足 | 检查账户余额 |
| 50004 | 订单不存在 | 确认订单ID |
| 50011 | 订单状态错误 | 检查订单状态 |
| 50014 | 下单金额过小 | 增加下单金额 |
| 50026 | 系统繁忙 | 稍后重试 |

## 📚 进阶功能

### 1. 算法交易

```python
class TWAPStrategy:
    """时间加权平均价格策略"""
    
    def __init__(self, exchange, symbol, total_amount, duration_minutes):
        self.exchange = exchange
        self.symbol = symbol
        self.total_amount = total_amount
        self.duration = duration_minutes
        self.interval = 60  # 每分钟执行一次
        
    async def execute(self):
        """执行TWAP策略"""
        slice_amount = self.total_amount / self.duration
        
        for i in range(self.duration):
            try:
                # 获取当前市价
                ticker = await self.exchange.public_get_market_ticker({
                    'instId': self.symbol
                })
                current_price = float(ticker['data'][0]['last'])
                
                # 下市价单
                await self.exchange.private_post_trade_order({
                    'instId': self.symbol,
                    'tdMode': 'cash',
                    'side': 'buy',
                    'ordType': 'market',
                    'sz': str(slice_amount)
                })
                
                # 等待下一个时间片
                await asyncio.sleep(self.interval)
                
            except Exception as e:
                print(f"TWAP执行错误: {e}")
```

### 2. 风险管理

```python
class RiskManager:
    """风险管理器"""
    
    def __init__(self, max_position_ratio=0.1, max_daily_loss=0.05):
        self.max_position_ratio = max_position_ratio  # 最大仓位比例
        self.max_daily_loss = max_daily_loss          # 最大日损失
        self.daily_pnl = 0
        
    async def check_position_limit(self, exchange, symbol, order_amount):
        """检查仓位限制"""
        # 获取账户余额
        balance = await exchange.private_get_account_balance()
        total_equity = float(balance['data'][0]['totalEq'])
        
        # 获取当前持仓
        positions = await exchange.private_get_account_positions({
            'instId': symbol
        })
        
        current_position = 0
        if positions['data']:
            current_position = float(positions['data'][0]['pos'])
        
        # 计算新仓位比例
        new_position = current_position + order_amount
        position_ratio = abs(new_position * current_price) / total_equity
        
        if position_ratio > self.max_position_ratio:
            raise Exception(f"超出最大仓位限制: {position_ratio:.2%}")
            
    async def check_daily_loss_limit(self):
        """检查日损失限制"""
        if self.daily_pnl < -self.max_daily_loss:
            raise Exception(f"超出日损失限制: {self.daily_pnl:.2%}")
```

## 🔧 工具和实用函数

### 1. 价格精度处理

```python
def format_price(price, symbol_info):
    """格式化价格精度"""
    tick_size = float(symbol_info['tickSz'])
    precision = len(str(tick_size).split('.')[1]) if '.' in str(tick_size) else 0
    return round(float(price), precision)

def format_quantity(quantity, symbol_info):
    """格式化数量精度"""
    lot_size = float(symbol_info['lotSz'])
    precision = len(str(lot_size).split('.')[1]) if '.' in str(lot_size) else 0
    return round(float(quantity), precision)
```

### 2. 技术指标计算

```python
def calculate_rsi(prices, period=14):
    """计算RSI指标"""
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    gains = [delta if delta > 0 else 0 for delta in deltas]
    losses = [-delta if delta < 0 else 0 for delta in deltas]
    
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    rs = avg_gain / avg_loss if avg_loss != 0 else 0
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """计算布林带"""
    if len(prices) < period:
        return None, None, None
        
    sma = sum(prices[-period:]) / period
    variance = sum([(p - sma) ** 2 for p in prices[-period:]]) / period
    std = variance ** 0.5
    
    upper_band = sma + (std * std_dev)
    lower_band = sma - (std * std_dev)
    
    return upper_band, sma, lower_band
```

## 📊 性能监控

### 1. 延迟监控

```python
import time

class LatencyMonitor:
    def __init__(self):
        self.latencies = []
        
    async def measure_latency(self, api_func, *args, **kwargs):
        """测量API延迟"""
        start_time = time.time()
        result = await api_func(*args, **kwargs)
        end_time = time.time()
        
        latency = (end_time - start_time) * 1000  # 毫秒
        self.latencies.append(latency)
        
        return result, latency
        
    def get_stats(self):
        """获取延迟统计"""
        if not self.latencies:
            return {}
            
        return {
            'avg': sum(self.latencies) / len(self.latencies),
            'min': min(self.latencies),
            'max': max(self.latencies),
            'count': len(self.latencies)
        }
```

### 2. 错误统计

```python
class ErrorTracker:
    def __init__(self):
        self.errors = {}
        
    def record_error(self, error_code, error_msg):
        """记录错误"""
        if error_code not in self.errors:
            self.errors[error_code] = {
                'count': 0,
                'messages': set(),
                'last_occurrence': None
            }
            
        self.errors[error_code]['count'] += 1
        self.errors[error_code]['messages'].add(error_msg)
        self.errors[error_code]['last_occurrence'] = datetime.now()
        
    def get_error_summary(self):
        """获取错误摘要"""
        return {
            code: {
                'count': info['count'],
                'last_occurrence': info['last_occurrence'],
                'sample_message': list(info['messages'])[0]
            }
            for code, info in self.errors.items()
        }
```

## 🎯 完整交易示例

```python
async def complete_trading_example():
    """完整的交易示例"""
    
    # 1. 初始化
    config = {
        'apiKey': 'your_api_key',
        'secret': 'your_secret_key',
        'passphrase': 'your_passphrase',
        'sandbox': True,
        'enableRateLimit': True
    }
    
    exchange = ccxt.okx(config)
    risk_manager = RiskManager()
    
    try:
        # 2. 获取市场信息
        instruments = await exchange.public_get_public_instruments({
            'instType': 'SPOT'
        })
        btc_usdt = next(inst for inst in instruments['data'] 
                       if inst['instId'] == 'BTC-USDT')
        
        # 3. 获取当前价格
        ticker = await exchange.public_get_market_ticker({
            'instId': 'BTC-USDT'
        })
        current_price = float(ticker['data'][0]['last'])
        
        # 4. 风险检查
        order_amount = 0.01
        await risk_manager.check_position_limit(exchange, 'BTC-USDT', order_amount)
        
        # 5. 下单
        order_params = {
            'instId': 'BTC-USDT',
            'tdMode': 'cash',
            'side': 'buy',
            'ordType': 'limit',
            'px': str(format_price(current_price * 0.99, btc_usdt)),
            'sz': str(format_quantity(order_amount, btc_usdt)),
            'clOrdId': f'example_{int(time.time())}'
        }
        
        order_result = await exchange.private_post_trade_order(order_params)
        
        if order_result['code'] == '0':
            order_id = order_result['data'][0]['ordId']
            print(f"下单成功，订单ID: {order_id}")
            
            # 6. 监控订单状态
            while True:
                order_info = await exchange.private_get_trade_order({
                    'instId': 'BTC-USDT',
                    'ordId': order_id
                })
                
                status = order_info['data'][0]['state']
                print(f"订单状态: {status}")
                
                if status in ['filled', 'canceled']:
                    break
                    
                await asyncio.sleep(1)
        
    except Exception as e:
        print(f"交易示例失败: {e}")
        
    finally:
        await exchange.close()
```

## 📝 总结

本指南基于OKX官方API文档提供了完整的实践案例，涵盖了：

1. **基础连接**: API密钥配置、连接测试
2. **市场数据**: 行情、深度、K线数据获取  
3. **账户管理**: 余额查询、持仓管理
4. **订单管理**: 下单、查询、修改、撤销
5. **高级功能**: 策略实现、风险管理、性能监控
6. **最佳实践**: 错误处理、限速管理、安全建议

### 下一步建议

1. **从测试环境开始**: 所有功能先在沙盒环境测试
2. **逐步增加复杂度**: 从简单的查询API开始，逐步实现交易功能
3. **完善错误处理**: 针对不同错误码实现相应的处理逻辑
4. **性能优化**: 监控API调用延迟，优化请求频率
5. **安全第一**: 始终遵循API安全最佳实践

更多详细信息请参考OKX官方文档：https://www.okx.com/docs-v5/
