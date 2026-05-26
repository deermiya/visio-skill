# visio-skill

这是一个 AI Agent 技能（Skill），通过调用本地 Visio COM 接口自动化生成或修改 Microsoft Visio `.vsdx` 图表文件。

## 简介

该技能使 AI Agent（如 Cursor、Copilot、Antigravity 等）能够在 Windows 计算机上原生创建真实的、可编辑的 Microsoft Visio 图表。它的工作原理是将 Agent 对图表结构的理解转换为声明式的 JSON 配置规范，随后由专用的 PowerShell 脚本解析该规范，并调用本地 Visio COM API 渲染出标准的 `.vsdx` 文件。

## 核心特性

- **原生 `.vsdx` 生成**：直接构建可编辑的 Microsoft Visio 图表文件，而非静态图片或普通的 SVG。
- **JSON 驱动设计**：通过简单的 JSON Schema 声明页面（pages）、节点（nodes）和连线（connections）来生成图表。
- **精准的坐标定位**：使用显式的英寸坐标（x, y, w, h），确保图表布局一致且符合预期。
- **多场景图表支持**：支持绘制流程图、架构图、泳道图、网络拓扑图等多种常见图表。

## 目录结构

- `SKILL.md` - Agent 的主指令文件，定义了 AI 的工作流、行为准则及图表绘制约束。
- `scripts/New-VisioDiagram.ps1` - 核心 PowerShell 脚本，负责与 Visio COM 对象交互并构建图表。
- `references/spec-format.md` - 完整的 JSON 规范文档，详述节点和连线的数据结构及格式要求。
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

- *“@visio-skill 请帮我画一个电商系统的架构图，包含 Web 端、API 网关、订单服务、库存服务和数据库。”*
- *“用 Visio 画一个用户登录的流程图，要求横向排列。”*

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

## 精简版 JSON 示例

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
