# Visio Diagram JSON Spec

Use this format with `scripts/New-VisioDiagram.ps1`.

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

Supported `shape` values: `rectangle`, `roundrect`, `ellipse`, `diamond`.

Coordinates are in inches. `x` and `y` are the lower-left corner. `w` and `h` are width and height.

When omitted, node text defaults to `Microsoft YaHei` and `16 pt`.

## Connection

```json
{
  "from": "api",
  "to": "users",
  "text": "REST",
  "line": "#555555",
  "fontName": "Microsoft YaHei",
  "fontSize": 16,
  "textPinX": 0.35,
  "textOffsetY": 0.18,
  "endArrow": 4
}
```

`from` and `to` must match node IDs on the same page. `endArrow` defaults to `4`.

Connection labels default to `Microsoft YaHei` and `16 pt`. `textPinX` is the label position along the connector width (`0.35` keeps it away from the arrowhead). `textOffsetY` moves the label above the line in inches.

## Notes

- Use hex colors as `#RRGGBB`.
- Omit optional style fields for Visio defaults.
- Use deterministic IDs so later edits can refer to existing logical nodes.
- For side-by-side nodes with a labeled connector, leave a horizontal gap wider than the label. A practical rule is `max(1.4 in, label characters * 0.12 in)`, plus arrowhead room.
