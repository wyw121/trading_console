# Trading Console

一个现代化的加密货币交易策略管理平台，支持多交易所接入和自动化交易策略执行。

## 功能特性

- 🔐 用户认证与授权
- 🏦 多交易所账户管理（Binance、OKX等）
- 📊 策略配置与管理
- 🤖 自动化策略执行
- 📈 实时交易监控
- 💰 账户余额查看
- 📋 交易历史记录

## 技术栈

### 后端
- **Python 3.11**
- **FastAPI** - 高性能API框架
- **SQLAlchemy** - ORM数据库操作
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和消息队列
- **CCXT** - 统一交易所API接口
- **TA-Lib** - 技术指标计算
- **APScheduler** - 任务调度

### 前端
- **Vue.js 3** - 渐进式JavaScript框架
- **Element Plus** - Vue 3组件库
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Axios** - HTTP客户端
- **ECharts** - 数据可视化

## 快速开始

### 使用 Docker（推荐）

1. **克隆项目**
```bash
git clone <repository-url>
cd trading_console
```

2. **启动服务**
```bash
docker-compose up -d
```

3. **访问应用**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

### 手动安装

#### 后端设置

1. **创建虚拟环境**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **设置环境变量**
```bash
copy .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
```

4. **启动数据库**
```bash
# 确保 PostgreSQL 和 Redis 正在运行
```

5. **启动后端服务**
```bash
uvicorn main:app --reload
```

#### 前端设置

1. **安装依赖**
```bash
cd frontend
npm install
```

2. **启动开发服务器**
```bash
npm run dev
```

## 项目结构

```
trading_console/
├── backend/                 # 后端代码
│   ├── routers/            # API路由
│   ├── database.py         # 数据库模型
│   ├── schemas.py          # Pydantic模型
│   ├── auth.py             # 认证逻辑
│   ├── trading_engine.py   # 交易引擎
│   ├── scheduler.py        # 任务调度器
│   ├── main.py             # 应用入口
│   └── requirements.txt    # Python依赖
├── frontend/               # 前端代码
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── views/          # 页面组件
│   │   ├── stores/         # Pinia状态管理
│   │   ├── utils/          # 工具函数
│   │   └── router/         # 路由配置
│   ├── package.json        # Node.js依赖
│   └── vite.config.js      # Vite配置
└── docker-compose.yml      # Docker编排文件
```

## 使用说明

### 1. 用户注册与登录
- 访问 http://localhost:3000
- 点击"立即注册"创建账户
- 使用用户名和密码登录

### 2. 配置交易所账户
- 进入"交易所配置"页面
- 添加您的交易所API密钥
- 支持的交易所：Binance、OKX等

### 3. 创建交易策略
- 进入"策略配置"页面
- 选择策略类型（如：5分钟布林带+MA60策略）
- 配置交易参数（交易对、金额、止盈止损等）
- 启动策略自动执行

### 4. 监控交易
- 在"控制台概览"查看整体统计
- 在"交易记录"查看详细交易历史
- 实时监控策略运行状态

## API文档

启动后端服务后，访问 http://localhost:8000/docs 查看完整的API文档。

## 安全说明

⚠️ **重要安全提示**：

1. **API密钥安全**：您的交易所API密钥将加密存储在数据库中
2. **权限设置**：建议为API密钥设置最小必要权限（交易权限，禁用提币）
3. **测试模式**：初次使用建议先在测试网络进行验证
4. **密钥管理**：请妥善保管您的SECRET_KEY等环境变量

## 开发说明

### 添加新的交易策略

1. 在 `trading_engine.py` 中实现策略逻辑
2. 在数据库模型中添加相应的策略参数字段
3. 在前端策略配置页面添加对应的配置表单

### 支持新的交易所

1. 确认CCXT库支持该交易所
2. 在 `ExchangeManager` 中添加交易所特定配置
3. 在前端添加交易所选项

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！

## 许可证

MIT License

## 免责声明

本软件仅供学习和研究使用。使用本软件进行实际交易的风险由用户自行承担。作者不对任何投资损失负责。

在使用前请务必：
1. 充分了解加密货币交易风险
2. 在测试环境中验证策略
3. 使用小额资金进行测试
4. 制定合理的风险管理策略
