#!/usr/bin/env python3
"""
代理连接测试脚本
用于验证代理配置是否正确
"""
import requests

def test_proxy(proxy_type, host, port):
    proxy_url = f"{proxy_type}://{host}:{port}"
    proxies = {'http': proxy_url, 'https': proxy_url}
    
    try:
        # 测试获取外部IP
        response = requests.get('http://httpbin.org/ip', proxies=proxies, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 代理工作正常")
            print(f"   外部IP: {data.get('origin')}")
            return True
        else:
            print(f"❌ 代理响应异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 代理连接失败: {e}")
        return False

if __name__ == "__main__":
    print("测试代理配置...")
    # 测试你的代理配置
    result = test_proxy('socks5', '127.0.0.1', 1080)
    
    if result:
        print("\n🎉 代理配置正确！现在可以使用交易系统了。")
    else:
        print("\n⚠️ 请检查SSR客户端配置。")
