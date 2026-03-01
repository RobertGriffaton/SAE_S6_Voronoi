"""Geometric helpers for Voronoi computation."""

from __future__ import annotations

from voronoi_app.constants import BBOX_PADDING_FACTOR, EPSILON, MIN_BBOX_SIZE
from voronoi_app.models import BoundingBox, Point


def compute_bounding_box(points: list[Point]) -> BoundingBox:
    """Builds a padded bounding box around points."""
    min_x = min(point.x for point in points)
    max_x = max(point.x for point in points)
    min_y = min(point.y for point in points)
    max_y = max(point.y for point in points)

    width = max(max_x - min_x, MIN_BBOX_SIZE)
    height = max(max_y - min_y, MIN_BBOX_SIZE)

    pad_x = width * BBOX_PADDING_FACTOR
    pad_y = height * BBOX_PADDING_FACTOR

    return BoundingBox(
        min_x=min_x - pad_x,
        min_y=min_y - pad_y,
        max_x=max_x + pad_x,
        max_y=max_y + pad_y,
    )


def bounding_box_to_polygon(bbox: BoundingBox) -> list[Point]:
    """Converts a bounding box to a polygon in clockwise order."""
    return [
        Point(bbox.min_x, bbox.min_y),
        Point(bbox.max_x, bbox.min_y),
        Point(bbox.max_x, bbox.max_y),
        Point(bbox.min_x, bbox.max_y),
    ]


def clip_polygon_with_half_plane(
    polygon: list[Point],
    normal_x: float,
    normal_y: float,
    offset: float,
) -> list[Point]:
    """Clips a polygon by half-plane normal·x <= offset using Sutherland-Hodgman."""
    if not polygon:
        return []

    def is_inside(point: Point) -> bool:
        value = normal_x * point.x + normal_y * point.y
        return value <= offset + EPSILON

    def intersect_segment(start: Point, end: Point) -> Point:
        denom = normal_x * (end.x - start.x) + normal_y * (end.y - start.y)
        if abs(denom) <= EPSILON:
            return start
        t = (offset - normal_x * start.x - normal_y * start.y) / denom
        return Point(
            x=start.x + t * (end.x - start.x),
            y=start.y + t * (end.y - start.y),
        )

    result: list[Point] = []
    previous = polygon[-1]
    previous_inside = is_inside(previous)

    for current in polygon:
        current_inside = is_inside(current)

        if current_inside:
            if not previous_inside:
                result.append(intersect_segment(previous, current))
            result.append(current)
        elif previous_inside:
            result.append(intersect_segment(previous, current))

        previous = current
        previous_inside = current_inside

    return _remove_consecutive_duplicates(result)


def _remove_consecutive_duplicates(points: list[Point]) -> list[Point]:
    if not points:
        return []

    cleaned = [points[0]]
    for point in points[1:]:
        if _distance_squared(point, cleaned[-1]) > EPSILON**2:
            cleaned.append(point)

    if len(cleaned) > 1 and _distance_squared(cleaned[0], cleaned[-1]) <= EPSILON**2:
        cleaned.pop()

    return cleaned


def _distance_squared(first: Point, second: Point) -> float:
    dx = first.x - second.x
    dy = first.y - second.y
    return dx * dx + dy * dy
