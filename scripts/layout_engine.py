"""
布局引擎 - 自动计算节点坐标
支持多种布局算法：网格、层次、容器等
"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import json


@dataclass
class LayoutConfig:
    """布局配置"""
    engine: str = "manual"              # manual | auto | grid | hierarchical | flow
    horizontal_spacing: float = 1.0     # 横向最小间距（英寸）
    vertical_spacing: float = 0.8       # 纵向最小间距
    padding: float = 0.3                # 容器内边距
    direction: str = "LR"               # LR | TB | RL | BT
    check_collisions: bool = True       # 是否检测碰撞
    auto_adjust: bool = True            # 是否自动修正重叠
    columns: int = 3                    # 网格布局的列数
    layer_spacing: float = 3.0          # 层次布局的层间距

    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'LayoutConfig':
        """从字典创建配置"""
        spacing = config_dict.get('spacing', {})
        return cls(
            engine=config_dict.get('engine', 'manual'),
            horizontal_spacing=spacing.get('horizontal', 1.0),
            vertical_spacing=spacing.get('vertical', 0.8),
            padding=spacing.get('padding', 0.3),
            direction=config_dict.get('direction', 'LR'),
            check_collisions=config_dict.get('checkCollisions', True),
            auto_adjust=config_dict.get('autoAdjust', True),
            columns=config_dict.get('columns', 3),
            layer_spacing=config_dict.get('layerSpacing', 3.0)
        )


class LayoutEngine:
    """布局引擎基类"""

    def __init__(self, config: LayoutConfig):
        self.config = config

    def compute_layout(self, nodes: List[Dict]) -> List[Dict]:
        """
        计算节点布局，返回带坐标的节点列表

        子类必须实现此方法
        """
        raise NotImplementedError

    def _get_node_size(self, node: Dict) -> Tuple[float, float]:
        """获取节点尺寸"""
        w = node.get('w', 2.0)
        h = node.get('h', 1.0)
        return (w, h)


class GridLayout(LayoutEngine):
    """
    网格布局引擎

    节点必须有 grid: [row, col] 属性
    """

    def compute_layout(self, nodes: List[Dict]) -> List[Dict]:
        """根据 grid: [row, col] 计算实际坐标"""
        result = []

        # 分离有 grid 属性和无 grid 属性的节点
        grid_nodes = [n for n in nodes if 'grid' in n]
        other_nodes = [n for n in nodes if 'grid' not in n]

        if not grid_nodes:
            return nodes  # 没有网格节点，返回原样

        # 按网格位置分组
        grid_map = {}
        for node in grid_nodes:
            row, col = node['grid']
            grid_map[(row, col)] = node

        # 计算每行高度和每列宽度（取该行/列的最大值）
        row_heights = {}
        col_widths = {}

        for (row, col), node in grid_map.items():
            w, h = self._get_node_size(node)
            row_heights[row] = max(row_heights.get(row, 0), h)
            col_widths[col] = max(col_widths.get(col, 0), w)

        # 计算起始位置
        start_x = 1.0
        start_y = 1.0

        # 计算每个节点的坐标
        for (row, col), node in grid_map.items():
            # 计算该格子的左下角坐标
            x = start_x + sum(
                col_widths.get(c, 0) + self.config.horizontal_spacing
                for c in range(col)
            )
            y = start_y + sum(
                row_heights.get(r, 0) + self.config.vertical_spacing
                for r in range(row)
            )

            node['x'] = x
            node['y'] = y
            result.append(node)

        # 非网格节点保持原样
        result.extend(other_nodes)

        return result


class HierarchicalLayout(LayoutEngine):
    """
    层次布局引擎（适合流程图）

    节点必须有 layer 属性表示层级
    """

    def compute_layout(self, nodes: List[Dict]) -> List[Dict]:
        """根据 layer 属性分层布局"""
        result = []

        # 分离有 layer 属性和无 layer 属性的节点
        layer_nodes = [n for n in nodes if 'layer' in n]
        other_nodes = [n for n in nodes if 'layer' not in n]

        if not layer_nodes:
            return nodes

        # 按层分组
        layers = {}
        for node in layer_nodes:
            layer = node.get('layer', 0)
            if layer not in layers:
                layers[layer] = []
            layers[layer].append(node)

        # 计算每层的位置
        for layer_idx in sorted(layers.keys()):
            layer_node_list = layers[layer_idx]

            # 计算该层的总高度
            total_height = sum(self._get_node_size(n)[1] for n in layer_node_list)
            total_height += self.config.vertical_spacing * (len(layer_node_list) - 1)

            # 该层的起始 Y 坐标（居中）
            start_y = 5.0 + total_height / 2

            current_y = start_y

            for node in layer_node_list:
                w, h = self._get_node_size(node)

                if self.config.direction == "LR":
                    # 从左到右布局
                    x = 1.0 + layer_idx * self.config.layer_spacing
                    y = current_y - h
                elif self.config.direction == "TB":
                    # 从上到下布局
                    x = 1.0 + layer_node_list.index(node) * (w + self.config.horizontal_spacing)
                    y = 10.0 - layer_idx * self.config.layer_spacing
                else:
                    x = 1.0 + layer_idx * self.config.layer_spacing
                    y = current_y - h

                node['x'] = x
                node['y'] = y

                current_y -= (h + self.config.vertical_spacing)
                result.append(node)

        # 非层次节点保持原样
        result.extend(other_nodes)

        return result


class ContainerLayout(LayoutEngine):
    """
    容器布局引擎

    处理 type='container' 的节点，自动排列其 children
    """

    def compute_layout(self, nodes: List[Dict]) -> List[Dict]:
        """处理容器内的子元素自动布局"""
        result = []

        for node in nodes:
            if node.get('type') == 'container' and 'children' in node:
                # 容器本身的位置和尺寸
                container_x = node.get('x', 1.0)
                container_y = node.get('y', 5.0)
                container_w = node.get('w', 8.0)
                container_h = node.get('h', 4.0)

                # 容器的布局配置
                container_layout = node.get('layout', {})
                layout_type = container_layout.get('type', 'flow')
                direction = container_layout.get('direction', 'horizontal')
                padding = container_layout.get('padding', self.config.padding)
                spacing = container_layout.get('spacing', self.config.horizontal_spacing)

                children = node['children']

                if layout_type == 'flow':
                    self._layout_flow(
                        children, container_x, container_y, container_w, container_h,
                        direction, padding, spacing
                    )
                elif layout_type == 'grid':
                    cols = container_layout.get('columns', 3)
                    self._layout_grid_in_container(
                        children, container_x, container_y, container_w, container_h,
                        cols, padding, spacing
                    )

                # 将子节点加入结果
                result.extend(children)

                # 容器本身也加入（但移除 children 避免重复）
                container_node = node.copy()
                container_node.pop('children', None)
                container_node['zOrder'] = container_node.get('zOrder', 0)  # 背景层
                result.append(container_node)

            else:
                # 非容器节点直接加入
                result.append(node)

        return result

    def _layout_flow(
        self,
        children: List[Dict],
        cx: float, cy: float, cw: float, ch: float,
        direction: str,
        padding: float,
        spacing: float
    ):
        """流式布局（横向或纵向）"""
        if direction == 'horizontal':
            # 横向流式布局（从左到右，自动换行）
            current_x = cx + padding
            current_y = cy + ch - padding  # 从容器顶部开始

            row_height = 0
            row_nodes = []

            for child in children:
                child_w, child_h = self._get_node_size(child)

                # 检查是否需要换行
                if current_x + child_w > cx + cw - padding:
                    # 换行：先放置当前行的节点（纵向居中）
                    if row_nodes:
                        self._align_row_vertical(row_nodes, current_y, row_height)

                    # 开始新行
                    current_x = cx + padding
                    current_y -= (row_height + spacing)
                    row_height = 0
                    row_nodes = []

                child['x'] = current_x
                child['y'] = current_y - child_h  # 临时位置
                current_x += child_w + spacing

                row_height = max(row_height, child_h)
                row_nodes.append(child)

            # 放置最后一行
            if row_nodes:
                self._align_row_vertical(row_nodes, current_y, row_height)

        else:  # vertical
            # 纵向流式布局（从上到下）
            current_x = cx + padding
            current_y = cy + ch - padding

            for child in children:
                child_w, child_h = self._get_node_size(child)

                current_y -= child_h
                child['x'] = current_x
                child['y'] = current_y

                current_y -= spacing

    def _layout_grid_in_container(
        self,
        children: List[Dict],
        cx: float, cy: float, cw: float, ch: float,
        columns: int,
        padding: float,
        spacing: float
    ):
        """容器内网格布局"""
        # 计算每个单元格的尺寸
        available_width = cw - 2 * padding - (columns - 1) * spacing
        cell_width = available_width / columns

        current_x = cx + padding
        current_y = cy + ch - padding

        for i, child in enumerate(children):
            col = i % columns
            row = i // columns

            x = cx + padding + col * (cell_width + spacing)
            y = current_y - row * (self._get_node_size(child)[1] + spacing) - self._get_node_size(child)[1]

            child['x'] = x
            child['y'] = y

    def _align_row_vertical(self, row_nodes: List[Dict], base_y: float, row_height: float):
        """将一行节点纵向居中对齐"""
        for node in row_nodes:
            node_h = self._get_node_size(node)[1]
            # 居中：基准 Y - 行高的一半 + 节点高的一半
            node['y'] = base_y - row_height + (row_height - node_h) / 2


def auto_layout(spec: Dict, verbose: bool = True) -> Dict:
    """
    主入口：根据 spec 自动选择布局引擎

    Args:
        spec: 完整的图表规格
        verbose: 是否打印详细信息

    Returns:
        处理后的 spec
    """
    if 'layout' not in spec:
        # 没有布局配置，保持原样
        return spec

    layout_config = LayoutConfig.from_dict(spec['layout'])

    if layout_config.engine == 'manual':
        # 手动布局，不处理
        if verbose:
            print("[LAYOUT] Using manual layout")
        return spec

    if verbose:
        print(f"[LAYOUT] Using auto-layout engine: {layout_config.engine}")

    for page in spec.get('pages', []):
        nodes = page.get('nodes', [])

        # 根据配置选择布局引擎
        if layout_config.engine == 'grid':
            engine = GridLayout(layout_config)
            nodes = engine.compute_layout(nodes)

        elif layout_config.engine == 'hierarchical':
            engine = HierarchicalLayout(layout_config)
            nodes = engine.compute_layout(nodes)

        elif layout_config.engine == 'auto':
            # 智能检测：如果有容器，用容器布局
            has_container = any(n.get('type') == 'container' for n in nodes)
            if has_container:
                if verbose:
                    print("   - Detected container nodes, using container layout")
                engine = ContainerLayout(layout_config)
                nodes = engine.compute_layout(nodes)
            else:
                # 检测是否有 layer 或 grid 属性
                has_layer = any('layer' in n for n in nodes)
                has_grid = any('grid' in n for n in nodes)

                if has_layer:
                    if verbose:
                        print("   - Detected layer attributes, using hierarchical layout")
                    engine = HierarchicalLayout(layout_config)
                    nodes = engine.compute_layout(nodes)
                elif has_grid:
                    if verbose:
                        print("   - Detected grid attributes, using grid layout")
                    engine = GridLayout(layout_config)
                    nodes = engine.compute_layout(nodes)

        # 碰撞检测和自动调整
        if layout_config.check_collisions:
            from collision_detector import detect_and_fix_collisions
            min_spacing = min(layout_config.horizontal_spacing, layout_config.vertical_spacing)
            nodes = detect_and_fix_collisions(
                nodes,
                min_spacing=min_spacing,
                auto_fix=layout_config.auto_adjust,
                verbose=verbose
            )

        page['nodes'] = nodes

    return spec


def validate_spec(spec: Dict) -> Tuple[bool, List[str]]:
    """
    验证 JSON spec 的有效性

    Returns:
        (is_valid, error_messages)
    """
    errors = []

    if 'pages' not in spec:
        errors.append("缺少 'pages' 字段")
        return (False, errors)

    for i, page in enumerate(spec['pages']):
        if 'nodes' not in page:
            errors.append(f"页面 {i} 缺少 'nodes' 字段")
            continue

        for j, node in enumerate(page['nodes']):
            if 'id' not in node:
                errors.append(f"页面 {i} 节点 {j} 缺少 'id' 字段")

            # 检查必需的坐标（如果不是自动布局）
            layout_engine = spec.get('layout', {}).get('engine', 'manual')
            if layout_engine == 'manual':
                if 'x' not in node or 'y' not in node:
                    errors.append(f"节点 '{node.get('id', j)}' 缺少 x 或 y 坐标")

    return (len(errors) == 0, errors)
