@echo off
echo ====================================
echo 启动交易控制台后端服务
echo ====================================

cd /d C:\trading_console\backend

if not exist "venv\Scripts\activate.bat" (
    echo 错误：找不到Python虚拟环境
    echo 请先运行: python -m venv venv
    pause
    exit /b 1
)

echo 激活Python虚拟环境...
call venv\Scripts\activate.bat

echo 设置代理环境变量...
set HTTP_PROXY=socks5h://127.0.0.1:1080
set HTTPS_PROXY=socks5h://127.0.0.1:1080
set USE_PROXY=true

echo 启动FastAPI服务器...
echo 服务地址: http://localhost:8000
echo API文档: http://localhost:8000/docs
echo 按 Ctrl+C 停止服务
echo.

python main.py

pause
