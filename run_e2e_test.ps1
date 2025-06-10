# Trading Console 端到端测试启动脚本

param(
    [switch]$SkipServiceCheck,
    [switch]$AutoStartServices,
    [switch]$Verbose
)

Write-Host '=' * 80 -ForegroundColor Green
Write-Host '🚀 Trading Console 端到端测试' -ForegroundColor Green
Write-Host '测试流程：用户注册 → 登录 → 配置交易所 → 创建策略' -ForegroundColor Cyan
Write-Host '=' * 80 -ForegroundColor Green
Write-Host ''

# 检查Python是否可用
Write-Host '🔍 检查测试环境...' -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host '❌ Python 未安装或不在 PATH 中' -ForegroundColor Red
    Write-Host '请安装 Python 3.7+ 并确保在 PATH 中' -ForegroundColor Yellow
    exit 1
}

# 检查必要的Python包
Write-Host '📦 检查Python依赖...' -ForegroundColor Yellow
try {
    python -c 'import aiohttp, asyncio' 2>$null
    Write-Host '✅ aiohttp 已安装' -ForegroundColor Green
} catch {
    Write-Host '⚠️ 正在安装 aiohttp...' -ForegroundColor Yellow
    pip install aiohttp
}

if (-not $SkipServiceCheck) {
    # 检查后端服务
    Write-Host ''
    Write-Host '🔍 检查服务状态...' -ForegroundColor Yellow

    $backendRunning = $false
    $frontendRunning = $false

    try {
        $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -Method GET -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host '✅ 后端服务正在运行 (端口 8000)' -ForegroundColor Green
            $backendRunning = $true
        }
    } catch {
        Write-Host '❌ 后端服务未运行 (端口 8000)' -ForegroundColor Red
    }

    try {
        $response = Invoke-WebRequest -Uri 'http://localhost:5173' -Method GET -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host '✅ 前端服务正在运行 (端口 5173)' -ForegroundColor Green
            $frontendRunning = $true
        }
    } catch {
        Write-Host '⚠️ 前端服务未运行 (端口 5173)' -ForegroundColor Yellow
    }

    # 自动启动服务（如果请求）
    if ($AutoStartServices) {
        if (-not $backendRunning) {
            Write-Host ''
            Write-Host '🚀 启动后端服务...' -ForegroundColor Yellow
            Start-Process -FilePath 'powershell' -ArgumentList '-Command', "cd '$PWD\backend'; python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000" -WindowStyle Normal
            Write-Host '⏳ 等待后端服务启动...' -ForegroundColor Yellow
            Start-Sleep -Seconds 8

            # 再次检查
            try {
                $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -Method GET -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    Write-Host '✅ 后端服务启动成功' -ForegroundColor Green
                    $backendRunning = $true
                }
            } catch {
                Write-Host '❌ 后端服务启动失败' -ForegroundColor Red
            }
        }

        if (-not $frontendRunning) {
            Write-Host ''
            Write-Host '🚀 启动前端服务...' -ForegroundColor Yellow
            Start-Process -FilePath 'powershell' -ArgumentList '-Command', "cd '$PWD\frontend'; npm run dev" -WindowStyle Normal
            Write-Host '⏳ 等待前端服务启动...' -ForegroundColor Yellow
            Start-Sleep -Seconds 10

            # 再次检查
            try {
                $response = Invoke-WebRequest -Uri 'http://localhost:5173' -Method GET -TimeoutSec 5
                if ($response.StatusCode -eq 200) {
                    Write-Host '✅ 前端服务启动成功' -ForegroundColor Green
                    $frontendRunning = $true
                }
            } catch {
                Write-Host '⚠️ 前端服务可能仍在启动中' -ForegroundColor Yellow
            }
        }
    }

    # 服务状态汇总
    Write-Host ''
    if (-not $backendRunning) {
        Write-Host '⚠️ 后端服务未运行，部分测试可能失败' -ForegroundColor Yellow
        Write-Host '   启动后端: cd backend && python -m uvicorn main:app --reload' -ForegroundColor Gray
    }

    if (-not $frontendRunning) {
        Write-Host '⚠️ 前端服务未运行，前端测试将跳过' -ForegroundColor Yellow
        Write-Host '   启动前端: cd frontend && npm run dev' -ForegroundColor Gray
    }
}

# 运行端到端测试
Write-Host ''
Write-Host '🧪 开始执行端到端测试...' -ForegroundColor Cyan
Write-Host ''

$testStartTime = Get-Date

try {
    if ($Verbose) {
        python e2e_test_registration_to_strategy.py -v
    } else {
        python e2e_test_registration_to_strategy.py
    }

    $exitCode = $LASTEXITCODE
    $testEndTime = Get-Date
    $testDuration = ($testEndTime - $testStartTime).TotalSeconds

    Write-Host ''
    Write-Host '=' * 80 -ForegroundColor Blue

    if ($exitCode -eq 0) {
        Write-Host '🎉 端到端测试成功完成！' -ForegroundColor Green
        Write-Host "⏱️ 测试耗时: $($testDuration.ToString('F1')) 秒" -ForegroundColor Cyan
        Write-Host ''
        Write-Host '🌟 您的交易控制台已准备就绪！' -ForegroundColor Green
        Write-Host ''
        Write-Host '📱 快速访问:' -ForegroundColor Yellow
        Write-Host '   • 前端界面: http://localhost:5173' -ForegroundColor White
        Write-Host '   • 后端API: http://localhost:8000' -ForegroundColor White
        Write-Host '   • API文档: http://localhost:8000/docs' -ForegroundColor White
        Write-Host ''
        Write-Host '🚀 下一步建议:' -ForegroundColor Yellow
        Write-Host '   1. 在浏览器中打开前端界面测试用户交互' -ForegroundColor White
        Write-Host '   2. 查看API文档了解所有可用端点' -ForegroundColor White
        Write-Host '   3. 配置真实的交易所API密钥（使用测试网络）' -ForegroundColor White
        Write-Host '   4. 创建和测试交易策略' -ForegroundColor White
    } else {
        Write-Host '❌ 端到端测试失败' -ForegroundColor Red
        Write-Host "⏱️ 测试耗时: $($testDuration.ToString('F1')) 秒" -ForegroundColor Cyan
        Write-Host ''
        Write-Host '🔧 故障排除建议:' -ForegroundColor Yellow
        Write-Host '   1. 检查后端服务是否正常运行' -ForegroundColor White
        Write-Host '   2. 检查数据库连接配置' -ForegroundColor White
        Write-Host '   3. 查看详细错误日志' -ForegroundColor White
        Write-Host '   4. 运行基础测试: .\run_backend_tests.ps1' -ForegroundColor White
    }

} catch {
    Write-Host "💥 测试执行异常: $($_.Exception.Message)" -ForegroundColor Red
    $exitCode = 1
}

Write-Host '=' * 80 -ForegroundColor Blue

# 提供其他测试选项
Write-Host ''
Write-Host '🔧 其他测试选项:' -ForegroundColor Yellow
Write-Host '   • 运行所有测试: .\run_all_tests.ps1' -ForegroundColor Gray
Write-Host '   • 后端单元测试: .\run_backend_tests.ps1' -ForegroundColor Gray
Write-Host '   • 前端组件测试: .\run_frontend_tests.ps1' -ForegroundColor Gray
Write-Host '   • 性能压力测试: .\run_performance_tests.ps1' -ForegroundColor Gray

exit $exitCode
