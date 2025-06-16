# PowerShell脚本：测试SSR代理配置
# 用于验证你的项目是否正确使用ShadowsocksR代理

Write-Host "=== Trading Console 代理配置测试 ===" -ForegroundColor Green
Write-Host ""

# 1. 检查Python环境
Write-Host "1. 检查Python环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✅ Python版本: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python未安装或不在PATH中" -ForegroundColor Red
    exit 1
}

# 2. 检查环境变量文件
Write-Host ""
Write-Host "2. 检查环境变量配置..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env文件存在" -ForegroundColor Green

    # 读取代理配置
    $envContent = Get-Content ".env"
    $useProxy = ($envContent | Where-Object { $_ -match "USE_PROXY=(.+)" }) -replace "USE_PROXY=", ""
    $proxyHost = ($envContent | Where-Object { $_ -match "PROXY_HOST=(.+)" }) -replace "PROXY_HOST=", ""
    $proxyPort = ($envContent | Where-Object { $_ -match "PROXY_PORT=(.+)" }) -replace "PROXY_PORT=", ""
    $proxyType = ($envContent | Where-Object { $_ -match "PROXY_TYPE=(.+)" }) -replace "PROXY_TYPE=", ""

    Write-Host "   USE_PROXY: $useProxy"
    Write-Host "   PROXY_HOST: $proxyHost"
    Write-Host "   PROXY_PORT: $proxyPort"
    Write-Host "   PROXY_TYPE: $proxyType"
} else {
    Write-Host "❌ .env文件不存在" -ForegroundColor Red
}

# 3. 检查SSR端口是否开放
Write-Host ""
Write-Host "3. 检查ShadowsocksR服务状态..." -ForegroundColor Yellow
try {
    $tcpConnection = Test-NetConnection -ComputerName "127.0.0.1" -Port 1080 -WarningAction SilentlyContinue
    if ($tcpConnection.TcpTestSucceeded) {
        Write-Host "✅ SSR服务运行正常 (端口1080)" -ForegroundColor Green
    } else {
        Write-Host "❌ SSR服务无法连接 (端口1080)" -ForegroundColor Red

        # 尝试常见的其他端口
        $otherPorts = @(1081, 7890, 8080)
        foreach ($port in $otherPorts) {
            $testResult = Test-NetConnection -ComputerName "127.0.0.1" -Port $port -WarningAction SilentlyContinue
            if ($testResult.TcpTestSucceeded) {
                Write-Host "✅ 发现SSR服务在端口 $port" -ForegroundColor Green
                Write-Host "   请更新.env文件中的PROXY_PORT=$port" -ForegroundColor Yellow
                break
            }
        }
    }
} catch {
    Write-Host "❌ 无法检查SSR服务状态" -ForegroundColor Red
}

# 4. 运行Python代理测试
Write-Host ""
Write-Host "4. 运行Python代理测试..." -ForegroundColor Yellow
try {
    python simple_proxy_test.py
} catch {
    Write-Host "❌ Python测试脚本运行失败" -ForegroundColor Red
}

# 5. 提供配置建议
Write-Host ""
Write-Host "=== 配置建议 ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "如果测试失败，请检查以下配置：" -ForegroundColor White
Write-Host ""
Write-Host "ShadowsocksR客户端设置："
Write-Host "  - 确保SSR客户端正在运行"
Write-Host "  - 检查'本地端口'设置（通常是1080）"
Write-Host "  - 启用'允许来自局域网的连接'"
Write-Host ""
Write-Host ".env文件配置："
Write-Host "  USE_PROXY=true"
Write-Host "  PROXY_HOST=127.0.0.1"
Write-Host "  PROXY_PORT=1080  # 或你的SSR实际端口"
Write-Host "  PROXY_TYPE=socks5"
Write-Host ""
Write-Host "常见问题解决："
Write-Host "  - 如果IP地址没有变化，检查SSR是否正常工作"
Write-Host "  - 如果连接超时，尝试其他端口（1081, 7890）"
Write-Host "  - 如果OKX访问失败，检查SSR节点是否可用"

Write-Host ""
Write-Host "测试完成！" -ForegroundColor Green
