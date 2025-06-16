#!/usr/bin/env python3
"""
快速代理测试脚本 - 修复版
"""
import os
import sys
import requests
import socket
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def print_env_info():
    """打印环境变量信息"""
    print('=== 环境变量检查 ===')
    print(f'USE_PROXY: {os.getenv("USE_PROXY", "未设置")}')
    print(f'PROXY_HOST: {os.getenv("PROXY_HOST", "未设置")}')
    print(f'PROXY_PORT: {os.getenv("PROXY_PORT", "未设置")}')
    print(f'PROXY_TYPE: {os.getenv("PROXY_TYPE", "未设置")}')

def test_proxy_config():
    """测试代理配置"""
    print('\n=== 代理配置状态 ===')
    try:
        from proxy_config import proxy_config
        print(f'代理启用: {proxy_config.proxy_enabled}')
        print(f'代理地址: {proxy_config.proxy_host}:{proxy_config.proxy_port}')
        print(f'代理类型: {proxy_config.proxy_type}')
        
        if proxy_config.proxy_enabled:
            proxy_dict = proxy_config.get_proxy_dict()
            print(f'代理配置: {proxy_dict}')
            return proxy_dict
        return None
    except Exception as e:
        print(f'加载代理配置失败: {e}')
        return None

def test_port(host, port):
    """测试端口连接"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_ssr_ports():
    """测试SSR端口连接"""
    print('\n=== SSR端口连接测试 ===')
    
    # 测试常见SSR端口
    common_ports = [1080, 1081, 7890, 10808, 10809]
    proxy_host = os.getenv("PROXY_HOST", "127.0.0.1")
    current_port = int(os.getenv("PROXY_PORT", "1080"))
    
    available_ports = []
    
    for port in common_ports:
        status = test_port(proxy_host, port)
        status_text = "✅ 可用" if status else "❌ 不可用"
        current_mark = " (当前配置)" if port == current_port else ""
        print(f'端口 {port}: {status_text}{current_mark}')
        
        if status:
            available_ports.append(port)
    
    return available_ports

def test_direct_connection():
    """测试直连"""
    print('\n=== 直连测试 ===')
    try:
        response = requests.get('https://www.google.com', timeout=5)
        print(f'直连Google: ✅ 成功 (状态码: {response.status_code})')
        return True
    except Exception as e:
        print(f'直连Google: ❌ 失败 ({str(e)})')
        return False

def test_proxy_connection(proxy_dict):
    """测试代理连接"""
    print('\n=== 代理连接测试 ===')
    
    if not proxy_dict:
        print('代理配置为空，跳过测试')
        return False
    
    test_results = []
    
    # 测试Google连接
    try:
        response = requests.get('https://www.google.com', proxies=proxy_dict, timeout=10)
        print(f'代理连接Google: ✅ 成功 (状态码: {response.status_code})')
        test_results.append(True)
    except Exception as e:
        print(f'代理连接Google: ❌ 失败 ({str(e)})')
        test_results.append(False)
    
    # 测试获取外部IP
    try:
        response = requests.get('https://httpbin.org/ip', proxies=proxy_dict, timeout=10)
        ip_info = response.json()
        print(f'外部IP: ✅ {ip_info.get("origin", "未知")}')
        test_results.append(True)
    except Exception as e:
        print(f'获取外部IP: ❌ 失败 ({str(e)})')
        test_results.append(False)
    
    # 测试OKX连接
    try:
        response = requests.get('https://www.okx.com/api/v5/public/time', proxies=proxy_dict, timeout=15)
        if response.status_code == 200:
            time_data = response.json()
            if time_data.get('code') == '0':
                print(f'代理连接OKX: ✅ 成功')
                test_results.append(True)
            else:
                print(f'代理连接OKX: ❌ API返回错误')
                test_results.append(False)
        else:
            print(f'代理连接OKX: ❌ 失败 (状态码: {response.status_code})')
            test_results.append(False)
    except Exception as e:
        print(f'代理连接OKX: ❌ 失败 ({str(e)})')
        test_results.append(False)
    
    return any(test_results)

def check_ssr_port():
    """检查ShadowsocksR端口"""
    proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
    proxy_port = int(os.getenv('PROXY_PORT', '1080'))
    
    print(f"\n=== 检查ShadowsocksR端口 ===")
    print(f"检查端口: {proxy_host}:{proxy_port}")
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex((proxy_host, proxy_port))
        if result == 0:
            print("✅ 端口可访问，ShadowsocksR可能正在运行")
            return True
        else:
            print("❌ 端口无法访问，请检查ShadowsocksR是否运行")
            return False
    except Exception as e:
        print(f"❌ 端口检查失败: {str(e)}")
        return False
    finally:
        sock.close()

def main():
    """主函数"""
    print("Trading Console 代理快速测试")
    print("="*50)
    
    # 1. 检查环境变量
    print_env_info()
    
    # 2. 测试代理配置
    proxy_dict = test_proxy_config()
    
    # 3. 测试端口
    available_ports = test_ssr_ports()
    
    # 4. 测试直连
    direct_ok = test_direct_connection()
    
    # 5. 测试代理连接
    proxy_ok = False
    if proxy_dict:
        proxy_ok = test_proxy_connection(proxy_dict)
    
    # 6. 检查主要端口
    main_port_ok = check_ssr_port()
    
    # 总结
    print("\n" + "="*50)
    print("📊 测试结果总结:")
    print(f"  可用端口: {available_ports}")
    print(f"  主端口状态: {'✅ 正常' if main_port_ok else '❌ 异常'}")
    print(f"  直连状态: {'✅ 正常' if direct_ok else '❌ 异常'}")
    print(f"  代理状态: {'✅ 正常' if proxy_ok else '❌ 异常'}")
    
    if main_port_ok and proxy_ok:
        print("\n🎉 代理配置成功！可以访问海外网站。")
        print("现在可以正常使用OKX API了。")
        return True
    else:
        print("\n❌ 代理测试失败，请检查配置。")
        if not main_port_ok:
            print("\n修复建议：")
            print("1. 确认ShadowsocksR客户端正在运行")
            print("2. 检查.env文件中的PROXY_PORT设置")
            print("3. 确认本地端口没有被其他程序占用")
        if not proxy_ok and proxy_dict:
            print("4. 检查代理服务器连接")
            print("5. 确认网络防火墙设置")
        return False

if __name__ == "__main__":
    main()
