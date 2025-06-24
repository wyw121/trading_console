#!/usr/bin/env python3
"""
OKX API诊断工具
专门诊断API密钥权限和配置问题
"""
import os
import requests
import time
import logging
from okx_api_manager import OKXAPIManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def diagnose_okx_api():
    """诊断OKX API配置问题"""
    
    # 你的API凭据
    API_KEY = "5a0ba67e-8e05-4c8f-a294-9674e40e3ce5"
    SECRET_KEY = "11005BB74DB1BD54D11F92CF207E479B"
    PASSPHRASE = "vf5Y3UeUFiz6xfF!"
    
    print("🔍 OKX API 配置诊断")
    print("=" * 60)
    print(f"API Key: {API_KEY}")
    print(f"Secret: {SECRET_KEY[:8]}...{SECRET_KEY[-8:]}")
    print(f"Passphrase: {PASSPHRASE}")
    print(f"配置的IP白名单: 23.145.24.14")
    print(f"权限: 读取、提现、交易")
    print("=" * 60)
    
    # 1. 检查当前IP
    print("\n1️⃣ 检查当前IP地址...")
    try:
        # 通过代理检查IP
        proxies = {'http': 'socks5h://127.0.0.1:1080', 'https': 'socks5h://127.0.0.1:1080'}
        response = requests.get('https://httpbin.org/ip', proxies=proxies, timeout=10)
        current_ip = response.json().get('origin', '未知')
        print(f"✅ 当前IP: {current_ip}")
        
        if '23.145.24.14' in current_ip:
            print("✅ IP地址匹配白名单")
        else:
            print("⚠️ IP地址不匹配白名单，这可能是问题所在")
    except Exception as e:
        print(f"❌ 无法获取当前IP: {e}")
    
    # 2. 测试公开API
    print("\n2️⃣ 测试公开API（不需要认证）...")
    try:
        manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
        
        # 获取服务器时间
        time_result = manager.get_server_time()
        if time_result.get('code') == '0':
            server_time = time_result['data'][0]['ts']
            local_time = int(time.time() * 1000)
            time_diff = abs(int(server_time) - local_time)
            print(f"✅ 服务器时间: {server_time}")
            print(f"✅ 本地时间: {local_time}")
            print(f"✅ 时间差: {time_diff}ms")
            
            if time_diff > 30000:  # 超过30秒
                print("⚠️ 时间差较大，可能影响API调用")
            else:
                print("✅ 时间同步正常")
        else:
            print(f"❌ 获取服务器时间失败: {time_result}")
            
        # 获取价格信息
        ticker_result = manager.get_ticker('BTC-USDT')
        if ticker_result.get('code') == '0':
            price = ticker_result['data'][0]['last']
            print(f"✅ BTC价格: ${price}")
        else:
            print(f"❌ 获取价格失败: {ticker_result}")
            
    except Exception as e:
        print(f"❌ 公开API测试失败: {e}")
    
    # 3. 分析私有API问题
    print("\n3️⃣ 分析私有API问题...")
    try:
        manager = OKXAPIManager(API_KEY, SECRET_KEY, PASSPHRASE)
        
        # 尝试多种时间戳策略
        strategies = [
            ("服务器时间戳", "server"),
            ("本地时间戳", "local"),
            ("本地时间戳-1秒", "local-1"),
            ("本地时间戳-2秒", "local-2"),
        ]
        
        for strategy_name, strategy_type in strategies:
            print(f"\n🔄 尝试策略: {strategy_name}")
            
            if strategy_type == "server":
                # 使用服务器时间戳
                try:
                    time_response = requests.get('https://www.okx.com/api/v5/public/time', 
                                               proxies=manager.proxies, timeout=5)
                    if time_response.status_code == 200:
                        server_data = time_response.json()
                        timestamp = server_data['data'][0]['ts']
                    else:
                        continue
                except:
                    continue
            elif strategy_type == "local":
                timestamp = str(int(time.time() * 1000))
            elif strategy_type == "local-1":
                timestamp = str(int((time.time() - 1) * 1000))
            elif strategy_type == "local-2":
                timestamp = str(int((time.time() - 2) * 1000))
            
            # 手动构造请求测试
            try:
                import hmac
                import hashlib
                import base64
                
                method = 'GET'
                request_path = '/api/v5/account/balance'
                body = ''
                
                message = timestamp + method + request_path + body
                signature = base64.b64encode(
                    hmac.new(SECRET_KEY.encode('utf-8'), 
                            message.encode('utf-8'), 
                            hashlib.sha256).digest()
                ).decode('utf-8')
                
                headers = {
                    'OK-ACCESS-KEY': API_KEY,
                    'OK-ACCESS-SIGN': signature,
                    'OK-ACCESS-TIMESTAMP': timestamp,
                    'OK-ACCESS-PASSPHRASE': PASSPHRASE,
                    'Content-Type': 'application/json'
                }
                
                url = f'https://www.okx.com{request_path}'
                response = requests.get(url, headers=headers, proxies=manager.proxies, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('code') == '0':
                        print(f"✅ {strategy_name} 成功!")
                        return result
                    else:
                        error_code = result.get('code', 'unknown')
                        error_msg = result.get('msg', 'unknown')
                        print(f"❌ {strategy_name} 失败: [{error_code}] {error_msg}")
                        
                        # 分析错误码
                        if error_code == '50102':
                            print("   时间戳问题")
                        elif error_code == '50111':
                            print("   API密钥无效")
                        elif error_code == '50113':
                            print("   权限不足")
                        elif error_code in ['50114', '401']:
                            print("   IP限制")
                else:
                    print(f"❌ {strategy_name} HTTP错误: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {strategy_name} 异常: {e}")
                
    except Exception as e:
        print(f"❌ 私有API分析失败: {e}")
    
    # 4. 提供诊断建议
    print("\n4️⃣ 诊断建议")
    print("=" * 60)
    print("基于测试结果，建议检查以下项目:")
    print("1. ✅ 确认API密钥信息是否正确输入")
    print("2. ✅ 确认API密钥是否已过期")
    print("3. ⚠️ 检查API权限设置（需要'读取'权限）")
    print("4. ⚠️ 检查IP白名单设置")
    print("   - 当前IP应该是: 23.145.24.14")
    print("   - 或者可以尝试将IP白名单设为空（允许所有IP）")
    print("5. ⚠️ 确认API密钥状态是否正常（未被冻结）")
    print("6. ⚠️ 检查是否有其他安全限制")
    
    print("\n💡 如果时间戳错误持续出现，这通常意味着:")
    print("   - API密钥权限不足（最常见）")
    print("   - IP地址不在白名单中")
    print("   - API密钥配置有误")
    print("   - 而不是真正的时间同步问题")

if __name__ == "__main__":
    diagnose_okx_api()
