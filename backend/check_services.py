"""
交易控制台服务状态检查工具
检查前后端服务、数据库连接、API可用性等
"""
import requests
import time
import subprocess
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_port(port, service_name):
    """检查端口是否被占用"""
    try:
        # 确保不使用代理进行本地连接检查
        response = requests.get(f"http://localhost:{port}", timeout=5, proxies={'http': None, 'https': None})
        return f"✅ {service_name} (端口 {port}) 正在运行"
    except requests.exceptions.ConnectionError:
        return f"❌ {service_name} (端口 {port}) 未响应"
    except Exception as e:
        return f"⚠️ {service_name} (端口 {port}) 检查失败: {str(e)}"

def check_backend_api():
    """检查后端API接口"""
    try:
        # 检查健康接口，不使用代理
        response = requests.get("http://localhost:8000/", timeout=10, proxies={'http': None, 'https': None})
        if response.status_code == 200:
            return "✅ 后端API根接口正常"
        else:
            return f"⚠️ 后端API根接口返回 {response.status_code}"
    except Exception as e:
        return f"❌ 后端API不可用: {str(e)}"

def check_exchange_api():
    """检查交易所API接口"""
    try:
        # 这个接口需要认证，403是正常的，不使用代理
        response = requests.get("http://localhost:8000/api/exchanges/", timeout=10, proxies={'http': None, 'https': None})
        if response.status_code == 200:
            return "✅ 交易所账户列表API正常"
        elif response.status_code == 403:
            return "✅ 交易所API需要认证 (正常响应)"
        elif response.status_code == 401:
            return "✅ 交易所API需要认证 (正常响应)"
        else:
            return f"⚠️ 交易所API返回 {response.status_code}"
    except Exception as e:
        return f"❌ 交易所API不可用: {str(e)}"

def check_proxy_connection():
    """检查代理连接"""
    try:
        # 检查代理设置
        use_proxy = os.getenv('USE_PROXY', 'false').lower() == 'true'
        if not use_proxy:
            return "ℹ️ 代理未启用"
        
        proxy_host = os.getenv('PROXY_HOST', '127.0.0.1')
        proxy_port = os.getenv('PROXY_PORT', '1080')
        
        proxies = {
            'http': f'socks5h://{proxy_host}:{proxy_port}',
            'https': f'socks5h://{proxy_host}:{proxy_port}'
        }
        
        # 测试通过代理访问OKX公共API
        response = requests.get(
            "https://www.okx.com/api/v5/public/time",
            proxies=proxies,
            timeout=10
        )
        
        if response.status_code == 200:
            return "✅ 代理连接正常，可访问OKX API"
        else:
            return f"⚠️ 代理连接异常: HTTP {response.status_code}"
            
    except Exception as e:
        return f"❌ 代理连接失败: {str(e)}"

def check_database_connection():
    """检查数据库连接"""
    try:
        from database import get_db, engine
        from sqlalchemy import text
        
        # 测试数据库连接
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return "✅ 数据库连接正常"
    except Exception as e:
        return f"❌ 数据库连接失败: {str(e)}"

def main():
    """主检查函数"""
    print("🔍 交易控制台服务状态检查")
    print("=" * 60)
      # 检查各项服务
    checks = [
        ("前端服务", lambda: check_port(3000, "前端服务")),
        ("后端服务", lambda: check_port(8000, "后端服务")),
        ("后端API", check_backend_api),
        ("交易所API", check_exchange_api),
        ("数据库连接", check_database_connection),
        ("代理连接", check_proxy_connection),
    ]
    
    results = []
    
    for name, check_func in checks:
        print(f"\n🔍 检查 {name}...")
        try:
            result = check_func()
            print(f"   {result}")
            results.append((name, result))
        except Exception as e:
            error_msg = f"❌ 检查失败: {str(e)}"
            print(f"   {error_msg}")
            results.append((name, error_msg))
        
        time.sleep(0.5)  # 避免频繁请求
    
    # 输出总结
    print("\n" + "=" * 60)
    print("📊 检查结果总结:")
    
    success_count = 0
    for name, result in results:
        print(f"   {name}: {result}")
        if result.startswith("✅"):
            success_count += 1
    
    print(f"\n🎯 成功率: {success_count}/{len(results)} ({success_count/len(results)*100:.1f}%)")
    
    # 给出建议
    if success_count == len(results):
        print("\n🎉 所有服务状态正常！")
    else:
        print("\n💡 建议:")
        print("   - 确保前后端服务已启动")
        print("   - 检查数据库服务是否运行")
        print("   - 验证代理设置和网络连接")
        print("   - 查看服务日志以获取更多信息")

if __name__ == "__main__":
    main()
