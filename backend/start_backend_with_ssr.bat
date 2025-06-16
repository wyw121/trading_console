@echo off
echo 🚀 启动交易控制台后端服务 (SSR代理)
echo ==================================================

cd /d %~dp0

echo 📍 当前目录: %CD%

REM 检查Python
py --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python未安装或未配置PATH
    pause
    exit /b 1
)

echo ✅ Python环境检查通过

REM 检查.env文件
if not exist ".env" (
    echo ❌ .env配置文件不存在
    pause
    exit /b 1
)

echo ✅ .env配置文件存在

echo.
echo 📋 SSR代理配置:
echo    代理类型: SOCKS5
echo    代理地址: 127.0.0.1:1080  
echo    DNS解析: 通过代理 (socks5h://)
echo    环境变量: HTTP_PROXY, HTTPS_PROXY

echo.
echo 🔄 启动后端服务...
echo 💡 提示: 按 Ctrl+C 停止服务
echo.

py main.py

echo.
echo ⏹️ 服务已停止
pause
