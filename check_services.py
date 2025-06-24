#!/usr/bin/env python3
"""
交易所控制台服务状态检查脚本
"""
import subprocess
import time
import sys
from datetime import datetime

def check_port(port, service_name):
    """检查端口是否被占用"""
    try:
        result = subprocess.run(
            ['powershell', '-Command', f'Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue'],
            capture_output=True, text=True, timeout=5
        )
        if result.stdout.strip():
            return True
        return False
    except:
        return False

def main():
    print(f"\n{'='*60}")
    print("交易所控制台 - 服务状态检查")
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    services = [
        (8000, "后端服务 (FastAPI)", "http://localhost:8000"),
        (3001, "前端服务 (Vue.js)", "http://localhost:3001"),
        (3000, "前端备用端口", "http://localhost:3000")
    ]
    
    running_services = []
    
    for port, name, url in services:
        print(f"\n检查 {name}...")
        if check_port(port, name):
            print(f"   ✅ {name} 正在运行 - 端口 {port}")
            print(f"   🔗 访问地址: {url}")
            running_services.append((name, url))
        else:
            print(f"   ❌ {name} 未运行 - 端口 {port}")
    
    print(f"\n{'='*60}")
    print("📊 服务状态总结:")
    
    if len(running_services) >= 2:
        print("🎉 前后端服务都在运行！")
        for name, url in running_services:
            print(f"   • {name}: {url}")
        
        print(f"\n🚀 您可以开始使用交易所控制台:")
        print("   1. 打开浏览器访问前端应用")
        print("   2. 登录或注册账户")
        print("   3. 配置交易所API")
        print("   4. 开始交易!")
        
    elif any("后端" in name for name, url in running_services):
        print("⚠️  后端运行正常，但前端可能有问题")
        print("   请检查前端启动状态")
        
    elif any("前端" in name for name, url in running_services):
        print("⚠️  前端运行正常，但后端可能有问题")
        print("   请检查后端启动状态")
        
    else:
        print("❌ 服务未正常启动")
        print("   建议操作:")
        print("   1. 检查terminal中的启动日志")
        print("   2. 确认虚拟环境已激活")
        print("   3. 检查端口是否被占用")
    
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
