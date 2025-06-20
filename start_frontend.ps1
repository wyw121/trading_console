# 前端启动脚本
Write-Host "启动交易控制台前端服务..." -ForegroundColor Green

# 检查目录
if (!(Test-Path "C:\trading_console\frontend")) {
    Write-Host "错误：找不到frontend目录" -ForegroundColor Red
    exit 1
}

# 切换到前端目录
Set-Location "C:\trading_console\frontend"

# 检查package.json
if (!(Test-Path ".\package.json")) {
    Write-Host "错误：找不到package.json" -ForegroundColor Red
    exit 1
}

# 检查Node.js和npm
Write-Host "检查Node.js环境..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version
    $npmVersion = npm --version
    Write-Host "Node.js版本: $nodeVersion" -ForegroundColor Cyan
    Write-Host "npm版本: $npmVersion" -ForegroundColor Cyan
} catch {
    Write-Host "错误：未找到Node.js或npm" -ForegroundColor Red
    Write-Host "请先安装Node.js: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# 检查依赖
if (!(Test-Path ".\node_modules")) {
    Write-Host "安装npm依赖..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "依赖安装失败，尝试使用国内镜像..." -ForegroundColor Yellow
        npm install --registry https://registry.npmmirror.com
    }
} else {
    Write-Host "依赖已存在，跳过安装" -ForegroundColor Green
}

# 启动服务
Write-Host "启动Vite开发服务器..." -ForegroundColor Yellow
Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Magenta

npm run dev
