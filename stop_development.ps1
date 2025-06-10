# Trading Console 开发环境停止脚本
# 停止所有相关服务

Write-Host '正在停止 Trading Console 开发环境...' -ForegroundColor Yellow

# 停止Python进程（后端）
Write-Host '停止后端服务器...' -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq 'python' } | Stop-Process -Force -ErrorAction SilentlyContinue

# 停止Node.js进程（前端）
Write-Host '停止前端开发服务器...' -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -eq 'node' } | Stop-Process -Force -ErrorAction SilentlyContinue

# 停止数据库容器
Write-Host '停止数据库容器...' -ForegroundColor Yellow
Set-Location 'c:\trading_console'
docker-compose down

Write-Host '所有服务已停止！' -ForegroundColor Green
