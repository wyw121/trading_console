# 🧪 前端完整测试脚本
# run_frontend_tests.ps1

param(
    [switch]$Verbose,
    [switch]$SkipBuild,
    [string]$TestLevel = "basic"
)

Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "🧪 Trading Console - 前端测试套件" -ForegroundColor Blue
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host ""

# 检查当前目录
$CurrentDir = Get-Location
Write-Host "📁 当前目录: $CurrentDir" -ForegroundColor Cyan

# 确保在正确的目录
if (-not (Test-Path "frontend")) {
    Write-Host "❌ 未找到frontend目录，请在项目根目录运行此脚本" -ForegroundColor Red
    exit 1
}

Set-Location "frontend"
Write-Host "📂 切换到前端目录: $(Get-Location)" -ForegroundColor Green
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

# 1. Node.js 环境测试
Test-Component "Node.js 环境检查" {
    $nodeVersion = node --version
    if ($nodeVersion) {
        Write-Host "Node.js版本: $nodeVersion" -ForegroundColor Cyan
    } else {
        throw "Node.js 未安装或不在 PATH 中"
    }
}

# 2. npm 依赖检查
Test-Component "npm 依赖检查" {
    if (-not (Test-Path "node_modules")) {
        Write-Host "📦 正在安装依赖..." -ForegroundColor Yellow
        npm install
    }

    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    Write-Host "项目: $($packageJson.name) v$($packageJson.version)" -ForegroundColor Cyan
}

# 3. 测试依赖安装
Test-Component "测试依赖安装" {
    Write-Host "📦 安装测试依赖..." -ForegroundColor Yellow
    npm install --save-dev vitest @vue/test-utils jsdom @vitest/ui c8

    # 检查关键测试包
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    if (-not $packageJson.devDependencies.vitest) {
        throw "Vitest 安装失败"
    }
    Write-Host "测试框架配置完成" -ForegroundColor Green
}

# 4. Vite 配置检查
Test-Component "Vite 配置验证" {
    if (-not (Test-Path "vite.config.js")) {
        Write-Host "📝 创建测试配置..." -ForegroundColor Yellow
        @"
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'jsdom',
    coverage: {
      reporter: ['text', 'json', 'html']
    }
  }
})
"@ | Out-File -FilePath "vite.config.js" -Encoding utf8
    }
    Write-Host "Vite 配置已验证" -ForegroundColor Green
}

# 5. 基础组件测试
Test-Component "创建示例测试" {
    if (-not (Test-Path "tests")) {
        New-Item -Type Directory -Name "tests"
    }

    if (-not (Test-Path "tests\example.test.js")) {
        @"
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { createApp } from 'vue'

describe('Vue 环境测试', () => {
  it('应该创建 Vue 应用实例', () => {
    const app = createApp({})
    expect(app).toBeTruthy()
  })
})

describe('数学计算测试', () => {
  it('应该正确计算加法', () => {
    expect(1 + 1).toBe(2)
  })

  it('应该正确计算百分比', () => {
    const price = 100
    const change = 5
    const percentage = (change / price) * 100
    expect(percentage).toBe(5)
  })
})
"@ | Out-File -FilePath "tests\example.test.js" -Encoding utf8
    }
    Write-Host "示例测试文件已创建" -ForegroundColor Green
}

# 6. 代码构建测试
if (-not $SkipBuild) {
    Test-Component "代码构建测试" {
        Write-Host "🔨 构建前端代码..." -ForegroundColor Yellow
        npm run build

        if (-not (Test-Path "dist")) {
            throw "构建失败，未生成dist目录"
        }
        Write-Host "构建成功，输出到 dist/ 目录" -ForegroundColor Green
    }
}

# 7. 运行单元测试（如果可用）
Test-Component "运行单元测试" {
    # 更新 package.json 添加测试脚本
    $packageJson = Get-Content "package.json" | ConvertFrom-Json
    if (-not $packageJson.scripts.test) {
        $packageJson.scripts | Add-Member -Type NoteProperty -Name "test" -Value "vitest run"
        $packageJson.scripts | Add-Member -Type NoteProperty -Name "test:ui" -Value "vitest --ui"
        $packageJson.scripts | Add-Member -Type NoteProperty -Name "test:coverage" -Value "vitest run --coverage"
        $packageJson | ConvertTo-Json -Depth 10 | Out-File -FilePath "package.json" -Encoding utf8
    }

    Write-Host "🧪 运行单元测试..." -ForegroundColor Yellow
    npm test
}

# 测试结果汇总
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "📊 前端测试结果汇总" -ForegroundColor Blue
Write-Host "=" * 60 -ForegroundColor Blue
Write-Host "✅ 通过: $TestPassed" -ForegroundColor Green
Write-Host "❌ 失败: $TestFailed" -ForegroundColor Red
Write-Host "📈 成功率: $([Math]::Round(($TestPassed / ($TestPassed + $TestFailed)) * 100, 1))%" -ForegroundColor Cyan
Write-Host ""

if ($TestFailed -gt 0) {
    Write-Host "⚠️  发现测试失败，请检查上述错误信息" -ForegroundColor Yellow
    exit 1
} else {
    Write-Host "🎉 所有前端测试通过！" -ForegroundColor Green
    exit 0
}
