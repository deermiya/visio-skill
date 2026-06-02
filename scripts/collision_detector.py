"""
碰撞检测和自动修正模块
用于检测 Visio 图形中的重叠并提供自动修正建议
"""
from typing import List, Dict, Tuple, Optional


def rectangles_overlap(r1: Dict, r2: Dict, margin: float = 0.0) -> bool:
    """
    检测两个矩形是否重叠（Visio坐标系：左下角为原点，Y轴向上）

    Args:
        r1: 第一个矩形 {x, y, w, h}
        r2: 第二个矩形 {x, y, w, h}
        margin: 额外的边距（用于检测"太接近"的情况）

    Returns:
        True 如果重叠，False 否则
    """
    # 跳过没有坐标的节点
    if 'x' not in r1 or 'y' not in r1 or 'x' not in r2 or 'y' not in r2:
        return False

    r1_left = r1.get('x', 0) - margin
    r1_right = r1_left + r1.get('w', 1) + 2 * margin
    r1_bottom = r1.get('y', 0) - margin
    r1_top = r1_bottom + r1.get('h', 1) + 2 * margin

    r2_left = r2.get('x', 0)
    r2_right = r2_left + r2.get('w', 1)
    r2_bottom = r2.get('y', 0)
    r2_top = r2_bottom + r2.get('h', 1)

    # 检测是否重叠（注意：边界相接不算重叠）
    return not (r1_right <= r2_left or
                r1_left >= r2_right or
                r1_top <= r2_bottom or
                r1_bottom >= r2_top)


def calculate_overlap_area(r1: Dict, r2: Dict) -> float:
    """
    计算两个矩形的重叠面积

    Returns:
        重叠面积（平方英寸），如果不重叠则返回 0.0
    """
    if not rectangles_overlap(r1, r2):
        return 0.0

    r1_left = r1.get('x', 0)
    r1_right = r1_left + r1.get('w', 1)
    r1_bottom = r1.get('y', 0)
    r1_top = r1_bottom + r1.get('h', 1)

    r2_left = r2.get('x', 0)
    r2_right = r2_left + r2.get('w', 1)
    r2_bottom = r2.get('y', 0)
    r2_top = r2_bottom + r2.get('h', 1)

    overlap_width = min(r1_right, r2_right) - max(r1_left, r2_left)
    overlap_height = min(r1_top, r2_top) - max(r1_bottom, r2_bottom)

    return max(0, overlap_width) * max(0, overlap_height)


def calculate_spacing(r1: Dict, r2: Dict) -> Tuple[float, float]:
    """
    计算两个矩形之间的横向和纵向间距

    Returns:
        (h_spacing, v_spacing) - 负数表示重叠
    """
    r1_right = r1.get('x', 0) + r1.get('w', 1)
    r2_left = r2.get('x', 0)
    r2_right = r2_left + r2.get('w', 1)
    r1_left = r1.get('x', 0)

    r1_top = r1.get('y', 0) + r1.get('h', 1)
    r2_bottom = r2.get('y', 0)
    r2_top = r2_bottom + r2.get('h', 1)
    r1_bottom = r1.get('y', 0)

    # 横向间距（右边的左边界 - 左边的右边界）
    h_spacing = min(
        abs(r2_left - r1_right),  # r1 在左，r2 在右
        abs(r1_left - r2_right)   # r2 在左，r1 在右
    )

    # 纵向间距
    v_spacing = min(
        abs(r2_bottom - r1_top),  # r1 在下，r2 在上
        abs(r1_bottom - r2_top)   # r2 在下，r1 在上
    )

    # 如果重叠，返回负值
    if rectangles_overlap(r1, r2):
        return (-h_spacing, -v_spacing)

    return (h_spacing, v_spacing)


def detect_collisions(nodes: List[Dict], min_spacing: float = 0.0) -> List[Dict]:
    """
    检测所有节点之间的重叠

    Args:
        nodes: 节点列表
        min_spacing: 最小间距要求（英寸）

    Returns:
        碰撞列表，每项包含 {node1, node2, area, h_spacing, v_spacing}
    """
    collisions = []

    for i, node1 in enumerate(nodes):
        # 跳过容器类型的节点（背景框）
        if node1.get('type') == 'container':
            continue

        for j, node2 in enumerate(nodes[i+1:], i+1):
            if node2.get('type') == 'container':
                continue

            # 使用 min_spacing 作为边距检测
            if rectangles_overlap(node1, node2, margin=min_spacing):
                area = calculate_overlap_area(node1, node2)
                h_spacing, v_spacing = calculate_spacing(node1, node2)

                collisions.append({
                    'node1': node1.get('id', f'node_{i}'),
                    'node2': node2.get('id', f'node_{j}'),
                    'area': area,
                    'h_spacing': h_spacing,
                    'v_spacing': v_spacing,
                    'node1_obj': node1,
                    'node2_obj': node2,
                    'severity': 'overlap' if area > 0 else 'too_close'
                })

    return collisions


def suggest_fix(node1: Dict, node2: Dict, min_spacing: float = 0.5) -> Dict:
    """
    为碰撞提供修复建议（不修改原数据）

    Returns:
        修复建议 {direction, shift_amount, new_x, new_y}
    """
    r1_right = node1.get('x', 0) + node1.get('w', 1)
    r1_top = node1.get('y', 0) + node1.get('h', 1)

    r2_left = node2.get('x', 0)
    r2_bottom = node2.get('y', 0)

    # 计算需要移动的距离
    h_shift = r1_right + min_spacing - r2_left
    v_shift = r1_top + min_spacing - r2_bottom

    # 选择移动距离较小的方向
    if h_shift > 0 and (v_shift <= 0 or abs(h_shift) < abs(v_shift)):
        # 横向移动（向右）
        return {
            'direction': 'horizontal',
            'shift_amount': h_shift,
            'new_x': r1_right + min_spacing,
            'new_y': node2.get('y', 0)
        }
    elif v_shift > 0:
        # 纵向移动（向上）
        return {
            'direction': 'vertical',
            'shift_amount': v_shift,
            'new_x': node2.get('x', 0),
            'new_y': r1_top + min_spacing
        }
    else:
        # 无需移动
        return {
            'direction': 'none',
            'shift_amount': 0,
            'new_x': node2.get('x', 0),
            'new_y': node2.get('y', 0)
        }


def fix_collision(node1: Dict, node2: Dict, min_spacing: float = 0.5) -> None:
    """
    修正两个节点的重叠（就地修改 node2 的坐标）

    策略：将 node2 向右或向上移动，选择移动距离较小的方向
    """
    suggestion = suggest_fix(node1, node2, min_spacing)

    if suggestion['direction'] != 'none':
        node2['x'] = suggestion['new_x']
        node2['y'] = suggestion['new_y']


def detect_and_fix_collisions(
    nodes: List[Dict],
    min_spacing: float = 0.5,
    auto_fix: bool = True,
    verbose: bool = True
) -> List[Dict]:
    """
    检测并修正所有碰撞

    Args:
        nodes: 节点列表
        min_spacing: 最小间距（英寸）
        auto_fix: 是否自动修正
        verbose: 是否打印详细信息

    Returns:
        修正后的节点列表（如果 auto_fix=True）
    """
    # 首次检测
    collisions = detect_collisions(nodes, min_spacing=min_spacing)

    if not collisions:
        if verbose:
            print("[COLLISION] No overlaps or insufficient spacing detected")
        return nodes

    if verbose:
        print(f"\n[COLLISION] Detected {len(collisions)} issue(s):")
        for i, c in enumerate(collisions, 1):
            if c['severity'] == 'overlap':
                print(f"   {i}. [{c['node1']}] <-> [{c['node2']}]  "
                      f"overlap area: {c['area']:.3f} in^2")
            else:
                h_sp, v_sp = c['h_spacing'], c['v_spacing']
                print(f"   {i}. [{c['node1']}] <-> [{c['node2']}]  "
                      f"spacing insufficient (h:{h_sp:.2f}\" v:{v_sp:.2f}\")")

    if not auto_fix:
        if verbose:
            print("\n[HINT] Set layout.autoAdjust = true to enable auto-fix")
        return nodes

    # 自动修正
    if verbose:
        print("\n[FIX] Auto-fixing collisions...")

    # 按重叠面积排序（先修复严重的）
    collisions.sort(key=lambda x: x['area'], reverse=True)

    fixed_count = 0
    max_iterations = 10  # 防止无限循环
    iteration = 0

    while collisions and iteration < max_iterations:
        for c in collisions:
            fix_collision(c['node1_obj'], c['node2_obj'], min_spacing=min_spacing)
            fixed_count += 1

        # 重新检测
        collisions = detect_collisions(nodes, min_spacing=min_spacing)
        iteration += 1

        if verbose and collisions:
            print(f"   Round {iteration}: {len(collisions)} issue(s) remaining...")

    if collisions:
        if verbose:
            print(f"[WARN] Some issues cannot be auto-fixed ({len(collisions)} remaining), please adjust manually")
    else:
        if verbose:
            print(f"[OK] Auto-fix completed ({fixed_count} fix(es) applied)\n")

    return nodes


def validate_layout(nodes: List[Dict], config: Dict) -> bool:
    """
    验证布局是否符合要求

    Returns:
        True 如果布局有效，False 否则
    """
    min_h_spacing = config.get('spacing', {}).get('horizontal', 0.8)
    min_v_spacing = config.get('spacing', {}).get('vertical', 0.6)

    collisions = detect_collisions(nodes, min_spacing=min(min_h_spacing, min_v_spacing))

    return len(collisions) == 0
