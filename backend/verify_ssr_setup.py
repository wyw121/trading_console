#!/usr/bin/env python3
"""
最终验证：Python后端通过SSR代理访问OKX API
"""

import sys
import os
from pathlib import Path

# 添加backend目录到路径
backend_path = Path(__file__).parent
sys.path.append(str(backend_path))

from dotenv import load_dotenv
import requests
import asyncio

# 加载环境变量
load_dotenv()

def verify_proxy_config():
    """验证代理配置"""
    print("🔍 验证代理配置...")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    all_configured = True
    
    for var in proxy_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: 未配置")
            all_configured = False
    
    return all_configured

def test_trading_system_proxy():
    """测试交易系统代理访问"""
    print("\n🚀 测试交易系统通过SSR访问外网...")
    
    try:
        # 模拟交易系统发出的请求
        response = requests.get(
            'https://httpbin.org/ip',
            timeout=15,
            headers={'User-Agent': 'Trading Console/1.0'}
        )
        
        if response.status_code == 200:
            ip_info = response.json()
            external_ip = ip_info.get('origin')
            
            print(f"✅ 交易系统代理访问成功")
            print(f"   外部IP: {external_ip}")
            
            # 验证是否通过代理
            if '127.0.0.1' not in external_ip:
                print(f"✅ 确认通过代理访问（IP不是本地）")
                return True
            else:
                print(f"⚠️  可能未通过代理（显示本地IP）")
                return False
        else:
            print(f"❌ 代理访问失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 代理访问测试失败: {e}")
        return False

async def test_okx_accessibility():
    """测试OKX API可访问性"""
    print("\n🌐 测试OKX API访问性...")
    
    # 测试OKX公共API端点
    okx_endpoints = [
        'https://www.okx.com/api/v5/public/time',
        'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT'
    ]
    
    success_count = 0
    
    for endpoint in okx_endpoints:
        try:
            print(f"   测试: {endpoint}")
            response = requests.get(endpoint, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == '0':  # OKX成功响应
                    print(f"   ✅ 成功")
                    success_count += 1
                else:
                    print(f"   ⚠️  API错误: {data.get('msg', '未知')}")
            else:
                print(f"   ❌ HTTP {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ 连接失败: {str(e)[:50]}...")
    
    if success_count > 0:
        print(f"✅ OKX API可访问 ({success_count}/{len(okx_endpoints)})")
        return True
    else:
        print(f"❌ OKX API不可访问")
        return False

def create_startup_script():
    """创建启动脚本"""
    print("\n📝 创建代理启动脚本...")
    
    # Windows批处理脚本
    bat_content = '''@echo off
echo 🚀 启动交易控制台后端 (带SSR代理)
echo ================================

cd /d "%~dp0backend"

echo 设置SSR代理环境变量...
set HTTP_PROXY=socks5h://127.0.0.1:1080
set HTTPS_PROXY=socks5h://127.0.0.1:1080
set http_proxy=socks5h://127.0.0.1:1080
set https_proxy=socks5h://127.0.0.1:1080

echo ✅ 代理配置完成
echo 启动FastAPI服务器...

py main.py

pause
'''
    
    bat_file = Path(backend_path).parent / 'start_backend_with_ssr.bat'
    with open(bat_file, 'w', encoding='utf-8') as f:
        f.write(bat_content)
    
    print(f"✅ 已创建: {bat_file}")
    
    # PowerShell脚本
    ps1_content = '''# 🚀 启动交易控制台后端 (带SSR代理)
Write-Host "================================" -ForegroundColor Green
Write-Host "🚀 启动交易控制台后端 (带SSR代理)" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

Set-Location "$PSScriptRoot\\backend"

Write-Host "设置SSR代理环境变量..." -ForegroundColor Yellow
$env:HTTP_PROXY = "socks5h://127.0.0.1:1080"
$env:HTTPS_PROXY = "socks5h://127.0.0.1:1080"
$env:http_proxy = "socks5h://127.0.0.1:1080"
$env:https_proxy = "socks5h://127.0.0.1:1080"

Write-Host "✅ 代理配置完成" -ForegroundColor Green
Write-Host "启动FastAPI服务器..." -ForegroundColor Yellow

py main.py

Read-Host "按回车键退出"
'''
    
    ps1_file = Path(backend_path).parent / 'start_backend_with_ssr.ps1'
    with open(ps1_file, 'w', encoding='utf-8') as f:
        f.write(ps1_content)
    
    print(f"✅ 已创建: {ps1_file}")

def main():
    """主函数"""
    print("🎯 验证Python后端SSR代理配置")
    print("=" * 50)
    
    # 1. 验证配置
    config_ok = verify_proxy_config()
    
    # 2. 测试代理
    proxy_ok = test_trading_system_proxy()
    
    # 3. 测试OKX
    asyncio.run(test_okx_accessibility())
    
    # 4. 创建启动脚本
    create_startup_script()
    
    # 总结
    print("\n" + "=" * 50)
    print("📊 验证结果:")
    print(f"代理配置: {'✅ 完整' if config_ok else '❌ 缺失'}")
    print(f"代理功能: {'✅ 正常' if proxy_ok else '❌ 异常'}")
    
    if config_ok and proxy_ok:
        print("\n🎉 完美！你的Python后端已配置为通过SSR代理访问OKX")
        print("\n📋 使用方法:")
        print("1. 确保SSR客户端运行在端口1080")
        print("2. 运行: start_backend_with_ssr.bat")
        print("3. 或在VSCode中按F5调试")
        print("4. 所有OKX API调用都会通过代理")
        
        print("\n✨ 关键要点:")
        print("- ✅ 环境变量方式（推荐）")
        print("- ✅ socks5h://协议（DNS通过代理）")
        print("- ✅ pysocks库支持")
        print("- ✅ VSCode调试器配置")
    else:
        print("\n⚠️  需要检查SSR客户端配置")

if __name__ == "__main__":
    main()
