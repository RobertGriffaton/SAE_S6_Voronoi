"""Application service for Voronoi diagram generation."""

from __future__ import annotations

from dataclasses import dataclass

from voronoi_app.algorithms.base import VoronoiAlgorithm
from voronoi_app.models import Point, Segment


@dataclass(frozen=True)
class VoronoiDiagram:
    """Holds sites and polygonal cells."""

    sites: list[Point]
    cells: dict[Point, list[Point]]
    segments: list[Segment]


class VoronoiDiagramService:
    """Coordinates Voronoi algorithm usage and edge extraction."""

    def __init__(self, algorithm: VoronoiAlgorithm) -> None:
        self._algorithm = algorithm

    def build_diagram(self, points: list[Point]) -> VoronoiDiagram:
        cells = self._algorithm.compute_cells(points)
        segments = self._extract_segments(cells)
        return VoronoiDiagram(sites=points, cells=cells, segments=segments)

    def _extract_segments(self, cells: dict[Point, list[Point]]) -> list[Segment]:
        unique_segments: dict[tuple[tuple[float, float], tuple[float, float]], Segment] = {}

        for polygon in cells.values():
            if len(polygon) < 2:
                continue

            for index, start in enumerate(polygon):
                end = polygon[(index + 1) % len(polygon)]
                key = self._segment_key(start, end)
                unique_segments[key] = Segment(start=start, end=end)

        return list(unique_segments.values())

    def _segment_key(self, start: Point, end: Point) -> tuple[tuple[float, float], tuple[float, float]]:
        first = (round(start.x, 9), round(start.y, 9))
        second = (round(end.x, 9), round(end.y, 9))
        return (first, second) if first <= second else (second, first)
