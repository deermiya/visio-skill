# visio-skill

这是一个 AI Agent 技能（Skill），通过调用本地 Visio COM 接口自动化生成或修改 Microsoft Visio `.vsdx` 图表文件。

## 简介

该技能使 AI Agent（如 Cursor、Copilot、Antigravity 等）能够在 Windows 计算机上原生创建真实的、可编辑的 Microsoft Visio 图表。它的工作原理是将 Agent 对图表结构的理解转换为声明式的 JSON 配置规范，随后由专用的 PowerShell 脚本解析该规范，并调用本地 Visio COM API 渲染出标准的 `.vsdx` 文件。

## 核心特性

- **原生 `.vsdx` 生成**：直接构建可编辑的 Microsoft Visio 图表文件，而非静态图片或普通的 SVG。
- **JSON 驱动设计**：通过简单的 JSON Schema 声明页面（pages）、节点（nodes）和连线（connections）来生成图表。
- **Visio 内置图标库支持**：支持使用 Visio 自带的专业 Stencil 模板（网络设备、服务器、云服务、Cisco/Azure/AWS 图标等），告别五花八门的自制图标。
- **精准的坐标定位**：使用显式的英寸坐标（x, y, w, h），确保图表布局一致且符合预期。
- **多场景图表支持**：支持绘制流程图、架构图、时序图、泳道图、网络拓扑图等多种常见图表。
- **专业时序图支持**：内置 UML 时序图模式，自动绘制生命线、激活框和消息箭头，支持同步/异步/返回消息类型。
- **混合使用基本形状与专业图标**：可在同一图表中混合使用基本几何形状和 Stencil 专业图标。

## 目录结构

- `SKILL.md` - Agent 的主指令文件，定义了 AI 的工作流、行为准则及图表绘制约束。
- `scripts/New-VisioDiagram.ps1` - 核心 PowerShell 脚本，负责与 Visio COM 对象交互并构建图表。
- `references/spec-format.md` - 标准图表的 JSON 规范文档，详述节点和连线的数据结构及格式要求。
- `references/sequence-format.md` - 时序图的 JSON 规范文档，详述 actors、messages 和 layout 的格式要求。
- `references/stencil-reference.md` - Visio Stencil 模板参考文档，列出常用的 Stencil 文件及其 Master 图标名称。
- `examples/` - 示例 JSON 文件，包含各种类型的图表示例。
- `agents/` - 针对特定 AI Agent 平台的专属配置、提示词（Prompt）或封装脚本。

## 环境要求

- **Windows 操作系统**
- 本地已安装 **Microsoft Visio**，且能够正常调用 COM 接口。
- **PowerShell** 运行环境

*(如需验证 Visio COM 接口是否可用，可在 PowerShell 中运行：`New-Object -ComObject Visio.Application`)*

## 安装与使用说明

### 1. 安装技能
通常情况下，你只需将本仓库克隆（或下载解压）到你的 AI Agent 约定的 Skills 目录下即可（例如 `~/.cursor/skills/visio-skill` 或 `~/.gemini/antigravity/skills/visio-skill`）。
*注意：请保持现有的目录结构。AI 会以 `SKILL.md` 为统一入口，并在后台自主调用 `scripts` 和 `references` 等目录下的文件。*

### 2. 使用方法
作为用户，你**无需手动去运行任何脚本、加载多个文件，或配置 JSON**。只需在支持技能的 AI 工具（如 Cursor、Antigravity 等）的对话窗口中，直接提及该技能并提出绘图需求即可。例如：

- *”@visio-skill 请帮我画一个电商系统的架构图，包含 Web 端、API 网关、订单服务、库存服务和数据库。”*
- *”用 Visio 画一个用户登录的流程图，要求横向排列。”*
- *”画一个用户认证的时序图，包含 User、Web App、Auth Service 和 Database 四个参与者。”*

**背后发生了什么？**
1. AI 识别触发意图后，会主动阅读本目录下的 `SKILL.md` 指令。
2. 根据 `SKILL.md` 的指示，AI 会在后台自动读取所需格式的参考文件，并生成结构化的 JSON 数据。
3. AI 自动通过终端运行本目录下的 `scripts/New-VisioDiagram.ps1` 脚本，将图表渲染出来。
整个多文件协作的过程，完全由 AI Agent 在后台自主闭环完成，对用户透明。

## 工作流程（供 Agent 参考）

1. **理解与规划**：AI 解析用户的图表绘制需求，并规划整体布局。
2. **生成 JSON**：AI 创建一份表示节点和连线结构的 JSON 配置文件，并保存到本地（如 `diagram.json`）。
3. **执行脚本**：AI 调用 PowerShell 脚本以渲染生成文件：
   ```powershell
   powershell -ExecutionPolicy Bypass -File "<skill目录>/scripts/New-VisioDiagram.ps1" -SpecPath "diagram.json" -OutputPath "diagram.vsdx"
   ```

## JSON 示例

### 标准流程图

```json
{
  "title": "Example Flowchart",
  "pages": [
    {
      "name": "Page-1",
      "nodes": [
        { "id": "start", "text": "Start", "x": 1, "y": 6, "w": 2, "h": 0.8 },
        { "id": "process", "text": "Process", "x": 4, "y": 6, "w": 2, "h": 0.8 }
      ],
      "connections": [
        { "from": "start", "to": "process", "text": "flow" }
      ]
    }
  ]
}
```

### 时序图

```json
{
  "type": "sequence",
  "title": "User Authentication Flow",
  "actors": [
    { "id": "user", "name": "User", "type": "actor" },
    { "id": "web", "name": "Web App", "type": "system" },
    { "id": "api", "name": "Auth Service", "type": "system" },
    { "id": "db", "name": "Database", "type": "database" }
  ],
  "messages": [
    { "from": "user", "to": "web", "text": "Enter credentials", "type": "sync" },
    { "from": "web", "to": "api", "text": "POST /login", "type": "sync" },
    { "from": "api", "to": "db", "text": "Query user", "type": "sync" },
    { "from": "db", "to": "api", "text": "User record", "type": "return" },
    { "from": "api", "to": "web", "text": "JWT token", "type": "return" },
    { "from": "web", "to": "user", "text": "Redirect to dashboard", "type": "return" }
  ]
}
```

---

## 更新日志

### v2.0 - 2026-05-28
**🎉 新增：时序图支持**

- ✨ **新增时序图模式**：通过设置 `"type": "sequence"` 自动生成 UML 时序图
- 📐 **自动布局**：智能绘制 actors、lifelines、消息箭头，无需手动计算坐标
- 🎨 **语义化配色**：4 种参与者类型自动着色（actor/system/database/external）
- 📄 **完整文档**：新增 `references/sequence-format.md` 详细规范
- 🔄 **消息类型**：支持同步调用（实线箭头）和返回消息（虚线箭头）
- 🎯 **示例文件**：提供 `example-sequence.json` 参考模板

**技术细节**：
- 扩展 `New-VisioDiagram.ps1` 脚本，新增 `Add-SequenceDiagram` 函数
- 支持自定义布局参数（actorSpacing、messageSpacing、startY、lifelineHeight）
- 兼容原有的标准图表绘制模式，通过 `type` 字段自动分支

---

### v1.0 - 初始版本
**基础功能**

- ✅ 标准图表支持：流程图、架构图、泳道图、网络拓扑图
- ✅ JSON 驱动设计：通过声明式配置生成图表
- ✅ 精准坐标定位：英寸级坐标控制（x, y, w, h）
- ✅ 多页面支持：单个 .vsdx 文件包含多个页面
- ✅ 自定义样式：支持颜色、字体、线型等完整配置
- ✅ COM 自动化：PowerShell 脚本调用 Visio COM 接口
