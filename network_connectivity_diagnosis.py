# OKX API 网络连接诊断工具
import requests
import time
from datetime import datetime

def test_okx_connectivity():
    """测试 OKX API 连接性"""
    print("🔍 OKX API 连接诊断开始...")
    print("=" * 60)
    
    # 测试多个 OKX API 端点
    test_endpoints = [
        {
            'name': 'OKX 主站 API',
            'url': 'https://www.okx.com/api/v5/public/time',
            'description': '主要的 OKX API 端点'
        },
        {
            'name': 'OKX AWS API',
            'url': 'https://aws.okx.com/api/v5/public/time',
            'description': 'AWS 托管的 OKX API'
        },
        {
            'name': 'OKX 香港站',
            'url': 'https://okx.com/api/v5/public/time',
            'description': '香港站点 API'
        },
        {
            'name': 'OKX 公共行情',
            'url': 'https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT',
            'description': '获取 BTC-USDT 价格数据'
        }
    ]
    
    results = []
    
    for endpoint in test_endpoints:
        print(f"\n🌐 测试: {endpoint['name']}")
        print(f"📍 URL: {endpoint['url']}")
        print(f"📝 说明: {endpoint['description']}")
        
        try:
            start_time = time.time()
            response = requests.get(
                endpoint['url'], 
                timeout=10,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            )
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                print(f"✅ 连接成功!")
                print(f"⏱️  响应时间: {response_time:.2f}ms")
                print(f"📊 状态码: {response.status_code}")
                
                # 尝试解析响应数据
                try:
                    data = response.json()
                    if 'data' in data:
                        print(f"📦 数据示例: {str(data)[:100]}...")
                    else:
                        print(f"📦 响应内容: {str(data)[:100]}...")
                except:
                    print(f"📦 响应内容: {response.text[:100]}...")
                
                results.append({
                    'endpoint': endpoint['name'],
                    'status': 'SUCCESS',
                    'response_time': response_time,
                    'status_code': response.status_code
                })
            else:
                print(f"❌ 连接失败!")
                print(f"📊 状态码: {response.status_code}")
                print(f"📦 错误信息: {response.text[:200]}...")
                
                results.append({
                    'endpoint': endpoint['name'],
                    'status': 'FAILED',
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'error': response.text[:200]
                })
                
        except requests.exceptions.Timeout:
            print(f"⏰ 连接超时 (>10秒)")
            results.append({
                'endpoint': endpoint['name'],
                'status': 'TIMEOUT',
                'error': 'Connection timeout after 10 seconds'
            })
            
        except requests.exceptions.ConnectionError as e:
            print(f"🚫 连接错误: {str(e)[:200]}...")
            results.append({
                'endpoint': endpoint['name'],
                'status': 'CONNECTION_ERROR',
                'error': str(e)[:200]
            })
            
        except Exception as e:
            print(f"❌ 未知错误: {str(e)[:200]}...")
            results.append({
                'endpoint': endpoint['name'],
                'status': 'ERROR',
                'error': str(e)[:200]
            })
    
    # 总结报告
    print("\n" + "=" * 60)
    print("📊 连接测试总结报告")
    print("=" * 60)
    
    successful_connections = sum(1 for r in results if r['status'] == 'SUCCESS')
    total_tests = len(results)
    
    print(f"✅ 成功连接: {successful_connections}/{total_tests}")
    print(f"❌ 连接失败: {total_tests - successful_connections}/{total_tests}")
    
    if successful_connections > 0:
        print("\n🎉 恭喜! 您的网络可以连接到 OKX API")
        avg_response_time = sum(r.get('response_time', 0) for r in results if r['status'] == 'SUCCESS') / successful_connections
        print(f"⚡ 平均响应时间: {avg_response_time:.2f}ms")
        
        # 建议最佳端点
        best_endpoint = min(
            [r for r in results if r['status'] == 'SUCCESS'],
            key=lambda x: x.get('response_time', float('inf'))
        )
        print(f"🏆 最佳端点: {best_endpoint['endpoint']} ({best_endpoint['response_time']:.2f}ms)")
        
    else:
        print("\n🚫 很遗憾，所有 OKX API 端点都无法连接")
        print("\n🔍 可能的原因:")
        print("   1. 网络防火墙阻止了对 OKX 域名的访问")
        print("   2. ISP (网络服务提供商) 限制了对加密货币交易所的访问")
        print("   3. 地理位置限制 (某些地区可能无法访问)")
        print("   4. 代理或VPN设置问题")
        
        print("\n💡 解决方案建议:")
        print("   1. 尝试使用 VPN 连接到其他地区")
        print("   2. 检查防火墙和代理设置")
        print("   3. 联系网络服务提供商")
        print("   4. 使用模拟模式进行开发和测试")
    
    # 详细结果表格
    print(f"\n📋 详细测试结果:")
    print(f"{'端点名称':<20} {'状态':<15} {'响应时间':<10} {'状态码':<8}")
    print("-" * 60)
    
    for result in results:
        status_icon = {
            'SUCCESS': '✅',
            'FAILED': '❌',
            'TIMEOUT': '⏰',
            'CONNECTION_ERROR': '🚫',
            'ERROR': '❌'
        }.get(result['status'], '❓')
        
        response_time = f"{result.get('response_time', 0):.0f}ms" if 'response_time' in result else "N/A"
        status_code = result.get('status_code', 'N/A')
        
        print(f"{result['endpoint']:<20} {status_icon} {result['status']:<13} {response_time:<10} {status_code:<8}")
    
    return successful_connections > 0

def test_alternative_apis():
    """测试替代的加密货币 API"""
    print("\n🔄 测试替代的加密货币 API...")
    print("=" * 60)
    
    alternative_apis = [
        {
            'name': 'Binance API',
            'url': 'https://api.binance.com/api/v3/time',
            'description': '币安交易所 API'
        },
        {
            'name': 'CoinGecko API',
            'url': 'https://api.coingecko.com/api/v3/ping',
            'description': '免费的加密货币数据 API'
        },
        {
            'name': 'CoinMarketCap API',
            'url': 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=1',
            'description': 'CoinMarketCap 数据 API'
        }
    ]
    
    alternative_working = []
    
    for api in alternative_apis:
        print(f"\n🌐 测试: {api['name']}")
        print(f"📍 URL: {api['url']}")
        
        try:
            response = requests.get(api['url'], timeout=10)
            if response.status_code == 200:
                print(f"✅ {api['name']} 连接成功!")
                alternative_working.append(api['name'])
            else:
                print(f"❌ {api['name']} 连接失败 (状态码: {response.status_code})")
        except Exception as e:
            print(f"❌ {api['name']} 连接错误: {str(e)[:100]}...")
    
    if alternative_working:
        print(f"\n✅ 可用的替代 API: {', '.join(alternative_working)}")
        print("💡 这说明您的网络连接正常，问题可能是 OKX 特定的访问限制")
    else:
        print(f"\n❌ 所有替代 API 也无法连接")
        print("💡 这可能表明网络连接存在更广泛的问题")

if __name__ == "__main__":
    print("🚀 OKX API 网络连接诊断工具")
    print(f"📅 测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🌍 测试位置: 本地网络环境")
    
    # 主要测试
    okx_available = test_okx_connectivity()
    
    # 替代API测试
    test_alternative_apis()
    
    # 最终建议
    print("\n" + "=" * 60)
    print("🎯 最终建议和下一步行动")
    print("=" * 60)
    
    if okx_available:
        print("✅ 您的网络可以正常连接 OKX API!")
        print("💡 建议:")
        print("   - 可以启用真实的 OKX API 连接")
        print("   - 在交易控制台中配置真实的 API 密钥")
        print("   - 建议先在测试网络进行验证")
    else:
        print("🚫 您的网络无法连接 OKX API")
        print("💡 当前解决方案:")
        print("   - 系统已自动使用模拟数据模式")
        print("   - 所有功能仍然可以正常使用")
        print("   - 数据为模拟生成，用于开发和测试")
        print("\n🛠️  如需连接真实 API，建议:")
        print("   1. 使用 VPN 尝试连接其他地区")
        print("   2. 检查网络防火墙设置")
        print("   3. 联系网络管理员或 ISP")
