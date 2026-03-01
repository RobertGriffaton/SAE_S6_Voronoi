"""Voronoi computation via half-plane intersection."""

from __future__ import annotations

from voronoi_app.algorithms.base import VoronoiAlgorithm
from voronoi_app.geometry import (
    bounding_box_to_polygon,
    clip_polygon_with_half_plane,
    compute_bounding_box,
)
from voronoi_app.models import Point


class HalfPlaneVoronoiAlgorithm(VoronoiAlgorithm):
    """Computes finite Voronoi cells by clipping with perpendicular bisector half-planes."""

    def compute_cells(self, points: list[Point]) -> dict[Point, list[Point]]:
        if len(points) < 2:
            raise ValueError("At least two points are required.")

        bbox = compute_bounding_box(points)
        initial_polygon = bounding_box_to_polygon(bbox)
        cells: dict[Point, list[Point]] = {}

        for site in points:
            polygon = initial_polygon.copy()

            for other in points:
                if other == site:
                    continue

                normal_x = other.x - site.x
                normal_y = other.y - site.y
                offset = (other.x * other.x + other.y * other.y - site.x * site.x - site.y * site.y) / 2.0

                polygon = clip_polygon_with_half_plane(
                    polygon=polygon,
                    normal_x=normal_x,
                    normal_y=normal_y,
                    offset=offset,
                )
                if not polygon:
                    break

            cells[site] = polygon

        return cells
