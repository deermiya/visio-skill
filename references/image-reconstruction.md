# Image Reconstruction to Editable Visio

Use `scripts/image_to_visio.py` when the user provides a raster image of a
diagram and wants an editable `.vsdx` reconstruction. Supported source images
include flowcharts, architecture diagrams, logic block diagrams, timelines,
tables, and Gantt charts.

## Fast Geometry Reconstruction

```bash
python "<skill>/scripts/image_to_visio.py" "<input.png>" "<output.vsdx>" \
  --mode auto \
  --json "<output.json>" \
  --preview "<preview.png>"
```

The local OpenCV parser detects:

- rectangles, rounded-looking rectangles, ellipses, and diamonds;
- long horizontal and vertical lines;
- table grids and Gantt-style task bars;
- sampled source colors;
- text labels when optional `pytesseract` and the Tesseract runtime are installed.

The result is a real editable Visio document. Shapes, grid lines, bars, and
labels remain independent Visio objects.

## Agent-Assisted Reconstruction

OCR and automatic contour extraction are not sufficient for every image.
When accurate text or semantics matter, inspect the source image visually and
use an annotation overlay:

```bash
python "<skill>/scripts/image_to_visio.py" "<input.png>" "<output.vsdx>" \
  --mode flowchart \
  --annotations "<overlay.json>" \
  --preview "<preview.png>"
```

Overlay format:

```json
{
  "title": "Release Process",
  "replaceLabels": true,
  "labels": [
    { "text": "Start", "x": 1.1, "y": 7.2, "w": 0.8, "h": 0.3 }
  ],
  "nodes": [
    { "id": "approval", "text": "Approval", "shape": "diamond", "x": 4, "y": 5, "w": 1.2, "h": 0.8 }
  ],
  "lines": [
    { "x1": 2, "y1": 6, "x2": 4, "y2": 6, "endArrow": 4 }
  ]
}
```

Optional booleans `replaceNodes`, `replaceLines`, and `replaceLabels` discard
the corresponding automatically detected elements before applying the overlay.
Without these flags, overlay elements are appended.

## Recommended Workflow

1. Run the fast reconstruction once with `--preview`.
2. If the user needs a faithful visual copy, inspect the source image and the
   preview side by side.
3. Add a small overlay only for missing labels, incorrect shapes, or semantic
   connections. Do not hand-redraw elements that the parser detected correctly.
4. Regenerate the `.vsdx`.

For clear diagrams, the first run is usually enough. For screenshots with UI
chrome, crop the actual diagram region first or reconstruct only the diagram
region with an overlay.
