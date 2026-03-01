"""Strategy interface for Voronoi algorithms."""

from __future__ import annotations

from abc import ABC, abstractmethod

from voronoi_app.models import Point


class VoronoiAlgorithm(ABC):
    """Strategy interface for Voronoi computation."""

    @abstractmethod
    def compute_cells(self, points: list[Point]) -> dict[Point, list[Point]]:
        """Returns polygons for each Voronoi site."""
