# 🎯 OKX API问题快速修复指南

## 🔍 问题诊断

您遇到的问题根本原因：
- **API密钥类型**: 正式网API密钥
- **系统设置**: 但配置为测试网环境
- **结果**: 认证失败，无法连接

## ✅ 解决方案 (选择其一)

### 方案1: 浏览器手动修复 (推荐)

1. **删除现有账户**:
   - 在浏览器中打开 http://localhost:3000
   - 进入"交易所配置"页面
   - 点击OKEX账户的"删除"按钮

2. **重新添加账户**:
   - 点击"添加账户"按钮
   - 交易所: 选择"OKX"
   - API Key: `edb07d2e-8fb5-46e8-84b8-5e1795c71ac0`
   - Secret Key: `CD6A497EEB00AA2DC60B2B0974DD2485`
   - Passphrase: `vf5Y3UeUFiz6xfF!`
   - **环境: 选择"正式网"** ⚠️ 重要！
   - 点击"保存"

3. **验证修复**:
   - 点击"测试连接" → 应该成功
   - 点击"查看余额" → 显示真实余额

### 方案2: 脚本自动修复

```powershell
# 在PowerShell中运行
cd c:\trading_console
.\fix_okx_account.ps1
```

## 🧪 验证结果

修复成功后，您应该看到：

### ✅ 测试连接
- 之前: "连接测试失败: Not Found"
- 现在: "连接测试成功" 或 具体的API错误

### ✅ 查看余额  
- 之前: "获取余额失败: Error fetching balance"
- 现在: 显示您的OKX账户实际余额

## ⚠️ 重要提醒

1. **API权限确认**:
   - 您的API已正确设置为"读取"权限 ✅
   - 建议不要开启"交易"权限（除非需要真实交易）
   - 绝对不要开启"提现"权限

2. **IP白名单**:
   - 建议在OKX后台设置IP白名单
   - 限制只允许您当前IP访问

3. **环境选择**:
   - 正式网 = 真实资金，真实交易
   - 测试网 = 虚拟资金，用于测试

## 📞 故障排除

如果修复后仍有问题：

1. **检查后端服务**:
   ```powershell
   netstat -an | Select-String ":8000"
   ```

2. **重启后端服务**:
   ```powershell
   cd c:\trading_console\backend
   python dev_server.py
   ```

3. **检查API状态**:
   - 登录OKX官网检查API密钥状态
   - 确认IP访问权限

---

## 🎯 快速操作

**推荐操作顺序**:
1. 浏览器删除现有OKEX账户
2. 重新添加，环境选择"正式网"
3. 测试连接验证修复

**预期结果**: 连接成功，可以查看真实余额。
