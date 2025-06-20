# 完整启动脚本 - 同时启动前后端
Write-Host "启动交易控制台完整服务..." -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan

# 检查项目目录
if (!(Test-Path "C:\trading_console")) {
    Write-Host "错误：找不到项目目录 C:\trading_console" -ForegroundColor Red
    exit 1
}

Set-Location "C:\trading_console"

# 检查SSR代理（可选）
Write-Host "检查SSR代理状态..." -ForegroundColor Yellow
$proxyCheck = netstat -an | Select-String ":1080"
if ($proxyCheck) {
    Write-Host "✅ SSR代理服务正在运行 (端口1080)" -ForegroundColor Green
} else {
    Write-Host "⚠️ 未检测到SSR代理服务，OKX API可能需要代理" -ForegroundColor Yellow
}

# 启动后端（后台）
Write-Host "`n启动后端服务..." -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan

$backendScript = Join-Path $PWD "start_backend.ps1"
if (Test-Path $backendScript) {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File `"$backendScript`"" -WindowStyle Normal
} else {
    Write-Host "错误：找不到后端启动脚本" -ForegroundColor Red
    exit 1
}

# 等待后端启动
Write-Host "等待后端服务启动..." -ForegroundColor Yellow
$backendReady = $false
$maxAttempts = 15
$attempt = 0

while (-not $backendReady -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 2
    $attempt++
    Write-Host "检查后端状态... ($attempt/$maxAttempts)" -ForegroundColor Gray

    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ 后端服务启动成功" -ForegroundColor Green
            $backendReady = $true
        }
    } catch {
        # 继续等待
    }
}

if (-not $backendReady) {
    Write-Host "⚠️ 后端服务启动时间较长，请手动检查" -ForegroundColor Yellow
    Write-Host "后端窗口应该已经打开，请查看启动状态" -ForegroundColor Yellow
}

# 启动前端
Write-Host "`n启动前端服务..." -ForegroundColor Yellow
Write-Host "===============================================" -ForegroundColor Cyan

$frontendScript = Join-Path $PWD "start_frontend.ps1"
if (Test-Path $frontendScript) {
    Start-Process -FilePath "powershell.exe" -ArgumentList "-ExecutionPolicy Bypass -File `"$frontendScript`"" -WindowStyle Normal
} else {
    Write-Host "错误：找不到前端启动脚本" -ForegroundColor Red
    exit 1
}

# 等待一下让前端启动
Start-Sleep -Seconds 3

# 显示服务信息
Write-Host "`n✅ 所有服务启动完成" -ForegroundColor Green
Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "🚀 后端服务: http://localhost:8000" -ForegroundColor Cyan
Write-Host "🎨 前端应用: http://localhost:3000" -ForegroundColor Cyan
Write-Host "📚 API文档: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "📖 ReDoc文档: http://localhost:8000/redoc" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

# 提供快速访问选项
Write-Host "`n选择要打开的服务:" -ForegroundColor Yellow
Write-Host "1. 前端应用 (http://localhost:3000)" -ForegroundColor White
Write-Host "2. API文档 (http://localhost:8000/docs)" -ForegroundColor White
Write-Host "3. 健康检查 (http://localhost:8000/health)" -ForegroundColor White
Write-Host "4. 不自动打开" -ForegroundColor White

$choice = Read-Host "请输入选择 (1-4)"

switch ($choice) {
    "1" {
        Start-Process "http://localhost:3000"
        Write-Host "已打开前端应用" -ForegroundColor Green
    }
    "2" {
        Start-Process "http://localhost:8000/docs"
        Write-Host "已打开API文档" -ForegroundColor Green
    }
    "3" {
        Start-Process "http://localhost:8000/health"
        Write-Host "已打开健康检查页面" -ForegroundColor Green
    }
    "4" {
        Write-Host "未自动打开浏览器" -ForegroundColor Gray
    }
    default {
        Write-Host "无效选择，未自动打开浏览器" -ForegroundColor Yellow
    }
}

Write-Host "`n📝 注意事项:" -ForegroundColor Yellow
Write-Host "- 前后端服务在单独的PowerShell窗口中运行" -ForegroundColor White
Write-Host "- 要停止服务，请在对应窗口中按 Ctrl+C" -ForegroundColor White
Write-Host "- 如果端口被占用，服务会自动尝试其他端口" -ForegroundColor White
Write-Host "- 开发模式支持热重载，修改代码后会自动更新" -ForegroundColor White

Write-Host "`n🎉 交易控制台已成功启动！" -ForegroundColor Green
Write-Host "按任意键退出此脚本..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
