"""
Visio COM automation - Python engine.
Replaces PowerShell version to avoid STA/MTA COM threading deadlocks.

Usage:
    python New-VisioDiagram.py <spec.json> <output.vsdx> [--visible] [--diagnostics]
"""

import argparse
import json
import os
import sys

import win32com.client


# ── Color helpers ──────────────────────────────────────────────

def hex_to_rgb_formula(hex_color: str) -> str | None:
    if not hex_color:
        return None
    clean = hex_color.strip().lstrip("#")
    if len(clean) != 6:
        raise ValueError(f"Color '{hex_color}' must use #RRGGBB format.")
    r, g, b = int(clean[0:2], 16), int(clean[2:4], 16), int(clean[4:6], 16)
    return f"RGB({r},{g},{b})"


def set_formula(shape, cell_name: str, formula: str):
    if formula:
        shape.CellsU(cell_name).FormulaU = formula


def set_result(shape, cell_name: str, value):
    if value is not None:
        shape.CellsU(cell_name).ResultIU = float(value)


def set_font_size(shape, pt):
    if pt is not None:
        shape.CellsU("Char.Size").FormulaU = f"{float(pt)} pt"


def set_font_family(shape, name: str):
    if name:
        escaped = name.replace('"', '""')
        shape.CellsU("Char.Font").FormulaU = f'FONT("{escaped}")'


# ── Stencil loading ───────────────────────────────────────────

DEFAULT_STENCIL_PATH = r"C:\Program Files\Microsoft Office\root\Office16\Visio Content\2052"


def load_stencils(visio, stencil_specs: list) -> dict:
    stencil_map = {}
    if not stencil_specs:
        return stencil_map

    for spec in stencil_specs:
        sid = spec["id"]
        filename = spec["file"]

        if os.path.isabs(filename):
            full = filename
        elif os.path.exists(filename):
            full = os.path.abspath(filename)
        else:
            full = os.path.join(DEFAULT_STENCIL_PATH, filename)

        if not os.path.exists(full):
            print(f"WARNING: Stencil file not found: {full}", file=sys.stderr)
            continue

        try:
            stencil = visio.Documents.OpenEx(full, 64)  # visOpenRO | visOpenDocked
            stencil_map[sid] = stencil
        except Exception as e:
            print(f"WARNING: Failed to load stencil '{sid}': {e}", file=sys.stderr)

    return stencil_map


def get_master(stencil, master_name: str):
    try:
        return stencil.Masters.Item(master_name)
    except Exception:
        available = []
        for i in range(1, min(stencil.Masters.Count, 10) + 1):
            try:
                available.append(stencil.Masters.Item(i).Name)
            except Exception:
                pass
        raise ValueError(
            f"Master '{master_name}' not found in '{stencil.Name}'. "
            f"Available (first 10): {', '.join(available)}"
        )


# ── Node drawing ──────────────────────────────────────────────

def add_node(page, node: dict, stencil_map: dict):
    x = float(node["x"])
    y = float(node["y"])

    if node.get("stencil") and node.get("master"):
        sid = node["stencil"]
        if sid not in stencil_map:
            raise ValueError(f"Stencil '{sid}' not declared in stencils array.")
        master = get_master(stencil_map[sid], node["master"])
        shape = page.Drop(master, x, y)

        if node.get("w") is not None:
            shape.CellsU("Width").ResultIU = float(node["w"])
        if node.get("h") is not None:
            shape.CellsU("Height").ResultIU = float(node["h"])

        # Stencil masters drop at center; adjust to lower-left corner convention
        actual_w = shape.CellsU("Width").ResultIU
        actual_h = shape.CellsU("Height").ResultIU
        shape.CellsU("PinX").ResultIU = x + actual_w / 2
        shape.CellsU("PinY").ResultIU = y + actual_h / 2
    else:
        # Basic shapes
        w = float(node.get("w", 2.0))
        h = float(node.get("h", 0.8))
        kind = node.get("shape", "roundrect").lower()

        if kind == "ellipse":
            shape = page.DrawOval(x, y, x + w, y + h)
        elif kind == "diamond":
            pts = [
                x + w / 2, y + h,
                x + w,     y + h / 2,
                x + w / 2, y,
                x,         y + h / 2,
                x + w / 2, y + h,
            ]
            shape = page.DrawPolyline(pts, 0)
        elif kind == "roundrect":
            shape = page.DrawRectangle(x, y, x + w, y + h)
            set_formula(shape, "Rounding", "0.15 in")
        else:  # rectangle
            shape = page.DrawRectangle(x, y, x + w, y + h)

        fill_c = node.get("fill", "#EFF6FF")
        line_c = node.get("line", "#3B82F6")
        set_formula(shape, "FillForegnd", hex_to_rgb_formula(fill_c))
        set_formula(shape, "LineColor", hex_to_rgb_formula(line_c))

    # Text & font (both stencil and basic)
    if node.get("text"):
        shape.Text = str(node["text"])
    set_font_family(shape, node.get("fontName", "Microsoft YaHei"))
    set_font_size(shape, node.get("fontSize", 11))
    return shape


# ── Connection drawing ────────────────────────────────────────

def add_connection(visio, page, shapes_by_id: dict, conn: dict):
    fid, tid = str(conn["from"]), str(conn["to"])
    if fid not in shapes_by_id:
        raise ValueError(f"Connection source '{fid}' not found.")
    if tid not in shapes_by_id:
        raise ValueError(f"Connection target '{tid}' not found.")

    connector = page.Drop(visio.ConnectorToolDataObject, 0, 0)
    connector.CellsU("BeginX").GlueTo(shapes_by_id[fid].CellsU("PinX"))
    connector.CellsU("EndX").GlueTo(shapes_by_id[tid].CellsU("PinX"))

    if conn.get("text"):
        connector.Text = str(conn["text"])
    line_c = conn.get("line", "#475569")
    set_formula(connector, "LineColor", hex_to_rgb_formula(line_c))
    set_font_family(connector, conn.get("fontName", "Microsoft YaHei"))
    set_font_size(connector, conn.get("fontSize", 10))

    tpx = float(conn.get("textPinX", 0.35))
    toy = float(conn.get("textOffsetY", 0.18))
    connector.CellsU("TxtPinX").FormulaU = f"Width*{tpx}"
    connector.CellsU("TxtPinY").FormulaU = f"Height*0.5+{toy} in"
    end_arrow = int(conn.get("endArrow", 4))
    connector.CellsU("EndArrow").ResultIU = end_arrow


# ── Sequence diagram ──────────────────────────────────────────

ACTOR_TYPE_COLORS = {
    "actor":    ("#EFF6FF", "#3B82F6"),
    "system":   ("#F5F3FF", "#8B5CF6"),
    "database": ("#FEF3C7", "#D97706"),
    "external": ("#ECFDF5", "#10B981"),
}


def add_sequence_diagram(visio, page, spec: dict):
    actors = spec.get("actors", [])
    messages = spec.get("messages", [])
    layout = spec.get("layout", {})

    actor_spacing   = float(layout.get("actorSpacing", 3.0))
    message_spacing = float(layout.get("messageSpacing", 0.6))
    start_y         = float(layout.get("startY", 8.0))
    lifeline_height = float(layout.get("lifelineHeight", 6.0))

    box_w, box_h = 1.6, 0.6
    start_x = 1.0
    actor_data = {}

    # Draw actors and lifelines
    for i, actor in enumerate(actors):
        aid = str(actor["id"])
        cx = start_x + i * actor_spacing
        bx = cx - box_w / 2
        by = start_y - box_h

        atype = actor.get("type", "actor").lower()
        default_fill, default_line = ACTOR_TYPE_COLORS.get(atype, ACTOR_TYPE_COLORS["actor"])
        fill_c = actor.get("fill", default_fill)
        line_c = actor.get("line", default_line)

        box = page.DrawRectangle(bx, by, bx + box_w, by + box_h)
        box.Text = actor.get("name", aid)
        set_formula(box, "FillForegnd", hex_to_rgb_formula(fill_c))
        set_formula(box, "LineColor", hex_to_rgb_formula(line_c))
        set_font_family(box, "Microsoft YaHei")
        set_font_size(box, 10)

        ll_bottom = by - lifeline_height
        ll = page.DrawLine(cx, by, cx, ll_bottom)
        ll.CellsU("LinePattern").ResultIU = 2
        set_formula(ll, "LineColor", hex_to_rgb_formula("#94A3B8"))
        ll.CellsU("LineWeight").FormulaU = "0.5 pt"

        actor_data[aid] = {"cx": cx, "by": by}

    # Draw messages
    cur_y = start_y - box_h - 0.3
    for msg in messages:
        fid, tid = str(msg["from"]), str(msg["to"])
        if fid not in actor_data:
            raise ValueError(f"Message source '{fid}' not in actors.")
        if tid not in actor_data:
            raise ValueError(f"Message target '{tid}' not in actors.")

        fx, tx = actor_data[fid]["cx"], actor_data[tid]["cx"]
        mtype = msg.get("type", "sync")

        arrow = page.DrawLine(fx, cur_y, tx, cur_y)
        if msg.get("text"):
            arrow.Text = str(msg["text"])
            arrow.CellsU("TxtPinX").FormulaU = "Width*0.5"
            arrow.CellsU("TxtPinY").FormulaU = "Height*0.5+0.15 in"

        set_formula(arrow, "LineColor", hex_to_rgb_formula("#475569"))
        set_font_family(arrow, "Microsoft YaHei")
        set_font_size(arrow, 9)

        if mtype == "return":
            arrow.CellsU("LinePattern").ResultIU = 2
            arrow.CellsU("EndArrow").ResultIU = 1
        else:
            arrow.CellsU("EndArrow").ResultIU = 4

        cur_y -= message_spacing


# ── Main ──────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Generate Visio .vsdx from JSON spec")
    parser.add_argument("spec", help="Path to JSON spec file")
    parser.add_argument("output", help="Output .vsdx path")
    parser.add_argument("--visible", action="store_true", help="Show Visio window")
    parser.add_argument("--diagnostics", action="store_true", help="Print diagnostics")
    args = parser.parse_args()

    spec_path = os.path.abspath(args.spec)
    output_path = os.path.abspath(args.output)

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = json.load(f)

    out_dir = os.path.dirname(output_path)
    if out_dir and not os.path.exists(out_dir):
        os.makedirs(out_dir, exist_ok=True)

    visio = None
    doc = None
    try:
        # Use EnsureDispatch for better COM support
        try:
            visio = win32com.client.gencache.EnsureDispatch("Visio.Application")
        except:
            visio = win32com.client.Dispatch("Visio.Application")

        # Set visibility using integer (more compatible)
        try:
            visio.Visible = 0 if not args.visible else -1
        except:
            pass  # Some COM configurations don't support setting Visible

        doc = visio.Documents.Add("")

        # Load stencils
        stencil_map = load_stencils(visio, spec.get("stencils"))
        if args.diagnostics:
            print(f"Loaded {len(stencil_map)} stencil(s).")

        diagram_type = spec.get("type", "standard")

        if diagram_type == "sequence":
            page = visio.ActivePage
            if spec.get("title"):
                page.Name = str(spec["title"])
            pw = float(spec.get("pageWidth", 11))
            ph = float(spec.get("pageHeight", 8.5))
            page.PageSheet.CellsU("PageWidth").ResultIU = pw
            page.PageSheet.CellsU("PageHeight").ResultIU = ph
            add_sequence_diagram(visio, page, spec)
            if args.diagnostics:
                print(f"Sequence diagram '{page.Name}': {page.Shapes.Count} shapes.")
        else:
            # Standard diagram
            pages_spec = spec.get("pages", [spec])
            if not isinstance(pages_spec, list):
                pages_spec = [pages_spec]

            for i, page_spec in enumerate(pages_spec):
                page = visio.ActivePage if i == 0 else doc.Pages.Add()
                if page_spec.get("name"):
                    page.Name = str(page_spec["name"])

                pw = float(page_spec.get("pageWidth", spec.get("pageWidth", 11)))
                ph = float(page_spec.get("pageHeight", spec.get("pageHeight", 8.5)))
                page.PageSheet.CellsU("PageWidth").ResultIU = pw
                page.PageSheet.CellsU("PageHeight").ResultIU = ph

                shapes_by_id = {}
                for node in page_spec.get("nodes", []):
                    if not node.get("id"):
                        raise ValueError("Every node must include an id.")
                    shapes_by_id[str(node["id"])] = add_node(page, node, stencil_map)

                for conn in page_spec.get("connections", []):
                    add_connection(visio, page, shapes_by_id, conn)

                if args.diagnostics:
                    print(f"Page '{page.Name}': {page.Shapes.Count} shapes.")

        doc.SaveAs(output_path)
        print(output_path)
    finally:
        if doc:
            doc.Saved = True
            doc.Close()
        if visio:
            visio.Quit()


if __name__ == "__main__":
    main()
