"""
canvas_renderer.py — Draws a VoronoiDiagram onto a Tkinter Canvas.

Responsible solely for rendering: coordinate transformation and drawing calls.
The SVGExporter's ridge-clipping logic is reused via composition to avoid
duplicating the infinite-ridge handling code (DRY).
"""
from __future__ import annotations

import tkinter as tk
from typing import Optional

import numpy as np

from src.core.models import BoundingBox, VoronoiDiagram
from src.export.svg_exporter import SVGExporter  # reuse ridge helper

# Visual constants
RIDGE_COLOR: str = "#3a7bd5"
RIDGE_WIDTH: int = 1
SITE_COLOR: str = "#e74c3c"
SITE_RADIUS: int = 4
BACKGROUND_COLOR: str = "#f9f9f9"
CANVAS_PADDING: int = 20  # pixels of padding inside the canvas


class CanvasRenderer:
    """
    Renders a VoronoiDiagram on a given Tkinter Canvas widget.

    Single responsibility: coordinate mapping + draw calls.
    """

    def __init__(self, canvas: tk.Canvas) -> None:
        self._canvas = canvas
        self._ridge_helper = SVGExporter()

    def render(self, diagram: VoronoiDiagram) -> None:
        """Clear the canvas and draw *diagram*."""
        self._canvas.delete("all")
        self._canvas.configure(background=BACKGROUND_COLOR)

        canvas_width = self._canvas.winfo_width() or int(self._canvas["width"])
        canvas_height = self._canvas.winfo_height() or int(self._canvas["height"])

        bb = diagram.bounding_box

        # Draw ridges
        for rv, rp in zip(diagram.ridge_vertices, diagram.ridge_points):
            segment = self._ridge_helper._compute_ridge_segment(rv, rp, diagram)
            if segment is None:
                continue
            p1, p2 = segment
            x1, y1 = self._world_to_canvas(p1[0], p1[1], bb, canvas_width, canvas_height)
            x2, y2 = self._world_to_canvas(p2[0], p2[1], bb, canvas_width, canvas_height)
            self._canvas.create_line(x1, y1, x2, y2, fill=RIDGE_COLOR, width=RIDGE_WIDTH)

        # Draw site markers
        for site in diagram.sites:
            cx, cy = self._world_to_canvas(site.x, site.y, bb, canvas_width, canvas_height)
            r = SITE_RADIUS
            self._canvas.create_oval(cx - r, cy - r, cx + r, cy + r, fill=SITE_COLOR, outline="")

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _world_to_canvas(
        self,
        x: float,
        y: float,
        bb: BoundingBox,
        canvas_width: int,
        canvas_height: int,
    ) -> tuple[float, float]:
        """Map world coordinates to canvas pixel coordinates (y-axis flipped)."""
        draw_width = canvas_width - 2 * CANVAS_PADDING
        draw_height = canvas_height - 2 * CANVAS_PADDING

        scale_x = draw_width / bb.width if bb.width else 1.0
        scale_y = draw_height / bb.height if bb.height else 1.0
        scale = min(scale_x, scale_y)

        # Center the diagram
        offset_x = CANVAS_PADDING + (draw_width - bb.width * scale) / 2
        offset_y = CANVAS_PADDING + (draw_height - bb.height * scale) / 2

        px = offset_x + (x - bb.x_min) * scale
        py = offset_y + (bb.y_max - y) * scale
        return px, py
