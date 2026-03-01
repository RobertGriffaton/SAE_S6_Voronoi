"""SVG export support for Voronoi diagrams."""

from __future__ import annotations

from pathlib import Path

from voronoi_app.constants import POINT_RADIUS
from voronoi_app.models import Point
from voronoi_app.services.diagram_service import VoronoiDiagram


class SvgExporter:
    """Exports a Voronoi diagram into an SVG file."""

    def export(self, diagram: VoronoiDiagram, output_file: str | Path) -> None:
        if not diagram.sites:
            raise ValueError("Cannot export an empty diagram.")

        min_x, min_y, max_x, max_y = self._compute_bounds(diagram.sites)
        width = max(max_x - min_x, 1.0)
        height = max(max_y - min_y, 1.0)

        path = Path(output_file)
        path.parent.mkdir(parents=True, exist_ok=True)

        lines: list[str] = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            (
                f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x} {min_y} {width} {height}" '
                f'width="{width}" height="{height}">'
            ),
            '<rect width="100%" height="100%" fill="white"/>',
        ]

        for segment in diagram.segments:
            lines.append(
                (
                    f'<line x1="{segment.start.x}" y1="{segment.start.y}" '
                    f'x2="{segment.end.x}" y2="{segment.end.y}" '
                    'stroke="black" stroke-width="0.5"/>'
                )
            )

        for site in diagram.sites:
            lines.append(
                (
                    f'<circle cx="{site.x}" cy="{site.y}" r="{POINT_RADIUS}" '
                    'fill="red"/>'
                )
            )

        lines.append("</svg>")
        path.write_text("\n".join(lines), encoding="utf-8")

    def _compute_bounds(self, points: list[Point]) -> tuple[float, float, float, float]:
        min_x = min(point.x for point in points)
        min_y = min(point.y for point in points)
        max_x = max(point.x for point in points)
        max_y = max(point.y for point in points)
        return min_x, min_y, max_x, max_y
