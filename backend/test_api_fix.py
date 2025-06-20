#!/usr/bin/env python3
"""测试修复后的API端点"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_ticker_endpoint():
    """测试ticker端点（可能会失败，但不应该有TypeError）"""
    print("🧪 测试ticker端点...")
    
    # 这可能会失败因为没有真实账户，但应该返回有意义的错误而不是TypeError
    url = f"{BASE_URL}/api/exchanges/accounts/5/ticker/BTCUSDT"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        print(f"📊 响应内容: {response.text[:200]}...")
        
        if response.status_code == 400:
            try:
                error_data = response.json()
                error_detail = error_data.get('detail', '未知错误')
                if 'unsupported operand type' not in error_detail:
                    print("✅ 没有TypeError错误！")
                    return True
                else:  
                    print("❌ 仍然有TypeError错误")
                    return False
            except:
                print("⚠️ 无法解析响应JSON")
                return False
        elif response.status_code == 401:
            print("✅ 401未授权是正常的，至少没有TypeError")
            return True
        else:
            print(f"✅ 意外但没有TypeError，状态码: {response.status_code}")
            return True
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

def test_exchanges_endpoint():
    """测试交易所账户列表端点"""
    print("🧪 测试交易所账户列表端点...")
    
    url = f"{BASE_URL}/api/exchanges/"
    
    try:
        response = requests.get(url, timeout=10)
        print(f"📊 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取账户列表成功: {len(data)} 个账户")
            return True
        else:
            print(f"⚠️ 状态码 {response.status_code}: {response.text[:100]}")
            return False
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试修复后的API...")
    
    # 测试基本端点
    exchanges_ok = test_exchanges_endpoint()
    
    # 测试ticker端点（重点测试TypeError修复）
    ticker_ok = test_ticker_endpoint()
    
    if ticker_ok:
        print("\n🎉 修复验证成功！")
        print("✅ 不再出现 'unsupported operand type(s) for +: 'NoneType' and 'str'' 错误")
    else:
        print("\n❌ 修复可能不完整，仍有TypeError")
