# 布局系统规范 (Layout System Specification)

版本：2.0  
更新日期：2026-06-02

---

## 概述

Visio-skill 2.0 引入了**自动布局引擎**，可以自动计算节点坐标、检测碰撞并修正重叠。

### 核心特性

✅ **多种布局算法**：网格、层次、容器、流式  
✅ **碰撞检测**：自动检测节点重叠和间距不足  
✅ **自动修正**：智能调整坐标避免重叠  
✅ **向后兼容**：旧的手动坐标方式仍然有效  
✅ **Z-Order 管理**：控制图层渲染顺序

---

## 布局模式对比

| 模式 | 适用场景 | 节点属性 | 示例 |
|------|---------|---------|------|
| **manual** | 完全手动控制坐标 | `x`, `y`, `w`, `h` | 精确布局 |
| **grid** | 规则的网格排列 | `grid: [row, col]` | 图标墙、功能矩阵 |
| **hierarchical** | 分层流程图 | `layer: 0/1/2...` | 架构图、数据流 |
| **auto** | 智能检测（容器优先） | `type: "container"`, `children` | 系统架构、模块化设计 |

---

## 1. 全局布局配置

在 JSON 根级别添加 `layout` 配置：

```json
{
  "title": "我的架构图",
  "layout": {
    "engine": "auto",           // 布局引擎类型
    "spacing": {
      "horizontal": 1.0,        // 横向最小间距（英寸）
      "vertical": 0.8,          // 纵向最小间距
      "padding": 0.3            // 容器内边距
    },
    "checkCollisions": true,    // 是否检测碰撞
    "autoAdjust": true,         // 是否自动修正重叠
    "direction": "LR",          // 方向：LR(左右) | TB(上下)
    "columns": 3,               // 网格布局的列数
    "layerSpacing": 3.0         // 层次布局的层间距
  },
  "pages": [...]
}
```

### 配置项说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `engine` | string | `"manual"` | 布局引擎：`manual`、`auto`、`grid`、`hierarchical` |
| `spacing.horizontal` | number | `1.0` | 横向最小间距（英寸） |
| `spacing.vertical` | number | `0.8` | 纵向最小间距（英寸） |
| `spacing.padding` | number | `0.3` | 容器内边距（英寸） |
| `checkCollisions` | boolean | `true` | 是否检测碰撞 |
| `autoAdjust` | boolean | `true` | 是否自动修正重叠 |
| `direction` | string | `"LR"` | 布局方向：`LR`(左右)、`TB`(上下)、`RL`、`BT` |
| `columns` | number | `3` | 网格布局的列数 |
| `layerSpacing` | number | `3.0` | 层次布局的层间距（英寸） |

---

## 2. 手动布局（Manual）

**适用场景**：需要精确控制每个节点位置

```json
{
  "layout": { "engine": "manual" },
  "pages": [{
    "name": "手动布局示例",
    "nodes": [
      {
        "id": "n1",
        "text": "节点1",
        "x": 2.0,    // 必须指定
        "y": 5.0,    // 必须指定
        "w": 2.0,
        "h": 1.0
      },
      {
        "id": "n2",
        "text": "节点2",
        "x": 5.0,
        "y": 5.0,
        "w": 2.0,
        "h": 1.0
      }
    ]
  }]
}
```

**注意**：即使是手动布局，也可以启用 `checkCollisions` 来检测错误。

---

## 3. 网格布局（Grid）

**适用场景**：规则的网格排列，如功能模块矩阵、图标墙

```json
{
  "layout": {
    "engine": "grid",
    "columns": 3,
    "spacing": { "horizontal": 1.0, "vertical": 0.8 }
  },
  "pages": [{
    "nodes": [
      {
        "id": "n1",
        "text": "节点1",
        "grid": [0, 0],  // 行0, 列0
        "w": 2.0,
        "h": 1.0
      },
      {
        "id": "n2",
        "text": "节点2",
        "grid": [0, 1],  // 行0, 列1
        "w": 2.0,
        "h": 1.0
      },
      {
        "id": "n3",
        "text": "节点3",
        "grid": [1, 0],  // 行1, 列0
        "w": 2.0,
        "h": 1.0
      }
    ]
  }]
}
```

**自动计算**：
- 每行高度 = 该行最高节点的高度
- 每列宽度 = 该列最宽节点的宽度
- 自动添加间距

---

## 4. 层次布局（Hierarchical）

**适用场景**：分层流程图、数据流图、架构图

```json
{
  "layout": {
    "engine": "hierarchical",
    "direction": "LR",        // 从左到右
    "layerSpacing": 3.0,
    "spacing": { "vertical": 0.8 }
  },
  "pages": [{
    "nodes": [
      {
        "id": "input",
        "text": "输入层",
        "layer": 0,    // 第0层（最左）
        "w": 2.0,
        "h": 1.0
      },
      {
        "id": "process1",
        "text": "处理1",
        "layer": 1,    // 第1层
        "w": 2.0,
        "h": 1.0
      },
      {
        "id": "process2",
        "text": "处理2",
        "layer": 1,    // 同一层的节点纵向排列
        "w": 2.0,
        "h": 1.0
      },
      {
        "id": "output",
        "text": "输出层",
        "layer": 2,    // 第2层（最右）
        "w": 2.0,
        "h": 1.0
      }
    ]
  }]
}
```

**布局规则**：
- 相同 `layer` 的节点在同一垂直线上
- 层间距 = `layerSpacing`
- 同层节点纵向居中排列

---

## 5. 容器布局（Container/Auto）

**适用场景**：系统架构图、模块化设计（大框包含小框）

```json
{
  "layout": {
    "engine": "auto",
    "spacing": { "horizontal": 0.8, "padding": 0.5 },
    "checkCollisions": true,
    "autoAdjust": true
  },
  "pages": [{
    "nodes": [
      {
        "id": "container1",
        "text": "FPGA 核心",
        "type": "container",       // 标记为容器
        "x": 3.0,                  // 容器位置需要手动指定
        "y": 5.0,
        "w": 8.0,
        "h": 4.0,
        "fillColor": "#F0F9FF",
        "zOrder": 0,               // 背景层
        "layout": {
          "type": "flow",          // 子元素布局类型
          "direction": "horizontal",
          "padding": 0.5,
          "spacing": 0.8
        },
        "children": [              // 子元素（自动布局）
          {
            "id": "ch0",
            "text": "CH0",
            "w": 1.2,
            "h": 1.0
            // 不需要指定 x, y
          },
          {
            "id": "ch1",
            "text": "CH1",
            "w": 1.2,
            "h": 1.0
          },
          {
            "id": "ch2",
            "text": "CH2",
            "w": 1.2,
            "h": 1.0
          }
        ]
      },
      {
        "id": "external",
        "text": "外部接口",
        "x": 12.0,
        "y": 6.0,
        "w": 2.0,
        "h": 1.5
      }
    ]
  }]
}
```

### 容器布局类型

| 类型 | 说明 | 效果 |
|------|------|------|
| `flow` + `horizontal` | 横向流式布局 | 从左到右排列，超出宽度自动换行 |
| `flow` + `vertical` | 纵向流式布局 | 从上到下排列 |
| `grid` | 网格布局 | 按 `columns` 参数排列 |

---

## 6. Z-Order（图层顺序）

控制形状的渲染顺序，避免背景框遮挡内容。

### 使用方法

```json
{
  "nodes": [
    {
      "id": "background",
      "text": "背景框",
      "zOrder": 0,         // 最底层（先渲染）
      "sendToBack": true   // 或者用这个标记
    },
    {
      "id": "content",
      "text": "内容",
      "zOrder": 10         // 上层（后渲染）
    }
  ]
}
```

### zOrder 值建议

| 值 | 用途 |
|----|------|
| `0` | 背景框、容器 |
| `5` | 默认（普通节点） |
| `10` | 前景元素、标注 |
| `20` | 最前（高亮、标记） |

---

## 7. 碰撞检测

### 检测模式

设置 `checkCollisions: true` 后，系统会检测：

1. **完全重叠**：节点面积交叉
2. **间距不足**：节点间距小于 `spacing` 配置

### 输出示例

```
⚠️  检测到 3 处问题：
   1. [node1] ↔ [node2]  重叠面积: 0.450 in²
   2. [node3] ↔ [node4]  间距不足 (横:0.30" 纵:0.50")
   3. [node5] ↔ [node6]  间距不足 (横:0.20" 纵:0.70")
```

### 自动修正

设置 `autoAdjust: true` 后，系统会：

1. 按重叠面积排序（先修复严重的）
2. 自动移动节点（选择移动距离较小的方向）
3. 重新检测直到无重叠

```
🔧 自动修正中...
✅ 修正完成（共修正 3 处）
```

---

## 8. 命令行选项

```bash
python New-VisioDiagram.py spec.json output.vsdx [OPTIONS]

OPTIONS:
  --visible           显示 Visio 窗口（默认隐藏）
  --diagnostics       打印详细诊断信息
  --no-layout         禁用自动布局引擎
  --strict            严格模式（检测到重叠时拒绝生成）
```

### 示例

```bash
# 使用自动布局
python New-VisioDiagram.py e1_arch.json e1_arch.vsdx

# 严格模式（不允许重叠）
python New-VisioDiagram.py e1_arch.json e1_arch.vsdx --strict

# 禁用布局引擎（使用旧版行为）
python New-VisioDiagram.py e1_arch.json e1_arch.vsdx --no-layout
```

---

## 9. 迁移指南

### 从旧版 JSON 迁移

**旧版**（手动坐标）：
```json
{
  "nodes": [
    { "id": "n1", "x": 2, "y": 5, "w": 2, "h": 1 },
    { "id": "n2", "x": 5, "y": 5, "w": 2, "h": 1 }
  ]
}
```

**保持兼容**（无需修改）：
- 旧版 JSON 仍然有效
- 可选添加 `layout.checkCollisions: true` 进行检测

**迁移到容器布局**：
```json
{
  "layout": { "engine": "auto", "autoAdjust": true },
  "nodes": [
    {
      "id": "container",
      "type": "container",
      "x": 2, "y": 5, "w": 8, "h": 3,
      "layout": { "type": "flow", "direction": "horizontal" },
      "children": [
        { "id": "n1", "w": 2, "h": 1 },  // 自动计算 x, y
        { "id": "n2", "w": 2, "h": 1 }
      ]
    }
  ]
}
```

---

## 10. 常见问题

### Q: 自动布局后节点位置不符合预期？

**A**: 尝试：
1. 调整 `spacing` 参数
2. 使用 `--diagnostics` 查看详细信息
3. 混用手动坐标和自动布局（容器用手动，子元素用自动）

### Q: 碰撞检测报告误报？

**A**: 容器节点会被忽略（因为它们是背景框）。如果需要检测容器，移除 `type: "container"` 属性。

### Q: 自动修正后仍有重叠？

**A**: 可能原因：
1. 间距设置太小（增加 `spacing`）
2. 布局过于复杂（简化或使用手动布局）
3. 达到最大迭代次数（代码中 `max_iterations=10`）

### Q: 如何禁用某些节点的碰撞检测？

**A**: 目前不支持。解决方案：
1. 使用 `--no-layout` 禁用整个引擎
2. 手动布局 + `checkCollisions: false`

---

## 11. 最佳实践

### ✅ 推荐做法

1. **混合布局**：容器手动定位，子元素自动排列
2. **渐进式迁移**：先添加 `checkCollisions`，再启用 `autoAdjust`
3. **合理间距**：横向 ≥ 0.8"，纵向 ≥ 0.6"
4. **使用 z-order**：背景框 `zOrder: 0`，内容 `zOrder: 5+`

### ❌ 避免做法

1. 不要在 `auto` 模式下手动指定所有坐标（无意义）
2. 不要设置极小的间距（< 0.3"）
3. 不要在容器内嵌套多层容器（暂不支持）

---

## 附录：完整示例

参见 `examples/` 目录：
- `grid-layout.json` - 网格布局示例
- `hierarchical-layout.json` - 层次布局示例
- `container-layout.json` - 容器布局示例
- `mixed-layout.json` - 混合布局示例
