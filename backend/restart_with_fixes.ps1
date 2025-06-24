#!/usr/bin/env pwsh
# Trading Console 重启脚本 - 应用Dashboard修复

Write-Host "🔄 重启交易控制台服务..." -ForegroundColor Cyan
Write-Host "=" * 50

# 检查Python环境
Write-Host "📍 当前目录: $PWD" -ForegroundColor Yellow

# 切换到backend目录
Set-Location "C:\trading_console\backend"

# 检查虚拟环境
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "✅ 找到虚拟环境" -ForegroundColor Green
    & "venv\Scripts\activate.ps1"
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 虚拟环境不存在" -ForegroundColor Red
    exit 1
}

# 检查SSR代理
Write-Host "📡 检查SSR代理状态..." -ForegroundColor Yellow
try {
    $connection = New-Object System.Net.Sockets.TcpClient
    $connection.Connect("127.0.0.1", 1080)
    $connection.Close()
    Write-Host "✅ SSR代理端口1080可用" -ForegroundColor Green
} catch {
    Write-Host "⚠️  SSR代理端口1080不可用，请检查SSR客户端" -ForegroundColor Red
}

# 检查并安装bcrypt修复
Write-Host "🔧 检查bcrypt版本..." -ForegroundColor Yellow
python -c "import bcrypt; print(f'bcrypt版本: {bcrypt.__version__}')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "🔨 升级bcrypt..." -ForegroundColor Yellow
    pip install bcrypt==4.0.1 --upgrade
}

Write-Host "🚀 启动优化后的后端服务..." -ForegroundColor Green
Write-Host "📋 主要修复内容:" -ForegroundColor Cyan
Write-Host "   - Dashboard加载超时优化 (15秒)" -ForegroundColor White
Write-Host "   - OKX API连接错误处理" -ForegroundColor White
Write-Host "   - 余额获取回退机制" -ForegroundColor White
Write-Host "   - bcrypt版本兼容性修复" -ForegroundColor White
Write-Host "   - 前端错误处理改进" -ForegroundColor White

Write-Host ""
Write-Host "💡 提示: 按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "🌐 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "🏠 前端地址: http://localhost:3001" -ForegroundColor Cyan
Write-Host ""

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
