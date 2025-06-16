import requests
import os
from dotenv import load_dotenv

load_dotenv()

from proxy_config import proxy_config

print("=== 网络连接测试 ===")

# 测试直连
print("1. 测试直连...")
try:
    response = requests.get('https://www.google.com', timeout=5)
    print(f"   直连Google: ✅ 成功 ({response.status_code})")
    direct_ok = True
except Exception as e:
    print(f"   直连Google: ❌ 失败 ({e})")
    direct_ok = False

# 测试代理连接
print("2. 测试代理连接...")
if proxy_config.proxy_enabled:
    proxy_dict = proxy_config.get_proxy_dict()
    print(f"   使用代理: {proxy_dict['https']}")
    
    try:
        response = requests.get('https://www.google.com', proxies=proxy_dict, timeout=10)
        print(f"   代理连接Google: ✅ 成功 ({response.status_code})")
        proxy_ok = True
    except Exception as e:
        print(f"   代理连接Google: ❌ 失败 ({e})")
        proxy_ok = False
    
    # 测试OKX
    if proxy_ok:
        try:
            response = requests.get('https://www.okx.com', proxies=proxy_dict, timeout=10)
            print(f"   代理连接OKX: ✅ 成功 ({response.status_code})")
        except Exception as e:
            print(f"   代理连接OKX: ❌ 失败 ({e})")
    
    # 获取外部IP
    if proxy_ok:
        try:
            response = requests.get('https://httpbin.org/ip', proxies=proxy_dict, timeout=10)
            ip_info = response.json()
            print(f"   外部IP: {ip_info.get('origin')}")
        except Exception as e:
            print(f"   获取IP失败: {e}")
else:
    print("   代理未启用")
    proxy_ok = False

print("\n=== 结果分析 ===")
if direct_ok and not proxy_ok:
    print("🔍 直连可用，代理失败")
    print("   建议：检查SSR配置或使用直连模式")
elif not direct_ok and proxy_ok:
    print("🔍 直连失败，代理可用")
    print("   建议：使用代理模式访问外网")
elif direct_ok and proxy_ok:
    print("🔍 直连和代理都可用")
    print("   建议：可以使用代理模式获得更好的访问体验")
else:
    print("🔍 网络连接异常")
    print("   建议：检查网络连接和SSR配置")

print(f"\n=== 当前配置状态 ===")
print(f"你的代码现在配置为: {'使用代理' if proxy_config.proxy_enabled else '直连模式'}")
print(f"所有对OKX等交易所的API请求都会: {'通过SSR代理' if proxy_config.proxy_enabled else '直接连接'}")
