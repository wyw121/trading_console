#!/usr/bin/env python
"""
启动带SSR代理的后端服务
"""
import os
import sys
import subprocess
from pathlib import Path

def check_ssr_proxy():
    """检查SSR代理是否可用"""
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print("🚀 启动交易控制台后端服务 (SSR代理)")
    print("=" * 50)
    
    # 检查SSR代理
    if check_ssr_proxy():
        print("✅ SSR代理 (1080端口) 可用")
    else:
        print("❌ SSR代理不可用，请先启动SSR客户端")
        print("⚠️ 服务仍会启动，但可能无法访问OKX API")
    
    # 检查.env文件
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .env配置文件存在")
    else:
        print("❌ .env配置文件不存在")
        return
    
    print("\n📋 配置信息:")
    print("   代理类型: SOCKS5")
    print("   代理地址: 127.0.0.1:1080")
    print("   DNS解析: 通过代理 (socks5h://)")
    print("   环境变量: HTTP_PROXY, HTTPS_PROXY")
    
    print("\n🔄 启动后端服务...")
    try:
        # 启动FastAPI服务
        subprocess.run([sys.executable, "main.py"], check=True)
    except KeyboardInterrupt:
        print("\n⏹️ 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")

if __name__ == "__main__":
    main()
