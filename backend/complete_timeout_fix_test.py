#!/usr/bin/env python3
"""
交易所账户加载超时修复 - 完整测试脚本
"""
import requests
import time
import json
from datetime import datetime

def main():
    print(f"\n{'='*60}")
    print("交易所账户加载超时修复 - 完整测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    base_url = "http://localhost:8000"
    
    # 第一步：注册用户
    print("\n1. 创建测试用户...")
    register_data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f'{base_url}/api/auth/register', json=register_data, timeout=5)
        if response.status_code == 201:
            print("   ✅ 用户创建成功")
        elif response.status_code == 400 and "already exists" in response.text:
            print("   ℹ️  用户已存在，继续测试")
        else:
            print(f"   ⚠️  注册响应: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ 注册失败: {e}")
        return False
    
    # 第二步：登录获取token
    print("\n2. 用户登录...")
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    try:
        response = requests.post(f'{base_url}/api/auth/login', json=login_data, timeout=5)
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            if token:
                print(f"   ✅ 登录成功，获得token: {token[:20]}...")
            else:
                print("   ❌ 登录成功但未获得token")
                return False
        else:
            print(f"   ❌ 登录失败: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 登录请求失败: {e}")
        return False
    
    # 第三步：测试账户列表API的响应速度
    print("\n3. 测试账户列表API响应速度...")
    headers = {'Authorization': f'Bearer {token}'}
    
    times = []
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.get(f'{base_url}/api/exchanges/', headers=headers, timeout=8)
            response_time = time.time() - start_time
            times.append(response_time)
            
            print(f"   测试 {i+1}: {response_time:.2f}秒, 状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"      返回 {len(data)} 个账户")
            else:
                print(f"      错误响应: {response.text}")
                
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            times.append(999)  # 超时标记
            print(f"   测试 {i+1}: ❌ 超时 ({response_time:.1f}秒)")
            
        except Exception as e:
            response_time = time.time() - start_time
            times.append(999)  # 错误标记
            print(f"   测试 {i+1}: ❌ 错误 ({response_time:.1f}秒) - {e}")
        
        if i < 2:  # 不是最后一次测试时等待
            time.sleep(1)
    
    # 分析结果
    print(f"\n4. 测试结果分析...")
    valid_times = [t for t in times if t < 900]
    
    if not valid_times:
        print("   ❌ 所有测试都失败了，修复未成功")
        return False
    
    avg_time = sum(valid_times) / len(valid_times)
    max_time = max(valid_times)
    min_time = min(valid_times)
    
    print(f"   📊 响应时间统计:")
    print(f"      平均: {avg_time:.2f}秒")
    print(f"      最快: {min_time:.2f}秒")
    print(f"      最慢: {max_time:.2f}秒")
    print(f"      成功率: {len(valid_times)}/3")
    
    # 评估修复效果
    print(f"\n5. 修复效果评估...")
    
    if len(valid_times) == 3:
        if avg_time < 1.0:
            print("   🎉 修复效果: 优秀！API响应速度非常快")
            success_level = "优秀"
        elif avg_time < 2.0:
            print("   ✅ 修复效果: 良好！超时问题已解决")
            success_level = "良好"
        elif avg_time < 5.0:
            print("   ⚠️  修复效果: 一般，仍有优化空间")
            success_level = "一般"
        else:
            print("   ❌ 修复效果: 不理想，需要进一步优化")
            success_level = "不理想"
    else:
        print("   ❌ 修复效果: 不稳定，仍有请求失败")
        success_level = "不稳定"
    
    # 第六步：测试余额API（如果有账户）
    print(f"\n6. 测试余额API超时处理...")
    try:
        # 尝试获取第一个账户的余额（如果存在）
        response = requests.get(f'{base_url}/api/exchanges/accounts/1/balance', headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("   ✅ 余额API工作正常")
            else:
                print(f"   ⚠️  余额API返回友好错误: {data.get('message', '')}")
        elif response.status_code == 404:
            print("   ℹ️  没有账户，这是正常的")
        else:
            print(f"   ⚠️  余额API响应: {response.status_code}")
            
    except Exception as e:
        print(f"   ⚠️  余额API测试失败: {e}")
    
    print(f"\n{'='*60}")
    print(f"✅ 测试完成 - 修复效果: {success_level}")
    if success_level in ["优秀", "良好"]:
        print("🎉 交易所账户加载超时问题已成功修复！")
    else:
        print("⚠️  仍需进一步优化以达到最佳性能")
    print(f"{'='*60}\n")
    
    return success_level in ["优秀", "良好"]

if __name__ == "__main__":
    try:
        success = main()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        exit(1)
    except Exception as e:
        print(f"\n\n测试过程中发生错误: {e}")
        exit(1)
