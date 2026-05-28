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
- `Draw a sequence diagram for user authentication with User, Web App, Auth Service, and Database.`

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

## JSON Examples

### Standard Flowchart

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

### Sequence Diagram

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

## Validation

After execution, verify that the `.vsdx` file exists and is non‑empty. If needed, the skill can open the file via COM and export a PNG or PDF for quick visual QA.

---

## Compatibility Note

The skill relies on the Windows‑only Visio COM API; it will not run on macOS or Linux without a Windows VM or remote execution environment. In such cases, consider alternative formats like Mermaid, SVG, or draw.io.

---

---

## Changelog

### v2.0 - 2026-05-28
**🎉 New: Sequence Diagram Support**

- ✨ **Sequence diagram mode**: Set `"type": "sequence"` to auto-generate UML sequence diagrams
- 📐 **Auto-layout**: Intelligent rendering of actors, lifelines, and message arrows—no manual coordinate calculation
- 🎨 **Semantic coloring**: 4 actor types with automatic color coding (actor/system/database/external)
- 📄 **Complete documentation**: New `references/sequence-format.md` specification
- 🔄 **Message types**: Support for sync calls (solid arrows) and return messages (dashed arrows)
- 🎯 **Example file**: Includes `example-sequence.json` reference template

**Technical details**:
- Extended `New-VisioDiagram.ps1` script with new `Add-SequenceDiagram` function
- Customizable layout parameters (actorSpacing, messageSpacing, startY, lifelineHeight)
- Backward-compatible with standard diagram mode via `type` field detection

---

### v1.0 - Initial Release
**Core Features**

- ✅ Standard diagram support: flowcharts, architecture diagrams, swimlanes, network topology
- ✅ JSON-driven design: declarative configuration for diagram generation
- ✅ Precise coordinate control: inch-level positioning (x, y, w, h)
- ✅ Multi-page support: multiple pages in a single .vsdx file
- ✅ Custom styling: full support for colors, fonts, line patterns, etc.
- ✅ COM automation: PowerShell script invoking Visio COM interface

---

*Author: Chmy*
