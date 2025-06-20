@echo off
echo ====================================
echo 启动交易控制台前端服务
echo ====================================

cd /d C:\trading_console\frontend

if not exist "package.json" (
    echo 错误：找不到package.json
    pause
    exit /b 1
)

echo 检查Node.js环境...
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误：未找到Node.js
    echo 请先安装Node.js: https://nodejs.org/
    pause
    exit /b 1
)

echo Node.js版本:
node --version
echo npm版本:
npm --version

if not exist "node_modules" (
    echo 安装npm依赖...
    npm install
    if errorlevel 1 (
        echo 依赖安装失败，尝试使用国内镜像...
        npm install --registry https://registry.npmmirror.com
    )
) else (
    echo 依赖已存在，跳过安装
)

echo 启动Vite开发服务器...
echo 前端地址: http://localhost:3000
echo 按 Ctrl+C 停止服务
echo.

npm run dev

pause
