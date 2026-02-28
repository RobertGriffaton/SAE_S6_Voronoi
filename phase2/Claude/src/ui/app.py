"""
app.py — Main Tkinter application window.

Orchestrates the three layers:
  IO (PointFileReader) → Core (VoronoiEngine) → UI (CanvasRenderer / Exporters)

Design:
  - This class is purely an orchestrator (thin glue code).
  - Business logic lives exclusively in core/ and export/.
  - Error handling surfaces as user-friendly message boxes.
"""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Optional

from src.core.models import VoronoiDiagram
from src.core.voronoi_engine import InsufficientPointsError, VoronoiEngine
from src.export.image_exporter import ImageExporter
from src.export.svg_exporter import SVGExporter
from src.io.point_file_reader import PointFileReader, PointParseError
from src.ui.canvas_renderer import CanvasRenderer

# Window constants
WINDOW_TITLE: str = "Voronoï Diagram Viewer"
WINDOW_MIN_WIDTH: int = 800
WINDOW_MIN_HEIGHT: int = 600
CANVAS_DEFAULT_WIDTH: int = 780
CANVAS_DEFAULT_HEIGHT: int = 540

POINT_FILE_TYPES = [("Text / CSV files", "*.txt *.csv"), ("All files", "*.*")]
SVG_FILE_TYPES = [("SVG files", "*.svg")]
PNG_FILE_TYPES = [("PNG images", "*.png")]


class Application(tk.Tk):
    """
    Root Tkinter window for the Voronoï Diagram Viewer.

    Responsibilities:
      - Build and manage the UI layout
      - React to menu actions (open file, export)
      - Delegate all non-UI work to dedicated classes
    """

    def __init__(self) -> None:
        super().__init__()
        self._reader = PointFileReader()
        self._engine = VoronoiEngine()
        self._current_diagram: Optional[VoronoiDiagram] = None

        self._setup_window()
        self._build_menu()
        self._build_canvas()
        self._build_status_bar()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _setup_window(self) -> None:
        self.title(WINDOW_TITLE)
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self.resizable(True, True)

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=False)
        file_menu.add_command(label="Open points file…", command=self._on_open, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Export as SVG…", command=self._on_export_svg, state=tk.DISABLED)
        file_menu.add_command(label="Export as PNG…", command=self._on_export_png, state=tk.DISABLED)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.quit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        self.config(menu=menubar)
        self._file_menu = file_menu
        self.bind_all("<Control-o>", lambda _e: self._on_open())
        self.bind_all("<Control-q>", lambda _e: self.quit())

    def _build_canvas(self) -> None:
        frame = tk.Frame(self, bg="#e0e0e0")
        frame.pack(fill=tk.BOTH, expand=True, padx=4, pady=4)

        self._canvas = tk.Canvas(
            frame,
            width=CANVAS_DEFAULT_WIDTH,
            height=CANVAS_DEFAULT_HEIGHT,
            background="#f9f9f9",
            relief=tk.SUNKEN,
            bd=1,
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)
        self._renderer = CanvasRenderer(self._canvas)
        self._canvas.bind("<Configure>", self._on_canvas_resize)

    def _build_status_bar(self) -> None:
        self._status_var = tk.StringVar(value="Open a points file to get started.")
        status_bar = tk.Label(
            self,
            textvariable=self._status_var,
            anchor=tk.W,
            relief=tk.SUNKEN,
            font=("Helvetica", 10),
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=4, pady=2)

    # ------------------------------------------------------------------
    # Menu actions
    # ------------------------------------------------------------------

    def _on_open(self) -> None:
        file_path_str = filedialog.askopenfilename(
            title="Select a points file",
            filetypes=POINT_FILE_TYPES,
        )
        if not file_path_str:
            return  # user cancelled

        file_path = Path(file_path_str)
        try:
            points = self._reader.read(file_path)
            diagram = self._engine.compute(points)
        except (FileNotFoundError, PointParseError, InsufficientPointsError, ValueError) as exc:
            messagebox.showerror("Error loading file", str(exc))
            return

        self._current_diagram = diagram
        self._renderer.render(diagram)
        self._set_status(f"Loaded {len(points)} point(s) from '{file_path.name}'.")
        self._enable_export_menus()

    def _on_export_svg(self) -> None:
        self._export_diagram(SVGExporter(), SVG_FILE_TYPES, ".svg")

    def _on_export_png(self) -> None:
        self._export_diagram(ImageExporter(), PNG_FILE_TYPES, ".png")

    def _export_diagram(self, exporter, filetypes, default_extension: str) -> None:
        if self._current_diagram is None:
            return
        output_path_str = filedialog.asksaveasfilename(
            defaultextension=default_extension,
            filetypes=filetypes,
        )
        if not output_path_str:
            return
        try:
            exporter.export(self._current_diagram, Path(output_path_str))
            self._set_status(f"Diagram exported to '{Path(output_path_str).name}'.")
        except OSError as exc:
            messagebox.showerror("Export error", str(exc))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _on_canvas_resize(self, _event: tk.Event) -> None:
        if self._current_diagram is not None:
            self._renderer.render(self._current_diagram)

    def _set_status(self, message: str) -> None:
        self._status_var.set(message)

    def _enable_export_menus(self) -> None:
        self._file_menu.entryconfig("Export as SVG…", state=tk.NORMAL)
        self._file_menu.entryconfig("Export as PNG…", state=tk.NORMAL)
