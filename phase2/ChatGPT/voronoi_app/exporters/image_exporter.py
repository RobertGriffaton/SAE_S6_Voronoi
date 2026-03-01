"""Raster image export support for Voronoi diagrams."""

from __future__ import annotations

from pathlib import Path

from voronoi_app.constants import CANVAS_HEIGHT, CANVAS_WIDTH, POINT_RADIUS
from voronoi_app.rendering import build_transform
from voronoi_app.services.diagram_service import VoronoiDiagram


class ImageExporter:
    """Exports a Voronoi diagram into a PNG file using Pillow."""

    def export_png(self, diagram: VoronoiDiagram, output_file: str | Path) -> None:
        try:
            from PIL import Image, ImageDraw
        except ImportError as exception:
            raise RuntimeError("Pillow is required for PNG export. Install with: pip install Pillow") from exception

        image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), "white")
        draw = ImageDraw.Draw(image)
        transform = build_transform(
            points=diagram.sites,
            viewport_width=CANVAS_WIDTH,
            viewport_height=CANVAS_HEIGHT,
            padding=20,
        )

        for segment in diagram.segments:
            start = transform(segment.start)
            end = transform(segment.end)
            draw.line(
                [
                    start,
                    end,
                ],
                fill="black",
                width=1,
            )

        for point in diagram.sites:
            center_x, center_y = transform(point)
            draw.ellipse(
                [
                    (center_x - POINT_RADIUS, center_y - POINT_RADIUS),
                    (center_x + POINT_RADIUS, center_y + POINT_RADIUS),
                ],
                fill="red",
            )

        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, format="PNG")
