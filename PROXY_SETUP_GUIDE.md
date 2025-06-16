# ShadowsocksR 代理配置指南

本指南将帮助你配置Trading Console项目通过ShadowsocksR代理访问OKX等海外交易所API。

## 前提条件

1. **ShadowsocksR客户端已安装并正常工作**
   - 确保SSR客户端可以正常访问海外网站
   - 记录本地SOCKS5端口号（通常是1080或1081）

2. **Python环境**
   - Python 3.8+
   - 已安装项目依赖

## 配置步骤

### 1. 检查ShadowsocksR设置

在ShadowsocksR客户端中确认以下设置：
- ✅ 服务器连接正常
- ✅ 本地端口设置（默认1080）
- ✅ 开启"允许来自局域网的连接"
- ✅ 代理模式设置为"全局模式"或"PAC模式"

### 2. 配置环境变量

编辑 `backend/.env` 文件，添加代理配置：

```bash
# 代理配置
USE_PROXY=true
PROXY_HOST=127.0.0.1
PROXY_PORT=1080        # 修改为你的SSR端口
PROXY_TYPE=socks5
PROXY_USERNAME=
PROXY_PASSWORD=
```

### 3. 安装依赖

```powershell
cd backend
pip install -r requirements.txt
```

### 4. 测试代理连接

运行快速测试：
```powershell
python quick_proxy_test.py
```

运行完整测试：
```powershell
python test_proxy.py
```

### 5. 使用自动配置脚本（推荐）

运行PowerShell脚本自动配置：
```powershell
cd backend
.\setup_proxy.ps1
```

## 验证配置

### 成功标志
如果看到以下输出，说明配置成功：
```
✅ 端口可访问，ShadowsocksR可能正在运行
✅ 连接成功: https://httpbin.org/ip
   外部IP: 你的代理IP
✅ 连接成功: https://www.okx.com
🎉 代理配置成功！可以访问海外网站。
```

### 常见问题排解

#### 1. 端口连接失败
```
❌ 端口无法访问，请检查ShadowsocksR是否运行
```
**解决方案：**
- 确认SSR客户端正在运行
- 检查端口号是否正确
- 尝试重启SSR客户端

#### 2. 代理连接超时
```
❌ 连接异常: timeout
```
**解决方案：**
- 检查SSR服务器是否正常
- 尝试切换不同的SSR服务器
- 检查防火墙设置

#### 3. SOCKS5协议错误
```
❌ SOCKS5 proxy error
```
**解决方案：**
- 确认SSR客户端SOCKS5设置正确
- 检查"允许来自局域网的连接"是否开启
- 尝试重新安装pysocks: `pip install --upgrade pysocks`

## 不同SSR客户端配置

### ShadowsocksR-Windows
1. 右键系统托盘图标
2. 选择"选项设置"
3. 确认"本地端口"（默认1080）
4. 勾选"允许来自局域网的连接"

### ShadowsocksX-NG (macOS)
1. 打开偏好设置
2. 查看"本地SOCKS5监听端口"
3. 确保"允许局域网连接"已开启

### V2rayN
1. 参数设置 -> Core:基础设置
2. 查看"本地监听端口"
3. 确保"允许来自局域网的连接"已勾选

## 项目运行

配置完成后，可以正常启动项目：

### 本地开发模式
```powershell
cd backend
python main.py
```

### Docker模式
```powershell
# 在项目根目录
docker-compose up -d
```

## 验证OKX连接

启动项目后，可以通过以下方式验证：

1. **Web界面测试**
   - 访问 http://localhost:3000
   - 登录账户
   - 添加OKX交易所配置
   - 测试连接

2. **API测试**
   ```bash
   curl -X POST http://localhost:8000/api/exchanges/test \
   -H "Content-Type: application/json" \
   -d '{
     "exchange_name": "okx",
     "api_key": "your_api_key",
     "api_secret": "your_secret",
     "api_passphrase": "your_passphrase",
     "is_testnet": true
   }'
   ```

## 安全注意事项

1. **API密钥安全**
   - 使用只读权限的API密钥进行测试
   - 不要在代码中硬编码API密钥
   - 生产环境使用环境变量

2. **代理安全**
   - 确保SSR服务器可信
   - 定期更新SSR客户端
   - 不要在公共网络上运行代理

3. **日志安全**
   - 代理测试时会记录外部IP
   - 生产环境注意日志敏感信息

## 故障排除命令

```powershell
# 检查端口占用
netstat -an | findstr :1080

# 测试SOCKS5代理
curl --socks5 127.0.0.1:1080 https://httpbin.org/ip

# 查看Python网络连接
python -c "import requests; print(requests.get('https://httpbin.org/ip', proxies={'https':'socks5://127.0.0.1:1080'}).json())"
```

## 支持的交易所

通过代理配置，项目支持以下海外交易所：
- ✅ OKX (okx.com)
- ✅ Binance (binance.com)
- ✅ Coinbase Pro
- ✅ Kraken
- ✅ Bitfinex

国内交易所（无需代理）：
- ✅ 火币 (huobi.com)
- ✅ 抹茶 (mexc.com)

---

如有问题，请检查日志文件 `proxy_test.log` 获取详细错误信息。
