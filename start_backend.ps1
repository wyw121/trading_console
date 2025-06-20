# 后端启动脚本
Write-Host "启动交易控制台后端服务..." -ForegroundColor Green

# 检查目录
if (!(Test-Path "C:\trading_console\backend")) {
    Write-Host "错误：找不到backend目录" -ForegroundColor Red
    exit 1
}

# 切换到后端目录
Set-Location "C:\trading_console\backend"

# 检查虚拟环境
if (!(Test-Path ".\venv\Scripts\activate.ps1")) {
    Write-Host "错误：找不到虚拟环境" -ForegroundColor Red
    Write-Host "请先运行: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# 激活虚拟环境
Write-Host "激活Python虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 设置代理环境变量
Write-Host "设置代理配置..." -ForegroundColor Yellow
$env:HTTP_PROXY = "socks5h://127.0.0.1:1080"
$env:HTTPS_PROXY = "socks5h://127.0.0.1:1080"
$env:USE_PROXY = "true"

# 检查依赖
Write-Host "检查Python依赖..." -ForegroundColor Yellow
if (!(Test-Path ".\requirements.txt")) {
    Write-Host "警告：找不到requirements.txt" -ForegroundColor Yellow
} else {
    # 可以选择性地检查和安装依赖
    # pip install -r requirements.txt
}

# 启动服务
Write-Host "启动FastAPI服务器..." -ForegroundColor Yellow
Write-Host "服务地址: http://localhost:8000" -ForegroundColor Cyan
Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Magenta

python main.py
