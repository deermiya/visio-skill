# visio-vsdx

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

## 用户使用说明

作为用户，你无需手动运行任何脚本或配置 JSON。只需在支持技能的 AI 工具（如 Cursor、Antigravity 等）的对话窗口中直接提出绘图需求即可。例如：

- *“请帮我画一个电商系统的架构图，包含 Web 端、API 网关、订单服务、库存服务和数据库。”*
- *“用 Visio 画一个用户登录的流程图，要求横向排列。”*

AI 将自动理解你的需求，计算并规划排版坐标，最终在本地自动生成对应的 `.vsdx` 图表文件。

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
