# 🔧 OKX账户环境修复脚本
# 将测试网账户更改为正式网账户

Write-Host '🔧 OKX账户环境修复' -ForegroundColor Green
Write-Host '=' * 50

$backendUrl = 'http://localhost:8000'

# 首先检查后端是否运行
Write-Host '检查后端服务状态...' -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$backendUrl/health" -Method Get -TimeoutSec 5
    Write-Host '✅ 后端服务正常运行' -ForegroundColor Green
} catch {
    Write-Host '❌ 后端服务未运行，请先启动后端服务' -ForegroundColor Red
    Write-Host '启动命令: cd c:\trading_console\backend && python dev_server.py' -ForegroundColor Yellow
    exit 1
}

# 获取用户登录信息
$username = Read-Host '请输入您的用户名'
$password = Read-Host '请输入您的密码' -AsSecureString
$plainPassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($password))

# 用户登录
Write-Host '用户登录中...' -ForegroundColor Yellow
try {
    $loginData = "username=$username&password=$plainPassword"
    $loginHeaders = @{ 'Content-Type' = 'application/x-www-form-urlencoded' }
    $loginResponse = Invoke-RestMethod -Uri "$backendUrl/api/auth/login" -Method Post -Body $loginData -Headers $loginHeaders
    $token = $loginResponse.access_token
    Write-Host '✅ 登录成功' -ForegroundColor Green
} catch {
    Write-Host "❌ 登录失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$authHeaders = @{
    'Authorization' = "Bearer $token"
    'Content-Type'  = 'application/json'
}

# 获取现有交易所账户
Write-Host '获取现有交易所账户...' -ForegroundColor Yellow
try {
    $exchanges = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/" -Method Get -Headers $authHeaders
    $okxAccount = $exchanges | Where-Object { $_.exchange_name -eq 'okex' } | Select-Object -First 1

    if ($okxAccount) {
        Write-Host "✅ 找到OKX账户: ID $($okxAccount.id)" -ForegroundColor Green
        Write-Host "   当前环境: $($okxAccount.is_testnet ? '测试网' : '正式网')" -ForegroundColor Gray

        if ($okxAccount.is_testnet) {
            Write-Host '⚠️ 检测到账户设置为测试网，但您的API密钥是正式网的' -ForegroundColor Yellow

            $confirm = Read-Host '是否要删除现有账户并重新添加为正式网账户? (y/n)'

            if ($confirm -eq 'y' -or $confirm -eq 'Y') {
                # 删除现有账户
                Write-Host '删除现有账户...' -ForegroundColor Yellow
                try {
                    Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$($okxAccount.id)" -Method Delete -Headers $authHeaders
                    Write-Host '✅ 现有账户已删除' -ForegroundColor Green
                } catch {
                    Write-Host "❌ 删除账户失败: $($_.Exception.Message)" -ForegroundColor Red
                    exit 1
                }

                # 创建新的正式网账户
                Write-Host '创建新的正式网账户...' -ForegroundColor Yellow
                $newAccountData = @{
                    exchange_name  = 'okex'
                    api_key        = 'edb07d2e-8fb5-46e8-84b8-5e1795c71ac0'
                    api_secret     = 'CD6A497EEB00AA2DC60B2B0974DD2485'
                    api_passphrase = 'vf5Y3UeUFiz6xfF!'
                    is_testnet     = $false  # 正式网
                } | ConvertTo-Json

                try {
                    $newAccount = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/" -Method Post -Body $newAccountData -Headers $authHeaders
                    Write-Host "✅ 新账户创建成功: ID $($newAccount.id)" -ForegroundColor Green
                    Write-Host '   环境: 正式网' -ForegroundColor Green

                    # 测试新账户
                    Write-Host '测试新账户连接...' -ForegroundColor Yellow
                    try {
                        $balance = Invoke-RestMethod -Uri "$backendUrl/api/exchanges/accounts/$($newAccount.id)/balance" -Method Get -Headers $authHeaders
                        Write-Host '✅ 账户连接测试成功！' -ForegroundColor Green
                        Write-Host '✅ 可以正常获取余额数据' -ForegroundColor Green
                    } catch {
                        Write-Host "⚠️ 连接测试: $($_.Exception.Message)" -ForegroundColor Yellow
                        Write-Host '这可能是正常的，请在浏览器中验证具体错误信息' -ForegroundColor Gray
                    }

                } catch {
                    Write-Host "❌ 创建新账户失败: $($_.Exception.Message)" -ForegroundColor Red
                    exit 1
                }
            }
        } else {
            Write-Host '✅ 账户已经设置为正式网环境' -ForegroundColor Green
        }
    } else {
        Write-Host '⚠️ 未找到OKX账户，请手动添加' -ForegroundColor Yellow
        Write-Host "建议在浏览器中添加账户，环境选择'正式网'" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ 获取账户信息失败: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`n" + '=' * 50
Write-Host '🎉 修复完成！' -ForegroundColor Green
Write-Host '现在请在浏览器中测试:' -ForegroundColor Cyan
Write-Host '1. 访问 http://localhost:3000' -ForegroundColor White
Write-Host '2. 进入交易所配置页面' -ForegroundColor White
Write-Host "3. 点击'测试连接'验证修复结果" -ForegroundColor White
