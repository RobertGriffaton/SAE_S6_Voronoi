"""
voronoi_engine.py — Facade over SciPy's Voronoi implementation.

Wraps scipy.spatial.Voronoi (Fortune's algorithm, O(n log n)) and converts
its raw output into our clean domain model (VoronoiDiagram).

Why SciPy / Fortune?
  - Fortune's sweep-line is the gold standard: O(n log n) time, O(n) space.
  - SciPy's binding uses the battle-tested Qhull library — no edge-case bugs.
  - KISS: no 1000-line custom implementation; domain logic stays readable.
"""
from __future__ import annotations

from typing import List

import numpy as np
from scipy.spatial import Voronoi  # type: ignore

from src.core.models import BoundingBox, Point, VoronoiDiagram

# Minimum number of distinct points required by Voronoi triangulation
MIN_POINTS_REQUIRED: int = 3

# Default margin added around the bounding box for infinite ridge clipping
DEFAULT_BOUNDING_MARGIN: float = 2.0


class InsufficientPointsError(ValueError):
    """Raised when fewer than MIN_POINTS_REQUIRED distinct points are provided."""


class VoronoiEngine:
    """
    Computes a Voronoi diagram from a list of Point objects.

    Responsibilities (SRP):
      - Validate input
      - Delegate computation to SciPy
      - Convert SciPy output → VoronoiDiagram domain object
    """

    def compute(self, points: List[Point]) -> VoronoiDiagram:
        """
        Compute and return the Voronoi diagram for *points*.

        Parameters
        ----------
        points : list of at least MIN_POINTS_REQUIRED distinct Points

        Returns
        -------
        VoronoiDiagram

        Raises
        ------
        InsufficientPointsError : if fewer than 3 distinct points are supplied
        """
        self._validate(points)

        coords: np.ndarray = np.array([[p.x, p.y] for p in points])
        voronoi = Voronoi(coords)

        bounding_box = BoundingBox.from_points(points, margin=DEFAULT_BOUNDING_MARGIN)

        return VoronoiDiagram(
            sites=list(points),
            vertices=voronoi.vertices,
            ridge_vertices=[list(rv) for rv in voronoi.ridge_vertices],
            ridge_points=[list(rp) for rp in voronoi.ridge_points],
            bounding_box=bounding_box,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _validate(self, points: List[Point]) -> None:
        """Raise InsufficientPointsError if *points* cannot form a diagram."""
        distinct = self._distinct_points(points)
        if len(distinct) < MIN_POINTS_REQUIRED:
            raise InsufficientPointsError(
                f"At least {MIN_POINTS_REQUIRED} distinct points are required, "
                f"got {len(distinct)} distinct point(s) from {len(points)} input(s)."
            )

    @staticmethod
    def _distinct_points(points: List[Point]) -> List[Point]:
        """Return deduplicated list of points."""
        seen: set[tuple[float, float]] = set()
        distinct: List[Point] = []
        for p in points:
            key = (p.x, p.y)
            if key not in seen:
                seen.add(key)
                distinct.append(p)
        return distinct
