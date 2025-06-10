# 🧪 后端完整测试脚本
# run_backend_tests.ps1

param(
    [switch]$Verbose,
    [switch]$SkipDatabase,
    [string]$TestLevel = "basic"
)

Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "🧪 Trading Console - 后端测试套件" -ForegroundColor Blue
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host ""

# 检查当前目录
$CurrentDir = Get-Location
Write-Host "📁 当前目录: $CurrentDir" -ForegroundColor Cyan

# 确保在正确的目录
if (-not (Test-Path "backend")) {
    Write-Host "❌ 未找到backend目录，请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

Set-Location "backend"
Write-Host "📂 切换到后端目录: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# 测试计数器
$TestPassed = 0
$TestFailed = 0

function Test-Component {
    param([string]$Name, [scriptblock]$TestBlock)

    Write-Host "🔍 测试: $Name" -ForegroundColor Yellow
    try {
        & $TestBlock
        Write-Host "✅ $Name - 通过" -ForegroundColor Green
        $script:TestPassed++
    } catch {
        Write-Host "❌ $Name - 失败: $($_.Exception.Message)" -ForegroundColor Red
        if ($Verbose) {
            Write-Host $_.Exception.StackTrace -ForegroundColor DarkRed
        }
        $script:TestFailed++
    }
    Write-Host ""
}

# 1. Python环境测试
Test-Component "Python环境" {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python未安装或不在PATH中"
    }
    Write-Host "   Python版本: $pythonVersion" -ForegroundColor White
}

# 2. 基础导入测试
Test-Component "基础模块导入" {
    $output = python minimal_test.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "基础模块导入失败: $output"
    }
    Write-Host "   基础模块导入正常" -ForegroundColor White
}

# 3. 完整导入测试
Test-Component "完整模块导入" {
    $output = python test_imports.py 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "完整模块导入失败: $output"
    }
    Write-Host "   所有模块导入正常" -ForegroundColor White
}

# 4. 数据库测试
if (-not $SkipDatabase) {
    Test-Component "数据库连接" {
        $output = python test_db.py 2>&1
        if ($output -like "*failed*" -or $output -like "*error*") {
            throw "数据库连接失败: $output"
        }
        Write-Host "   数据库连接正常" -ForegroundColor White
    }
}

# 5. API服务器启动测试
Test-Component "API服务器启动" {
    # 启动测试服务器（后台）
    $job = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        python -m uvicorn test_server:app --host 127.0.0.1 --port 8099 2>&1
    }

    # 等待服务器启动
    Start-Sleep 3

    try {
        # 测试API响应
        $response = Invoke-RestMethod -Uri "http://localhost:8099/" -TimeoutSec 5
        if (-not $response -or -not $response.message) {
            throw "API响应格式错误"
        }
        Write-Host "   API服务器响应正常: $($response.message)" -ForegroundColor White

        # 测试健康检查
        $health = Invoke-RestMethod -Uri "http://localhost:8099/health" -TimeoutSec 5
        Write-Host "   健康检查: $($health.status)" -ForegroundColor White
          } finally {
        # 停止测试服务器
        Stop-Job $job -ErrorAction SilentlyContinue
        Remove-Job $job -ErrorAction SilentlyContinue
    }
}

# 6. 依赖检查
Test-Component "依赖包检查" {
    $packages = @("fastapi", "uvicorn", "sqlalchemy", "ccxt", "pandas", "numpy")
    foreach ($package in $packages) {
        $result = python -c "import $package; print('$package OK')" 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "依赖包 $package 导入失败"
        }
    }
    Write-Host "   核心依赖包检查通过" -ForegroundColor White
}

# 测试结果汇总
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "📊 测试结果汇总" -ForegroundColor Blue
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host ""
Write-Host "✅ 通过: $TestPassed" -ForegroundColor Green
Write-Host "❌ 失败: $TestFailed" -ForegroundColor Red
Write-Host ""

if ($TestFailed -eq 0) {
    Write-Host "🎉 所有测试通过！后端环境配置正确。" -ForegroundColor Green
    $exitCode = 0
} else {
    Write-Host "⚠️ 有 $TestFailed 个测试失败，请检查配置。" -ForegroundColor Yellow
    $exitCode = 1
}

# 回到原目录
Set-Location $CurrentDir

Write-Host ""
Write-Host "测试完成时间: $(Get-Date)" -ForegroundColor Cyan
exit $exitCode
