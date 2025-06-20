#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import asyncio
import ccxt.async_support as ccxt  # 使用异步CCXT
import requests

# 设置SOCKS5代理环境变量（全局生效）
os.environ.update({
    'HTTP_PROXY': 'socks5h://127.0.0.1:1080',
    'HTTPS_PROXY': 'socks5h://127.0.0.1:1080',
    'http_proxy': 'socks5h://127.0.0.1:1080',
    'https_proxy': 'socks5h://127.0.0.1:1080'
})

API_KEY = "edb07d2e-8fb5-46e8-84b8-5e1795c71ac0"
SECRET_KEY = "CD6A497EEB00AA2DC60B2B0974DD2485"
PASSPHRASE = "vf5Y3UeUFiz6xfF!"

print("\n🔑 测试OKX API连接 (仅SOCKS5代理, 避免HTTPS拦截)")
print("=" * 40)

# 1. 只用HTTP测试网络连通性
print("1. 测试HTTP网络连通性...")
try:
    proxies = {'http': 'socks5h://127.0.0.1:1080'}
    resp = requests.get('http://www.okx.com/api/v5/public/time', proxies=proxies, timeout=15)
    if resp.status_code == 200:
        print("✅ HTTP网络连接正常")
        print(f"   服务器时间: {resp.json()}")
    else:
        print(f"❌ HTTP网络连接失败: {resp.status_code}")
except Exception as e:
    print(f"❌ HTTP网络连接异常: {e}")

# 2. 测试CCXT API (强制SOCKS5代理)
print("\n2. 测试CCXT API (SOCKS5, 避免HTTPS)...")

async def test_api():
    try:
        exchange = ccxt.okx({
            'apiKey': API_KEY,
            'secret': SECRET_KEY,
            'password': PASSPHRASE,
            'sandbox': False,
            'timeout': 30000,
            'enableRateLimit': True,
            'proxies': {
                'http': 'socks5h://127.0.0.1:1080',
                'https': 'socks5h://127.0.0.1:1080'
            },
            'headers': {
                'User-Agent': 'ccxt/trading-console'
            }
        })
        print("正在连接到OKX (SOCKS5)...")
        # 公共API优先尝试HTTP
        try:
            markets = await exchange.load_markets()
            print(f"✅ 公共API连接成功，市场数量: {len(markets)}")
        except Exception as e:
            print(f"❌ 公共API连接失败: {e}")
            return
        # 私有API
        try:
            balance = await exchange.fetch_balance()
            print("✅ 私有API连接成功！")
            print("\n📊 账户余额:")
            total_balances = balance.get('total', {})
            for currency, amount in total_balances.items():
                if amount > 0:
                    print(f"   {currency}: {amount}")
            if not any(amount > 0 for amount in total_balances.values()):
                print("   账户余额为0或仅有极小余额")
        except Exception as e:
            print(f"❌ 私有API连接失败: {e}")
            print("   可能的原因:")
            print("   - API权限不足（当前权限：读取）")
            print("   - 网络连接问题")
            print("   - API密钥配置错误")
        await exchange.close()
        print("\n🎉 API测试完成！")
    except Exception as e:
        print(f"❌ API测试失败: {e}")
        import traceback
        print(f"详细错误: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_api())
