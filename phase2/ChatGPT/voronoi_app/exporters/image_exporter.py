"""Raster image export support for Voronoi diagrams."""

from __future__ import annotations

from pathlib import Path

from voronoi_app.constants import CANVAS_HEIGHT, CANVAS_PADDING, CANVAS_WIDTH, EDGE_WIDTH, POINT_RADIUS
from voronoi_app.rendering import build_transform
from voronoi_app.services.diagram_service import VoronoiDiagram
from voronoi_app.theme import CANVAS_BACKGROUND_COLOR, EDGE_COLOR, SITE_COLOR, get_cell_color


class ImageExporter:
    """Exports a Voronoi diagram into a PNG file using Pillow."""

    def export_png(self, diagram: VoronoiDiagram, output_file: str | Path) -> None:
        try:
            from PIL import Image, ImageDraw
        except ImportError as exception:
            raise RuntimeError("Pillow is required for PNG export. Install with: pip install Pillow") from exception

        image = Image.new("RGB", (CANVAS_WIDTH, CANVAS_HEIGHT), CANVAS_BACKGROUND_COLOR)
        draw = ImageDraw.Draw(image)
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
            transformed_vertices = [transform(vertex) for vertex in polygon]
            draw.polygon(transformed_vertices, fill=get_cell_color(index))

        for segment in diagram.segments:
            start = transform(segment.start)
            end = transform(segment.end)
            draw.line(
                [
                    start,
                    end,
                ],
                fill=EDGE_COLOR,
                width=EDGE_WIDTH,
            )

        for point in diagram.sites:
            center_x, center_y = transform(point)
            draw.ellipse(
                [
                    (center_x - POINT_RADIUS, center_y - POINT_RADIUS),
                    (center_x + POINT_RADIUS, center_y + POINT_RADIUS),
                ],
                fill=SITE_COLOR,
                outline=EDGE_COLOR,
                width=1,
            )

        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        image.save(path, format="PNG")
