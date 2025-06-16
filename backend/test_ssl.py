import requests
import urllib3
from dotenv import load_dotenv

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

from proxy_config import proxy_config

print("=== 网络连接测试 (跳过SSL验证) ===")

# 配置requests会话
session = requests.Session()
session.verify = False  # 跳过SSL验证

if proxy_config.proxy_enabled:
    proxy_dict = proxy_config.get_proxy_dict()
    session.proxies.update(proxy_dict)
    print(f"使用代理: {proxy_dict['https']}")

# 测试不同的网站
test_sites = [
    ('Google', 'https://www.google.com'),
    ('百度', 'https://www.baidu.com'),
    ('OKX', 'https://www.okx.com'),
    ('Binance', 'https://www.binance.com'),
    ('IP检查', 'https://httpbin.org/ip')
]

print("\n测试结果:")
success_count = 0

for name, url in test_sites:
    try:
        response = session.get(url, timeout=10, verify=False)
        if response.status_code == 200:
            print(f"✅ {name}: 成功 ({response.status_code})")
            success_count += 1
            
            # 如果是IP检查，显示IP
            if 'httpbin.org' in url:
                try:
                    ip_info = response.json()
                    print(f"   IP地址: {ip_info.get('origin')}")
                except:
                    pass
        else:
            print(f"⚠️  {name}: 状态码 {response.status_code}")
    except Exception as e:
        print(f"❌ {name}: 失败 - {str(e)[:100]}...")

print(f"\n=== 总结 ===")
print(f"成功连接: {success_count}/{len(test_sites)}")

if success_count > 0:
    print("✅ 网络连接正常！")
    if proxy_config.proxy_enabled:
        print("✅ 你的代码正在通过SSR代理访问外网")
        print("✅ 对OKX等交易所的API调用都会通过代理")
    else:
        print("✅ 你的代码正在直连访问网络")
else:
    print("❌ 网络连接异常，请检查:")
    print("   1. SSR客户端是否正在运行")
    print("   2. 代理端口是否正确 (当前: 1080)")
    print("   3. 防火墙设置")

print(f"\n当前代理状态: {'启用' if proxy_config.proxy_enabled else '禁用'}")
print("如需切换，请修改 .env 文件中的 USE_PROXY 设置")
