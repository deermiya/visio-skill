# Visio 图表风格转换指南

## 架构图风格 vs. 逻辑框图风格

### 视觉对比

| 特征 | 架构图风格（E1） | 逻辑框图风格（UART_DPRAM） |
|------|-----------------|---------------------------|
| 用途 | 系统架构、模块关系 | 硬件逻辑、RTL信号流 |
| 形状 | 圆角矩形 | 直角矩形 |
| 配色 | 彩色（蓝/紫/绿） | 灰度/黑白 |
| 布局 | 容器嵌套 | 横向分层 |
| 连线 | 粗线，标签分离 | 细线，标签紧贴 |
| 间距 | 宽松（视觉舒适） | 紧凑（信息密度高） |

---

## 配置转换对照表

### 1. 布局配置

#### 架构图
```json
{
  "layout": {
    "engine": "auto",
    "spacing": { "horizontal": 1.0, "vertical": 0.8, "padding": 0.5 },
    "checkCollisions": true,
    "autoAdjust": true
  }
}
```

#### 逻辑框图
```json
{
  "layout": {
    "engine": "hierarchical",
    "direction": "LR",
    "layerSpacing": 3.5,
    "spacing": { "horizontal": 1.2, "vertical": 0.5 }
  }
}
```

**关键差异**：
- 布局算法：`auto` → `hierarchical`
- 方向明确：加入 `direction: "LR"`
- 间距更紧凑：纵向从 0.8 降到 0.5

---

### 2. 节点样式

#### 架构图（容器风格）
```json
{
  "id": "fpga_core",
  "text": "FPGA 核心",
  "type": "container",
  "shape": "roundrect",
  "w": 8.0,
  "h": 4.0,
  "fill": "#EFF6FF",
  "line": "#3B82F6",
  "fontSize": 12,
  "fontName": "Microsoft YaHei",
  "zOrder": 0,
  "children": [...]
}
```

#### 逻辑框图（模块风格）
```json
{
  "id": "uart_rx",
  "text": "UART_Byte_Rx",
  "shape": "rectangle",
  "layer": 0,
  "w": 1.4,
  "h": 1.2,
  "fill": "#D9D9D9",
  "line": "#000000",
  "fontSize": 10,
  "fontName": "Arial"
}
```

**关键差异**：
- 移除 `type: "container"` 和 `children`
- 形状：`roundrect` → `rectangle`
- 颜色：彩色 → 灰度（`#D9D9D9` 填充，`#000000` 边框）
- 字体：微软雅黑 → Arial
- 布局：`zOrder` → `layer`（层次布局专用）

---

### 3. 连接线样式

#### 架构图
```json
{
  "from": "module1",
  "to": "module2",
  "text": "数据流",
  "line": "#475569",
  "fontSize": 10,
  "fontName": "Microsoft YaHei",
  "textPinX": 0.35,
  "textOffsetY": 0.18,
  "endArrow": 4
}
```

#### 逻辑框图
```json
{
  "from": "uart_rx",
  "to": "ctrl",
  "text": "Rx_Done",
  "line": "#000000",
  "fontSize": 8,
  "fontName": "Arial",
  "textPinX": 0.5,
  "textOffsetY": 0.12,
  "endArrow": 4
}
```

**关键差异**：
- 颜色：灰色 → 黑色
- 字号：10 → 8（更小）
- 标签位置：`textOffsetY` 从 0.18 → 0.12（更紧贴）
- 标签对齐：`textPinX` 从 0.35 → 0.5（居中）

---

## 快速转换步骤

### Step 1: 修改全局布局
```bash
# 在你的 JSON 文件顶部修改 layout 配置
{
  "layout": {
    "engine": "hierarchical",  # 改这行
    "direction": "LR",         # 加这行
    "layerSpacing": 3.5,       # 加这行
    "spacing": {
      "horizontal": 1.2,       # 改这行
      "vertical": 0.5          # 改这行（紧凑布局）
    }
  }
}
```

### Step 2: 批量替换节点属性
使用编辑器的查找替换功能：

| 查找 | 替换 |
|------|------|
| `"shape": "roundrect"` | `"shape": "rectangle"` |
| `"fill": "#EFF6FF"` | `"fill": "#D9D9D9"` |
| `"line": "#3B82F6"` | `"line": "#000000"` |
| `"fontName": "Microsoft YaHei"` | `"fontName": "Arial"` |
| `"fontSize": 12` | `"fontSize": 10` |
| `"zOrder":` | `"layer":` |

### Step 3: 移除容器结构
如果你的架构图使用了容器：

**之前（容器）**：
```json
{
  "id": "container",
  "type": "container",
  "x": 3.0, "y": 5.0,
  "children": [
    { "id": "ch0", "w": 1.2, "h": 1.0 },
    { "id": "ch1", "w": 1.2, "h": 1.0 }
  ]
}
```

**之后（平铺）**：
```json
{ "id": "ch0", "layer": 0, "w": 1.2, "h": 1.0 },
{ "id": "ch1", "layer": 0, "w": 1.2, "h": 1.0 }
```

将 `children` 提升到 `nodes` 数组，添加 `layer` 属性。

### Step 4: 修改连接线样式
批量替换：

| 查找 | 替换 |
|------|------|
| `"line": "#475569"` | `"line": "#000000"` |
| `"fontSize": 10` | `"fontSize": 8` |
| `"textOffsetY": 0.18` | `"textOffsetY": 0.12` |
| `"textPinX": 0.35` | `"textPinX": 0.5` |

---

## 完整示例对比

### 架构图（E1风格）
```json
{
  "title": "E1 架构图",
  "layout": { "engine": "auto" },
  "pages": [{
    "nodes": [
      {
        "id": "fpga",
        "type": "container",
        "shape": "roundrect",
        "x": 3.0, "y": 5.0, "w": 8.0, "h": 4.0,
        "fill": "#EFF6FF",
        "line": "#3B82F6",
        "fontSize": 12,
        "children": [...]
      }
    ]
  }]
}
```

### 逻辑框图（UART_DPRAM风格）
```json
{
  "title": "UART_DPRAM 逻辑框图",
  "layout": {
    "engine": "hierarchical",
    "direction": "LR",
    "layerSpacing": 3.5,
    "spacing": { "horizontal": 1.2, "vertical": 0.5 }
  },
  "pages": [{
    "nodes": [
      {
        "id": "uart_rx",
        "shape": "rectangle",
        "layer": 0,
        "w": 1.4, "h": 1.2,
        "fill": "#D9D9D9",
        "line": "#000000",
        "fontSize": 10
      },
      {
        "id": "ctrl",
        "shape": "rectangle",
        "layer": 1,
        "w": 1.8, "h": 1.5,
        "fill": "#D9D9D9",
        "line": "#000000",
        "fontSize": 10
      }
    ],
    "connections": [
      {
        "from": "uart_rx",
        "to": "ctrl",
        "text": "Rx_Done",
        "line": "#000000",
        "fontSize": 8,
        "textPinX": 0.5,
        "textOffsetY": 0.12
      }
    ]
  }]
}
```

---

## 常见问题

### Q: 转换后布局混乱？
**A**: 检查以下项：
1. 是否给每个节点添加了 `layer` 属性
2. 层次布局需要明确指定 `direction: "LR"` 或 `"TB"`
3. `layerSpacing` 是否合适（推荐 3.0-4.0）

### Q: 连接线标签重叠？
**A**: 调整参数：
```json
{
  "textPinX": 0.5,        // 标签左右位置（0-1）
  "textOffsetY": 0.12,    // 标签上下偏移（英寸）
  "spacing": { "horizontal": 1.5 }  // 增大横向间距
}
```

### Q: 想保留彩色但使用逻辑框图布局？
**A**: 可以混搭！只改布局和形状，保留颜色：
```json
{
  "layout": { "engine": "hierarchical", "direction": "LR" },
  "nodes": [
    {
      "shape": "rectangle",  // 使用直角矩形
      "fill": "#EFF6FF",     // 保留蓝色
      "line": "#3B82F6"      // 保留蓝色边框
    }
  ]
}
```

---

## 命令行测试

```bash
# 生成逻辑框图风格
python scripts/New-VisioDiagram.py examples/logic-diagram-style.json output.vsdx

# 查看诊断信息
python scripts/New-VisioDiagram.py examples/logic-diagram-style.json output.vsdx --diagnostics

# 严格模式（不允许重叠）
python scripts/New-VisioDiagram.py examples/logic-diagram-style.json output.vsdx --strict
```

---

## 参考资料

- [布局系统完整规范](./layout-spec.md)
- [示例文件](../examples/logic-diagram-style.json)
- [UART_DPRAM 原始截图](../test/逻辑框图.png)
