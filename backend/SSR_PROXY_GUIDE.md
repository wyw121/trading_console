# Python后端通过SSR代理访问OKX API完整指南

## 概述

根据您的项目结构，**Python后端**是通过CCXT库连接OKX API的核心组件。以下是让Python后端通过本地SSR代理访问OKX API的完整配置方案。

## 关键文件分析

### 1. 主要交易引擎文件
- `backend/trading_engine.py` - 主要交易引擎
- `backend/real_trading_engine.py` - 真实API连接引擎  
- `backend/trading_engine_clean.py` - 清理版交易引擎

### 2. 代理配置文件
- `backend/proxy_config.py` - 代理配置管理
- `backend/.env` - 环境变量配置

## 已有的SSR代理配置

### 环境变量配置 (.env文件)
```properties
# SSR代理配置
HTTP_PROXY=socks5h://127.0.0.1:1080
HTTPS_PROXY=socks5h://127.0.0.1:1080
http_proxy=socks5h://127.0.0.1:1080
https_proxy=socks5h://127.0.0.1:1080
```

### 主服务器配置 (main.py)
```python
# 设置代理环境变量（确保所有HTTP请求都通过SSR代理）
if os.getenv('HTTP_PROXY'):
    os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
    os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
    os.environ['http_proxy'] = os.getenv('http_proxy')
    os.environ['https_proxy'] = os.getenv('https_proxy')
    print(f"✅ 代理配置已加载: {os.getenv('HTTPS_PROXY')}")
```

## OKX API连接方式

### 1. CCXT库连接
您的项目主要通过CCXT库连接OKX：

```python
# trading_engine.py 中的配置
config = {
    'apiKey': exchange_account.api_key,
    'secret': exchange_account.api_secret,
    'passphrase': exchange_account.api_passphrase,
    'sandbox': exchange_account.is_testnet,
    'enableRateLimit': True,
    'timeout': 30000,
    'hostname': 'www.okx.com',
    'options': {
        'defaultType': 'spot',
    }
}
exchange = ccxt.okx(config)
```

### 2. 连接测试方式
```python
# 检查OKX连通性
def check_okx_connectivity() -> bool:
    test_urls = [
        'https://www.okx.com/api/v5/public/time',
        'https://aws.okx.com/api/v5/public/time',
    ]
    # 使用requests.get测试连接
```

## SSR代理配置最佳实践

### 1. 确保使用 socks5h:// 协议
```bash
# 正确格式 - DNS通过代理解析
HTTP_PROXY=socks5h://127.0.0.1:1080
HTTPS_PROXY=socks5h://127.0.0.1:1080

# 错误格式 - DNS本地解析（可能被拦截）
HTTP_PROXY=socks5://127.0.0.1:1080  # ❌
```

### 2. 安装必要依赖
```bash
# 安装SOCKS代理支持
pip install pysocks

# 或添加到requirements.txt
echo "pysocks>=1.7.1" >> requirements.txt
```

### 3. 环境变量优先级
```python
# 在main.py中确保环境变量生效
import os
from dotenv import load_dotenv

load_dotenv()  # 加载.env文件

# 显式设置环境变量（确保所有库都能读取）
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
for var in proxy_vars:
    if os.getenv(var):
        os.environ[var] = os.getenv(var)
```

## 具体实现方案

### 方案1: 环境变量法（推荐）

1. **配置.env文件**
```properties
HTTP_PROXY=socks5h://127.0.0.1:1080
HTTPS_PROXY=socks5h://127.0.0.1:1080
http_proxy=socks5h://127.0.0.1:1080
https_proxy=socks5h://127.0.0.1:1080
```

2. **在main.py中加载**
```python
from dotenv import load_dotenv
load_dotenv()

# 确保环境变量生效
if os.getenv('HTTP_PROXY'):
    for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
        if os.getenv(var):
            os.environ[var] = os.getenv(var)
```

3. **CCXT自动使用环境变量**
CCXT库会自动读取环境变量中的代理配置。

### 方案2: 代码配置法

1. **修改proxy_config.py**
```python
def get_ccxt_proxy_config(self) -> Dict:
    """获取CCXT库使用的代理配置"""
    if not self.proxy_enabled:
        return {}
    
    return {
        'timeout': 30000,
        'enableRateLimit': True,
        'proxies': {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
    }
```

2. **在交易引擎中应用**
```python
from proxy_config import proxy_config

# 创建交易所时添加代理配置  
config.update(proxy_config.get_ccxt_proxy_config())
exchange = ccxt.okx(config)
```

## 测试验证步骤

### 1. 检查SSR客户端
```bash
# 检查端口是否开放
netstat -an | findstr 1080
# 或使用telnet测试
telnet 127.0.0.1 1080
```

### 2. 测试Python代理
```python
import requests

proxies = {
    'http': 'socks5h://127.0.0.1:1080',
    'https': 'socks5h://127.0.0.1:1080'
}

# 测试代理IP
response = requests.get('https://httpbin.org/ip', proxies=proxies)
print(f"代理IP: {response.json()['origin']}")

# 测试OKX连接
response = requests.get('https://www.okx.com/api/v5/public/time', proxies=proxies)
print(f"OKX连接: {response.status_code}")
```

### 3. 测试CCXT连接
```python
import ccxt
import asyncio

async def test_okx():
    exchange = ccxt.okx({
        'sandbox': True,
        'timeout': 30000,
        # 环境变量中的代理会自动使用
    })
    
    try:
        markets = await exchange.load_markets()
        print(f"成功加载 {len(markets)} 个市场")
    finally:
        await exchange.close()

asyncio.run(test_okx())
```

## 常见问题与解决方案

### 1. DNS解析失败
**问题**: 无法解析OKX域名
**解决**: 确保使用 `socks5h://` 而不是 `socks5://`

### 2. 连接超时
**问题**: 请求超时
**解决**: 
- 检查SSR客户端是否运行
- 增加timeout设置
- 尝试不同的OKX域名

### 3. 代理认证失败
**问题**: 代理连接被拒绝
**解决**: 
- 检查SSR客户端本地连接设置
- 确认端口1080是否正确
- 检查防火墙设置

## 最佳实践建议

### 1. 开发环境
- 使用环境变量配置代理
- 在.env文件中管理代理设置
- 使用测试网环境验证连接

### 2. 生产环境
- 确保代理稳定性
- 配置备用代理
- 监控连接状态
- 添加故障转移机制

### 3. 安全考虑
- 不在日志中记录代理配置
- 使用环境变量管理敏感信息
- 定期检查代理连接安全性

## 总结

您的Python后端主要通过以下文件连接OKX API：
- `trading_engine.py` - 主交易引擎（使用CCXT）
- `real_trading_engine.py` - 真实API连接
- 各种测试文件和API路由

通过配置.env文件中的SSR代理环境变量，并确保main.py正确加载这些变量，所有的HTTP/HTTPS请求（包括CCXT库的请求）都会自动通过SSR代理。

**关键点**：
1. 使用 `socks5h://127.0.0.1:1080` 格式
2. 确保安装 `pysocks` 依赖
3. 确保SSR客户端运行在1080端口
4. 环境变量在main.py中正确设置

这样配置后，Python后端就能成功通过SSR代理访问OKX API了。
