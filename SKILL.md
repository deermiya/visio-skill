---
name: visio-vsdx
description: Generate or modify Microsoft Visio .vsdx diagrams using local Visio COM automation. Use when the user asks Codex to create Visio files, draw flowcharts, architecture diagrams, swimlane-style layouts, network topology diagrams, process maps, or to automate shapes/connectors/text in Microsoft Visio on Windows.
---

# Visio VSDX

## Workflow

Use local Microsoft Visio COM automation when Visio is installed and the user wants a real `.vsdx` file. Prefer the bundled script for new diagrams:

```powershell
powershell -ExecutionPolicy Bypass -File "<skill>/scripts/New-VisioDiagram.ps1" -SpecPath "<diagram.json>" -OutputPath "<diagram.vsdx>"
```

Create a JSON spec first, then run the script. Keep output files in the user's requested folder, or in the active workspace when unspecified.

## JSON Spec

Read `references/spec-format.md` when you need the full format. The minimum useful shape is:

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

## Drawing Guidance

- Use explicit coordinates for predictable layout.
- Keep diagrams readable: align nodes in rows/columns, leave at least `0.4` inches between shapes, and route left-to-right or top-to-bottom unless the user asks otherwise.
- Default node text is `Microsoft YaHei` at `16 pt`; make boxes tall and wide enough for this size.
- For side-by-side boxes with labeled connectors, make the connector span longer than the label text. Leave at least `max(1.4 in, label characters * 0.12 in)` of horizontal gap, plus arrowhead room.
- Use short labels inside shapes. Put longer explanations in callouts or external notes.
- For architecture diagrams, group by layer: clients, edge/API, services, data, external systems.
- For process diagrams, use left-to-right flow unless there are many steps; then use rows.
- For swimlane-like diagrams, represent lanes with lightly filled large rectangles behind nodes, or create separate rows with lane labels.

## Validation

After generating a `.vsdx`, confirm the file exists and has nonzero size. If the user needs visual QA, open it with Visio COM and optionally export a PNG/PDF preview.

If COM creation fails, check whether Visio is installed and registered:

```powershell
New-Object -ComObject Visio.Application
```

When Visio is unavailable, offer Mermaid, SVG, draw.io, or another importable format instead of pretending the `.vsdx` was created.
