# Visio Diagram JSON Spec

Use this format with `scripts/New-VisioDiagram.py`.

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
  "stencils": [],
  "pages": []
}
```

`pageWidth` and `pageHeight` default to US landscape letter dimensions in inches.

## Stencils (Optional)

To use Visio built-in stencil shapes (network devices, servers, cloud icons, etc.), declare them in the `stencils` array:

```json
{
  "stencils": [
    {
      "id": "network",
      "file": "NETSYM_M.VSSX"
    },
    {
      "id": "server",
      "file": "SERVER_M.VSSX"
    },
    {
      "id": "cisco",
      "file": "CISCONETWORKSHAPES_M.VSSX"
    }
  ]
}
```

- `id`: A short identifier to reference this stencil in nodes
- `file`: Stencil filename (`.vssx` or `.vss`) or full path

**Common stencil files** (installed with Visio):
- `NETSYM_M.VSSX` - Network symbols (路由器, 工作组交换机, 网关, 主机, etc.)
- `SERVER_M.VSSX` - Servers (服务器, Web 服务器, 数据库服务器, 打印服务器, etc.)
- `COMPS_M.VSSX` - Computers (PC, 笔记本电脑, 平板电脑, LCD 显示器, etc.)
- `AZURECLOUD_M.VSSX` - Azure cloud services
- `AWSCOMPUTE_M.VSSX` - AWS compute services

See `stencil-reference.md` for a comprehensive list.

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

### Using Basic Shapes

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

### Using Stencil Master Shapes

To use professional icons from Visio stencils:

```json
{
  "id": "router1",
  "stencil": "network",
  "master": "路由器",
  "text": "Core Router",
  "x": 2,
  "y": 5,
  "w": 1.5,
  "h": 1.2,
  "fontName": "Microsoft YaHei",
  "fontSize": 10
}
```

- `stencil`: References a stencil `id` declared in the top-level `stencils` array
- `master`: The exact name of the master shape within that stencil
- When using `stencil` + `master`, the `shape` field is ignored
- `fill` and `line` colors typically don't apply to stencil masters (they have predefined styling)
- `w` and `h` are optional for stencil shapes; if omitted, the master's default size is used

**Position and Size:**
- Coordinates are in inches. `x` and `y` are the lower-left corner. `w` and `h` are width and height.
- When omitted for basic shapes: node defaults to `roundrect`, fill `#EFF6FF`, border `#3B82F6`, text `Microsoft YaHei` at `11 pt`.
- When using stencil masters: `w` and `h` default to the master's intrinsic size.

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

Optional connector refinements:

- `textOffsetX`: move the connector label horizontally in inches.
- `lineWeight`: set connector thickness in points. Use a heavier line for data buses.

## Notes

- Use hex colors as `#RRGGBB`.
- Omit optional style fields for Visio defaults.
- Use deterministic IDs so later edits can refer to existing logical nodes.
- For side-by-side nodes with a labeled connector, leave a horizontal gap wider than the label. A practical rule is `max(1.4 in, label characters * 0.12 in)`, plus arrowhead room.

## Complete Example: Network Topology with Stencils

```json
{
  "title": "Corporate Network",
  "pageWidth": 11,
  "pageHeight": 8.5,
  "stencils": [
    { "id": "network", "file": "NETSYM_M.VSSX" },
    { "id": "server", "file": "SERVER_M.VSSX" },
    { "id": "computer", "file": "COMPS_M.VSSX" }
  ],
  "pages": [
    {
      "name": "Topology",
      "nodes": [
        {
          "id": "router",
          "stencil": "network",
          "master": "路由器",
          "text": "边界路由器",
          "x": 2,
          "y": 6
        },
        {
          "id": "switch",
          "stencil": "network",
          "master": "工作组交换机",
          "text": "核心交换机",
          "x": 5,
          "y": 6
        },
        {
          "id": "server1",
          "stencil": "server",
          "master": "服务器",
          "text": "Web服务器",
          "x": 8,
          "y": 7
        },
        {
          "id": "client",
          "stencil": "computer",
          "master": "PC",
          "text": "客户端",
          "x": 8,
          "y": 5
        },
        {
          "id": "internet",
          "shape": "ellipse",
          "text": "Internet",
          "x": 0.5,
          "y": 5.7,
          "w": 1.2,
          "h": 0.8,
          "fill": "#ECFDF5",
          "line": "#10B981"
        }
      ],
      "connections": [
        { "from": "internet", "to": "router", "text": "WAN" },
        { "from": "router", "to": "switch", "text": "Gigabit" },
        { "from": "switch", "to": "server1", "text": "LAN" },
        { "from": "switch", "to": "client", "text": "LAN" }
      ]
    }
  ]
}
```

This example demonstrates:
- Loading multiple stencils (network, server, computer)
- Using master shapes from stencils for professional device icons
- Mixing stencil masters with basic shapes (ellipse for Internet cloud)
- Standard connections between all node types
