# 测试连接功能修复
# 测试ticker端点的URL格式修复

Write-Host '🔧 Testing Connection Fix' -ForegroundColor Green
Write-Host '=' * 40

$backendUrl = 'http://localhost:8000'

# 快速注册和登录测试用户
$timestamp = [int](Get-Date -UFormat %s)
$testUser = @{
    username = "testuser_$timestamp"
    email    = "test_$timestamp@example.com"
    password = 'TestPassword123'
} | ConvertTo-Json

$headers = @{ 'Content-Type' = 'application/json' }

Write-Host 'Registering test user...' -ForegroundColor Yellow
$registerResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/register" -Method Post -Body $testUser -Headers $headers

$loginData = "username=$(($testUser | ConvertFrom-Json).username)&password=$(($testUser | ConvertFrom-Json).password)"
$loginHeaders = @{ 'Content-Type' = 'application/x-www-form-urlencoded' }

Write-Host 'Logging in...' -ForegroundColor Yellow
$loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" -Method Post -Body $loginData -Headers $loginHeaders
$token = $loginResponse.access_token

$authHeaders = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}

# 创建测试交易所账户
$exchangeData = @{
    exchange_name  = 'okex'
    api_key        = 'test_api_key_12345'
    api_secret     = 'test_api_secret_67890'
    api_passphrase = 'test_passphrase'
    is_testnet     = $true
} | ConvertTo-Json

Write-Host 'Creating test exchange account...' -ForegroundColor Yellow
$newExchange = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/" -Method Post -Body $exchangeData -Headers $authHeaders
$accountId = $newExchange.id

Write-Host "✅ Exchange account created: ID $accountId" -ForegroundColor Green

# 测试修复前的URL格式 (应该失败)
Write-Host "`nTesting OLD format (BTC/USDT) - Should fail..." -ForegroundColor Red
try {
    Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$accountId/ticker/BTC/USDT" -Method Get -Headers $authHeaders
    Write-Host '❌ Old format unexpectedly worked' -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host '✅ Old format correctly failed with 404 (Not Found)' -ForegroundColor Green
    } else {
        Write-Host "❌ Old format failed with unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# 测试修复后的URL格式 (应该返回400而不是404)
Write-Host "`nTesting NEW format (BTCUSDT) - Should return 400 BadRequest..." -ForegroundColor Cyan
try {
    Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$accountId/ticker/BTCUSDT" -Method Get -Headers $authHeaders
    Write-Host '✅ New format worked (unexpected but good)' -ForegroundColor Green
} catch {
    if ($_.Exception.Response.StatusCode -eq 404) {
        Write-Host '❌ New format still returns 404 - Route issue!' -ForegroundColor Red
    } elseif ($_.Exception.Response.StatusCode -eq 400) {
        Write-Host '✅ New format correctly returns 400 (BadRequest) - Route exists!' -ForegroundColor Green
    } else {
        Write-Host "⚠️ New format returns: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

# 清理
Write-Host "`nCleaning up..." -ForegroundColor Gray
Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$accountId" -Method Delete -Headers $authHeaders

Write-Host "`n🎯 Test Results Summary:" -ForegroundColor Cyan
Write-Host '- Old format (BTC/USDT): Should fail with 404' -ForegroundColor Gray
Write-Host '- New format (BTCUSDT): Should fail with 400 (route exists, invalid API)' -ForegroundColor Gray
Write-Host "`n✅ If new format returns 400 instead of 404, the fix is working!" -ForegroundColor Green
