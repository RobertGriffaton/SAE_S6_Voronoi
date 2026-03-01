"""Domain models for the Voronoi application."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Point:
    """Represents a 2D point."""

    x: float
    y: float


@dataclass(frozen=True)
class Segment:
    """Represents a line segment in 2D."""

    start: Point
    end: Point


@dataclass(frozen=True)
class BoundingBox:
    """Represents an axis-aligned bounding box."""

    min_x: float
    min_y: float
    max_x: float
    max_y: float
