# 代理配置和测试脚本
# 用于配置ShadowsocksR代理并测试连接

Write-Host "================================" -ForegroundColor Green
Write-Host "  Trading Console 代理配置脚本" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# 检查Python环境
Write-Host "1. 检查Python环境..." -ForegroundColor Yellow
python --version
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Python未安装或未添加到PATH" -ForegroundColor Red
    exit 1
}

# 安装依赖
Write-Host "2. 安装/更新Python依赖..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ 依赖安装失败" -ForegroundColor Red
    exit 1
}

# 检查ShadowsocksR配置
Write-Host "3. 代理配置指导..." -ForegroundColor Yellow
Write-Host ""
Write-Host "请确认以下ShadowsocksR设置："
Write-Host "  - ShadowsocksR客户端正在运行" -ForegroundColor Cyan
Write-Host "  - 本地SOCKS5端口（通常是1080）" -ForegroundColor Cyan
Write-Host "  - 已开启'允许来自局域网的连接'" -ForegroundColor Cyan
Write-Host ""

# 询问用户代理端口
$defaultPort = "1080"
$proxyPort = Read-Host "请输入ShadowsocksR的本地端口 (默认: $defaultPort)"
if ([string]::IsNullOrWhiteSpace($proxyPort)) {
    $proxyPort = $defaultPort
}

# 更新.env文件
Write-Host "4. 更新代理配置..." -ForegroundColor Yellow
$envContent = Get-Content .env -ErrorAction SilentlyContinue
if ($envContent) {
    # 更新现有配置
    $newContent = @()
    $updatedPort = $false

    foreach ($line in $envContent) {
        if ($line -match "^PROXY_PORT=") {
            $newContent += "PROXY_PORT=$proxyPort"
            $updatedPort = $true
        }
        elseif ($line -match "^USE_PROXY=") {
            $newContent += "USE_PROXY=true"
        }
        else {
            $newContent += $line
        }
    }

    # 如果没有找到PROXY_PORT，添加它
    if (-not $updatedPort) {
        $newContent += "PROXY_PORT=$proxyPort"
    }

    $newContent | Out-File .env -Encoding UTF8
}

Write-Host "✅ 代理配置已更新: 端口 $proxyPort" -ForegroundColor Green

# 运行代理测试
Write-Host "5. 运行代理连接测试..." -ForegroundColor Yellow
Write-Host ""
python test_proxy.py

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "配置完成！" -ForegroundColor Green
Write-Host ""
Write-Host "如果测试失败，请检查：" -ForegroundColor Yellow
Write-Host "1. ShadowsocksR客户端是否正在运行" -ForegroundColor White
Write-Host "2. 端口号是否正确（默认1080）" -ForegroundColor White
Write-Host "3. 防火墙是否阻止了连接" -ForegroundColor White
Write-Host "4. SSR服务器是否正常工作" -ForegroundColor White
Write-Host ""
Write-Host "测试成功后，可以启动服务器：python main.py" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
