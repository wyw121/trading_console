# Trading Console 启动脚本

Write-Host "=== Trading Console 启动脚本 ===" -ForegroundColor Green
Write-Host ""

# 检查 Docker 是否安装
try {
          docker --version | Out-Null
          $dockerInstalled = $true
}
catch {
          $dockerInstalled = $false
}

# 检查 Docker Compose 是否安装
try {
          docker-compose --version | Out-Null
          $dockerComposeInstalled = $true
}
catch {
          $dockerComposeInstalled = $false
}

if ($dockerInstalled -and $dockerComposeInstalled) {
          Write-Host "检测到 Docker 和 Docker Compose，使用 Docker 启动..." -ForegroundColor Yellow
          Write-Host ""
    
          # 检查 .env 文件是否存在
          if (!(Test-Path "backend\.env")) {
                    Write-Host "复制环境变量文件..." -ForegroundColor Yellow
                    Copy-Item "backend\.env.example" "backend\.env"
                    Write-Host "请编辑 backend\.env 文件以配置数据库连接等信息" -ForegroundColor Cyan
          }
    
          Write-Host "启动 Docker 容器..." -ForegroundColor Yellow
          docker-compose up -d
    
          Write-Host ""
          Write-Host "=== 启动完成 ===" -ForegroundColor Green
          Write-Host "前端地址: http://localhost:3000" -ForegroundColor Cyan
          Write-Host "后端API: http://localhost:8000" -ForegroundColor Cyan
          Write-Host "API文档: http://localhost:8000/docs" -ForegroundColor Cyan
          Write-Host ""
          Write-Host "查看日志: docker-compose logs -f" -ForegroundColor Yellow
          Write-Host "停止服务: docker-compose down" -ForegroundColor Yellow
    
}
else {
          Write-Host "未检测到 Docker，将引导您手动安装..." -ForegroundColor Yellow
          Write-Host ""
    
          Write-Host "=== 手动安装步骤 ===" -ForegroundColor Cyan
          Write-Host ""
    
          Write-Host "1. 后端设置:" -ForegroundColor Yellow
          Write-Host "   cd backend"
          Write-Host "   python -m venv venv"
          Write-Host "   venv\Scripts\activate"
          Write-Host "   pip install -r requirements.txt"
          Write-Host "   copy .env.example .env"
          Write-Host "   # 编辑 .env 文件配置数据库连接"
          Write-Host "   uvicorn main:app --reload"
          Write-Host ""
    
          Write-Host "2. 前端设置:" -ForegroundColor Yellow
          Write-Host "   cd frontend"
          Write-Host "   npm install"
          Write-Host "   npm run dev"
          Write-Host ""
    
          Write-Host "3. 数据库设置:" -ForegroundColor Yellow
          Write-Host "   确保 PostgreSQL 和 Redis 正在运行"
          Write-Host "   PostgreSQL: localhost:5432"
          Write-Host "   Redis: localhost:6379"
          Write-Host ""
    
          Write-Host "推荐安装 Docker Desktop 以简化部署流程" -ForegroundColor Cyan
          Write-Host "下载地址: https://www.docker.com/products/docker-desktop/" -ForegroundColor Blue
}

Write-Host ""
Write-Host "如需帮助，请查看 README.md 文件" -ForegroundColor Green
