# Visio Skill (English)

## Overview

The **Visio Skill** automatically generates or modifies Microsoft Visio `.vsdx` diagrams using local Visio COM automation. It is designed for Windows environments where Microsoft Visio is installed. Users only need to describe the desired diagram in natural language; the skill handles JSON spec creation and PowerShell script execution behind the scenes.

---

## Installation

1. Clone or download the repository into your AI Agent's skills directory (e.g., `~/.cursor/skills/visio-skill` or `~/.gemini/antigravity/skills/visio-skill`).
2. Keep the directory structure intact – the skill entry point is `SKILL.md`, and supporting scripts reside in `scripts/`.

---

## How to Use

From any AI‑enabled tool that supports skills (Cursor, Antigravity, etc.), simply mention the skill and describe the diagram you need. Example prompts:

- `@visio-skill Please draw an e‑commerce architecture diagram with Web Frontend, API Gateway, Order Service, Inventory Service, and Database.`
- `Create a user‑login flowchart in Visio, arranged horizontally.`

The agent will automatically: 
1. Parse the request.
2. Generate a structured JSON spec.
3. Execute `scripts/New-VisioDiagram.ps1` to render the `.vsdx` file.

---

## Workflow (for the Agent)

1. **Understanding & Planning** – Analyze the user request and decide on a layout.
2. **JSON Generation** – Produce a JSON file (e.g., `diagram.json`) that describes pages, nodes, and connections.
3. **Script Execution** – Run the PowerShell script:
```powershell
powershell -ExecutionPolicy Bypass -File "<skill_dir>/scripts/New-VisioDiagram.ps1" -SpecPath "diagram.json" -OutputPath "diagram.vsdx"
```
4. **Result Delivery** – Return the generated `.vsdx` (or a PNG/PDF preview) to the user.

---

## Minimal JSON Example

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

---

## Validation

After execution, verify that the `.vsdx` file exists and is non‑empty. If needed, the skill can open the file via COM and export a PNG or PDF for quick visual QA.

---

## Compatibility Note

The skill relies on the Windows‑only Visio COM API; it will not run on macOS or Linux without a Windows VM or remote execution environment. In such cases, consider alternative formats like Mermaid, SVG, or draw.io.

---

*Author: Chmy*
