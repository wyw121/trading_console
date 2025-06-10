# PowerShell script to run the end-to-end test
Write-Host "🚀 启动Trading Console端到端测试..." -ForegroundColor Green
Write-Host "=" * 50

# 检查后端服务
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ 后端服务正常运行" -ForegroundColor Green
        $healthData = $response.Content | ConvertFrom-Json
        Write-Host "   环境: $($healthData.environment)"
        Write-Host "   数据库: $($healthData.database)"
    }
} catch {
    Write-Host "❌ 后端服务连接失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 运行Python测试
Write-Host "`n🐍 运行Python测试脚本..." -ForegroundColor Yellow
python simple_e2e_test_working.py

Write-Host "`n✅ 测试脚本执行完成" -ForegroundColor Green
