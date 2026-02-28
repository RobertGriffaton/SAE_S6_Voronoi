"""
test_voronoi_engine.py — Unit tests for VoronoiEngine.

Pattern: Arrange / Act / Assert (AAA).
Naming:  Should_<expected>_given_<context>
"""
from __future__ import annotations

import pytest

from src.core.models import Point, VoronoiDiagram
from src.core.voronoi_engine import InsufficientPointsError, VoronoiEngine


@pytest.fixture
def engine() -> VoronoiEngine:
    return VoronoiEngine()


class TestVoronoiEngine:

    def test_Should_return_VoronoiDiagram_given_four_valid_points(
        self, engine, four_cardinal_points
    ):
        # Act
        diagram = engine.compute(four_cardinal_points)
        # Assert
        assert isinstance(diagram, VoronoiDiagram)

    def test_Should_preserve_all_sites_given_input_points(
        self, engine, four_cardinal_points
    ):
        diagram = engine.compute(four_cardinal_points)
        assert diagram.sites == four_cardinal_points

    def test_Should_produce_vertices_given_valid_input(
        self, engine, four_cardinal_points
    ):
        diagram = engine.compute(four_cardinal_points)
        assert len(diagram.vertices) > 0

    def test_Should_produce_ridges_given_valid_input(
        self, engine, four_cardinal_points
    ):
        diagram = engine.compute(four_cardinal_points)
        assert len(diagram.ridge_vertices) > 0
        assert len(diagram.ridge_points) == len(diagram.ridge_vertices)

    def test_Should_raise_InsufficientPointsError_given_only_two_distinct_points(
        self, engine
    ):
        # Arrange
        points = [Point(0, 0), Point(1, 1)]
        # Act / Assert
        with pytest.raises(InsufficientPointsError):
            engine.compute(points)

    def test_Should_raise_InsufficientPointsError_given_empty_list(self, engine):
        with pytest.raises(InsufficientPointsError):
            engine.compute([])

    def test_Should_raise_InsufficientPointsError_given_duplicate_points_below_minimum(
        self, engine
    ):
        # Three entries but only 2 distinct
        points = [Point(0, 0), Point(1, 1), Point(0, 0)]
        with pytest.raises(InsufficientPointsError):
            engine.compute(points)

    def test_Should_compute_diagram_given_duplicate_points_above_minimum(self, engine):
        # Four distinct (after dedup) out of five entries → should succeed
        points = [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1), Point(0, 0)]
        diagram = engine.compute(points)
        assert isinstance(diagram, VoronoiDiagram)

    def test_Should_produce_correct_bounding_box_given_known_points(
        self, engine, four_cardinal_points
    ):
        diagram = engine.compute(four_cardinal_points)
        bb = diagram.bounding_box
        # All sites must lie inside the bounding box
        for site in four_cardinal_points:
            assert bb.x_min <= site.x <= bb.x_max
            assert bb.y_min <= site.y <= bb.y_max

    def test_Should_handle_large_point_set_given_100_random_points(self, engine):
        import random
        random.seed(0)
        points = [Point(random.uniform(0, 100), random.uniform(0, 100)) for _ in range(100)]
        diagram = engine.compute(points)
        assert len(diagram.sites) == 100

    def test_Should_handle_collinear_points_given_three_collinear_points(self, engine):
        """SciPy can handle collinear points without crashing."""
        points = [Point(0, 0), Point(1, 0), Point(2, 0), Point(0, 1)]
        diagram = engine.compute(points)
        assert isinstance(diagram, VoronoiDiagram)
