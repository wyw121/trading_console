# GitHub Copilot 自定义指令和提示文件使用指南

## 概述

本项目已配置 GitHub Copilot 的自定义指令和提示文件功能，以提供更准确、符合项目规范的代码生成和协助。

## 文件结构

```
.github/
├── copilot-instructions.md           # 主要项目指令文件
├── instructions/                     # 特定任务指令文件夹
│   ├── backend-api.instructions.md   # 后端 API 开发指令
│   ├── frontend-vue.instructions.md  # 前端 Vue.js 开发指令
│   ├── trading-engine.instructions.md # 交易引擎指令
│   └── database.instructions.md      # 数据库开发指令
└── prompts/                          # 可重用提示文件夹
    ├── create-fastapi-endpoint.prompt.md    # 创建 FastAPI 端点
    ├── create-vue-component.prompt.md       # 创建 Vue.js 组件
    ├── create-trading-strategy.prompt.md    # 创建交易策略
    ├── debug-issue.prompt.md               # 调试问题
    └── security-review.prompt.md           # 安全代码审查
```

## 功能说明

### 1. 自定义指令 (Custom Instructions)

#### 主指令文件 (.github/copilot-instructions.md)
- **自动应用**: 所有 Copilot 对话都会自动包含这些指令
- **内容**: 项目概述、技术栈、编码规范、最佳实践
- **适用范围**: 整个项目的所有代码生成任务

#### 特定指令文件 (.github/instructions/*.instructions.md)
- **条件应用**: 根据文件类型自动应用相应指令
- **文件匹配**: 使用 `applyTo` 属性指定适用的文件模式
- **专业化**: 针对特定技术栈的详细指令

**示例使用场景**:
- 编辑 `backend/routers/users.py` 时，自动应用后端 API 指令
- 编辑 `frontend/src/components/UserList.vue` 时，自动应用 Vue.js 指令
- 编辑包含 "trading" 的文件时，自动应用交易引擎指令

### 2. 提示文件 (Prompt Files)

提示文件是可重用的任务模板，可以快速执行常见的开发任务。

#### 使用方法

**方法 1: 命令面板**
1. 按 `Ctrl+Shift+P` 打开命令面板
2. 输入 "Chat: Run Prompt"
3. 选择要运行的提示文件

**方法 2: 聊天界面**
在 Copilot Chat 中输入 `/` 加提示文件名：
```
/create-fastapi-endpoint
/create-vue-component
/create-trading-strategy
/debug-issue
/security-review
```

**方法 3: 文件编辑器**
1. 打开提示文件（.prompt.md）
2. 点击编辑器标题栏的播放按钮

#### 可用提示文件

1. **create-fastapi-endpoint**: 创建新的 FastAPI 端点
   - 包含路径、方法、描述参数
   - 自动生成路由、模型、错误处理代码

2. **create-vue-component**: 创建新的 Vue.js 组件
   - 支持页面组件和普通组件
   - 集成 Element Plus 和 Pinia 状态管理

3. **create-trading-strategy**: 实现新的交易策略
   - 包含策略类、技术分析、风险管理
   - 遵循 CCXT 集成模式

4. **debug-issue**: 系统性调试问题
   - 涵盖后端、前端、交易引擎各个层面
   - 提供详细的调试步骤和工具

5. **security-review**: 安全代码审查
   - 全面的安全检查清单
   - 针对交易应用的特定安全考虑

## 配置设置

项目已在 `.vscode/settings.json` 中启用以下配置：

```json
{
  "github.copilot.chat.codeGeneration.useInstructionFiles": true,
  "chat.promptFiles": true,
  "chat.instructionsFilesLocations": [
    ".github/instructions"
  ],
  "chat.promptFilesLocations": [
    ".github/prompts"
  ]
}
```

## 使用示例

### 示例 1: 创建新的 API 端点

1. 在 Chat 中输入: `/create-fastapi-endpoint`
2. 填写提示的参数:
   - Path: `/api/v1/strategies/{strategy_id}/backtest`
   - Method: `POST`
   - Description: `Run backtest for a trading strategy`
3. Copilot 会生成完整的端点代码，包括路由、模型、错误处理

### 示例 2: 创建 Vue.js 组件

1. 在 Chat 中输入: `/create-vue-component`
2. 填写参数:
   - Component Name: `StrategyBacktest`
   - Purpose: `Display backtest results with charts`
   - Parent Route: `/strategies`
3. 生成完整的 Vue 组件代码

### 示例 3: 调试问题

1. 在 Chat 中输入: `/debug-issue`
2. 描述问题:
   - Problem: `OKX API connection timeout`
   - Component: `trading engine`
   - Error Message: `Connection timeout after 30 seconds`
3. 获得系统性的调试指导

## 自定义和扩展

### 添加新的指令文件

1. 在 `.github/instructions/` 创建新的 `.instructions.md` 文件
2. 添加前置元数据指定适用文件:
```markdown
---
description: "Your instruction description"
applyTo: "path/pattern/**/*.ext"
---
```

### 添加新的提示文件

1. 在 `.github/prompts/` 创建新的 `.prompt.md` 文件
2. 添加前置元数据:
```markdown
---
description: "Your prompt description"
mode: "agent"
tools: ["filesystem", "terminal"]
---
```

### 使用变量

在提示文件中可以使用以下变量：
- `${input:variableName:placeholder}` - 用户输入
- `${workspaceFolder}` - 工作区路径
- `${file}` - 当前文件路径
- `${selection}` - 当前选中文本

## 最佳实践

1. **保持指令简洁明确**: 避免过于复杂的指令，保持单一职责
2. **使用具体示例**: 在指令中包含代码示例和具体要求
3. **定期更新**: 根据项目演进更新指令内容
4. **测试提示文件**: 创建新提示文件后要测试其效果
5. **版本控制**: 将指令文件纳入版本控制，便于团队协作

## 故障排除

### 指令文件未生效
1. 检查 VS Code 设置中是否启用了相关配置
2. 确认文件路径和文件名格式正确
3. 重新启动 VS Code 或重新加载窗口

### 提示文件无法运行
1. 检查文件扩展名是否为 `.prompt.md`
2. 确认前置元数据格式正确
3. 检查是否在正确的目录中

### 指令冲突
1. 避免在不同指令文件中有矛盾的要求
2. 使用更具体的 `applyTo` 模式
3. 检查指令的优先级和应用顺序

## 更多资源

- [VS Code Copilot 自定义文档](https://code.visualstudio.com/docs/copilot/copilot-customization)
- [GitHub Copilot 官方文档](https://docs.github.com/en/copilot)
- [项目编码规范](./copilot-instructions.md)
