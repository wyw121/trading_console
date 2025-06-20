#!/usr/bin/env python3
"""
简单的连接测试
"""
import requests
import socket

def test_port():
    """测试端口连接"""
    try:
        sock = socket.create_connection(('localhost', 8000), timeout=5)
        sock.close()
        print("✅ Port 8000 is accessible")
        return True
    except Exception as e:
        print(f"❌ Port connection failed: {e}")
        return False

def test_http():
    """测试 HTTP 连接"""
    try:
        response = requests.get('http://localhost:8000/health', timeout=10)
        print(f"✅ HTTP response: {response.status_code} - {response.text}")
        return True
    except Exception as e:
        print(f"❌ HTTP test failed: {e}")
        return False

if __name__ == "__main__":
    print("🔍 简单连接测试")
    test_port()
    test_http()
