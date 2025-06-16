#!/usr/bin/env python3
"""
代理连接测试脚本
用于验证ShadowsocksR代理配置是否正确
"""
import sys
import os
import logging
import asyncio
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from proxy_config import proxy_config, test_proxy_connection
from real_trading_engine import RealExchangeManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('proxy_test.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

def print_separator(title: str):
    """打印分隔符"""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def test_proxy_basic():
    """基本代理配置测试"""
    print_separator("基本代理配置测试")
    
    print(f"代理启用状态: {proxy_config.proxy_enabled}")
    print(f"代理类型: {proxy_config.proxy_type}")
    print(f"代理地址: {proxy_config.proxy_host}:{proxy_config.proxy_port}")
    
    if proxy_config.proxy_enabled:
        proxy_dict = proxy_config.get_proxy_dict()
        print(f"Requests代理配置: {proxy_dict}")
        
        ccxt_config = proxy_config.get_ccxt_proxy_config()
        print(f"CCXT代理配置keys: {list(ccxt_config.keys())}")

def test_network_connectivity():
    """网络连通性测试"""
    print_separator("网络连通性测试")
    
    success = test_proxy_connection()
    print(f"代理连接测试结果: {'✅ 成功' if success else '❌ 失败'}")
    
    return success

async def test_okx_connection():
    """测试OKX连接"""
    print_separator("OKX API连接测试")
    
    try:
        # 创建真实交易引擎
        engine = RealExchangeManager()
        
        # 测试配置（使用测试API密钥）
        test_config = {
            'apiKey': 'test_api_key',
            'secret': 'test_secret',
            'passphrase': 'test_passphrase',
            'sandbox': True  # 使用沙盒环境
        }
        
        print("正在测试OKX连接...")
        
        try:
            # 尝试创建OKX连接
            exchange = await engine.create_real_exchange('okx', test_config)
            print("✅ OKX连接创建成功")
            
            # 测试公共API
            try:
                markets = exchange.markets
                print(f"✅ 成功获取市场数据，共{len(markets)}个交易对")
            except Exception as e:
                print(f"⚠️  获取市场数据失败: {str(e)}")
            
            # 关闭连接
            if hasattr(exchange, 'close'):
                await exchange.close()
                
            return True
            
        except Exception as e:
            error_msg = str(e)
            if "API key" in error_msg or "authentication" in error_msg.lower():
                print("ℹ️  API认证失败（这是正常的，因为我们使用的是测试密钥）")
                print("✅ 网络连接正常，可以访问OKX服务器")
                return True
            else:
                print(f"❌ OKX连接失败: {error_msg}")
                return False
                
    except Exception as e:
        print(f"❌ OKX连接测试异常: {str(e)}")
        return False

def check_shadowsocksr_status():
    """检查ShadowsocksR状态"""
    print_separator("ShadowsocksR状态检查")
    
    import socket
    
    # 检查代理端口是否开放
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    
    try:
        result = sock.connect_ex((proxy_config.proxy_host, proxy_config.proxy_port))
        if result == 0:
            print(f"✅ ShadowsocksR服务运行正常 ({proxy_config.proxy_host}:{proxy_config.proxy_port})")
            return True
        else:
            print(f"❌ ShadowsocksR服务无法连接 ({proxy_config.proxy_host}:{proxy_config.proxy_port})")
            return False
    except Exception as e:
        print(f"❌ 检查ShadowsocksR服务失败: {str(e)}")
        return False
    finally:
        sock.close()

def provide_troubleshooting_tips():
    """提供故障排除建议"""
    print_separator("故障排除建议")
    
    print("如果遇到连接问题，请检查以下几点：")
    print("")
    print("1. ShadowsocksR客户端：")
    print("   - 确保ShadowsocksR客户端正在运行")
    print("   - 检查本地端口设置（通常是1080或1081）")
    print("   - 确认'允许来自局域网的连接'已开启")
    print("")
    print("2. 代理配置：")
    print("   - 检查.env文件中的PROXY_PORT是否与SSR客户端一致")
    print("   - 确认PROXY_TYPE设置为socks5")
    print("   - 检查USE_PROXY=true")
    print("")
    print("3. 网络设置：")
    print("   - 确保防火墙允许Python访问网络")
    print("   - 检查SSR服务器是否正常工作")
    print("   - 尝试在浏览器中测试代理是否正常")
    print("")
    print("4. 常见端口：")
    print("   - ShadowsocksR默认: 1080 (SOCKS5)")
    print("   - 部分客户端使用: 1081")
    print("   - HTTP代理通常使用: 8080 或 1087")

async def main():
    """主测试函数"""
    print("开始代理配置和连接测试...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 基本配置测试
    test_proxy_basic()
    
    # 2. ShadowsocksR状态检查
    ssr_ok = check_shadowsocksr_status()
    
    # 3. 网络连通性测试
    if ssr_ok and proxy_config.proxy_enabled:
        network_ok = test_network_connectivity()
    else:
        print("⚠️  跳过网络连通性测试（ShadowsocksR未运行或代理未启用）")
        network_ok = False
    
    # 4. OKX连接测试
    if network_ok:
        okx_ok = await test_okx_connection()
    else:
        print("⚠️  跳过OKX连接测试（网络连接失败）")
        okx_ok = False
    
    # 5. 总结
    print_separator("测试结果总结")
    print(f"ShadowsocksR服务: {'✅ 正常' if ssr_ok else '❌ 异常'}")
    print(f"代理网络连接: {'✅ 正常' if network_ok else '❌ 异常'}")
    print(f"OKX API访问: {'✅ 正常' if okx_ok else '❌ 异常'}")
    
    if ssr_ok and network_ok and okx_ok:
        print("\n🎉 所有测试通过！你的代理配置正确，可以正常访问OKX API。")
    else:
        print("\n⚠️  部分测试失败，请参考故障排除建议。")
        provide_troubleshooting_tips()

if __name__ == "__main__":
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 运行测试
    asyncio.run(main())
