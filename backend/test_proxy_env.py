
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
