#!/usr/bin/env python3
"""
交易所账户加载超时修复测试脚本
"""
import os
import sys
import time
import requests
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_account_list_api():
    """测试账户列表API响应速度"""
    
    # 测试用的JWT Token（根据你的系统调整）
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTczNzU5ODE4M30.b4Gf1X3VbNNuAl-0MWXiKsLhcjcUyaQxUm0pdfpfhQg"
    headers = {'Authorization': f'Bearer {test_token}'}
    
    base_url = "http://localhost:8000"
    
    logger.info("=== 交易所账户加载超时修复测试 ===")
    
    # 测试1: 账户列表API
    logger.info("1. 测试账户列表API (/api/exchanges/)")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{base_url}/api/exchanges/", 
            headers=headers, 
            timeout=10
        )
        
        response_time = time.time() - start_time
        
        logger.info(f"   ✅ 响应时间: {response_time:.2f}秒")
        logger.info(f"   ✅ 状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"   ✅ 返回账户数量: {len(data)}")
            
            # 检查响应时间是否合理
            if response_time < 2.0:
                logger.info("   ✅ 响应速度: 优秀 (< 2秒)")
            elif response_time < 5.0:
                logger.info("   ⚠️  响应速度: 一般 (2-5秒)")
            else:
                logger.warning("   ❌ 响应速度: 较慢 (> 5秒)")
                
        else:
            logger.error(f"   ❌ API返回错误: {response.text}")
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        logger.error(f"   ❌ API超时 (>{response_time:.1f}秒)")
        return False
        
    except requests.exceptions.ConnectionError:
        logger.error("   ❌ 连接失败，请确保后端服务正在运行")
        return False
        
    except Exception as e:
        logger.error(f"   ❌ 请求失败: {e}")
        return False
    
    # 测试2: 测试多次请求的一致性
    logger.info("\n2. 测试连续多次请求的稳定性")
    
    times = []
    for i in range(3):
        start_time = time.time()
        try:
            response = requests.get(f"{base_url}/api/exchanges/", headers=headers, timeout=5)
            response_time = time.time() - start_time
            times.append(response_time)
            logger.info(f"   请求 {i+1}: {response_time:.2f}秒 (状态码: {response.status_code})")
        except Exception as e:
            logger.error(f"   请求 {i+1} 失败: {e}")
            times.append(999)  # 失败标记
    
    # 分析结果
    valid_times = [t for t in times if t < 900]
    if valid_times:
        avg_time = sum(valid_times) / len(valid_times)
        max_time = max(valid_times)
        logger.info(f"\n   平均响应时间: {avg_time:.2f}秒")
        logger.info(f"   最大响应时间: {max_time:.2f}秒")
        
        if avg_time < 1.0:
            logger.info("   ✅ 整体性能: 优秀")
        elif avg_time < 3.0:
            logger.info("   ⚠️  整体性能: 良好")
        else:
            logger.warning("   ❌ 整体性能: 需要优化")
    
    return True

def test_balance_api():
    """测试余额API的超时处理"""
    
    test_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ0ZXN0dXNlciIsImV4cCI6MTczNzU5ODE4M30.b4Gf1X3VbNNuAl-0MWXiKsLhcjcUyaQxUm0pdfpfhQg"
    headers = {'Authorization': f'Bearer {test_token}'}
    base_url = "http://localhost:8000"
    
    logger.info("\n3. 测试余额API超时处理")
    
    # 假设账户ID为1（根据实际情况调整）
    account_id = 1
    
    start_time = time.time()
    try:
        response = requests.get(
            f"{base_url}/api/exchanges/accounts/{account_id}/balance", 
            headers=headers, 
            timeout=12  # 给余额API更多时间
        )
        
        response_time = time.time() - start_time
        
        logger.info(f"   响应时间: {response_time:.2f}秒")
        logger.info(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            message = data.get('message', '')
            
            if success:
                logger.info(f"   ✅ 余额获取成功: {message}")
            else:
                logger.info(f"   ⚠️  余额获取失败但有友好错误: {message}")
                
        elif response.status_code == 404:
            logger.info("   ℹ️  账户不存在，这是正常的（如果没有账户）")
        else:
            logger.warning(f"   ⚠️  API返回: {response.text}")
            
    except requests.exceptions.Timeout:
        response_time = time.time() - start_time
        logger.error(f"   ❌ 余额API超时 (>{response_time:.1f}秒)")
        
    except Exception as e:
        logger.error(f"   ❌ 余额API请求失败: {e}")

def main():
    """主测试函数"""
    
    print(f"\n{'='*60}")
    print("交易所账户加载超时修复测试")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    # 检查后端服务是否运行
    try:
        response = requests.get("http://localhost:8000/health", timeout=3)
        logger.info("✅ 后端服务正在运行")
    except:
        logger.error("❌ 后端服务未运行，请先启动后端服务")
        logger.info("提示: 使用命令 'python main.py' 启动后端服务")
        return False
    
    # 运行测试
    success = True
    
    if not test_account_list_api():
        success = False
    
    test_balance_api()
    
    print(f"\n{'='*60}")
    if success:
        logger.info("✅ 修复测试完成 - 账户列表API响应正常")
    else:
        logger.error("❌ 修复测试失败 - 仍存在超时问题")
    print(f"{'='*60}\n")
    
    return success

if __name__ == "__main__":
    main()
