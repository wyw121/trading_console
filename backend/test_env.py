import os
from dotenv import load_dotenv

load_dotenv()

print("=== 环境变量测试 ===")
print(f"USE_PROXY: {os.getenv('USE_PROXY')}")
print(f"PROXY_HOST: {os.getenv('PROXY_HOST')}")  
print(f"PROXY_PORT: {os.getenv('PROXY_PORT')}")
print(f"PROXY_TYPE: {os.getenv('PROXY_TYPE')}")

print("\n=== 代理配置测试 ===")
try:
    from proxy_config import proxy_config
    print(f"代理启用: {proxy_config.proxy_enabled}")
    print(f"代理地址: {proxy_config.proxy_host}:{proxy_config.proxy_port}")
    if proxy_config.proxy_enabled:
        print(f"代理配置: {proxy_config.get_proxy_dict()}")
except Exception as e:
    print(f"错误: {e}")

print("\n=== 端口测试 ===")
import socket

def test_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

ports = [1080, 1081, 7890, 10808]
for port in ports:
    status = "可用" if test_port("127.0.0.1", port) else "不可用" 
    current = " (当前)" if port == int(os.getenv('PROXY_PORT', '1080')) else ""
    print(f"端口 {port}: {status}{current}")
