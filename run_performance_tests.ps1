# 🚀 Trading Console 性能测试脚本
# run_performance_tests.ps1

param(
    [int]$Duration = 30,
    [int]$Concurrency = 10,
    [switch]$Verbose
)

Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "🚀 Trading Console - 性能测试套件" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host ""

$StartTime = Get-Date

# 检查性能测试工具
function Test-PerformanceTools {
    Write-Host "🔧 检查性能测试工具..." -ForegroundColor Yellow

    # 检查curl
    try {
        $curlVersion = curl --version | Select-Object -First 1
        Write-Host "✅ cURL: $curlVersion" -ForegroundColor Green
    } catch {
        Write-Host "❌ cURL 不可用，某些测试可能无法执行" -ForegroundColor Red
    }

    # 检查Python性能测试库
    try {
        Set-Location "backend"
        python -c "import time, concurrent.futures, requests; print('✅ Python性能测试库可用')"
        Set-Location ".."
        Write-Host "✅ Python性能测试库已准备" -ForegroundColor Green
    } catch {
        Write-Host "❌ Python性能测试库不可用" -ForegroundColor Red
    }
}

# API压力测试
function Test-APIPerformance {
    param([string]$BaseURL = "http://localhost:8000")

    Write-Host "🌐 API性能测试 (持续时间: ${Duration}秒, 并发: ${Concurrency})" -ForegroundColor Yellow

    # 创建Python性能测试脚本
    $perfScript = @"
import time
import requests
import concurrent.futures
import statistics
from datetime import datetime

def test_endpoint(url, endpoint_name):
    start = time.time()
    try:
        response = requests.get(url, timeout=10)
        elapsed = time.time() - start
        return {
            'endpoint': endpoint_name,
            'status': response.status_code,
            'time': elapsed,
            'success': response.status_code == 200
        }
    except Exception as e:
        elapsed = time.time() - start
        return {
            'endpoint': endpoint_name,
            'status': 0,
            'time': elapsed,
            'success': False,
            'error': str(e)
        }

def run_performance_test():
    base_url = '$BaseURL'
    endpoints = [
        ('/health', 'health_check'),
        ('/api/v1/health', 'api_health'),
        ('/', 'root')
    ]

    print(f'🚀 开始性能测试 - 基础URL: {base_url}')
    print(f'⏱️  测试时长: $Duration 秒')
    print(f'🔥 并发请求: $Concurrency')
    print('')

    results = []
    start_time = time.time()
    end_time = start_time + $Duration

    with concurrent.futures.ThreadPoolExecutor(max_workers=$Concurrency) as executor:
        while time.time() < end_time:
            # 为每个端点提交任务
            futures = []
            for endpoint, name in endpoints:
                url = f'{base_url}{endpoint}'
                future = executor.submit(test_endpoint, url, name)
                futures.append(future)

            # 收集结果
            for future in concurrent.futures.as_completed(futures, timeout=15):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f'❌ 请求失败: {e}')

    # 分析结果
    if not results:
        print('❌ 没有收集到性能数据')
        return

    successful_results = [r for r in results if r['success']]
    total_requests = len(results)
    successful_requests = len(successful_results)
    error_rate = ((total_requests - successful_requests) / total_requests) * 100

    if successful_results:
        response_times = [r['time'] for r in successful_results]
        avg_response_time = statistics.mean(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max_response_time
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0

    # 输出结果
    print('📊 性能测试结果:')
    print(f'🔢 总请求数: {total_requests}')
    print(f'✅ 成功请求: {successful_requests}')
    print(f'❌ 错误率: {error_rate:.2f}%')
    print(f'⚡ 平均响应时间: {avg_response_time*1000:.2f} ms')
    print(f'🚀 最快响应: {min_response_time*1000:.2f} ms')
    print(f'🐌 最慢响应: {max_response_time*1000:.2f} ms')
    print(f'📈 95%响应时间: {p95_response_time*1000:.2f} ms')
    print(f'💪 QPS: {successful_requests/$Duration:.2f} 请求/秒')

if __name__ == '__main__':
    run_performance_test()
"@

    $perfScript | Out-File -FilePath "backend\performance_test.py" -Encoding utf8

    # 启动后端服务器
    Write-Host "🔄 启动后端服务器..." -ForegroundColor Yellow
    $serverJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD
        Set-Location "backend"
        python -m uvicorn app:app --host 0.0.0.0 --port 8000
    }

    Start-Sleep 5  # 等待服务器启动

    try {
        # 运行性能测试
        Set-Location "backend"
        python performance_test.py
        Set-Location ".."
        Write-Host "✅ API性能测试完成" -ForegroundColor Green
    } finally {
        # 停止服务器
        Stop-Job -Job $serverJob -ErrorAction SilentlyContinue
        Remove-Job -Job $serverJob -ErrorAction SilentlyContinue
    }
}

# 前端构建性能测试
function Test-BuildPerformance {
    Write-Host "🔨 前端构建性能测试..." -ForegroundColor Yellow

    Set-Location "frontend"

    # 清理之前的构建
    if (Test-Path "dist") {
        Remove-Item -Path "dist" -Recurse -Force
    }

    $buildStart = Get-Date
    try {
        npm run build
        $buildEnd = Get-Date
        $buildDuration = ($buildEnd - $buildStart).TotalSeconds

        # 检查构建输出大小
        if (Test-Path "dist") {
            $distSize = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum
            $distSizeMB = [Math]::Round($distSize / 1MB, 2)

            Write-Host "✅ 前端构建完成" -ForegroundColor Green
            Write-Host "⏱️  构建时间: $($buildDuration.ToString('F1')) 秒" -ForegroundColor Cyan
            Write-Host "📦 构建大小: $distSizeMB MB" -ForegroundColor Cyan
        } else {
            Write-Host "❌ 构建失败，未生成dist目录" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ 前端构建失败: $($_.Exception.Message)" -ForegroundColor Red
    }

    Set-Location ".."
}

# 数据库性能测试
function Test-DatabasePerformance {
    Write-Host "🗄️ 数据库性能测试..." -ForegroundColor Yellow

    $dbPerfScript = @"
import time
import asyncio
from database import get_db, User
from sqlalchemy.orm import Session
from sqlalchemy import text

async def test_db_performance():
    print('🗄️  数据库性能测试开始')

    # 连接测试
    start = time.time()
    db = next(get_db())
    connect_time = time.time() - start
    print(f'📡 数据库连接时间: {connect_time*1000:.2f} ms')

    # 简单查询测试
    start = time.time()
    result = db.execute(text('SELECT 1')).fetchone()
    query_time = time.time() - start
    print(f'🔍 简单查询时间: {query_time*1000:.2f} ms')

    # 批量插入测试（如果用户表存在）
    try:
        start = time.time()
        # 测试查询用户表结构
        db.execute(text('SELECT COUNT(*) FROM users LIMIT 1'))
        table_time = time.time() - start
        print(f'📊 表查询时间: {table_time*1000:.2f} ms')
    except Exception as e:
        print(f'⚠️  用户表测试跳过: {e}')

    db.close()
    print('✅ 数据库性能测试完成')

if __name__ == '__main__':
    asyncio.run(test_db_performance())
"@

    $dbPerfScript | Out-File -FilePath "backend\db_performance_test.py" -Encoding utf8

    try {
        Set-Location "backend"
        python db_performance_test.py
        Set-Location ".."
        Write-Host "✅ 数据库性能测试完成" -ForegroundColor Green
    } catch {
        Write-Host "❌ 数据库性能测试失败: $($_.Exception.Message)" -ForegroundColor Red
        Set-Location ".."
    }
}

# 执行性能测试
Test-PerformanceTools
Write-Host ""

Test-DatabasePerformance
Write-Host ""

Test-BuildPerformance
Write-Host ""

Test-APIPerformance
Write-Host ""

# 测试完成
$EndTime = Get-Date
$TotalDuration = ($EndTime - $StartTime).TotalSeconds

Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "📊 性能测试完成" -ForegroundColor Magenta
Write-Host "=" * 60 -ForegroundColor Magenta
Write-Host "⏱️  总耗时: $($TotalDuration.ToString('F1')) 秒" -ForegroundColor Cyan
Write-Host "📝 性能测试脚本已保存到 backend/ 目录" -ForegroundColor Blue
Write-Host ""
Write-Host "🎯 性能优化建议:" -ForegroundColor Yellow
Write-Host "  • API响应时间应 < 200ms" -ForegroundColor White
Write-Host "  • 前端构建时间应 < 30s" -ForegroundColor White
Write-Host "  • 数据库查询应 < 50ms" -ForegroundColor White
Write-Host "  • 错误率应 < 1%" -ForegroundColor White
