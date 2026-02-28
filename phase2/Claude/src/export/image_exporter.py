"""
image_exporter.py — Exports a VoronoiDiagram to a PNG image using Pillow.

Concrete Strategy implementation.  Uses the same coordinate-mapping logic
as SVGExporter but draws via PIL's ImageDraw.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw  # type: ignore

from src.core.models import BoundingBox, VoronoiDiagram
from src.export.exporter_base import DiagramExporter
from src.export.svg_exporter import SVGExporter  # reuse ridge computation

# Visual constants
IMAGE_BACKGROUND_COLOR: Tuple[int, int, int] = (255, 255, 255)
RIDGE_COLOR_RGB: Tuple[int, int, int] = (58, 123, 213)
SITE_COLOR_RGB: Tuple[int, int, int] = (231, 76, 60)
SITE_RADIUS_PX: int = 4
RIDGE_WIDTH_PX: int = 1
IMAGE_SCALE: float = 4.0   # world units → pixels
VIEWPORT_PADDING_PX: int = 20


class ImageExporter(DiagramExporter):
    """Concrete Strategy: writes Voronoi diagram as a PNG image."""

    def __init__(self) -> None:
        # Reuse SVGExporter's ridge-clipping logic via composition
        self._ridge_helper = SVGExporter()

    @property
    def file_extension(self) -> str:
        return ".png"

    def export(self, diagram: VoronoiDiagram, output_path: Path) -> None:
        bb = diagram.bounding_box
        img_width = int(bb.width * IMAGE_SCALE) + 2 * VIEWPORT_PADDING_PX
        img_height = int(bb.height * IMAGE_SCALE) + 2 * VIEWPORT_PADDING_PX

        image = Image.new("RGB", (img_width, img_height), IMAGE_BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)

        # Draw ridges
        for rv, rp in zip(diagram.ridge_vertices, diagram.ridge_points):
            segment = self._ridge_helper._compute_ridge_segment(rv, rp, diagram)
            if segment is None:
                continue
            p1, p2 = segment
            x1, y1 = self._to_px(p1[0], p1[1], bb)
            x2, y2 = self._to_px(p2[0], p2[1], bb)
            draw.line([(x1, y1), (x2, y2)], fill=RIDGE_COLOR_RGB, width=RIDGE_WIDTH_PX)

        # Draw site markers
        for site in diagram.sites:
            cx, cy = self._to_px(site.x, site.y, bb)
            r = SITE_RADIUS_PX
            draw.ellipse([(cx - r, cy - r), (cx + r, cy + r)], fill=SITE_COLOR_RGB)

        image.save(str(output_path), format="PNG")

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _to_px(self, x: float, y: float, bb: BoundingBox) -> Tuple[int, int]:
        """Map world coordinates to pixel coordinates."""
        px = int((x - bb.x_min) * IMAGE_SCALE) + VIEWPORT_PADDING_PX
        py = int((bb.y_max - y) * IMAGE_SCALE) + VIEWPORT_PADDING_PX
        return px, py
