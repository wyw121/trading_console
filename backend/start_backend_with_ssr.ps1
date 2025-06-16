# 启动交易控制台后端服务 (SSR代理)
Write-Host '🚀 启动交易控制台后端服务 (SSR代理)' -ForegroundColor Green
Write-Host '=' * 50

Set-Location $PSScriptRoot

Write-Host "📍 当前目录: $(Get-Location)"

# 检查Python
try {
    $pythonVersion = py --version
    Write-Host "✅ Python环境检查通过: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host '❌ Python未安装或未配置PATH' -ForegroundColor Red
    Read-Host '按任意键退出'
    exit 1
}

# 检查.env文件
if (-not (Test-Path '.env')) {
    Write-Host '❌ .env配置文件不存在' -ForegroundColor Red
    Read-Host '按任意键退出'
    exit 1
}

Write-Host '✅ .env配置文件存在' -ForegroundColor Green

# 检查SSR代理端口
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.ConnectAsync('127.0.0.1', 1080).Wait(3000)
    if ($tcpClient.Connected) {
        Write-Host '✅ SSR代理端口1080可用' -ForegroundColor Green
        $tcpClient.Close()
    } else {
        Write-Host '⚠️ SSR代理端口1080不可用，请检查SSR客户端' -ForegroundColor Yellow
    }
} catch {
    Write-Host '⚠️ 无法检测SSR代理状态' -ForegroundColor Yellow
}

Write-Host ''
Write-Host '📋 SSR代理配置:' -ForegroundColor Cyan
Write-Host '   代理类型: SOCKS5'
Write-Host '   代理地址: 127.0.0.1:1080'
Write-Host '   DNS解析: 通过代理 (socks5h://)'
Write-Host '   环境变量: HTTP_PROXY, HTTPS_PROXY'

Write-Host ''
Write-Host '🔄 启动后端服务...' -ForegroundColor Yellow
Write-Host '💡 提示: 按 Ctrl+C 停止服务'
Write-Host ''

try {
    py main.py
} catch {
    Write-Host "❌ 服务启动失败: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ''
Write-Host '⏹️ 服务已停止' -ForegroundColor Yellow
Read-Host '按任意键退出'
