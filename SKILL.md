---
name: visio-skill
description: Generate or modify Microsoft Visio .vsdx diagrams using local Visio COM automation. Use when the user asks Codex to create Visio files, draw flowcharts, architecture diagrams, sequence diagrams, swimlane-style layouts, network topology diagrams, process maps, or to automate shapes/connectors/text in Microsoft Visio on Windows.
---

# Visio Skill

## Workflow

Use local Microsoft Visio COM automation when Visio is installed and the user wants a real `.vsdx` file. Prefer the bundled script for new diagrams:

```powershell
powershell -ExecutionPolicy Bypass -File "<skill>/scripts/New-VisioDiagram.ps1" -SpecPath "<diagram.json>" -OutputPath "<diagram.vsdx>"
```

Create a JSON spec first, then run the script. Keep output files in the user's requested folder, or in the active workspace when unspecified.

## JSON Spec

This skill supports two diagram types:

### 1. Standard Diagrams (flowcharts, architecture, etc.)

Read `references/spec-format.md` for the full format. Minimum example:

```json
{
  "title": "Example",
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

Coordinates are in Visio inches. `x` and `y` are the lower-left corner of the node; `w` and `h` are width and height.

### 2. Stencil Icons (模具图标)

Standard diagrams can drop **real Visio icons** from built-in stencils (e.g., routers, servers, PCs). Declare stencils at top level, then reference them in nodes:

```json
{
  "title": "Network Topology",
  "stencils": [
    { "id": "net", "file": "NETSYM_M.VSSX" },
    { "id": "srv", "file": "SERVER_M.VSSX" },
    { "id": "hw",  "file": "PERIPH_M.VSSX" }
  ],
  "nodes": [
    { "id": "r1", "stencil": "net", "master": "Router", "text": "核心路由", "x": 4, "y": 7 },
    { "id": "s1", "stencil": "srv", "master": "Web server", "text": "Web服务器", "x": 7, "y": 7 },
    { "id": "fw", "stencil": "hw",  "master": "Firewall", "text": "防火墙", "x": 4, "y": 4 }
  ],
  "connections": [
    { "from": "r1", "to": "fw", "text": "LAN" },
    { "from": "fw", "to": "s1", "text": "DMZ" }
  ]
}
```

**Key rules**:
- `file`: stencil filename (auto-resolved, no full path needed). See `references/stencil-catalog.md` for all available stencils and master names.
- `master`: prefer **NameU** (English, cross-language stable), e.g., `"Router"`, `"Web server"`, `"Firewall"`. Chinese Name also works.
- Master node `x`,`y` = **center point** (unlike geometric nodes where `x`,`y` = lower-left corner).
- Master nodes ignore `fill`/`line`/`shape`; the icon has its own styling.
- Geometric nodes and master nodes can coexist on the same page.

### 3. Sequence Diagrams (UML interaction diagrams)

Read `references/sequence-format.md` for the full specification. Minimum example:

```json
{
  "type": "sequence",
  "title": "Login Flow",
  "actors": [
    { "id": "user", "name": "User", "type": "actor" },
    { "id": "api", "name": "API", "type": "system" },
    { "id": "db", "name": "Database", "type": "database" }
  ],
  "messages": [
    { "from": "user", "to": "api", "text": "POST /login", "type": "sync" },
    { "from": "api", "to": "db", "text": "Query user", "type": "sync" },
    { "from": "db", "to": "api", "text": "User record", "type": "return" },
    { "from": "api", "to": "user", "text": "JWT token", "type": "return" }
  ]
}
```

**Key features**:
- Set `"type": "sequence"` to activate sequence diagram mode
- Define `actors` (participants) with optional type (`actor`, `system`, `database`, `external`)
- Define `messages` with `from`, `to`, `text`, and `type` (`sync`, `async`, or `return`)
- Actors are positioned left-to-right, messages flow top-to-bottom
- Lifelines and activation boxes are drawn automatically

## Drawing Guidance

### Standard Diagrams

- Use explicit coordinates for predictable layout.
- Keep diagrams readable: align nodes in rows/columns, leave at least `0.6` to `1.0` inches between shapes, and route left-to-right or top-to-bottom unless the user asks otherwise.
- Default shape is `roundrect` (rounded rectangle). Default fill is a premium light blue `#EFF6FF` with a border of `#3B82F6`. Default node text is `Microsoft YaHei` at `11 pt`.
- Default connector line color is slate gray `#475569` with `10 pt` text, automatically using `"textPinX": 0.35` and `"textOffsetY": 0.18` to avoid overlap.
- Utilize premium, low-saturation pastel colors for different layers/roles (e.g., `#EFF6FF` / `#3B82F6` for main logic, `#ECFDF5` / `#10B981` for start/success, `#FEF3C7` / `#D97706` for storage, `#F5F3FF` / `#8B5CF6` for external API).
- For side-by-side boxes with labeled connectors, leave at least `max(1.4 in, label characters * 0.12 in)` of horizontal gap, plus arrowhead room.
- Use short labels inside shapes. Put longer explanations in callouts or external notes.
- For architecture diagrams, group by layer: clients, edge/API, services, data, external systems.
- For process diagrams, use left-to-right flow unless there are many steps; then use rows.
- For swimlane-like diagrams, represent lanes with lightly filled large rectangles behind nodes, or create separate rows with lane labels.

### Sequence Diagrams

- Define actors in **logical order** (left-to-right), typically: user → frontend → backend → database → external services.
- Use **descriptive actor names** that clearly identify each participant (e.g., "User", "Web App", "Auth Service", "PostgreSQL").
- Choose appropriate **actor types** for automatic color coding:
  - `"actor"` for users/people (blue)
  - `"system"` for internal services (purple)
  - `"database"` for data stores (amber)
  - `"external"` for third-party APIs (green)
- Order messages **chronologically** from top to bottom, representing the actual execution flow.
- Use `"type": "sync"` for method calls/requests, `"type": "return"` for responses (shown as dashed arrows).
- Keep message labels **concise but meaningful** (e.g., "POST /login", "Query user", "JWT token").
- For complex flows, limit to **4-6 actors** maximum; split into multiple diagrams if needed.
- Default spacing is sensible; override `layout.actorSpacing` or `layout.messageSpacing` only if the diagram is too cramped or sparse.

## Validation

After generating a `.vsdx`, confirm the file exists and has nonzero size. If the user needs visual QA, open it with Visio COM and optionally export a PNG/PDF preview.

If COM creation fails, check whether Visio is installed and registered:

```powershell
New-Object -ComObject Visio.Application
```

When Visio is unavailable, offer Mermaid, SVG, draw.io, or another importable format instead of pretending the `.vsdx` was created.
