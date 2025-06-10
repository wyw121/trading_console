# 🧪 Trading Console 测试指南

## 📋 测试概述

本项目包含多层次的测试：
- **后端API测试** - FastAPI应用和数据库测试
- **前端组件测试** - Vue.js组件和集成测试
- **端到端测试** - 完整的用户流程测试
- **系统集成测试** - 前后端通信测试

## 🔧 测试环境准备

### 后端测试环境
```powershell
# 进入后端目录
cd backend

# 确保虚拟环境激活（如果使用）
# .\venv\Scripts\Activate.ps1

# 安装测试依赖
pip install pytest pytest-asyncio httpx pytest-cov
```

### 前端测试环境
```powershell
# 进入前端目录
cd frontend

# 安装测试依赖
npm install --save-dev vitest @vue/test-utils jsdom
```

## 🚀 快速开始

### 📋 测试脚本概览
- `run_all_tests.ps1` - 运行所有测试套件
- `run_backend_tests.ps1` - 后端API和数据库测试
- `run_frontend_tests.ps1` - 前端组件和构建测试
- `run_performance_tests.ps1` - 性能和负载测试

### ⚡ 一键运行所有测试
```powershell
# 运行完整测试套件
.\run_all_tests.ps1

# 运行测试并显示详细输出
.\run_all_tests.ps1 -Verbose

# 跳过某些测试组件
.\run_all_tests.ps1 -SkipFrontend
.\run_all_tests.ps1 -SkipBackend -SkipIntegration
```

### 🎯 分别运行测试

#### 后端测试
```powershell
# 运行完整后端测试
.\run_backend_tests.ps1

# 跳过数据库测试
.\run_backend_tests.ps1 -SkipDatabase

# 显示详细错误信息
.\run_backend_tests.ps1 -Verbose
```

#### 前端测试
```powershell
# 运行完整前端测试
.\run_frontend_tests.ps1

# 跳过构建测试
.\run_frontend_tests.ps1 -SkipBuild

# 显示详细输出
.\run_frontend_tests.ps1 -Verbose
```

#### 性能测试
```powershell
# 运行性能测试 (默认30秒，10并发)
.\run_performance_tests.ps1

# 自定义测试参数
.\run_performance_tests.ps1 -Duration 60 -Concurrency 20
```

## 🔧 手动测试步骤

### 1. 后端基础测试

#### Python环境测试
```powershell
cd backend
python minimal_test.py
```

#### 模块导入测试
```powershell
cd backend
python test_imports.py
```

#### 数据库连接测试
```powershell
cd backend
python test_db.py
```

### 2. 后端API测试

#### 启动测试服务器
```powershell
cd backend
python -m uvicorn test_server:app --host 0.0.0.0 --port 8001 --reload
```

#### API健康检查测试
```powershell
# 在新终端窗口中运行
Invoke-RestMethod -Uri "http://localhost:8001/" -Method Get
Invoke-RestMethod -Uri "http://localhost:8001/health" -Method Get
```

### 3. 前端测试

#### 开发服务器测试
```powershell
cd frontend
# 使用我们的启动脚本
.\start_frontend.ps1
```

#### 组件测试（需要安装测试依赖后）
```powershell
cd frontend
npm run test
```

### 4. 集成测试

#### 前后端通信测试
```powershell
# 确保后端运行在 8000 端口
# 确保前端运行在 5173 端口
# 然后访问前端应用测试API调用
```

## 📊 测试脚本

### 自动化测试脚本

#### 后端完整测试
```powershell
# run_backend_tests.ps1
cd backend

Write-Host "🧪 开始后端测试..." -ForegroundColor Green

Write-Host "1. Python环境测试"
python minimal_test.py

Write-Host "`n2. 模块导入测试"
python test_imports.py

Write-Host "`n3. 数据库连接测试"
python test_db.py

Write-Host "`n✅ 后端测试完成!" -ForegroundColor Green
```

#### 前端完整测试
```powershell
# run_frontend_tests.ps1
cd frontend

Write-Host "🎨 开始前端测试..." -ForegroundColor Green

Write-Host "1. 依赖检查"
if (Test-Path "node_modules") {
    Write-Host "✅ 依赖已安装" -ForegroundColor Green
} else {
    Write-Host "⚠️ 正在安装依赖..." -ForegroundColor Yellow
    npm install
}

Write-Host "`n2. 构建测试"
npm run build

Write-Host "`n✅ 前端测试完成!" -ForegroundColor Green
```

## 🔍 测试检查清单

### ✅ 后端测试检查
- [ ] Python环境正常
- [ ] 所有模块可正常导入
- [ ] 数据库连接成功
- [ ] FastAPI应用启动成功
- [ ] API端点响应正常
- [ ] 路由和中间件工作正常

### ✅ 前端测试检查
- [ ] Node.js环境正常
- [ ] 依赖包安装完成
- [ ] Vite开发服务器启动成功
- [ ] Vue组件渲染正常
- [ ] 路由导航工作正常
- [ ] API调用成功

### ✅ 集成测试检查
- [ ] 前后端通信正常
- [ ] CORS配置正确
- [ ] 认证流程工作
- [ ] 数据流转正常
- [ ] 错误处理正确

## 🐛 常见问题排查

### 后端问题
1. **模块导入失败** - 检查虚拟环境和依赖安装
2. **数据库连接失败** - 检查SQLite文件权限
3. **端口冲突** - 使用不同端口或停止冲突服务

### 前端问题
1. **依赖安装失败** - 清理node_modules重新安装
2. **Vite启动失败** - 检查端口占用和配置文件
3. **API调用失败** - 检查后端服务状态和CORS配置

### 集成问题
1. **404错误** - 检查API路径和代理配置
2. **认证失败** - 检查JWT令牌和用户状态
3. **CORS错误** - 检查后端CORS中间件配置

## 📈 性能测试

### API压力测试
```powershell
# 使用curl进行简单压力测试
for ($i=1; $i -le 10; $i++) {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get
    Write-Host "请求 $i : $($response.status)"
}
```

### 前端加载测试
```powershell
# 测试前端首页加载时间
Measure-Command { 
    Invoke-WebRequest -Uri "http://localhost:5173" 
} | Select-Object TotalMilliseconds
```

## 📝 测试报告

### 生成测试报告
```powershell
# 创建测试结果文件
$TestResults = @{
    Date = Get-Date
    BackendStatus = "Pass"
    FrontendStatus = "Pass"
    IntegrationStatus = "Pass"
}

$TestResults | ConvertTo-Json | Out-File "test_results.json"
```

## 🔄 持续测试

### 自动化测试流程
1. **开发阶段** - 每次代码修改后运行单元测试
2. **集成阶段** - 每次提交前运行集成测试
3. **部署阶段** - 部署前运行完整测试套件

### 测试监控
- 使用GitHub Actions进行CI/CD测试
- 设置测试覆盖率目标
- 定期运行回归测试
