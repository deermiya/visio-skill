"""
Reconstruct an editable Visio diagram from a raster image.

The script extracts geometry locally with OpenCV. OCR is optional. For complex
or text-heavy images, an AI agent can inspect the image and pass a small JSON
overlay through --annotations to correct labels or add semantic elements.

Usage:
    python image_to_visio.py input.png output.vsdx
        [--mode auto|flowchart|gantt|diagram]
        [--json output.json] [--preview output.png]
        [--annotations overlay.json] [--ocr auto|off]
"""

from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np


PAGE_MARGIN = 0.35
MAX_PAGE_WIDTH = 15.5
MAX_PAGE_HEIGHT = 10.5
FONT = "Microsoft YaHei"


def pixel_box_to_visio(box, scale: float, image_height: int):
    x, y, w, h = box
    return (
        PAGE_MARGIN + x * scale,
        PAGE_MARGIN + (image_height - y - h) * scale,
        w * scale,
        h * scale,
    )


def pixel_line_to_visio(line, scale: float, image_height: int):
    x1, y1, x2, y2 = line
    return {
        "x1": round(PAGE_MARGIN + x1 * scale, 3),
        "y1": round(PAGE_MARGIN + (image_height - y1) * scale, 3),
        "x2": round(PAGE_MARGIN + x2 * scale, 3),
        "y2": round(PAGE_MARGIN + (image_height - y2) * scale, 3),
    }


def bgr_to_hex(color) -> str:
    b, g, r = [int(item) for item in color]
    return f"#{r:02X}{g:02X}{b:02X}"


def sampled_fill(image, box) -> str:
    x, y, w, h = box
    inset_x, inset_y = max(2, int(w * 0.18)), max(2, int(h * 0.18))
    crop = image[y + inset_y : y + h - inset_y, x + inset_x : x + w - inset_x]
    if crop.size == 0:
        return "#FFFFFF"
    median = np.median(crop.reshape(-1, 3), axis=0)
    return bgr_to_hex(median)


def near_duplicate(box, accepted, tolerance: int = 8) -> bool:
    x, y, w, h = box
    for other in accepted:
        ox, oy, ow, oh = other
        if abs(x - ox) <= tolerance and abs(y - oy) <= tolerance and abs(w - ow) <= tolerance and abs(h - oh) <= tolerance:
            return True
    return False


def mostly_contains(box, other, margin: int = 5) -> bool:
    x, y, w, h = box
    ox, oy, ow, oh = other
    return x - margin <= ox and y - margin <= oy and x + w + margin >= ox + ow and y + h + margin >= oy + oh


def classify_contour(contour, box) -> str:
    x, y, w, h = box
    perimeter = cv2.arcLength(contour, True)
    if perimeter <= 0:
        return "rectangle"
    approx = cv2.approxPolyDP(contour, 0.025 * perimeter, True)
    area = cv2.contourArea(contour)
    circularity = 4 * math.pi * area / max(perimeter * perimeter, 1)
    if len(approx) >= 7 and circularity > 0.72:
        return "ellipse"
    if len(approx) == 4:
        points = approx.reshape(-1, 2)
        normalized = [((px - x) / max(w, 1), (py - y) / max(h, 1)) for px, py in points]
        expected = ((0.5, 0.0), (1.0, 0.5), (0.5, 1.0), (0.0, 0.5))
        axis_aligned = all(
            min(math.dist(point, target) for target in expected) < 0.24
            for point in normalized
        )
        if axis_aligned and abs(w - h) < max(w, h) * 0.55:
            return "diamond"
    return "rectangle"


def detect_shapes(image, mode: str):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    binary = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 9)
    contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    height, width = gray.shape
    image_area = width * height
    accepted_boxes = []
    shapes = []
    min_area = image_area * (0.00035 if mode == "gantt" else 0.001)

    for contour in sorted(contours, key=cv2.contourArea, reverse=True):
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        box = (x, y, w, h)
        if area < min_area or w < 18 or h < 12:
            continue
        if w * h > image_area * 0.72:
            continue
        if w / max(h, 1) > 45 or h / max(w, 1) > 28:
            continue
        rectangularity = area / max(w * h, 1)
        if rectangularity < 0.22:
            continue
        shape_kind = classify_contour(contour, box)
        if shape_kind == "rectangle" and rectangularity < 0.68:
            continue
        if shape_kind == "diamond" and not 0.34 <= rectangularity <= 0.72:
            continue
        if near_duplicate(box, accepted_boxes):
            continue
        if any(mostly_contains(box, other) and w * h > ow * oh * 1.28 for other in accepted_boxes for ox, oy, ow, oh in [other]):
            continue
        accepted_boxes.append(box)
        fill = sampled_fill(image, box)
        shapes.append({
            "pixelBox": box,
            "shape": shape_kind,
            "fill": fill,
            "line": "#111827",
        })
    return shapes, binary


def point_inside_any(x: float, y: float, shapes, inset: int = 4) -> bool:
    for item in shapes:
        sx, sy, sw, sh = item["pixelBox"]
        if sx + inset < x < sx + sw - inset and sy + inset < y < sy + sh - inset:
            return True
    return False


def normalized_line(line):
    x1, y1, x2, y2 = [int(item) for item in line]
    if abs(x2 - x1) >= abs(y2 - y1):
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        y = int(round((y1 + y2) / 2))
        return (x1, y, x2, y)
    if y1 > y2:
        x1, x2 = x2, x1
        y1, y2 = y2, y1
    x = int(round((x1 + x2) / 2))
    return (x, y1, x, y2)


def merge_lines(lines, tolerance: int = 7):
    current = list(sorted(set(lines)))
    while True:
        merged = []
        changed = False
        for line in current:
            x1, y1, x2, y2 = line
            horizontal = y1 == y2
            combined = False
            for i, other in enumerate(merged):
                ox1, oy1, ox2, oy2 = other
                other_horizontal = oy1 == oy2
                if horizontal and other_horizontal and abs(y1 - oy1) <= tolerance and x1 <= ox2 + tolerance and x2 >= ox1 - tolerance:
                    merged[i] = (min(x1, ox1), int(round((y1 + oy1) / 2)), max(x2, ox2), int(round((y1 + oy1) / 2)))
                    combined = True
                    changed = True
                    break
                if not horizontal and not other_horizontal and abs(x1 - ox1) <= tolerance and y1 <= oy2 + tolerance and y2 >= oy1 - tolerance:
                    merged[i] = (int(round((x1 + ox1) / 2)), min(y1, oy1), int(round((x1 + ox1) / 2)), max(y2, oy2))
                    combined = True
                    changed = True
                    break
            if not combined:
                merged.append(line)
        current = sorted(set(merged))
        if not changed:
            return current


def overlaps_shape_edge(line, shapes, tolerance: int = 6) -> bool:
    x1, y1, x2, y2 = line
    horizontal = y1 == y2
    for item in shapes:
        sx, sy, sw, sh = item["pixelBox"]
        if horizontal and (abs(y1 - sy) <= tolerance or abs(y1 - (sy + sh)) <= tolerance):
            overlap = max(0, min(x2, sx + sw) - max(x1, sx))
            if overlap >= min(abs(x2 - x1), sw) * 0.72:
                return True
        if not horizontal and (abs(x1 - sx) <= tolerance or abs(x1 - (sx + sw)) <= tolerance):
            overlap = max(0, min(y2, sy + sh) - max(y1, sy))
            if overlap >= min(abs(y2 - y1), sh) * 0.72:
                return True
    return False


def detect_lines(binary, shapes, mode: str):
    height, width = binary.shape
    min_length = max(28, int(min(width, height) * (0.035 if mode == "gantt" else 0.075)))
    raw = cv2.HoughLinesP(binary, 1, np.pi / 180, threshold=38, minLineLength=min_length, maxLineGap=10)
    if raw is None:
        return []
    candidates = []
    for item in raw[:, 0, :]:
        line = normalized_line(item)
        x1, y1, x2, y2 = line
        if abs(x2 - x1) < min_length and abs(y2 - y1) < min_length:
            continue
        midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
        if mode != "gantt" and point_inside_any(*midpoint, shapes):
            continue
        if overlaps_shape_edge(line, shapes):
            continue
        candidates.append(line)
    return merge_lines(candidates)


def infer_mode(image) -> str:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 31, 9)
    height, width = gray.shape
    raw = cv2.HoughLinesP(
        binary,
        1,
        np.pi / 180,
        threshold=48,
        minLineLength=max(36, int(min(width, height) * 0.12)),
        maxLineGap=8,
    )
    if raw is None:
        return "diagram"
    merged = merge_lines([normalized_line(item) for item in raw[:, 0, :]])
    horizontal = [
        line for line in merged
        if line[1] == line[3] and abs(line[2] - line[0]) >= width * 0.35
    ]
    vertical = [
        line for line in merged
        if line[0] == line[2] and abs(line[3] - line[1]) >= height * 0.35
    ]
    intersections = sum(
        1
        for hx1, hy, hx2, _ in horizontal
        for vx, vy1, _, vy2 in vertical
        if hx1 <= vx <= hx2 and vy1 <= hy <= vy2
    )
    return "gantt" if len(horizontal) >= 4 and len(vertical) >= 4 and intersections >= 10 else "diagram"


def optional_ocr(image, scale: float):
    try:
        import pytesseract
    except ImportError:
        return []
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    data = pytesseract.image_to_data(rgb, output_type=pytesseract.Output.DICT)
    labels = []
    height = image.shape[0]
    for i, text in enumerate(data["text"]):
        text = text.strip()
        confidence = float(data["conf"][i])
        if not text or confidence < 55:
            continue
        x, y, w, h = data["left"][i], data["top"][i], data["width"][i], data["height"][i]
        vx, vy, vw, vh = pixel_box_to_visio((x, y, w, h), scale, height)
        labels.append({
            "text": text,
            "x": round(vx, 3),
            "y": round(vy, 3),
            "w": round(max(vw, 0.25), 3),
            "h": round(max(vh, 0.16), 3),
            "fontName": FONT,
            "fontSize": 8,
            "fill": "#FFFFFF",
            "line": "#FFFFFF",
        })
    return labels


def overlay_spec(spec: dict, annotations_path: Path | None):
    if not annotations_path:
        return spec
    overlay = json.loads(annotations_path.read_text(encoding="utf-8"))
    page = spec["pages"][0]
    if overlay.get("replaceNodes"):
        page["nodes"] = []
    if overlay.get("replaceLines"):
        page["lines"] = []
    if overlay.get("replaceLabels"):
        page["labels"] = []
    page["nodes"].extend(overlay.get("nodes", []))
    page["lines"].extend(overlay.get("lines", []))
    page["labels"].extend(overlay.get("labels", []))
    if overlay.get("title"):
        spec["title"] = overlay["title"]
        page["name"] = overlay["title"]
    return spec


def build_spec(image, mode: str, use_ocr: bool, annotations_path: Path | None):
    height, width = image.shape[:2]
    scale = min((MAX_PAGE_WIDTH - PAGE_MARGIN * 2) / width, (MAX_PAGE_HEIGHT - PAGE_MARGIN * 2) / height)
    page_width = PAGE_MARGIN * 2 + width * scale
    page_height = PAGE_MARGIN * 2 + height * scale
    shapes, binary = detect_shapes(image, mode)
    lines = detect_lines(binary, shapes, mode)

    nodes = []
    for index, item in enumerate(shapes, 1):
        x, y, w, h = pixel_box_to_visio(item["pixelBox"], scale, height)
        nodes.append({
            "id": f"shape_{index:03d}",
            "text": "",
            "shape": item["shape"],
            "x": round(x, 3),
            "y": round(y, 3),
            "w": round(w, 3),
            "h": round(h, 3),
            "fill": item["fill"],
            "line": item["line"],
            "fontName": FONT,
            "fontSize": 10,
        })

    visio_lines = []
    for line in lines:
        item = pixel_line_to_visio(line, scale, height)
        item.update({"line": "#475569", "lineWeight": 0.8})
        visio_lines.append(item)

    labels = optional_ocr(image, scale) if use_ocr else []
    spec = {
        "title": f"Reconstructed {mode.title()} Diagram",
        "pageWidth": round(page_width, 3),
        "pageHeight": round(page_height, 3),
        "layout": {"engine": "manual", "checkCollisions": False},
        "pages": [{
            "name": "Image Reconstruction",
            "nodes": nodes,
            "connections": [],
            "lines": visio_lines,
            "labels": labels,
        }],
        "reconstruction": {
            "mode": mode,
            "imageWidth": width,
            "imageHeight": height,
            "detectedShapes": len(nodes),
            "detectedLines": len(visio_lines),
            "ocrLabels": len(labels),
        },
    }
    return overlay_spec(spec, annotations_path)


def export_preview(vsdx: Path, preview: Path):
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


def main():
    parser = argparse.ArgumentParser(description="Reconstruct an editable Visio diagram from an image")
    parser.add_argument("image", help="Input PNG/JPG/BMP diagram")
    parser.add_argument("output", help="Output .vsdx path")
    parser.add_argument("--mode", choices=("auto", "flowchart", "gantt", "diagram"), default="auto")
    parser.add_argument("--json", dest="json_path", help="Generated intermediate JSON path")
    parser.add_argument("--preview", help="Export a PNG preview after rendering")
    parser.add_argument("--annotations", help="Optional JSON overlay with corrected nodes, lines, or labels")
    parser.add_argument("--ocr", choices=("auto", "off"), default="auto")
    args = parser.parse_args()

    image_path = Path(args.image)
    output = Path(args.output).resolve()
    json_path = Path(args.json_path).resolve() if args.json_path else output.with_suffix(".json")
    annotations = Path(args.annotations).resolve() if args.annotations else None
    image = cv2.imread(str(image_path.resolve()))
    if image is None:
        raise SystemExit(f"Unable to read image: {image_path}")

    mode = infer_mode(image) if args.mode == "auto" else args.mode
    spec = build_spec(image, mode, args.ocr != "off", annotations)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")

    renderer = Path(__file__).with_name("New-VisioDiagram.py")
    subprocess.run([sys.executable, str(renderer), str(json_path), str(output), "--no-layout"], check=True)
    if args.preview:
        export_preview(output, Path(args.preview))
    stats = spec["reconstruction"]
    print(f"Mode: {stats['mode']}")
    print(f"Detected shapes: {stats['detectedShapes']}")
    print(f"Detected lines: {stats['detectedLines']}")
    print(f"OCR labels: {stats['ocrLabels']}")
    print(f"JSON: {json_path}")
    print(f"VSDX: {output}")
    if args.preview:
        print(f"Preview: {Path(args.preview).resolve()}")


if __name__ == "__main__":
    main()
