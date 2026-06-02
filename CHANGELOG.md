# Visio Skill Changelog

## Version 2.0 - 2026-06-02

### 🎨 **重大更新：自动布局引擎**

#### 新增功能

1. **多种布局算法**
   - ✅ 网格布局（Grid Layout）
   - ✅ 层次布局（Hierarchical Layout）  
   - ✅ 容器布局（Container Layout）
   - ✅ 流式布局（Flow Layout）

2. **智能碰撞检测**
   - 自动检测节点重叠
   - 检测间距不足
   - 报告碰撞详情（面积、间距）

3. **自动修正**
   - 智能调整节点位置避免重叠
   - 多轮迭代直到无碰撞
   - 可配置修正策略

4. **Z-Order 管理**
   - 控制图层渲染顺序
   - 支持 `zOrder` 属性
   - 支持 `sendToBack` 标记

#### 新增文件

```
scripts/
├── layout_engine.py          # 布局引擎核心
├── collision_detector.py     # 碰撞检测模块
└── New-VisioDiagram.py       # 主入口（已修改）

references/
└── layout-spec.md            # 布局系统完整文档
```

#### API 变更

**新增 JSON 字段**：

```json
{
  "layout": {
    "engine": "auto" | "manual" | "grid" | "hierarchical",
    "spacing": {
      "horizontal": 1.0,
      "vertical": 0.8,
      "padding": 0.3
    },
    "checkCollisions": true,
    "autoAdjust": true,
    "direction": "LR" | "TB",
    "columns": 3,
    "layerSpacing": 3.0
  }
}
```

**新增节点属性**：
- `grid: [row, col]` - 网格布局位置
- `layer: 0/1/2...` - 层次布局层级
- `type: "container"` - 容器节点
- `children: [...]` - 子节点（自动布局）
- `zOrder: 0-20` - 渲染顺序
- `sendToBack: true` - 发送到底层

**新增命令行选项**：
- `--no-layout` - 禁用自动布局
- `--strict` - 严格模式（碰撞时拒绝生成）

#### 向后兼容性

✅ **完全兼容旧版 JSON**  
- 手动坐标方式仍然有效
- 默认 `engine: "manual"`
- 无需修改现有 JSON

#### 已知限制

1. 容器嵌套：暂不支持多层嵌套
2. 编码问题：部分中文输出在 Windows GBK 环境下显示为乱码（功能不受影响）
3. 自动修正：复杂布局可能需要多轮迭代

#### 性能

- **碰撞检测**：O(n²) 复杂度
- **自动修正**：最多 10 轮迭代
- **内存占用**：与节点数成正比

#### 测试

已通过测试：
- ✅ 容器布局（8 个子节点）
- ✅ 碰撞检测（3 处碰撞）
- ✅ 自动修正（9 次调整）
- ✅ Z-Order 渲染

---

## Version 1.0 - 2026-05-XX

初始版本，支持基本的手动布局和序列图。
