#!/usr/bin/env python3
"""
简化的代理连接测试
"""
import requests
import socket
from proxy_config import proxy_config

def test_shadowsocksr_port():
    """测试ShadowsocksR端口是否开放"""
    print(f"测试ShadowsocksR端口: {proxy_config.proxy_host}:{proxy_config.proxy_port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex((proxy_config.proxy_host, proxy_config.proxy_port))
        if result == 0:
            print("✅ ShadowsocksR端口可以连接")
            return True
        else:
            print("❌ ShadowsocksR端口无法连接")
            return False
    except Exception as e:
        print(f"❌ 端口测试失败: {e}")
        return False
    finally:
        sock.close()

def test_proxy_request():
    """测试通过代理发送HTTP请求"""
    if not proxy_config.proxy_enabled:
        print("代理未启用")
        return False
    
    proxy_dict = proxy_config.get_proxy_dict()
    print(f"使用代理配置: {proxy_dict}")
    
    test_urls = [
        'https://httpbin.org/ip',
        'https://www.okx.com',
    ]
    
    for url in test_urls:
        try:
            print(f"测试连接: {url}")
            response = requests.get(
                url, 
                proxies=proxy_dict, 
                timeout=15,
                headers={'User-Agent': 'Trading Console/1.0'}
            )
            
            if response.status_code == 200:
                print(f"✅ 成功连接: {url}")
                if 'httpbin.org' in url:
                    try:
                        ip_info = response.json()
                        print(f"   外部IP: {ip_info.get('origin', 'unknown')}")
                    except:
                        pass
                return True
            else:
                print(f"❌ 连接失败: {url}, 状态码: {response.status_code}")
                
        except Exception as e:
            print(f"❌ 连接失败: {url}, 错误: {str(e)}")
    
    return False

def main():
    print("=== ShadowsocksR代理测试 ===")
    print(f"代理启用: {proxy_config.proxy_enabled}")
    print(f"代理配置: {proxy_config.proxy_host}:{proxy_config.proxy_port} ({proxy_config.proxy_type})")
    print()
    
    # 1. 测试端口
    port_ok = test_shadowsocksr_port()
    print()
    
    # 2. 测试HTTP请求
    if port_ok:
        request_ok = test_proxy_request()
    else:
        print("跳过HTTP测试（端口不可用）")
        request_ok = False
    
    print()
    print("=== 测试结果 ===")
    print(f"端口连接: {'✅ 正常' if port_ok else '❌ 失败'}")
    print(f"HTTP请求: {'✅ 正常' if request_ok else '❌ 失败'}")
    
    if port_ok and request_ok:
        print("\n🎉 代理配置正确！可以访问外网服务。")
    elif port_ok:
        print("\n⚠️  端口正常但HTTP请求失败，可能是代理服务器问题。")
    else:
        print("\n❌ 代理连接失败，请检查ShadowsocksR是否正在运行。")
    
    print("\n=== 故障排除提示 ===")
    print("1. 确保ShadowsocksR客户端正在运行")
    print("2. 检查本地监听端口（通常是1080或1081）")
    print("3. 确认'允许来自局域网的连接'已开启")
    print("4. 检查防火墙设置")

if __name__ == "__main__":
    main()
