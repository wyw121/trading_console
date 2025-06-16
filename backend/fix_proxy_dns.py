"""
代理DNS解析问题修复方案
"""
import requests
import socket
import urllib3

# 禁用SSL警告
urllib3.disable_warnings()

def test_dns_resolution():
    """测试DNS解析"""
    print("=== 测试DNS解析 ===")
    
    domains = ['www.okx.com', 'okx.com', 'www.google.com']
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            print(f"✅ {domain} -> {ip}")
        except Exception as e:
            print(f"❌ {domain} -> 解析失败: {e}")

def test_direct_ip_access():
    """测试直接IP访问"""
    print("\n=== 测试直接IP访问 ===")
    
    # 常见的DNS服务器
    dns_servers = ['8.8.8.8', '1.1.1.1', '114.114.114.114']
    
    for dns in dns_servers:
        try:
            # 测试DNS服务器连通性
            response = requests.get(f'http://{dns}', timeout=5)
            print(f"✅ DNS {dns} 可访问")
        except:
            print(f"❌ DNS {dns} 不可访问")

def test_proxy_with_ip():
    """使用IP地址测试代理"""
    print("\n=== 使用IP测试代理 ===")
    
    # 尝试解析OKX的IP
    try:
        # 先在本地解析域名
        okx_ip = socket.gethostbyname('www.okx.com')
        print(f"OKX IP: {okx_ip}")
        
        # 使用代理访问IP
        proxies = {
            'http': 'socks5://127.0.0.1:1080',
            'https': 'socks5://127.0.0.1:1080'
        }
        
        # 构造请求（使用IP但保持Host头）
        headers = {
            'Host': 'www.okx.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(
            f'https://{okx_ip}/api/v5/public/time',
            proxies=proxies,
            headers=headers,
            timeout=15,
            verify=False
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 通过IP访问成功: {data}")
            return True
        else:
            print(f"❌ IP访问失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ IP访问异常: {e}")
    
    return False

def test_http_proxy_instead():
    """测试HTTP代理替代SOCKS"""
    print("\n=== 测试HTTP代理 ===")
    
    # 检查SSR是否也提供HTTP代理
    http_ports = [1087, 8080, 8888]
    
    for port in http_ports:
        try:
            # 测试端口
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                print(f"✅ HTTP代理端口 {port} 可用")
                
                # 测试HTTP代理
                proxies = {
                    'http': f'http://127.0.0.1:{port}',
                    'https': f'http://127.0.0.1:{port}'
                }
                
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies=proxies,
                    timeout=10
                )
                
                if response.status_code == 200:
                    ip_info = response.json()
                    print(f"   外部IP: {ip_info['origin']}")
                    return port
                    
            else:
                print(f"❌ HTTP代理端口 {port} 不可用")
                
        except Exception as e:
            print(f"❌ 测试端口 {port} 失败: {e}")
    
    return None

def fix_proxy_config():
    """修复代理配置"""
    print("\n=== 修复建议 ===")
    
    print("1. DNS解析问题的解决方案：")
    print("   - 方案A：使用HTTP代理替代SOCKS5")
    print("   - 方案B：配置系统DNS")
    print("   - 方案C：使用远程DNS解析")
    
    # 测试HTTP代理
    http_port = test_http_proxy_instead()
    
    if http_port:
        print(f"\n✅ 找到可用的HTTP代理端口: {http_port}")
        print("建议修改 .env 文件:")
        print(f"PROXY_TYPE=http")
        print(f"PROXY_PORT={http_port}")
        
        # 自动更新.env文件
        try:
            with open('.env', 'r') as f:
                content = f.read()
            
            # 替换配置
            content = content.replace('PROXY_TYPE=socks5', 'PROXY_TYPE=http')
            content = content.replace('PROXY_PORT=1080', f'PROXY_PORT={http_port}')
            
            with open('.env', 'w') as f:
                f.write(content)
            
            print("✅ 已自动更新 .env 文件")
            
        except Exception as e:
            print(f"❌ 更新配置文件失败: {e}")
    
    else:
        print("\n备选方案：")
        print("1. 检查SSR客户端是否开启了HTTP代理")
        print("2. 更换DNS服务器（使用8.8.8.8或1.1.1.1）")
        print("3. 检查系统防火墙设置")

if __name__ == "__main__":
    print("开始诊断代理DNS问题...\n")
    
    # 运行诊断
    test_dns_resolution()
    test_direct_ip_access()
    
    # 尝试修复
    fix_proxy_config()
    
    print("\n=== 诊断完成 ===")
    print("请根据上述建议修复配置，然后重新测试。")
