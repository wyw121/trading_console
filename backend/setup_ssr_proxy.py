#!/usr/bin/env python3
"""
环境变量代理配置脚本
基于你的研究资料 - 使用socks5h://协议
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_ssr_proxy_environment():
    """设置SSR代理环境变量"""
    
    print("🔧 设置SSR代理环境变量...")
    
    # 基于你的研究 - 推荐使用socks5h://协议
    proxy_url = "socks5h://localhost:1080"
    
    # 设置环境变量
    env_vars = {
        'HTTP_PROXY': proxy_url,
        'HTTPS_PROXY': proxy_url,
        'http_proxy': proxy_url,
        'https_proxy': proxy_url
    }
    
    # 在Python中设置
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"✅ {key}={value}")
    
    # 更新.env文件
    env_file = Path('.env')
    env_content = []
    
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            env_content = f.readlines()
    
    # 添加代理配置到.env
    proxy_config = [
        "# SSR代理配置 - 基于研究资料\n",
        "USE_PROXY=true\n",
        f"HTTP_PROXY={proxy_url}\n",
        f"HTTPS_PROXY={proxy_url}\n",
        f"http_proxy={proxy_url}\n",
        f"https_proxy={proxy_url}\n",
        "\n"
    ]
    
    # 检查是否已存在代理配置
    has_proxy_config = any('HTTP_PROXY' in line for line in env_content)
    
    if not has_proxy_config:
        env_content.extend(proxy_config)
        
        with open(env_file, 'w', encoding='utf-8') as f:
            f.writelines(env_content)
        
        print(f"✅ 已更新.env文件")
    
    return True

def test_proxy_with_requests():
    """测试代理连接"""
    print("\n🧪 测试代理连接...")
    
    try:
        import requests
        
        # 测试代理
        proxies = {
            'http': os.environ.get('HTTP_PROXY'),
            'https': os.environ.get('HTTPS_PROXY')
        }
        
        print(f"使用代理: {proxies['https']}")
        
        # 测试获取外部IP
        response = requests.get(
            'https://httpbin.org/ip', 
            proxies=proxies, 
            timeout=10
        )
        
        if response.status_code == 200:
            ip_info = response.json()
            print(f"✅ 代理测试成功")
            print(f"   外部IP: {ip_info.get('origin')}")
            return True
        else:
            print(f"❌ 代理测试失败: HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 代理测试失败: {e}")
        return False

def create_vscode_launch_config():
    """创建VSCode调试配置"""
    print("\n📝 创建VSCode调试配置...")
    
    vscode_dir = Path('.vscode')
    vscode_dir.mkdir(exist_ok=True)
    
    launch_config = {
        "version": "0.2.0",
        "configurations": [
            {
                "name": "Python: 当前文件 (带SSR代理)",
                "type": "python",
                "request": "launch",
                "program": "${file}",
                "console": "integratedTerminal",
                "env": {
                    "HTTP_PROXY": "socks5h://localhost:1080",
                    "HTTPS_PROXY": "socks5h://localhost:1080",
                    "http_proxy": "socks5h://localhost:1080", 
                    "https_proxy": "socks5h://localhost:1080"
                }
            },
            {
                "name": "FastAPI: 主应用 (带SSR代理)",
                "type": "python",
                "request": "launch",
                "program": "${workspaceFolder}/backend/main.py",
                "console": "integratedTerminal",
                "cwd": "${workspaceFolder}/backend",
                "env": {
                    "HTTP_PROXY": "socks5h://localhost:1080",
                    "HTTPS_PROXY": "socks5h://localhost:1080",
                    "http_proxy": "socks5h://localhost:1080",
                    "https_proxy": "socks5h://localhost:1080"
                }
            }
        ]
    }
    
    launch_file = vscode_dir / 'launch.json'
    
    import json
    with open(launch_file, 'w', encoding='utf-8') as f:
        json.dump(launch_config, f, indent=4, ensure_ascii=False)
    
    print(f"✅ 已创建 {launch_file}")
    print("   现在你可以在VSCode中使用F5调试，自动使用SSR代理")

def install_pysocks():
    """安装pysocks库"""
    print("\n📦 检查pysocks库...")
    
    try:
        import socks
        print("✅ pysocks已安装")
        return True
    except ImportError:
        print("⚠️  pysocks未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pysocks'])
            print("✅ pysocks安装成功")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ pysocks安装失败: {e}")
            return False

if __name__ == "__main__":
    print("🚀 SSR代理配置工具")
    print("基于你的研究资料 - 环境变量方式")
    print("=" * 50)
    
    # 1. 安装必要库
    if not install_pysocks():
        print("❌ 无法安装pysocks，请手动安装: pip install pysocks")
        sys.exit(1)
    
    # 2. 设置环境变量
    setup_ssr_proxy_environment()
    
    # 3. 测试代理
    if test_proxy_with_requests():
        print("\n🎉 代理配置成功！")
        
        # 4. 创建VSCode配置
        create_vscode_launch_config()
        
        print("\n📋 使用说明:")
        print("1. 确保SSR客户端运行在端口1080")
        print("2. 在VSCode中使用F5调试，自动使用代理")
        print("3. 或在终端运行: python main.py")
        print("4. 所有HTTP/HTTPS请求都会通过SSR代理")
        
    else:
        print("\n⚠️  代理测试失败，请检查:")
        print("1. SSR客户端是否运行")
        print("2. 端口是否为1080")
        print("3. 是否允许本地连接")
