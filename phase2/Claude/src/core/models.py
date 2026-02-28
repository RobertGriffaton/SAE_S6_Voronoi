"""
models.py — Immutable domain data structures.

Using dataclasses for clean, typed, value-object semantics.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np


@dataclass(frozen=True)
class Point:
    """A 2-D point with floating-point coordinates."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not (np.isfinite(self.x) and np.isfinite(self.y)):
            raise ValueError(f"Point coordinates must be finite numbers, got ({self.x}, {self.y})")

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y])

    def __repr__(self) -> str:
        return f"Point({self.x}, {self.y})"


@dataclass(frozen=True)
class BoundingBox:
    """Axis-aligned bounding box used for clipping infinite Voronoi ridges."""

    x_min: float
    y_min: float
    x_max: float
    y_max: float

    @classmethod
    def from_points(cls, points: List[Point], margin: float = 1.0) -> "BoundingBox":
        """Build a bounding box that contains all given points, with extra margin."""
        xs = [p.x for p in points]
        ys = [p.y for p in points]
        return cls(
            x_min=min(xs) - margin,
            y_min=min(ys) - margin,
            x_max=max(xs) + margin,
            y_max=max(ys) + margin,
        )

    @property
    def width(self) -> float:
        return self.x_max - self.x_min

    @property
    def height(self) -> float:
        return self.y_max - self.y_min


@dataclass
class VoronoiDiagram:
    """
    Holds the result of a Voronoi computation.

    Attributes
    ----------
    sites : original input points (generators)
    vertices : Voronoi vertex coordinates
    ridge_vertices : pairs of vertex indices forming each ridge
                     (-1 means the ridge extends to infinity)
    ridge_points : pairs of site indices on each side of a ridge
    bounding_box : the clipping region used for rendering
    """

    sites: List[Point]
    vertices: np.ndarray                   # shape (V, 2)
    ridge_vertices: List[List[int]]        # list of [i, j] pairs
    ridge_points: List[List[int]]          # list of [p, q] pairs
    bounding_box: BoundingBox
