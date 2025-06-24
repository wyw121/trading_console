#!/usr/bin/env python3
"""
Trading Console 系统状态检查器
"""
import requests
import asyncio
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append('.')

from error_handler import console_logger
from trading_engine import exchange_manager, check_okx_connectivity

def check_backend_health():
    """检查后端健康状态"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            return True, "后端服务正常"
        else:
            return False, f"后端返回状态码: {response.status_code}"
    except Exception as e:
        return False, f"后端连接失败: {str(e)}"

def check_frontend_health():
    """检查前端健康状态"""
    try:
        response = requests.get('http://localhost:3001', timeout=5)
        if response.status_code == 200:
            return True, "前端服务正常"
        else:
            return False, f"前端返回状态码: {response.status_code}"
    except Exception as e:
        return False, f"前端连接失败: {str(e)}"

def check_proxy_status():
    """检查代理状态"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        if result == 0:
            return True, "SSR代理端口1080可用"
        else:
            return False, "SSR代理端口1080不可用"
    except Exception as e:
        return False, f"代理检查失败: {str(e)}"

async def main():
    """主检查流程"""
    print("🔍 Trading Console 系统状态检查")
    print("=" * 50)
    print(f"检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查后端
    backend_ok, backend_msg = check_backend_health()
    print(f"🔧 后端服务: {'✅' if backend_ok else '❌'} {backend_msg}")
    
    # 检查前端
    frontend_ok, frontend_msg = check_frontend_health()
    print(f"🌐 前端服务: {'✅' if frontend_ok else '❌'} {frontend_msg}")
    
    # 检查代理
    proxy_ok, proxy_msg = check_proxy_status()
    print(f"🔗 代理状态: {'✅' if proxy_ok else '❌'} {proxy_msg}")
    
    # 检查OKX连接
    okx_ok = check_okx_connectivity()
    print(f"📈 OKX连接: {'✅' if okx_ok else '⚠️'} {'直连可用' if okx_ok else '使用模拟模式'}")
    
    print()
    
    # 总结
    total_checks = 4
    passed_checks = sum([backend_ok, frontend_ok, proxy_ok, okx_ok])
    
    if passed_checks == total_checks:
        print("🎉 系统状态: 全部正常")
        print("💡 提示: 您可以正常使用所有功能")
    elif passed_checks >= 2:
        print("⚠️  系统状态: 基本功能可用")
        print("💡 提示: 部分功能可能受限，但主要功能可用")
    else:
        print("❌ 系统状态: 需要修复")
        print("💡 提示: 请检查服务启动状态")
    
    print()
    print("🔗 访问地址:")
    print(f"   前端: http://localhost:3001")
    print(f"   后端API: http://localhost:8000/docs")
    print(f"   健康检查: http://localhost:8000/health")

if __name__ == "__main__":
    asyncio.run(main())
