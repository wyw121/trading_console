@echo off
chcp 65001 >nul
echo ================================================
echo Trading Console 代理配置测试
echo ================================================
echo.

echo 1. 检查Python环境...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python未安装或不在PATH中
    pause
    exit /b 1
)
echo ✅ Python环境正常
echo.

echo 2. 检查环境变量配置...
if exist .env (
    echo ✅ .env文件存在
    echo 当前代理配置:
    findstr "USE_PROXY\|PROXY_HOST\|PROXY_PORT\|PROXY_TYPE" .env
) else (
    echo ❌ .env文件不存在
)
echo.

echo 3. 检查ShadowsocksR服务状态...
netstat -an | findstr ":1080.*LISTENING" >nul
if %errorlevel% equ 0 (
    echo ✅ 检测到端口1080监听（可能是SSR服务）
) else (
    echo ⚠️  端口1080未监听，检查其他常见端口...
    netstat -an | findstr ":1081.*LISTENING" >nul
    if %errorlevel% equ 0 (
        echo ✅ 检测到端口1081监听
        echo    请将.env中的PROXY_PORT改为1081
    ) else (
        netstat -an | findstr ":7890.*LISTENING" >nul
        if %errorlevel% equ 0 (
            echo ✅ 检测到端口7890监听
            echo    请将.env中的PROXY_PORT改为7890
        ) else (
            echo ❌ 未检测到常见代理端口，请确认SSR是否运行
        )
    )
)
echo.

echo 4. 运行Python代理测试...
python simple_proxy_test.py
echo.

echo ================================================
echo 配置建议
echo ================================================
echo.
echo 如果测试失败，请检查以下配置：
echo.
echo ShadowsocksR客户端：
echo   - 确保SSR客户端正在运行
echo   - 检查本地端口设置（通常是1080或1081）
echo   - 开启"允许来自局域网的连接"
echo.
echo .env文件配置：
echo   USE_PROXY=true
echo   PROXY_HOST=127.0.0.1
echo   PROXY_PORT=1080  # 或你的SSR实际端口
echo   PROXY_TYPE=socks5
echo.
echo 常见问题解决：
echo   - 如果IP地址没有变化，检查SSR是否正常工作
echo   - 如果连接超时，尝试其他端口
echo   - 如果OKX访问失败，检查SSR节点是否可用
echo.

pause
