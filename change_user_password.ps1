# 更改用户111密码为123456
Write-Host '🔐 更改用户111密码为123456' -ForegroundColor Green
Write-Host ('=' * 40)

# 切换到后端目录
Set-Location 'c:\trading_console\backend'

# 执行Python命令更改密码
$pythonScript = @'
import sys
import os
sys.path.append('.')

from database import SessionLocal, User
from auth import get_password_hash

# 创建数据库会话
db = SessionLocal()

try:
    # 查找用户111
    user = db.query(User).filter(User.username == '111').first()

    if user:
        print(f'📋 找到用户: {user.username} (ID: {user.id})')

        # 更新密码为123456
        user.hashed_password = get_password_hash('123456')
        db.commit()

        print('✅ 密码更改成功!')
        print('   新密码: 123456')
        print('   密码长度: 6位 (符合要求)')

    else:
        print('❌ 用户111未找到')

        # 显示所有用户
        users = db.query(User).all()
        print(f'📋 数据库中共有 {len(users)} 个用户:')
        for u in users:
            print(f'   - {u.username} (ID: {u.id})')

except Exception as e:
    print(f'❌ 错误: {e}')
    db.rollback()
finally:
    db.close()
'@

# 将Python脚本写入临时文件
$tempFile = 'temp_change_password.py'
$pythonScript | Out-File -FilePath $tempFile -Encoding UTF8

# 执行Python脚本
python $tempFile

# 删除临时文件
Remove-Item $tempFile -Force

Write-Host ''
Write-Host '🎉 密码更改完成!' -ForegroundColor Green
Write-Host '📝 新的登录信息:' -ForegroundColor Yellow
Write-Host '   用户名: 111' -ForegroundColor White
Write-Host '   密码: 123456' -ForegroundColor White
Write-Host ''
Write-Host '🌐 可以使用新密码登录:' -ForegroundColor Cyan
Write-Host '   http://localhost:3000/login' -ForegroundColor White
