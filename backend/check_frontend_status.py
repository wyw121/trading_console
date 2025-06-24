#!/usr/bin/env python3
"""
前端状态检查脚本
"""
import requests
import time

def check_frontend_status():
    """检查前端服务状态"""
    print("=== 前端服务状态检查 ===")
    
    try:
        # 检查前端主页
        response = requests.get('http://localhost:3001', timeout=5)
        if response.status_code == 200:
            print("✅ 前端服务正常运行 (端口3001)")
        else:
            print(f"⚠️  前端服务响应异常: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ 前端服务连接失败: {e}")
    
    # 检查后端服务
    try:
        response = requests.get('http://localhost:8000', timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务正常运行 (端口8000)")
        else:
            print(f"⚠️  后端服务响应异常: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ 后端服务连接失败: {e}")
    
    # 测试前后端API通信 (CORS)
    print("\n=== 测试API通信 ===")
    try:
        headers = {
            'Origin': 'http://localhost:3001',
            'Content-Type': 'application/json'
        }
        response = requests.options('http://localhost:8000/api/auth/me', headers=headers, timeout=5)
        if response.status_code in [200, 204]:
            print("✅ CORS预检请求正常")
        else:
            print(f"⚠️  CORS预检请求异常: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ CORS预检请求失败: {e}")

if __name__ == "__main__":
    check_frontend_status()
