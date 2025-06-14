# OKX API 配置文件
# 请复制此文件为 okx_config.py 并填入您的真实API密钥

# =========================
# OKX API 配置
# =========================

# 生产环境 API 配置
PRODUCTION_CONFIG = {
    'api_key': 'your_production_api_key_here',
    'secret_key': 'your_production_secret_key_here', 
    'passphrase': 'your_production_passphrase_here',
    'is_sandbox': False,  # 生产环境
    'description': '生产环境配置 - 请谨慎使用'
}

# 测试环境 API 配置 (推荐)
SANDBOX_CONFIG = {
    'api_key': 'your_sandbox_api_key_here',
    'secret_key': 'your_sandbox_secret_key_here',
    'passphrase': 'your_sandbox_passphrase_here', 
    'is_sandbox': True,  # 测试环境
    'description': '测试环境配置 - 安全测试使用'
}

# 默认使用的配置
DEFAULT_CONFIG = SANDBOX_CONFIG  # 默认使用测试环境

# =========================
# API 权限配置
# =========================

# 建议的API权限设置
RECOMMENDED_PERMISSIONS = {
    'read': True,        # 读取权限 - 必需
    'trade': False,      # 交易权限 - 测试时建议关闭
    'withdraw': False,   # 提现权限 - 强烈建议关闭
    'description': '推荐权限配置：只开启读取权限进行测试'
}

# =========================
# 安全配置
# =========================

SECURITY_CONFIG = {
    'enable_ip_whitelist': True,     # 启用IP白名单
    'api_key_rotation_days': 30,     # API密钥轮换周期(天)
    'max_daily_api_calls': 10000,    # 每日最大API调用次数
    'rate_limit_buffer': 0.8,        # 限速缓冲比例
    'timeout_seconds': 30,           # 请求超时时间
}

# =========================
# 交易配置
# =========================

TRADING_CONFIG = {
    'default_symbol': 'BTC-USDT',     # 默认交易对
    'min_order_size': 0.0001,        # 最小下单量
    'max_order_size': 1.0,           # 最大下单量
    'price_precision': 2,            # 价格精度
    'quantity_precision': 4,         # 数量精度
    'stop_loss_ratio': 0.02,         # 止损比例 (2%)
    'take_profit_ratio': 0.05,       # 止盈比例 (5%)
}

# =========================
# 日志配置
# =========================

LOGGING_CONFIG = {
    'level': 'INFO',                 # 日志级别
    'enable_api_logging': True,      # 启用API调用日志
    'enable_trade_logging': True,    # 启用交易日志
    'log_file': 'okx_trading.log',   # 日志文件
    'max_log_size_mb': 100,         # 最大日志文件大小(MB)
    'backup_count': 5,              # 日志备份数量
}

# =========================
# 如何获取 OKX API 密钥
# =========================

API_KEY_GUIDE = """
🔑 OKX API密钥获取步骤:

1. 【注册/登录】
   - 访问 https://www.okx.com
   - 注册并完成身份验证

2. 【进入模拟交易】(推荐先测试)
   - 点击【交易】→ 【模拟交易】
   - 进入模拟交易环境

3. 【创建API密钥】
   - 点击右上角头像 → 【模拟交易API】
   - 点击【创建API密钥】
   - 填写API名称
   - 设置权限（建议先只开启读取权限）
   - 设置IP白名单（可选但推荐）

4. 【保存密钥信息】
   - API Key: 公开密钥
   - Secret Key: 私有密钥 
   - Passphrase: API密码短语
   
   ⚠️ 重要：密钥信息只显示一次，请务必保存！

5. 【配置到代码】
   - 将密钥信息填入上方配置
   - 建议使用环境变量存储密钥
   - 不要将密钥上传到代码仓库

6. 【测试连接】
   - 运行测试脚本验证连接
   - 确认权限和功能正常

📚 相关文档:
- API文档: https://www.okx.com/docs-v5/
- Python SDK: https://github.com/okxapi/python-okx
- 交易教程: https://www.okx.com/help/
"""

# =========================
# 环境变量配置示例
# =========================

ENV_VARS_EXAMPLE = """
# 环境变量配置示例 (.env 文件)
# 推荐使用环境变量存储敏感信息

# OKX API 配置
OKX_API_KEY=your_api_key_here
OKX_SECRET_KEY=your_secret_key_here  
OKX_PASSPHRASE=your_passphrase_here
OKX_IS_SANDBOX=true

# 安全配置
OKX_ENABLE_LOGGING=true
OKX_MAX_API_CALLS=10000
OKX_TIMEOUT=30

# 使用方法:
import os
from dotenv import load_dotenv

load_dotenv()

config = {
    'api_key': os.getenv('OKX_API_KEY'),
    'secret_key': os.getenv('OKX_SECRET_KEY'),
    'passphrase': os.getenv('OKX_PASSPHRASE'),
    'is_sandbox': os.getenv('OKX_IS_SANDBOX', 'true').lower() == 'true'
}
"""

# =========================
# 配置验证函数
# =========================

def validate_config(config):
    """验证配置是否有效"""
    required_fields = ['api_key', 'secret_key', 'passphrase']
    
    for field in required_fields:
        if not config.get(field) or config[field].startswith('your_'):
            return False, f"缺少或未配置字段: {field}"
    
    return True, "配置验证通过"

def get_config(env='sandbox'):
    """获取指定环境的配置"""
    if env == 'production':
        return PRODUCTION_CONFIG
    else:
        return SANDBOX_CONFIG

def print_setup_guide():
    """打印设置指南"""
    print(API_KEY_GUIDE)
    print("\n" + "="*50)
    print("📋 配置检查清单:")
    print("□ 已获取OKX API密钥")
    print("□ 已设置适当的API权限")
    print("□ 已配置IP白名单（可选）")
    print("□ 已在配置文件中填入密钥")
    print("□ 已通过连接测试")
    print("□ 已了解API限速规则")

if __name__ == "__main__":
    print_setup_guide()
