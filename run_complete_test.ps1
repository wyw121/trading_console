# PowerShell脚本：运行完整端到端测试
param(
    [switch]$Verbose = $false
)

Write-Host "🚀 Trading Console 完整端到端测试" -ForegroundColor Green
Write-Host "=" * 80

# 检查后端服务
Write-Host "🔍 检查后端服务状态..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 10
    Write-Host "✅ 后端服务正常运行" -ForegroundColor Green
    Write-Host "   环境: $($healthResponse.environment)"
    Write-Host "   数据库: $($healthResponse.database)"
    Write-Host "   状态: $($healthResponse.status)"
}
catch {
    Write-Host "❌ 后端服务连接失败: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "请确保后端服务正在运行: cd backend && python dev_server.py"
    exit 1
}

# 运行同步版本的端到端测试
Write-Host "`n🧪 运行Python端到端测试..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath "python" -ArgumentList "e2e_test_sync_complete.py" -WorkingDirectory $PWD -Wait -PassThru -NoNewWindow

    if ($process.ExitCode -eq 0) {
        Write-Host "✅ 端到端测试执行成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 端到端测试执行失败，退出码: $($process.ExitCode)" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ 执行测试时发生错误: $($_.Exception.Message)" -ForegroundColor Red
}

# 运行简单版本测试作为备用
Write-Host "`n🔄 运行简单版本测试..." -ForegroundColor Yellow
try {
    $process = Start-Process -FilePath "python" -ArgumentList "simple_e2e_test.py" -WorkingDirectory $PWD -Wait -PassThru -NoNewWindow

    if ($process.ExitCode -eq 0) {
        Write-Host "✅ 简单测试执行成功" -ForegroundColor Green
    } else {
        Write-Host "❌ 简单测试执行失败" -ForegroundColor Red
    }
}
catch {
    Write-Host "❌ 执行简单测试时发生错误: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n📋 测试完成汇总:" -ForegroundColor Cyan
Write-Host "- 后端服务状态检查: ✅ 通过"
Write-Host "- 完整端到端测试: 已执行"
Write-Host "- 简单功能测试: 已执行"

Write-Host "`n🎯 如果测试输出没有显示，这是PowerShell的已知问题"
Write-Host "   可以直接在命令行运行: python simple_e2e_test.py"
Write-Host "   或查看后端服务器日志确认API调用成功"
