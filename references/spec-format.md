# Visio Diagram JSON Spec

Use this format with `scripts/New-VisioDiagram.ps1`.

## Diagram Types

This spec supports two diagram types:

1. **Standard Diagrams** (default) - Flowcharts, architecture diagrams, network topology, etc.
   - Use `nodes` and `connections` arrays
   - See format details below

2. **Sequence Diagrams** - UML-style interaction diagrams
   - Set `"type": "sequence"` in the JSON
   - Use `actors` and `messages` arrays
   - See [`sequence-format.md`](sequence-format.md) for full specification

---

## Standard Diagram Format

## Top Level

```json
{
  "title": "Optional document title",
  "pageWidth": 11,
  "pageHeight": 8.5,
  "pages": []
}
```

`pageWidth` and `pageHeight` default to US landscape letter dimensions in inches.

## Page

```json
{
  "name": "Architecture",
  "nodes": [],
  "connections": []
}
```

If `pages` is omitted, the script treats the top-level object as one page and reads `nodes` and `connections` there.

## Node

```json
{
  "id": "api",
  "text": "API Gateway",
  "shape": "rectangle",
  "x": 3,
  "y": 5,
  "w": 2,
  "h": 0.8,
  "fill": "#EAF3FF",
  "line": "#2B6CB0",
  "fontName": "Microsoft YaHei",
  "fontSize": 10
}
```

Supported `shape` values: `rectangle`, `roundrect`, `ellipse`, `diamond`. Defaults to `roundrect`.

Coordinates are in inches. `x` and `y` are the lower-left corner. `w` and `h` are width and height.

When omitted, node shape defaults to `roundrect`, fill to `#EFF6FF` (soft blue), border to `#3B82F6` (blue), and node text to `Microsoft YaHei` at `11 pt`.

## Connection

```json
{
  "from": "api",
  "to": "users",
  "text": "REST",
  "line": "#475569",
  "fontName": "Microsoft YaHei",
  "fontSize": 10,
  "textPinX": 0.35,
  "textOffsetY": 0.18,
  "endArrow": 4
}
```

`from` and `to` must match node IDs on the same page. `endArrow` defaults to `4`.

Connection labels default to `Microsoft YaHei` and `10 pt`. Connection line defaults to `#475569` (slate gray). `textPinX` is the label position along the connector width (`0.35` keeps it away from the arrowhead). `textOffsetY` moves the label above the line in inches.

## Notes

- Use hex colors as `#RRGGBB`.
- Omit optional style fields for Visio defaults.
- Use deterministic IDs so later edits can refer to existing logical nodes.
- For side-by-side nodes with a labeled connector, leave a horizontal gap wider than the label. A practical rule is `max(1.4 in, label characters * 0.12 in)`, plus arrowhead room.
