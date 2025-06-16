#!/usr/bin/env python3
"""
验证SSR代理配置的脚本
专门测试Python后端是否能通过SSR代理访问OKX API
"""
import os
import socket
import subprocess
import sys
from pathlib import Path

def check_ssr_port():
    """检查SSR代理端口是否开放"""
    print("🔍 检查SSR代理端口1080...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('127.0.0.1', 1080))
        sock.close()
        
        if result == 0:
            print("✅ SSR代理端口1080可用")
            return True
        else:
            print("❌ SSR代理端口1080不可用")
            return False
    except Exception as e:
        print(f"❌ 端口检查失败: {e}")
        return False

def check_pysocks():
    """检查pysocks是否安装"""
    print("\n📦 检查pysocks依赖...")
    try:
        import socks
        print("✅ pysocks已安装")
        return True
    except ImportError:
        print("❌ pysocks未安装")
        print("   请运行: py -m pip install pysocks")
        return False

def check_env_file():
    """检查.env文件中的代理配置"""
    print("\n⚙️ 检查.env文件配置...")
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env文件不存在")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    found_configs = []
    
    for var in proxy_vars:
        if f"{var}=socks5h://127.0.0.1:1080" in content:
            found_configs.append(var)
            print(f"✅ {var}=socks5h://127.0.0.1:1080")
        else:
            print(f"⚠️ {var} 配置缺失或不正确")
    
    return len(found_configs) >= 2  # 至少需要HTTP_PROXY和HTTPS_PROXY

def test_proxy_with_requests():
    """使用requests测试代理连接"""
    print("\n🌐 测试代理连接...")
    
    try:
        import requests
        
        proxies = {
            'http': 'socks5h://127.0.0.1:1080',
            'https': 'socks5h://127.0.0.1:1080'
        }
        
        # 测试IP检测
        try:
            print("  测试IP检测...")
            response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
            if response.status_code == 200:
                ip_data = response.json()
                print(f"  ✅ 代理IP: {ip_data.get('origin')}")
            else:
                print(f"  ❌ IP检测失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ IP检测异常: {e}")
            return False
        
        # 测试OKX API
        try:
            print("  测试OKX API...")
            response = requests.get(
                'https://www.okx.com/api/v5/public/time', 
                proxies=proxies, 
                timeout=15
            )
            if response.status_code == 200:
                time_data = response.json()
                if time_data.get('code') == '0':
                    print(f"  ✅ OKX API可访问")
                    return True
                else:
                    print(f"  ❌ OKX API错误: {time_data}")
                    return False
            else:
                print(f"  ❌ OKX API失败: {response.status_code}")
                return False
        except Exception as e:
            print(f"  ❌ OKX API异常: {e}")
            return False
            
    except ImportError:
        print("❌ requests库未安装")
        return False

def test_environment_variables():
    """测试环境变量是否正确设置"""
    print("\n🔧 测试环境变量...")
    
    # 模拟main.py中的环境变量加载
    from dotenv import load_dotenv
    load_dotenv()
    
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    all_set = True
    
    for var in proxy_vars:
        value = os.getenv(var)
        if value and 'socks5h://127.0.0.1:1080' in value:
            print(f"✅ {var} = {value}")
        else:
            print(f"❌ {var} 未正确设置")
            all_set = False
    
    return all_set

def create_test_script():
    """创建一个简单的测试脚本"""
    test_script = '''
import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 设置环境变量（模拟main.py）
if os.getenv('HTTP_PROXY'):
    os.environ['HTTP_PROXY'] = os.getenv('HTTP_PROXY')
    os.environ['HTTPS_PROXY'] = os.getenv('HTTPS_PROXY')
    os.environ['http_proxy'] = os.getenv('http_proxy')
    os.environ['https_proxy'] = os.getenv('https_proxy')

# 测试代理（requests会自动使用环境变量）
try:
    response = requests.get('https://httpbin.org/ip', timeout=10)
    print(f"通过代理访问成功: {response.json()['origin']}")
    
    # 测试OKX
    response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
    print(f"OKX API访问: {response.status_code}")
    
except Exception as e:
    print(f"测试失败: {e}")
'''
    
    with open('test_proxy_env.py', 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    print("\n📝 已创建测试脚本: test_proxy_env.py")

def main():
    """主验证函数"""
    print("🚀 Python后端SSR代理配置验证")
    print("=" * 50)
    
    # 检查列表
    checks = [
        ("SSR代理端口", check_ssr_port),
        ("pysocks依赖", check_pysocks),
        (".env文件配置", check_env_file),
        ("环境变量", test_environment_variables),
        ("代理连接", test_proxy_with_requests),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name}检查失败: {e}")
            results.append((check_name, False))
    
    # 显示结果
    print("\n" + "=" * 50)
    print("📊 验证结果总结:")
    
    all_passed = True
    for check_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False
    
    # 总结和建议
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 所有检查通过！")
        print("💡 Python后端已正确配置SSR代理")
        print("📋 可以启动后端服务测试OKX API连接")
        print("\n启动命令:")
        print("  cd backend")
        print("  py main.py")
    else:
        print("⚠️ 部分检查失败，请按以下步骤修复:")
        
        if not results[0][1]:  # SSR端口
            print("  1. 启动SSR客户端，确保监听1080端口")
            
        if not results[1][1]:  # pysocks
            print("  2. 安装pysocks: py -m pip install pysocks")
            
        if not results[2][1]:  # .env配置
            print("  3. 检查.env文件中的代理配置")
            
        if not results[4][1]:  # 连接测试
            print("  4. 检查网络连接和防火墙设置")
    
    # 创建测试脚本
    create_test_script()
    print("\n🔧 可以运行 py test_proxy_env.py 进行进一步测试")

if __name__ == "__main__":
    main()
