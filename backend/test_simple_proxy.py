#!/usr/bin/env python3
"""
简化的SSR代理测试脚本
"""
import os
import socket
import requests

def test_proxy_port():
    """测试代理端口是否开放"""
    print("🔍 测试SSR代理端口...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        
        if result == 0:
            print("✅ SSR代理端口1080可用")
            return True
        else:
            print("❌ SSR代理端口1080不可用")
            return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_proxy_requests():
    """测试通过代理访问"""
    print("\n🌐 测试通过SSR代理访问网站...")
    
    # 代理配置
    proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    try:
        # 测试访问httpbin获取IP
        print("  访问 httpbin.org/ip ...")
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        if response.status_code == 200:
            ip_info = response.json()
            print(f"  ✅ 代理IP: {ip_info.get('origin')}")
            return True
        else:
            print(f"  ❌ 请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"  ❌ 请求异常: {e}")
        return False

def test_okx_api():
    """测试访问OKX API"""
    print("\n🏦 测试访问OKX API...")
    
    proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    try:
        # 测试OKX公共API
        print("  访问 OKX 公共时间API...")
        response = requests.get(
            'https://www.okx.com/api/v5/public/time', 
            proxies=proxies, 
            timeout=15
        )
        
        if response.status_code == 200:
            time_data = response.json()
            if time_data.get('code') == '0':
                timestamp = time_data.get('data', [{}])[0].get('ts')
                print(f"  ✅ OKX服务器时间: {timestamp}")
                return True
            else:
                print(f"  ❌ OKX API返回错误: {time_data}")
                return False
        else:
            print(f"  ❌ HTTP状态码: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  ❌ 访问OKX API失败: {e}")
        return False

def main():
    print("🚀 Python后端SSR代理测试")
    print("=" * 50)
    
    # 测试代理端口
    port_ok = test_proxy_port()
    if not port_ok:
        print("\n⚠️ 请确保:")
        print("   1. SSR客户端正在运行")
        print("   2. 本地端口1080已开放")
        return
    
    # 测试代理访问
    proxy_ok = test_proxy_requests()
    
    # 测试OKX访问
    okx_ok = test_okx_api()
    
    print("\n" + "=" * 50)
    print("📊 测试结果:")
    print(f"  代理端口: {'✅' if port_ok else '❌'}")
    print(f"  代理访问: {'✅' if proxy_ok else '❌'}")
    print(f"  OKX API: {'✅' if okx_ok else '❌'}")
    
    if port_ok and proxy_ok and okx_ok:
        print("\n🎉 所有测试通过！可以通过SSR代理访问OKX API")
    else:
        print("\n⚠️ 部分测试失败，请检查SSR配置")

if __name__ == "__main__":
    main()
