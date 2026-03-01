"""Tkinter user interface for Voronoi diagram generation."""

from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

from voronoi_app.constants import (
    CANVAS_HEIGHT,
    CANVAS_PADDING,
    CANVAS_WIDTH,
    CONTROL_SPACING,
    EDGE_WIDTH,
    FRAME_PADDING,
    POINT_RADIUS,
    SITE_OUTLINE_WIDTH,
    WINDOW_MIN_HEIGHT,
    WINDOW_MIN_WIDTH,
)
from voronoi_app.exporters.image_exporter import ImageExporter
from voronoi_app.exporters.svg_exporter import SvgExporter
from voronoi_app.parsing import PointFileParser
from voronoi_app.rendering import build_transform
from voronoi_app.services.diagram_service import VoronoiDiagram, VoronoiDiagramService
from voronoi_app.theme import (
    APP_BACKGROUND_COLOR,
    BUTTON_ACTIVE_COLOR,
    BUTTON_BACKGROUND_COLOR,
    BUTTON_TEXT_COLOR,
    CANVAS_BACKGROUND_COLOR,
    CANVAS_BORDER_COLOR,
    EDGE_COLOR,
    PANEL_BACKGROUND_COLOR,
    SITE_COLOR,
    STATUS_TEXT_COLOR,
    get_cell_color,
)


class VoronoiApp:
    """Main Tkinter application."""

    def __init__(
        self,
        root: tk.Tk,
        parser: PointFileParser,
        diagram_service: VoronoiDiagramService,
        svg_exporter: SvgExporter,
        image_exporter: ImageExporter,
    ) -> None:
        self._root = root
        self._parser = parser
        self._diagram_service = diagram_service
        self._svg_exporter = svg_exporter
        self._image_exporter = image_exporter
        self._diagram: VoronoiDiagram | None = None

        self._root.title("Voronoi Diagram Generator")
        self._root.configure(bg=APP_BACKGROUND_COLOR)
        self._root.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self._build_widgets()

    def _build_widgets(self) -> None:
        controls = tk.Frame(self._root, bg=PANEL_BACKGROUND_COLOR, padx=FRAME_PADDING, pady=FRAME_PADDING)
        controls.pack(fill=tk.X, padx=FRAME_PADDING, pady=(FRAME_PADDING, 0))

        button_options = {
            "bg": BUTTON_BACKGROUND_COLOR,
            "fg": BUTTON_TEXT_COLOR,
            "activebackground": BUTTON_ACTIVE_COLOR,
            "activeforeground": BUTTON_TEXT_COLOR,
            "relief": tk.FLAT,
            "bd": 0,
            "padx": 10,
            "pady": 6,
            "cursor": "hand2",
        }

        tk.Button(controls, text="Load Points", command=self._load_points, **button_options).pack(
            side=tk.LEFT,
            padx=(0, CONTROL_SPACING),
        )
        tk.Button(controls, text="Export SVG", command=self._export_svg, **button_options).pack(
            side=tk.LEFT,
            padx=(0, CONTROL_SPACING),
        )
        tk.Button(controls, text="Export PNG", command=self._export_png, **button_options).pack(side=tk.LEFT)

        self._status_var = tk.StringVar(value="Load a point file to start.")
        tk.Label(
            controls,
            textvariable=self._status_var,
            bg=PANEL_BACKGROUND_COLOR,
            fg=STATUS_TEXT_COLOR,
            font=("Helvetica", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(14, 0))

        canvas_frame = tk.Frame(
            self._root,
            bg=CANVAS_BORDER_COLOR,
            padx=2,
            pady=2,
            highlightthickness=0,
            bd=0,
        )
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=FRAME_PADDING, pady=FRAME_PADDING)

        self._canvas = tk.Canvas(
            canvas_frame,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg=CANVAS_BACKGROUND_COLOR,
            highlightthickness=0,
            bd=0,
        )
        self._canvas.pack(fill=tk.BOTH, expand=True)

    def _load_points(self) -> None:
        file_path = filedialog.askopenfilename(
            title="Select point file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if not file_path:
            return

        try:
            points = self._parser.parse_file(file_path)
            self._diagram = self._diagram_service.build_diagram(points)
            self._draw_diagram(self._diagram)
            self._status_var.set(f"Loaded {len(points)} points from {Path(file_path).name}.")
        except Exception as exception:  # noqa: BLE001
            messagebox.showerror("Error", str(exception))
            self._status_var.set("Failed to load file.")

    def _draw_diagram(self, diagram: VoronoiDiagram) -> None:
        self._canvas.delete("all")

        transform = build_transform(
            points=diagram.sites,
            viewport_width=CANVAS_WIDTH,
            viewport_height=CANVAS_HEIGHT,
            padding=CANVAS_PADDING,
        )

        for index, site in enumerate(diagram.sites):
            polygon = diagram.cells.get(site, [])
            if len(polygon) < 3:
                continue
            fill_color = get_cell_color(index)
            transformed_vertices = [transform(vertex) for vertex in polygon]
            flat_coordinates = [coordinate for vertex in transformed_vertices for coordinate in vertex]
            self._canvas.create_polygon(
                *flat_coordinates,
                fill=fill_color,
                outline="",
                smooth=False,
            )

        for segment in diagram.segments:
            x1, y1 = transform(segment.start)
            x2, y2 = transform(segment.end)
            self._canvas.create_line(
                x1,
                y1,
                x2,
                y2,
                fill=EDGE_COLOR,
                width=EDGE_WIDTH,
            )

        for point in diagram.sites:
            x, y = transform(point)
            self._canvas.create_oval(
                x - POINT_RADIUS,
                y - POINT_RADIUS,
                x + POINT_RADIUS,
                y + POINT_RADIUS,
                fill=SITE_COLOR,
                outline=EDGE_COLOR,
                width=SITE_OUTLINE_WIDTH,
            )

    def _export_svg(self) -> None:
        if self._diagram is None:
            messagebox.showwarning("Warning", "No diagram to export.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save SVG",
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg")],
        )
        if not output_path:
            return

        try:
            self._svg_exporter.export(self._diagram, output_path)
            self._status_var.set(f"SVG exported: {Path(output_path).name}")
        except Exception as exception:  # noqa: BLE001
            messagebox.showerror("Error", str(exception))

    def _export_png(self) -> None:
        if self._diagram is None:
            messagebox.showwarning("Warning", "No diagram to export.")
            return

        output_path = filedialog.asksaveasfilename(
            title="Save PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
        )
        if not output_path:
            return

        try:
            self._image_exporter.export_png(self._diagram, output_path)
            self._status_var.set(f"PNG exported: {Path(output_path).name}")
        except Exception as exception:  # noqa: BLE001
            messagebox.showerror("Error", str(exception))
