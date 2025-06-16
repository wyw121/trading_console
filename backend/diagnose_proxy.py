"""
代理诊断和配置指南
帮助用户正确配置ShadowsocksR代理
"""
import socket
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def diagnose_ssr_config():
    print("=== ShadowsocksR配置诊断 ===")
    
    # 1. 检查端口连通性
    print("\n1. 检查SSR端口状态:")
    common_ports = [1080, 1081, 7890, 10808, 10809, 1087, 8080]
    
    available_ports = []
    for port in common_ports:
        if test_port("127.0.0.1", port):
            print(f"   ✅ 端口 {port}: 可用")
            available_ports.append(port)
        else:
            print(f"   ❌ 端口 {port}: 不可用")
    
    if not available_ports:
        print("\n❌ 没有发现可用的代理端口！")
        print("请检查:")
        print("   - ShadowsocksR客户端是否正在运行")
        print("   - 本地端口设置")
        print("   - '允许来自局域网的连接'是否开启")
        return None
    
    # 2. 测试不同代理类型
    print(f"\n2. 测试代理类型 (使用端口 {available_ports[0]}):")
    
    proxy_types = ['socks5', 'socks4', 'http']
    working_configs = []
    
    for proxy_type in proxy_types:
        print(f"   测试 {proxy_type} 代理...")
        
        if proxy_type in ['socks5', 'socks4']:
            proxy_url = f"{proxy_type}://127.0.0.1:{available_ports[0]}"
        else:
            proxy_url = f"http://127.0.0.1:{available_ports[0]}"
        
        if test_proxy_type(proxy_url):
            print(f"   ✅ {proxy_type}: 工作正常")
            working_configs.append((proxy_type, available_ports[0], proxy_url))
        else:
            print(f"   ❌ {proxy_type}: 连接失败")
    
    return working_configs

def test_port(host, port):
    """测试端口连通性"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def test_proxy_type(proxy_url):
    """测试特定代理配置"""
    try:
        proxies = {'http': proxy_url, 'https': proxy_url}
        
        # 测试简单的HTTP请求
        response = requests.get(
            'http://httpbin.org/ip', 
            proxies=proxies, 
            timeout=10,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            # 检查返回的IP是否不是本地IP
            return '127.0.0.1' not in data.get('origin', '')
        
        return False
    except:
        return False

def generate_config_suggestions(working_configs):
    """生成配置建议"""
    print("\n=== 配置建议 ===")
    
    if not working_configs:
        print("❌ 没有找到可用的代理配置")
        print("\n故障排除步骤:")
        print("1. 确保ShadowsocksR客户端正在运行")
        print("2. 检查SSR客户端设置:")
        print("   - 本地端口 (通常是1080)")
        print("   - 本地代理类型 (SOCKS5)")
        print("   - 允许来自局域网的连接: 开启")
        print("3. 检查防火墙设置")
        print("4. 尝试重启SSR客户端")
        return
    
    print("✅ 找到可用配置:")
    
    best_config = working_configs[0]  # 选择第一个可用配置
    proxy_type, port, proxy_url = best_config
    
    print(f"\n推荐配置:")
    print(f"代理类型: {proxy_type}")
    print(f"代理端口: {port}")
    print(f"代理URL: {proxy_url}")
    
    # 生成.env配置
    print(f"\n请将以下配置添加到 .env 文件:")
    print(f"USE_PROXY=true")
    print(f"PROXY_HOST=127.0.0.1")
    print(f"PROXY_PORT={port}")
    print(f"PROXY_TYPE={proxy_type}")
    
    # 检查当前配置
    current_port = os.getenv('PROXY_PORT', '1080')
    current_type = os.getenv('PROXY_TYPE', 'socks5')
    
    if str(port) != current_port or proxy_type != current_type:
        print(f"\n⚠️ 当前配置需要更新:")
        print(f"当前端口: {current_port} -> 建议: {port}")
        print(f"当前类型: {current_type} -> 建议: {proxy_type}")

def provide_ssr_setup_guide():
    """提供SSR设置指南"""
    print("\n=== ShadowsocksR客户端设置指南 ===")
    print("\n如果你还没有正确配置SSR，请按以下步骤操作:")
    
    print("\n1. 检查SSR客户端设置:")
    print("   - 打开ShadowsocksR客户端")
    print("   - 确保服务器配置正确且已连接")
    print("   - 右键托盘图标 → 选项设置")
    
    print("\n2. 本地代理设置:")
    print("   - 本地端口: 1080 (默认)")
    print("   - 代理规则: 绕过局域网和大陆")
    print("   - 允许来自局域网的连接: 勾选")
    
    print("\n3. 系统代理设置:")
    print("   - 右键托盘图标 → 系统代理模式")
    print("   - 选择 'PAC模式' 或 '全局模式'")
    
    print("\n4. 测试连接:")
    print("   - 在浏览器中访问 google.com")
    print("   - 确保能正常访问外网")

def create_proxy_test_script():
    """创建代理测试脚本"""
    print("\n=== 创建代理测试脚本 ===")
    
    script_content = '''#!/usr/bin/env python3
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
    # 测试你的代理配置
    result = test_proxy('socks5', '127.0.0.1', 1080)
    
    if result:
        print("\\n🎉 代理配置正确！现在可以使用交易系统了。")
    else:
        print("\\n⚠️ 请检查SSR客户端配置。")
'''
    
    with open('test_my_proxy.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("已创建 test_my_proxy.py 文件")
    print("运行 'py test_my_proxy.py' 来测试你的代理")

if __name__ == "__main__":
    print("ShadowsocksR代理配置诊断工具")
    print("=" * 50)
    
    # 1. 诊断当前配置
    working_configs = diagnose_ssr_config()
    
    # 2. 生成配置建议
    generate_config_suggestions(working_configs)
    
    # 3. 提供设置指南
    if not working_configs:
        provide_ssr_setup_guide()
    
    # 4. 创建测试脚本
    create_proxy_test_script()
    
    print(f"\n=== 总结 ===")
    if working_configs:
        print("✅ 找到可用的代理配置")
        print("✅ 请按照建议更新 .env 文件")
        print("✅ 然后重新运行你的交易程序")
    else:
        print("❌ 需要先配置ShadowsocksR客户端")
        print("❌ 请按照设置指南操作")
        print("❌ 配置完成后重新运行此诊断工具")
