#!/usr/bin/env pwsh
# 快速重启脚本 - 应用修复

Write-Host "🔄 快速重启 Trading Console..." -ForegroundColor Cyan

# 检查当前目录
$currentDir = Get-Location
Write-Host "📍 当前目录: $currentDir" -ForegroundColor Yellow

# 切换到backend目录
if (Test-Path "C:\trading_console\backend") {
    Set-Location "C:\trading_console\backend"
    Write-Host "✅ 切换到backend目录" -ForegroundColor Green
} else {
    Write-Host "❌ backend目录不存在" -ForegroundColor Red
    exit 1
}

# 激活虚拟环境
if (Test-Path "venv\Scripts\activate.ps1") {
    Write-Host "🔧 激活Python虚拟环境..." -ForegroundColor Yellow
    & "venv\Scripts\activate.ps1"
    Write-Host "✅ 虚拟环境已激活" -ForegroundColor Green
} else {
    Write-Host "❌ 虚拟环境不存在" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🚀 启动优化后的后端服务..." -ForegroundColor Green
Write-Host "📋 已修复:" -ForegroundColor Cyan
Write-Host "   ✅ Dashboard超时问题" -ForegroundColor White
Write-Host "   ✅ OKX API连接错误" -ForegroundColor White
Write-Host "   ✅ 依赖包问题" -ForegroundColor White
Write-Host "   ✅ 错误处理优化" -ForegroundColor White
Write-Host ""

Write-Host "💡 提示: 按 Ctrl+C 停止服务" -ForegroundColor Yellow
Write-Host "🌐 前端地址: http://localhost:3001" -ForegroundColor Cyan
Write-Host "📡 后端API: http://localhost:8000" -ForegroundColor Cyan
Write-Host ""

# 启动服务
try {
    uvicorn main:app --host 0.0.0.0 --port 8000 --reload
} catch {
    Write-Host "❌ 启动失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "💡 请检查端口8000是否被占用" -ForegroundColor Yellow
}
