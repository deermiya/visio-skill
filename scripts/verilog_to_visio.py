"""
Generate an editable Visio RTL block diagram from a Verilog source directory.

The layout is deterministic: a horizontal datapath, control above it, clock and
configuration on the left, and status indicators below the datapath. This is
intended for top-level integration diagrams, not gate-level schematics.

Usage:
    python verilog_to_visio.py <verilog-dir-or-top.v> <output.vsdx>
        [--top top_module] [--json output.json] [--preview output.png]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path


DATA_COLOR = "#2563EB"
CONTROL_COLOR = "#F97316"
STATUS_COLOR = "#475569"
BLACK = "#000000"
BLOCK_FILL = "#E5E7EB"
WHITE = "#FFFFFF"
FONT = "Consolas"


@dataclass
class Port:
    name: str
    direction: str
    width: str = ""

    @property
    def is_bus(self) -> bool:
        return bool(self.width)


@dataclass
class Instance:
    module: str
    name: str
    connections: dict[str, str] = field(default_factory=dict)


@dataclass
class Module:
    name: str
    ports: dict[str, Port] = field(default_factory=dict)
    instances: list[Instance] = field(default_factory=list)


def strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//.*?$", "", text, flags=re.M)


def split_commas(text: str) -> list[str]:
    parts, start, depth = [], 0, 0
    for i, char in enumerate(text):
        if char in "([{":
            depth += 1
        elif char in ")]}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append(text[start:i].strip())
            start = i + 1
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return parts


def matching_paren(text: str, start: int) -> int:
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    raise ValueError("Unbalanced parentheses in Verilog source")


def parse_width(fragment: str) -> str:
    match = re.search(r"(\[[^\]]+\])", fragment)
    return match.group(1).replace(" ", "") if match else ""


def parse_ports(header: str, body: str) -> dict[str, Port]:
    ports: dict[str, Port] = {}
    current_direction, current_width = "", ""
    for item in split_commas(header):
        direction = re.search(r"\b(input|output|inout)\b", item)
        if direction:
            current_direction = direction.group(1)
            current_width = parse_width(item)
        if not current_direction:
            continue
        cleaned = re.sub(r"\b(input|output|inout|wire|reg|logic|signed)\b", " ", item)
        cleaned = re.sub(r"\[[^\]]+\]", " ", cleaned)
        names = re.findall(r"\b[A-Za-z_]\w*\b", cleaned)
        if names:
            ports[names[-1]] = Port(names[-1], current_direction, current_width)

    for match in re.finditer(
        r"\b(input|output|inout)\b\s*(?:wire|reg|logic)?\s*(\[[^\]]+\])?\s*([^;]+);",
        body,
    ):
        direction, width, names = match.group(1), (match.group(2) or "").replace(" ", ""), match.group(3)
        for name in split_commas(names):
            clean_name = re.search(r"\b[A-Za-z_]\w*\b", name)
            if clean_name:
                ports.setdefault(clean_name.group(0), Port(clean_name.group(0), direction, width))
    return ports


def parse_instances(body: str, known_modules: set[str]) -> list[Instance]:
    instances: list[Instance] = []
    for match in re.finditer(r"\b([A-Za-z_]\w*)\b", body):
        module_name = match.group(1)
        if module_name not in known_modules:
            continue
        pos = match.end()
        while pos < len(body) and body[pos].isspace():
            pos += 1
        if pos < len(body) and body[pos] == "#":
            pos += 1
            while pos < len(body) and body[pos].isspace():
                pos += 1
            if pos >= len(body) or body[pos] != "(":
                continue
            pos = matching_paren(body, pos) + 1
        while pos < len(body) and body[pos].isspace():
            pos += 1
        name_match = re.match(r"([A-Za-z_]\w*)", body[pos:])
        if not name_match:
            continue
        instance_name = name_match.group(1)
        pos += len(instance_name)
        while pos < len(body) and body[pos].isspace():
            pos += 1
        if pos >= len(body) or body[pos] != "(":
            continue
        end = matching_paren(body, pos)
        port_map = body[pos + 1 : end]
        connections = {
            port: signal.strip()
            for port, signal in re.findall(r"\.([A-Za-z_]\w*)\s*\(\s*([^)]+?)\s*\)", port_map)
        }
        instances.append(Instance(module_name, instance_name, connections))
    return instances


def parse_modules(paths: list[Path]) -> dict[str, Module]:
    sources = "\n".join(strip_comments(path.read_text(encoding="utf-8", errors="ignore")) for path in paths)
    blocks: list[tuple[str, str, str]] = []
    module_start = re.compile(r"\bmodule\s+([A-Za-z_]\w*)\b")
    for match in module_start.finditer(sources):
        name = match.group(1)
        endmodule = re.search(r"\bendmodule\b", sources[match.end() :])
        if not endmodule:
            continue
        block_end = match.end() + endmodule.end()
        block = sources[match.start() : block_end]
        header_open = block.find("(")
        if header_open < 0:
            continue
        if "#" in block[:header_open]:
            header_open = block.find("(", matching_paren(block, header_open) + 1)
        header_close = matching_paren(block, header_open)
        semicolon = block.find(";", header_close)
        blocks.append((name, block[header_open + 1 : header_close], block[semicolon + 1 :]))

    modules = {name: Module(name, parse_ports(header, body)) for name, header, body in blocks}
    known = set(modules)
    for name, _, body in blocks:
        modules[name].instances = parse_instances(body, known - {name})
    return modules


def role_for(module_name: str) -> str:
    name = module_name.lower()
    if any(word in name for word in ("clk", "clock", "pll", "divider")):
        return "clock"
    if any(word in name for word in ("debounce", "key", "button", "config")):
        return "config"
    if any(word in name for word in ("led", "indicator", "status", "debug")):
        return "status"
    if any(word in name for word in ("ctrl", "control", "fsm", "arbiter", "scheduler")):
        return "control"
    if any(word in name for word in ("fifo", "ram", "mem", "buffer", "bram")):
        return "storage"
    if any(word in name for word in ("rx", "receiver", "input", "source")):
        return "source"
    if any(word in name for word in ("tx", "transmit", "output", "sink")):
        return "sink"
    return "datapath"


def signal_width(signal: str, top: Module, modules: dict[str, Module], endpoints: list[tuple[str, str]]) -> bool:
    base = re.sub(r"\[[^\]]+\]", "", signal).strip()
    if "[" in signal:
        return True
    if base in top.ports and top.ports[base].is_bus:
        return True
    for instance_name, port_name in endpoints:
        instance = next((item for item in top.instances if item.name == instance_name), None)
        if instance and port_name in modules[instance.module].ports:
            if modules[instance.module].ports[port_name].is_bus:
                return True
    return False


def compact_signal(signal: str) -> str:
    signal = signal.strip()
    signal = re.sub(r"^uart_", "", signal)
    signal = re.sub(r"^fifo_(wr_en|rd_en|full|empty)$", r"\1", signal)
    return signal


def net_base(signal: str) -> str:
    return re.sub(r"\[[^\]]+\]", "", signal).strip()


def signal_label(signal: str, raw_signals: list[str], endpoints: list[tuple[str, str, str]], modules: dict[str, Module], top: Module) -> str:
    indexed = next((item.strip() for item in raw_signals if "[" in item and ":" not in item), None)
    if indexed:
        return compact_signal(indexed)
    label = compact_signal(signal)
    if "[" not in label:
        for instance_name, port_name, _ in endpoints:
            instance = next((item for item in top.instances if item.name == instance_name), None)
            port = modules[instance.module].ports.get(port_name) if instance else None
            if port and re.fullmatch(r"\[\d+:\d+\]", port.width):
                return label + port.width
    return label


def subtitle(module_name: str, role: str) -> str:
    name = module_name.lower()
    if role == "clock":
        return "clock generator"
    if "debounce" in name:
        return "input conditioning"
    if role == "control":
        return "read/write coordinator"
    if "fifo" in name:
        return "buffer storage"
    if role == "source":
        return "receive datapath"
    if role == "sink":
        return "transmit datapath"
    if role == "status":
        return "status monitor"
    return "logic block"


def node(node_id: str, text: str, x: float, y: float, w: float, h: float, **extra) -> dict:
    result = {
        "id": node_id,
        "text": text,
        "shape": "rectangle",
        "x": round(x, 2),
        "y": round(y, 2),
        "w": round(w, 2),
        "h": round(h, 2),
        "fill": BLOCK_FILL,
        "line": BLACK,
        "fontName": FONT,
        "fontSize": 11,
    }
    result.update(extra)
    return result


def connection(source: str, target: str, text: str = "", kind: str = "control") -> dict:
    colors = {"data": DATA_COLOR, "clock": DATA_COLOR, "status": STATUS_COLOR, "external": BLACK, "control": CONTROL_COLOR}
    result = {
        "from": source,
        "to": target,
        "line": colors[kind],
        "fontName": FONT,
        "fontSize": 9 if kind != "status" else 8,
        "textPinX": 0.5,
        "textOffsetY": 0.12,
    }
    if text:
        result["text"] = text
    if kind == "data":
        result["lineWeight"] = 2.2
    return result


def top_module_for(modules: dict[str, Module], requested: str | None) -> Module:
    if requested:
        if requested not in modules:
            raise ValueError(f"Top module '{requested}' was not found")
        return modules[requested]
    instantiated = {instance.module for module in modules.values() for instance in module.instances}
    candidates = [module for module in modules.values() if module.name not in instantiated and module.instances]
    if not candidates:
        raise ValueError("Unable to infer a top module; pass --top explicitly")
    return max(candidates, key=lambda module: len(module.instances))


def build_spec(top: Module, modules: dict[str, Module]) -> dict:
    instances = top.instances
    roles = {instance.name: role_for(instance.module) for instance in instances}
    by_role: dict[str, list[Instance]] = {}
    for instance in instances:
        by_role.setdefault(roles[instance.name], []).append(instance)

    main = [item for role in ("source", "datapath", "storage", "sink") for item in by_role.get(role, [])]
    if not main:
        main = [item for item in instances if roles[item.name] not in ("clock", "config", "control", "status")]
    upper = by_role.get("control", [])
    left_top = by_role.get("clock", [])
    left_bottom = by_role.get("config", [])
    lower = by_role.get("status", [])
    placed = {item.name for item in main + upper + left_top + left_bottom + lower}
    lower.extend(item for item in instances if item.name not in placed)

    page_width = max(15.5, 5.2 + len(main) * 3.55)
    page_height = 9.2
    nodes = [
        node("container", "", 1.25, 0.45, page_width - 2.0, 8.25, fill=WHITE, zOrder=0),
        node("title", f"{top.name} | RTL Logic Block Diagram", page_width / 2 - 3.2, 8.15, 6.4, 0.38, fill=WHITE, line=WHITE, fontSize=15),
    ]

    positions: dict[str, tuple[float, float]] = {}
    for i, instance in enumerate(main):
        positions[instance.name] = (3.0 + i * 3.65, 4.18)
    for i, instance in enumerate(upper):
        positions[instance.name] = (page_width / 2 - 1.2 + i * 2.7, 6.1)
    for i, instance in enumerate(left_top):
        positions[instance.name] = (1.75, 7.0 - i * 1.0)
    for i, instance in enumerate(left_bottom):
        positions[instance.name] = (2.1, 1.72 - i * 1.0)
    for i, instance in enumerate(lower):
        positions[instance.name] = (page_width - 5.45 - i * 3.0, 1.42)

    for instance in instances:
        role = roles[instance.name]
        x, y = positions[instance.name]
        w = 2.55 if role in ("storage", "status") else 2.15
        h = 1.2 if role == "storage" else 1.0
        label = f"{instance.module.upper()}\n{subtitle(instance.module, role)}"
        nodes.append(node(instance.name, label, x, y, w, h))

    net_endpoints: dict[str, list[tuple[str, str, str]]] = {}
    net_raw_signals: dict[str, list[str]] = {}
    for instance in instances:
        for port_name, net in instance.connections.items():
            port = modules[instance.module].ports.get(port_name)
            direction = port.direction if port else "inout"
            base = net_base(net)
            net_endpoints.setdefault(base, []).append((instance.name, port_name, direction))
            net_raw_signals.setdefault(base, []).append(net)

    connections: list[dict] = []
    grouped: dict[tuple[str, str, str], list[str]] = {}
    clocks, resets = [], []
    for net, endpoints in net_endpoints.items():
        base = net
        if re.search(r"(^|_)rst|reset", base, re.I):
            resets.append((net, endpoints))
            continue
        if re.search(r"(^|_)clk|clock", base, re.I):
            clocks.append((net, endpoints))
            continue
        drivers = [(inst, port) for inst, port, direction in endpoints if direction == "output"]
        loads = [(inst, port) for inst, port, direction in endpoints if direction != "output"]
        if base in top.ports:
            if top.ports[base].direction == "input":
                drivers.append((f"ext_in_{base}", base))
            else:
                loads.append((f"ext_out_{base}", base))
        if not drivers or not loads:
            continue
        has_bit_select = any(re.search(r"\[[^:\]]+\]", item) for item in net_raw_signals[net])
        is_bus = signal_width(net, top, modules, [(inst, port) for inst, port, _ in endpoints]) and not has_bit_select
        for driver, _ in drivers:
            for load, _ in loads:
                if driver == load:
                    continue
                load_role = roles.get(load, "external")
                driver_role = roles.get(driver, "external")
                kind = "data" if is_bus else "control"
                if "status" in (load_role, driver_role):
                    kind = "status"
                if "external" in (load_role, driver_role):
                    kind = "external" if not is_bus else "data"
                hide_config_label = driver_role == "config" and load_role == "control"
                label = "" if "external" in (load_role, driver_role) or hide_config_label else signal_label(net, net_raw_signals[net], endpoints, modules, top)
                grouped.setdefault((driver, load, kind), []).append(label)

    top_inputs = [port for port in top.ports.values() if port.direction == "input"]
    top_outputs = [port for port in top.ports.values() if port.direction == "output"]
    input_y, output_y = 7.28, 4.55
    for port in top_inputs:
        label = port.name + (port.width if port.width else "")
        y = input_y
        if re.search(r"rst|reset", port.name, re.I):
            y = 6.28
        elif re.search(r"key|button|switch", port.name, re.I):
            y = 2.0
        elif re.search(r"rx|rxd|input|din", port.name, re.I):
            y = 4.55
        input_y -= 0.48
        nodes.append(node(f"ext_in_{port.name}", label, 0.05, y, 1.0, 0.32, fill=WHITE, line=WHITE, fontSize=10))
    for port in top_outputs:
        label = port.name + (port.width if port.width else "")
        y = 1.75 if re.search(r"led|status|debug", port.name, re.I) else output_y
        nodes.append(node(f"ext_out_{port.name}", label, page_width - 1.3, y, 1.25, 0.32, fill=WHITE, line=WHITE, fontSize=10))
        output_y -= 0.48

    for (source, target, kind), signals in grouped.items():
        text = " / ".join(item for item in dict.fromkeys(signals) if item)
        connections.append(connection(source, target, text, kind))

    for net, endpoints in clocks:
        drivers = [(inst, port) for inst, port, direction in endpoints if direction == "output"]
        loads = [(inst, port) for inst, port, direction in endpoints if direction != "output"]
        if net in top.ports:
            drivers.append((f"ext_in_{net}", net))
        for driver, _ in drivers:
            # A top-level block diagram shows a representative clock fanout.
            # Drawing every clock endpoint obscures the functional datapath.
            visible_loads = [
                item for item in loads
                if roles.get(item[0]) in ("source", "control", "sink", "config")
            ]
            for load, _ in visible_loads:
                if driver != load:
                    connections.append(connection(driver, load, "", "clock"))
    for net, endpoints in resets:
        loads = [(inst, port) for inst, port, direction in endpoints if direction != "output"]
        base = net
        source = f"ext_in_{base}" if base in top.ports else None
        if source:
            # Reset is global. Keep one representative line so the page stays
            # readable; the Verilog source remains the port-level authority.
            preferred = next((item for item in loads if roles.get(item[0]) == "clock"), None)
            if preferred:
                connections.append(connection(source, preferred[0], "", "external"))

    return {
        "title": f"{top.name} RTL Logic Block Diagram",
        "pageWidth": round(page_width, 2),
        "pageHeight": page_height,
        "layout": {"engine": "manual", "checkCollisions": False},
        "pages": [{"name": "RTL Logic Block", "nodes": nodes, "connections": connections}],
    }


def export_preview(vsdx: Path, preview: Path) -> None:
    import win32com.client

    visio = win32com.client.Dispatch("Visio.Application")
    visio.Visible = 0
    doc = None
    try:
        doc = visio.Documents.Open(str(vsdx.resolve()))
        doc.Pages.Item(1).Export(str(preview.resolve()))
    finally:
        if doc:
            doc.Close()
        visio.Quit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an RTL Visio block diagram from Verilog")
    parser.add_argument("source", help="Verilog directory or top-level .v/.sv file")
    parser.add_argument("output", help="Output .vsdx path")
    parser.add_argument("--top", help="Top module name; inferred when omitted")
    parser.add_argument("--json", dest="json_path", help="Keep the generated Visio JSON spec")
    parser.add_argument("--preview", help="Export a PNG preview after creating the .vsdx")
    args = parser.parse_args()

    source = Path(args.source)
    if source.is_dir():
        paths = sorted(source.rglob("*.v")) + sorted(source.rglob("*.sv"))
    else:
        paths = sorted(source.parent.glob("*.v")) + sorted(source.parent.glob("*.sv"))
    if not paths:
        raise SystemExit("No .v or .sv files found")

    modules = parse_modules(paths)
    top = top_module_for(modules, args.top)
    spec = build_spec(top, modules)

    output = Path(args.output).resolve()
    json_path = Path(args.json_path).resolve() if args.json_path else output.with_suffix(".json")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

    renderer = Path(__file__).with_name("New-VisioDiagram.py")
    subprocess.run([sys.executable, str(renderer), str(json_path), str(output), "--no-layout"], check=True)
    if args.preview:
        export_preview(output, Path(args.preview))
    print(f"Top module: {top.name}")
    print(f"Instances: {len(top.instances)}")
    print(f"JSON: {json_path}")
    print(f"VSDX: {output}")
    if args.preview:
        print(f"Preview: {Path(args.preview).resolve()}")


if __name__ == "__main__":
    main()
