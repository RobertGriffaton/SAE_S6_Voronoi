# Voronoi Diagram Application

## Architecture

```
voronoi_app/
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py          # Point, VoronoiDiagram data classes
│   │   └── voronoi_engine.py  # Computation (SciPy Fortune's algorithm)
│   ├── io/
│   │   ├── __init__.py
│   │   └── point_file_reader.py  # Parses input files
│   ├── export/
│   │   ├── __init__.py
│   │   ├── exporter_base.py   # Abstract base (Strategy pattern)
│   │   ├── svg_exporter.py
│   │   └── image_exporter.py
│   └── ui/
│       ├── __init__.py
│       ├── app.py             # Tkinter main window
│       └── canvas_renderer.py # Draws the diagram
├── tests/
│   ├── conftest.py
│   ├── test_point_file_reader.py
│   ├── test_voronoi_engine.py
│   └── test_exporters.py
├── main.py
├── requirements.txt
└── README.md
```

## Algorithm Choice

**SciPy's `Voronoi` (Fortune's algorithm)** — O(n log n) time, O(n) space.  
Implementing Fortune's sweep-line from scratch is ~1000 lines and error-prone. SciPy wraps the battle-tested Qhull library, giving us correct, fast computation with a stable API. This aligns with the KISS principle: don't reinvent what already works.

## Design Patterns Used

| Pattern | Where | Why |
|---|---|---|
| **Strategy** | `DiagramExporter` (abstract) → `SVGExporter`, `ImageExporter` | Adding a new format requires only a new class, zero changes to existing code (OCP) |
| **Repository** | `PointFileReader` | Isolates file-parsing from business logic (SRP) |
| **Facade** | `VoronoiEngine` | Hides SciPy internals behind a clean domain API |

## Installation

```bash
cd voronoi_app
pip install -r requirements.txt
```

## Run the Application

```bash
python main.py
```

Then use **File → Open** to load a `.txt` / `.csv` file with one `x,y` coordinate per line:

```
2,4
5.3,4.5
18,29
12.5,23.7
```

## Run the Tests

```bash
pytest tests/ -v
```

## Export Formats

- **SVG** — scalable vector, ideal for print / web
- **PNG** — raster image via Pillow
