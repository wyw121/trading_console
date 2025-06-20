#!/usr/bin/env python3
"""
代理状态诊断脚本
"""
import socket
import requests
import os

def check_socks_proxy(host='127.0.0.1', port=1080):
    """检查SOCKS代理是否可用"""
    print(f"=== 检查SOCKS代理 {host}:{port} ===")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"✅ SOCKS代理端口 {port} 已开放")
            return True
        else:
            print(f"❌ SOCKS代理端口 {port} 无法连接")
            return False
    except Exception as e:
        print(f"❌ 检查代理失败: {e}")
        return False

def test_with_proxy():
    """测试通过代理访问"""
    print("\n=== 测试代理访问 ===")
    
    # 设置代理
    proxies = {
        'http': 'socks5h://127.0.0.1:1080',
        'https': 'socks5h://127.0.0.1:1080'
    }
    
    try:
        # 测试获取IP
        response = requests.get('http://httpbin.org/ip', 
                              proxies=proxies, 
                              timeout=10)
        ip_info = response.json()
        print(f"✅ 通过代理访问成功，IP: {ip_info.get('origin')}")
        
        # 测试访问OKX
        response = requests.get('https://www.okx.com/api/v5/public/time', 
                              proxies=proxies, 
                              timeout=10)
        if response.status_code == 200:
            print(f"✅ 通过代理访问OKX成功: {response.json()}")
            return True
        else:
            print(f"❌ 通过代理访问OKX失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 代理访问测试失败: {e}")
        return False

def check_environment():
    """检查环境配置"""
    print("\n=== 检查环境配置 ===")
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} 未设置")

def main():
    print("🔍 开始代理状态诊断")
    
    # 检查环境变量
    check_environment()
    
    # 检查SOCKS代理端口
    if check_socks_proxy():
        # 测试代理访问
        if test_with_proxy():
            print("\n🎉 代理配置正常，可以开始修复项目")
        else:
            print("\n❌ 代理无法访问外网，请检查SSR配置")
    else:
        print("\n❌ 请先启动SSR代理客户端")
        print("确保SSR客户端在127.0.0.1:1080监听")

if __name__ == "__main__":
    main()
