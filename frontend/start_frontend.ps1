# 前端开发启动脚本
# 用于启动Vite开发服务器

Write-Host '🚀 启动 Trading Console 前端开发服务器...' -ForegroundColor Green
Write-Host "📂 当前目录: $(Get-Location)" -ForegroundColor Cyan

# 检查依赖是否安装
if (-not (Test-Path 'node_modules')) {
    Write-Host '📦 安装依赖...' -ForegroundColor Yellow
    npm install
}

# 启动开发服务器
Write-Host '🌐 启动 Vite 开发服务器...' -ForegroundColor Blue
Write-Host '🔗 前端将在 http://localhost:5173 启动' -ForegroundColor Green
Write-Host '🔗 后端API: http://localhost:8000' -ForegroundColor Green

# 直接调用vite二进制文件
$vitePath = 'node_modules\.bin\vite.cmd'
if (Test-Path $vitePath) {
    & $vitePath
} else {
    # 备用方法：直接使用node调用
    node 'node_modules/vite/bin/vite.js'
}
