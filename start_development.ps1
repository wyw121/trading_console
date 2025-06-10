# Trading Console 开发环境启动脚本
# 启动所有必要的服务

Write-Host '正在启动 Trading Console 开发环境...' -ForegroundColor Green

# 检查Docker是否运行
Write-Host '检查Docker状态...' -ForegroundColor Yellow
try {
    docker ps | Out-Null
    Write-Host '✓ Docker 正在运行' -ForegroundColor Green
} catch {
    Write-Host '✗ Docker 未运行，请先启动Docker' -ForegroundColor Red
    exit 1
}

# 启动数据库容器
Write-Host '启动数据库容器...' -ForegroundColor Yellow
Set-Location 'c:\trading_console'
docker-compose up -d
Start-Sleep -Seconds 5

# 启动后端服务器
Write-Host '启动后端API服务器...' -ForegroundColor Yellow
Set-Location 'c:\trading_console\backend'
Start-Process -FilePath 'python' -ArgumentList '-m', 'uvicorn', 'main:app', '--reload', '--host', '0.0.0.0', '--port', '8000' -WindowStyle Minimized
Start-Sleep -Seconds 5

# 启动前端开发服务器
Write-Host '启动前端开发服务器...' -ForegroundColor Yellow
Set-Location 'c:\trading_console\frontend'
Start-Process -FilePath 'npm' -ArgumentList 'run', 'dev' -WindowStyle Minimized
Start-Sleep -Seconds 3

Write-Host '所有服务已启动！' -ForegroundColor Green
Write-Host '前端应用: http://localhost:3000' -ForegroundColor Cyan
Write-Host '后端API: http://localhost:8000' -ForegroundColor Cyan
Write-Host 'API文档: http://localhost:8000/docs' -ForegroundColor Cyan

Write-Host "`n按任意键打开浏览器..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown')

# 打开浏览器
Start-Process 'http://localhost:3000'
Start-Process 'http://localhost:8000/docs'
