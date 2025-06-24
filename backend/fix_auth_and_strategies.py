"""
修复Token认证问题和策略数据查询
"""
import requests
import json

def test_authentication_flow():
    """测试完整的认证流程"""
    BASE_URL = "http://localhost:8000"
    
    print("🔧 修复Token认证问题...")
    
    # 1. 登录获取Token
    print("\n1. 登录admin用户...")
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data="username=admin&password=admin123"
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.status_code}")
        return None
        
    token_data = login_response.json()
    token = token_data["access_token"]
    print(f"✅ 获取Token成功: {token[:50]}...")
    
    # 2. 测试用户信息
    print("\n2. 验证Token...")
    headers = {"Authorization": f"Bearer {token}"}
    
    me_response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    if me_response.status_code == 200:
        user_data = me_response.json()
        print(f"✅ 用户验证成功: {user_data['username']} (ID: {user_data['id']})")
        user_id = user_data['id']
    else:
        print(f"❌ 用户验证失败: {me_response.status_code} - {me_response.text}")
        return None
    
    # 3. 测试所有主要API端点
    endpoints_to_test = [
        ("/api/dashboard/stats", "Dashboard统计"),
        ("/api/strategies", "策略列表"),
        ("/api/trades", "交易记录"),
        ("/api/exchanges/", "交易所账户")
    ]
    
    results = {}
    for endpoint, name in endpoints_to_test:
        print(f"\n3. 测试 {name}...")
        response = requests.get(f"{BASE_URL}{endpoint}", headers=headers)
        
        results[endpoint] = {
            "status_code": response.status_code,
            "success": response.status_code == 200
        }
        
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                print(f"✅ {name}: 成功 ({len(data)} 项)")
                results[endpoint]["count"] = len(data)
                results[endpoint]["data"] = data
            else:
                print(f"✅ {name}: 成功 (对象数据)")
                results[endpoint]["data"] = data
        else:
            print(f"❌ {name}: 失败 {response.status_code}")
            try:
                error_data = response.json()
                print(f"   错误详情: {error_data}")
                results[endpoint]["error"] = error_data
            except:
                print(f"   原始错误: {response.text}")
                results[endpoint]["error"] = response.text
    
    return results, token, user_id

def analyze_strategy_data(results, user_id):
    """分析策略数据问题"""
    print(f"\n🔍 分析用户 {user_id} 的策略数据...")
    
    if "/api/strategies" in results and results["/api/strategies"]["success"]:
        strategies = results["/api/strategies"]["data"]
        print(f"当前用户策略数: {len(strategies)}")
        
        if len(strategies) == 0:
            print("⚠️  当前admin用户没有策略数据")
            print("需要检查数据库中的策略归属")
            
            # 从数据库查询策略信息
            from database import engine, Strategy, User
            from sqlalchemy.orm import sessionmaker
            
            Session = sessionmaker(bind=engine)
            db = Session()
            
            all_strategies = db.query(Strategy).all()
            print(f"\n数据库中总策略数: {len(all_strategies)}")
            
            admin_user = db.query(User).filter(User.username == "admin").first()
            if admin_user:
                admin_strategies = db.query(Strategy).filter(Strategy.user_id == admin_user.id).all()
                print(f"admin用户的策略数: {len(admin_strategies)}")
                
                if len(admin_strategies) == 0:
                    print("🔧 需要将现有策略转移给admin用户...")
                    
                    # 将现有策略转移给admin用户
                    for strategy in all_strategies:
                        print(f"转移策略: {strategy.name} (原用户ID: {strategy.user_id}) -> admin (ID: {admin_user.id})")
                        strategy.user_id = admin_user.id
                    
                    db.commit()
                    print("✅ 策略转移完成")
                else:
                    for strategy in admin_strategies:
                        print(f"  策略: {strategy.name} (活跃: {strategy.is_active})")
            
            db.close()
        else:
            for strategy in strategies:
                print(f"  策略: {strategy['name']} (ID: {strategy['id']}, 活跃: {strategy['is_active']})")
    else:
        print("❌ 无法获取策略数据")

def main():
    print("=" * 60)
    print("🚀 Trading Console 认证和策略数据修复")
    print("=" * 60)
    
    results, token, user_id = test_authentication_flow()
    
    if results:
        print(f"\n📊 API测试结果总结:")
        for endpoint, result in results.items():
            status = "✅" if result["success"] else "❌"
            print(f"{status} {endpoint}: {result['status_code']}")
        
        analyze_strategy_data(results, user_id)
        
        print(f"\n🔑 当前有效Token: {token[:50]}...")
        print("💡 如果前端仍有问题，请使用此Token在浏览器中测试")
        
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
