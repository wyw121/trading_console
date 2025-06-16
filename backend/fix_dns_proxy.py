"""
解决SOCKS代理DNS解析问题的方案
"""
import socket
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.connection import create_connection
import ccxt

# 方案1: 使用IP地址代替域名
OKX_HOSTS_MAP = {
    'www.okx.com': '43.198.155.107',
    'aws.okx.com': '52.83.245.23', 
    'okx.com': '43.198.155.107'
}

def patch_socket_for_socks():
    """修补socket以支持SOCKS代理的DNS解析"""
    import socks
    
    # 设置SOCKS代理
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
    socket.socket = socks.socksocket

def test_dns_resolution():
    """测试DNS解析"""
    print("=== DNS解析测试 ===")
    
    hosts = ['www.okx.com', 'okx.com', 'aws.okx.com']
    
    for host in hosts:
        try:
            ip = socket.gethostbyname(host)
            print(f"✅ {host} -> {ip}")
        except Exception as e:
            print(f"❌ {host} -> 解析失败: {e}")

def test_proxy_with_ip():
    """使用IP地址测试代理连接"""
    print("\n=== 使用IP地址测试OKX API ===")
    
    session = requests.Session()
    session.proxies = {
        'http': 'socks5://127.0.0.1:1080',
        'https': 'socks5://127.0.0.1:1080'
    }
    
    # 使用IP地址直接访问
    ip = '43.198.155.107'  # okx.com的IP
    
    try:
        # 测试API调用
        url = f'https://{ip}/api/v5/public/time'
        headers = {'Host': 'www.okx.com'}  # 设置Host头
        
        response = session.get(url, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 通过IP访问成功: {data}")
            return True
        else:
            print(f"❌ 响应错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
    
    return False

def test_system_proxy():
    """测试系统代理设置"""
    print("\n=== 测试系统代理 ===")
    
    import os
    
    # 设置系统代理环境变量
    os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:1080'
    os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:1080'
    
    try:
        # 不设置session代理，使用系统代理
        response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
        
        if response.status_code == 200:
            print("✅ 系统代理工作正常")
            return True
        else:
            print(f"❌ 系统代理失败: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 系统代理连接失败: {e}")
    finally:
        # 清理环境变量
        os.environ.pop('HTTP_PROXY', None)
        os.environ.pop('HTTPS_PROXY', None)
    
    return False

def test_pysocks_method():
    """测试PySocks方法"""
    print("\n=== 测试PySocks方法 ===")
    
    try:
        import socks
        import socket
        
        # 保存原始socket
        original_socket = socket.socket
        
        # 设置SOCKS代理
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
        socket.socket = socks.socksocket
        
        try:
            response = requests.get('https://www.okx.com/api/v5/public/time', timeout=15)
            
            if response.status_code == 200:
                print("✅ PySocks方法成功")
                return True
            else:
                print(f"❌ PySocks方法失败: {response.status_code}")
                
        except Exception as e:
            print(f"❌ PySocks连接失败: {e}")
        finally:
            # 恢复原始socket
            socket.socket = original_socket
            
    except ImportError:
        print("❌ PySocks未安装")
    except Exception as e:
        print(f"❌ PySocks方法异常: {e}")
    
    return False

def suggest_solutions():
    """提供解决方案建议"""
    print("\n=== 解决方案建议 ===")
    
    print("1. 检查SSR客户端设置:")
    print("   - 确保'远程DNS解析'已开启")
    print("   - 代理规则设置为'绕过局域网和大陆'")
    print("   - 尝试切换不同的代理模式")
    
    print("\n2. 检查系统DNS设置:")
    print("   - 尝试使用8.8.8.8或1.1.1.1作为DNS")
    print("   - 清除DNS缓存: ipconfig /flushdns")
    
    print("\n3. SSR客户端替代方案:")
    print("   - 尝试使用Clash for Windows")
    print("   - 尝试使用V2rayN")
    print("   - 确保代理软件支持应用程序代理")
    
    print("\n4. 代码层面解决:")
    print("   - 使用IP地址代替域名")
    print("   - 修改hosts文件添加域名映射")
    print("   - 使用系统代理模式")

if __name__ == "__main__":
    print("诊断SOCKS代理DNS解析问题")
    print("=" * 50)
    
    # 1. 测试DNS解析
    test_dns_resolution()
    
    # 2. 测试不同的代理方法
    methods = [
        ("IP地址方法", test_proxy_with_ip),
        ("系统代理方法", test_system_proxy),
        ("PySocks方法", test_pysocks_method)
    ]
    
    success_methods = []
    
    for name, test_func in methods:
        if test_func():
            success_methods.append(name)
    
    print(f"\n=== 测试结果 ===")
    if success_methods:
        print(f"✅ 可用方法: {', '.join(success_methods)}")
    else:
        print("❌ 所有方法都失败")
        suggest_solutions()
