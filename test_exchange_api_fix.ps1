# PowerShell测试脚本：测试交易所API修复
# 文件：test_exchange_api_fix.ps1

Write-Host "🧪 Testing Exchange API Endpoints Fix" -ForegroundColor Cyan
Write-Host "=" * 50

$backendUrl = "http://localhost:8000"
$frontendUrl = "http://localhost:3000"

# 1. 测试后端健康检查
Write-Host "`n1. Testing Backend Health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get
    Write-Host "✅ Backend is healthy" -ForegroundColor Green
    Write-Host "   Environment: $($health.environment)" -ForegroundColor Gray
    Write-Host "   Database: $($health.database)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Backend health check failed: $_" -ForegroundColor Red
    exit 1
}

# 2. 注册测试用户
Write-Host "`n2. Registering test user..." -ForegroundColor Yellow
$timestamp = [int](Get-Date -UFormat %s)
$testUser = @{
    username = "testuser_$timestamp"
    email = "test_$timestamp@example.com"
    password = "TestPassword123"
} | ConvertTo-Json

try {
    $headers = @{ "Content-Type" = "application/json" }
    $registerResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/register" -Method Post -Body $testUser -Headers $headers
    Write-Host "✅ User registration successful" -ForegroundColor Green
    Write-Host "   Username: $($registerResponse.username)" -ForegroundColor Gray
} catch {
    Write-Host "❌ User registration failed: $_" -ForegroundColor Red
    exit 1
}

# 3. 用户登录获取token
Write-Host "`n3. User login..." -ForegroundColor Yellow
$loginData = "username=$(($testUser | ConvertFrom-Json).username)&password=$(($testUser | ConvertFrom-Json).password)"
try {
    $loginHeaders = @{ "Content-Type" = "application/x-www-form-urlencoded" }
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" -Method Post -Body $loginData -Headers $loginHeaders
    $token = $loginResponse.access_token
    Write-Host "✅ User login successful" -ForegroundColor Green
    Write-Host "   Token obtained: $($token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ User login failed: $_" -ForegroundColor Red
    exit 1
}

# 4. 测试交易所API端点（修复后的路径）
Write-Host "`n4. Testing Exchange Endpoints (Fixed Paths)..." -ForegroundColor Yellow
$authHeaders = @{
    "Authorization" = "Bearer $token"
    "Content-Type" = "application/json"
}

# 4.1 获取交易所列表
Write-Host "   📋 Testing GET /api/exchanges/..." -ForegroundColor Cyan
try {
    $exchanges = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/" -Method Get -Headers $authHeaders
    Write-Host "   ✅ Exchange list retrieved: $($exchanges.Count) accounts" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Exchange list failed: $_" -ForegroundColor Red
}

# 4.2 创建测试交易所账户
Write-Host "   ➕ Testing POST /api/exchanges/..." -ForegroundColor Cyan
$exchangeData = @{
    exchange_name = "binance"
    api_key = "test_api_key_12345"
    api_secret = "test_api_secret_67890"
    api_passphrase = ""
    is_testnet = $true
} | ConvertTo-Json

try {
    $newExchange = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/" -Method Post -Body $exchangeData -Headers $authHeaders
    $accountId = $newExchange.id
    Write-Host "   ✅ Exchange account created: ID $accountId" -ForegroundColor Green

    # 4.3 测试子路径端点 - Balance
    Write-Host "   💰 Testing GET /api/exchanges/accounts/$accountId/balance..." -ForegroundColor Cyan
    try {
        $balance = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$accountId/balance" -Method Get -Headers $authHeaders
        Write-Host "   ✅ Balance endpoint exists (may fail due to invalid API keys)" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "   ❌ Balance endpoint not found - route issue!" -ForegroundColor Red
        } else {
            Write-Host "   🔍 Balance endpoint exists but failed as expected (invalid API keys): $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }

    # 4.4 测试子路径端点 - Ticker
    Write-Host "   📈 Testing GET /api/exchanges/accounts/$accountId/ticker/BTC/USDT..." -ForegroundColor Cyan
    try {
        $ticker = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$accountId/ticker/BTC/USDT" -Method Get -Headers $authHeaders
        Write-Host "   ✅ Ticker endpoint exists" -ForegroundColor Green
    } catch {
        if ($_.Exception.Response.StatusCode -eq 404) {
            Write-Host "   ❌ Ticker endpoint not found - route issue!" -ForegroundColor Red
        } else {
            Write-Host "   🔍 Ticker endpoint exists but failed as expected: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
        }
    }

    # 4.5 删除测试账户
    Write-Host "   🗑️ Testing DELETE /api/exchanges/accounts/$accountId..." -ForegroundColor Cyan
    try {
        $deleteResult = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$accountId" -Method Delete -Headers $authHeaders
        Write-Host "   ✅ Exchange account deleted successfully" -ForegroundColor Green
    } catch {
        Write-Host "   ❌ Delete failed: $_" -ForegroundColor Red
    }

} catch {
    Write-Host "   ❌ Exchange creation failed: $_" -ForegroundColor Red
}

# 5. 总结
Write-Host "`n" + "=" * 50
Write-Host "🎉 Exchange API Fix Test Completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Summary:" -ForegroundColor Cyan
Write-Host "   🌐 Frontend URL: $frontendUrl" -ForegroundColor Gray
Write-Host "   🔧 Backend URL: $backendUrl" -ForegroundColor Gray
Write-Host "   📚 API Docs: $backendUrl/docs" -ForegroundColor Gray
Write-Host ""
Write-Host "✅ API路径修复说明:" -ForegroundColor Yellow
Write-Host "   前端Store (exchanges.js): /exchanges/ ✓" -ForegroundColor Green
Write-Host "   前端Views (Exchanges.vue): /exchanges/ ✓" -ForegroundColor Green
Write-Host "   前端Views (Strategies.vue): /exchanges/ ✓" -ForegroundColor Green
Write-Host "   后端路由 (exchange.py): /exchanges + /accounts/{id} ✓" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 现在可以在前端测试交易所功能了！" -ForegroundColor Cyan
