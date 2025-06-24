#!/usr/bin/env python3
"""
快速修复脚本 - 解决Dashboard加载问题
"""
import os
import sys
import requests
import asyncio
from datetime import datetime

def test_backend():
    """简单测试后端"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=3)
        return response.status_code == 200
    except:
        return False

def test_frontend():
    """简单测试前端"""
    try:
        response = requests.get('http://localhost:3001', timeout=3)
        return response.status_code == 200
    except:
        return False

def test_proxy():
    """简单测试代理"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("🔧 Trading Console 快速修复检查")
    print("=" * 40)
    
    # 检查服务状态
    backend_ok = test_backend()
    frontend_ok = test_frontend()
    proxy_ok = test_proxy()
    
    print(f"后端服务: {'✅' if backend_ok else '❌'}")
    print(f"前端服务: {'✅' if frontend_ok else '❌'}")
    print(f"代理服务: {'✅' if proxy_ok else '❌'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 服务运行正常!")
        print("🌐 前端地址: http://localhost:3001")
        print("📡 后端API: http://localhost:8000/docs")
        
        # 测试Dashboard API
        try:
            # 这里需要登录token，所以可能会失败，但能测试连通性
            response = requests.get('http://localhost:8000/api/dashboard/stats', timeout=5)
            if response.status_code in [200, 401, 403]:
                print("✅ Dashboard API响应正常")
            else:
                print(f"⚠️ Dashboard API状态码: {response.status_code}")
        except Exception as e:
            print(f"⚠️ Dashboard API测试失败: {str(e)[:50]}")
    else:
        print("\n❌ 部分服务未运行")
        if not backend_ok:
            print("请启动后端: cd backend && python main.py")
        if not frontend_ok:
            print("请启动前端: cd frontend && npm run dev")

if __name__ == "__main__":
    main()
