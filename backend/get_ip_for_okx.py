#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取网络IP信息 - 用于OKX API白名单设置
"""

import requests
import socket
import os

def get_external_ip():
    """获取外网IP地址"""
    print("🔍 正在获取外网IP地址...")
    
    # 方法1：通过SSR代理获取
    try:
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        # 尝试多个IP查询服务
        services = [
            'https://api.ipify.org?format=json',
            'https://httpbin.org/ip',
            'https://ip.jsontest.com/',
        ]
        
        for service in services:
            try:
                print(f"   尝试服务: {service}")
                response = requests.get(service, proxies=proxies, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # 根据不同服务提取IP
                    if 'ip' in data:
                        ip = data['ip']
                    elif 'origin' in data:
                        ip = data['origin']
                    else:
                        ip = str(data)
                    
                    print(f"✅ 通过SSR代理的外网IP: {ip}")
                    return ip
                    
            except Exception as e:
                print(f"   服务 {service} 失败: {e}")
                continue
                
    except Exception as e:
        print(f"❌ 代理方式获取IP失败: {e}")
    
    return None

def get_local_ip():
    """获取本地IP地址"""
    try:
        # 获取本地IP
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        print(f"💻 本地IP地址: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"❌ 获取本地IP失败: {e}")
        return None

def main():
    print("🌐 OKX API白名单IP地址查询工具")
    print("=" * 50)
    
    # 获取外网IP
    external_ip = get_external_ip()
    
    # 获取本地IP
    local_ip = get_local_ip()
    
    print("\n" + "=" * 50)
    print("📋 OKX API白名单设置建议:")
    print("=" * 50)
    
    if external_ip:
        print(f"🎯 推荐设置: {external_ip}")
        print("   这是通过SSR代理访问的外网IP地址")
        print("   OKX会看到这个IP地址的API请求")
    else:
        print("❌ 无法自动获取外网IP")
        print("   请手动访问 https://www.whatismyipaddress.com/ 查询")
    
    if local_ip:
        print(f"💻 本地IP: {local_ip}")
        print("   通常不需要设置本地IP到白名单")
    
    print("\n🔧 设置说明:")
    print("1. 登录OKX官网 -> API管理")
    print("2. 创建新的API密钥")
    print("3. 权限设置：只选择'读取'权限")
    print("4. IP白名单：填入上面推荐的IP地址")
    print("5. 保存API Key、Secret Key和Passphrase")
    
    print("\n⚠️  注意事项:")
    print("- 如果IP地址变化，需要更新白名单")
    print("- 读取权限足够获取账户余额和市场数据")
    print("- 不要开启交易权限，避免安全风险")

if __name__ == "__main__":
    main()
