# 🧪 Trading Console 完整测试套件
# run_all_tests.ps1

param(
    [switch]$Verbose,
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$SkipIntegration,
    [string]$TestLevel = "comprehensive"
)

Write-Host "=" * 80 -ForegroundColor Magenta
Write-Host "🚀 Trading Console - 完整测试套件" -ForegroundColor Magenta
Write-Host "=" * 80 -ForegroundColor Magenta
Write-Host ""

$StartTime = Get-Date
$OverallPassed = 0
$OverallFailed = 0

function Run-TestSuite {
    param([string]$Name, [string]$Script, [array]$Args = @())

    Write-Host ""
    Write-Host "🔥 开始 $Name 测试" -ForegroundColor Yellow
    Write-Host "-" * 50 -ForegroundColor DarkYellow

    $argList = @($Script) + $Args
    if ($Verbose) { $argList += "-Verbose" }

    try {
        & powershell.exe -ExecutionPolicy Bypass -File @argList
        $exitCode = $LASTEXITCODE

        if ($exitCode -eq 0) {
            Write-Host "✅ $Name 测试套件通过" -ForegroundColor Green
            $script:OverallPassed++
        } else {
            Write-Host "❌ $Name 测试套件失败 (退出码: $exitCode)" -ForegroundColor Red
            $script:OverallFailed++
        }
    } catch {
        Write-Host "❌ $Name 测试套件执行失败: $($_.Exception.Message)" -ForegroundColor Red
        $script:OverallFailed++
    }
}

# 1. 后端测试
if (-not $SkipBackend) {
    Run-TestSuite "后端API" ".\run_backend_tests.ps1"
}

# 2. 前端测试
if (-not $SkipFrontend) {
    Run-TestSuite "前端组件" ".\run_frontend_tests.ps1"
}

# 3. 集成测试
if (-not $SkipIntegration) {
    Write-Host ""
    Write-Host "🔗 开始集成测试" -ForegroundColor Yellow
    Write-Host "-" * 50 -ForegroundColor DarkYellow

    # 检查Docker环境
    try {
        $dockerVersion = docker --version
        Write-Host "Docker版本: $dockerVersion" -ForegroundColor Cyan

        # 检查docker-compose
        $composeVersion = docker-compose --version
        Write-Host "Docker Compose版本: $composeVersion" -ForegroundColor Cyan

        Write-Host "✅ Docker 环境可用" -ForegroundColor Green
        $OverallPassed++
    } catch {
        Write-Host "❌ Docker 环境不可用: $($_.Exception.Message)" -ForegroundColor Red
        $OverallFailed++
    }

    # 数据库连接测试
    try {
        Write-Host "🗄️ 测试数据库连接..." -ForegroundColor Yellow
        Set-Location "backend"
        python test_db.py
        Set-Location ".."
        Write-Host "✅ 数据库连接测试通过" -ForegroundColor Green
        $OverallPassed++
    } catch {
        Write-Host "❌ 数据库连接测试失败" -ForegroundColor Red
        $OverallFailed++
    }

    # API健康检查
    try {
        Write-Host "🌐 测试API健康检查..." -ForegroundColor Yellow

        # 启动后端服务器（后台）
        $serverJob = Start-Job -ScriptBlock {
            Set-Location $using:PWD
            Set-Location "backend"
            python -m uvicorn app:app --host 0.0.0.0 --port 8000
        }

        Start-Sleep 5  # 等待服务器启动

        # 测试健康检查端点
        $response = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 10
        if ($response.status -eq "healthy") {
            Write-Host "✅ API健康检查通过" -ForegroundColor Green
            $OverallPassed++
        } else {
            throw "API响应状态异常"
        }

        # 停止服务器
        Stop-Job -Job $serverJob
        Remove-Job -Job $serverJob

    } catch {
        Write-Host "❌ API健康检查失败: $($_.Exception.Message)" -ForegroundColor Red
        $OverallFailed++

        # 清理后台任务
        if ($serverJob) {
            Stop-Job -Job $serverJob -ErrorAction SilentlyContinue
            Remove-Job -Job $serverJob -ErrorAction SilentlyContinue
        }
    }
}

# 生成测试报告
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Magenta
Write-Host "📊 完整测试报告" -ForegroundColor Magenta
Write-Host "=" * 80 -ForegroundColor Magenta
Write-Host "🕐 开始时间: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "🏁 结束时间: $($EndTime.ToString('yyyy-MM-dd HH:mm:ss'))" -ForegroundColor Cyan
Write-Host "⏱️  总耗时: $($Duration.TotalSeconds.ToString('F1')) 秒" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ 通过测试套件: $OverallPassed" -ForegroundColor Green
Write-Host "❌ 失败测试套件: $OverallFailed" -ForegroundColor Red

if ($OverallPassed + $OverallFailed -gt 0) {
    $successRate = [Math]::Round(($OverallPassed / ($OverallPassed + $OverallFailed)) * 100, 1)
    Write-Host "📈 总体成功率: $successRate%" -ForegroundColor Cyan
}

Write-Host ""

# 生成详细报告文件
$reportContent = @"
# Trading Console 测试报告

## 测试概览
- **测试时间**: $($StartTime.ToString('yyyy-MM-dd HH:mm:ss')) - $($EndTime.ToString('yyyy-MM-dd HH:mm:ss'))
- **总耗时**: $($Duration.TotalSeconds.ToString('F1')) 秒
- **通过套件**: $OverallPassed
- **失败套件**: $OverallFailed
- **成功率**: $successRate%

## 测试范围
- 后端API测试: $(if(-not $SkipBackend){'✅ 已执行'}else{'⏭️ 已跳过'})
- 前端组件测试: $(if(-not $SkipFrontend){'✅ 已执行'}else{'⏭️ 已跳过'})
- 集成测试: $(if(-not $SkipIntegration){'✅ 已执行'}else{'⏭️ 已跳过'})

## 建议
$(if($OverallFailed -gt 0){'⚠️ 发现测试失败，建议检查详细日志并修复问题'}else{'🎉 所有测试通过，系统状态良好'})

---
*报告生成时间: $(Get-Date)*
"@

$reportContent | Out-File -FilePath "test_report.md" -Encoding utf8
Write-Host "📄 详细测试报告已保存到: test_report.md" -ForegroundColor Blue

# 设置退出码
if ($OverallFailed -gt 0) {
    Write-Host ""
    Write-Host "⚠️  发现测试失败，请检查详细日志" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host ""
    Write-Host "🎉 所有测试通过，系统运行正常！" -ForegroundColor Green
    exit 0
}
