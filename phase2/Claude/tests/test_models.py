"""
test_models.py — Unit tests for domain data structures.

Pattern: Arrange / Act / Assert (AAA).
Naming:  Should_<expected>_given_<context>
"""
from __future__ import annotations

import math
import pytest

from src.core.models import BoundingBox, Point


class TestPoint:
    def test_Should_create_point_given_valid_integer_coordinates(self):
        # Arrange / Act
        p = Point(3, 4)
        # Assert
        assert p.x == 3
        assert p.y == 4

    def test_Should_create_point_given_valid_float_coordinates(self):
        p = Point(1.5, -2.7)
        assert p.x == pytest.approx(1.5)
        assert p.y == pytest.approx(-2.7)

    def test_Should_raise_ValueError_given_nan_x_coordinate(self):
        with pytest.raises(ValueError, match="finite"):
            Point(math.nan, 0)

    def test_Should_raise_ValueError_given_infinite_y_coordinate(self):
        with pytest.raises(ValueError, match="finite"):
            Point(0, math.inf)

    def test_Should_be_immutable_given_frozen_dataclass(self):
        p = Point(1, 2)
        with pytest.raises((AttributeError, TypeError)):
            p.x = 99  # type: ignore

    def test_Should_return_correct_numpy_array_given_point(self):
        import numpy as np
        p = Point(3.0, 5.0)
        arr = p.to_array()
        assert arr.tolist() == [3.0, 5.0]

    def test_Should_be_equal_given_same_coordinates(self):
        assert Point(1.0, 2.0) == Point(1.0, 2.0)

    def test_Should_not_be_equal_given_different_coordinates(self):
        assert Point(1.0, 2.0) != Point(1.0, 3.0)

    def test_Should_be_hashable_given_frozen_dataclass(self):
        # Can be used in a set
        points = {Point(1, 2), Point(3, 4), Point(1, 2)}
        assert len(points) == 2


class TestBoundingBox:
    def test_Should_compute_correct_dimensions_given_simple_box(self):
        bb = BoundingBox(0, 0, 10, 5)
        assert bb.width == 10
        assert bb.height == 5

    def test_Should_build_from_points_given_list_with_margin(self):
        points = [Point(1, 1), Point(4, 3), Point(2, 5)]
        margin = 1.0
        bb = BoundingBox.from_points(points, margin=margin)
        assert bb.x_min == pytest.approx(0.0)
        assert bb.y_min == pytest.approx(0.0)
        assert bb.x_max == pytest.approx(5.0)
        assert bb.y_max == pytest.approx(6.0)

    def test_Should_include_all_points_given_any_distribution(self):
        import random
        random.seed(42)
        points = [Point(random.uniform(-100, 100), random.uniform(-100, 100)) for _ in range(20)]
        bb = BoundingBox.from_points(points, margin=0)
        for p in points:
            assert bb.x_min <= p.x <= bb.x_max
            assert bb.y_min <= p.y <= bb.y_max
