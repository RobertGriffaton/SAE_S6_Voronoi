"""Coordinate transformation helpers for rendering."""

from __future__ import annotations

from typing import Callable

from voronoi_app.models import Point


def build_transform(
    points: list[Point],
    viewport_width: int,
    viewport_height: int,
    padding: int,
) -> Callable[[Point], tuple[float, float]]:
    """Builds a transform that maps world points into a viewport."""
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)

    width = max(max_x - min_x, 1.0)
    height = max(max_y - min_y, 1.0)

    scale_x = (viewport_width - 2 * padding) / width
    scale_y = (viewport_height - 2 * padding) / height
    scale = min(scale_x, scale_y)

    def transform(point: Point) -> tuple[float, float]:
        x = padding + (point.x - min_x) * scale
        y = viewport_height - (padding + (point.y - min_y) * scale)
        return x, y

    return transform
