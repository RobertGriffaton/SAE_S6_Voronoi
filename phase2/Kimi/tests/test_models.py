"""
Tests for the models module.

This module tests all data models including Point, VoronoiCell,
BoundingBox, and VoronoiDiagram.
"""

import math
import pytest

from src.models import Point, VoronoiCell, BoundingBox, VoronoiDiagram


class TestPoint:
    """Tests for the Point class."""
    
    def test_should_create_point_given_valid_coordinates(self) -> None:
        """Should create a Point when given valid coordinates."""
        # Arrange & Act
        point = Point(3.5, 4.2)
        
        # Assert
        assert point.x == 3.5
        assert point.y == 4.2
    
    def test_should_create_point_given_integer_coordinates(self) -> None:
        """Should create a Point when given integer coordinates."""
        # Arrange & Act
        point = Point(5, 10)
        
        # Assert
        assert point.x == 5.0
        assert point.y == 10.0
    
    def test_should_create_point_given_negative_coordinates(self) -> None:
        """Should create a Point when given negative coordinates."""
        # Arrange & Act
        point = Point(-3.5, -4.2)
        
        # Assert
        assert point.x == -3.5
        assert point.y == -4.2
    
    def test_should_raise_error_given_non_numeric_x(self) -> None:
        """Should raise TypeError when given non-numeric x coordinate."""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            Point("invalid", 4.2)
    
    def test_should_raise_error_given_non_numeric_y(self) -> None:
        """Should raise TypeError when given non-numeric y coordinate."""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            Point(3.5, "invalid")
    
    def test_should_raise_error_given_infinite_x(self) -> None:
        """Should raise ValueError when given infinite x coordinate."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            Point(float('inf'), 4.2)
    
    def test_should_raise_error_given_nan_coordinate(self) -> None:
        """Should raise ValueError when given NaN coordinate."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            Point(float('nan'), 4.2)
    
    def test_should_return_tuple_given_valid_point(self) -> None:
        """Should return tuple when converting valid point."""
        # Arrange
        point = Point(3.5, 4.2)
        
        # Act
        result = point.to_tuple()
        
        # Assert
        assert result == (3.5, 4.2)
    
    def test_should_calculate_distance_given_two_points(self) -> None:
        """Should calculate correct distance given two points."""
        # Arrange
        point1 = Point(0, 0)
        point2 = Point(3, 4)
        
        # Act
        distance = point1.distance_to(point2)
        
        # Assert
        assert distance == 5.0
    
    def test_should_return_zero_distance_given_same_point(self) -> None:
        """Should return zero distance when comparing point to itself."""
        # Arrange
        point = Point(3.5, 4.2)
        
        # Act
        distance = point.distance_to(point)
        
        # Assert
        assert distance == 0.0


class TestBoundingBox:
    """Tests for the BoundingBox class."""
    
    def test_should_create_bbox_given_valid_coordinates(self) -> None:
        """Should create BoundingBox when given valid coordinates."""
        # Arrange & Act
        bbox = BoundingBox(0, 10, 0, 5)
        
        # Assert
        assert bbox.min_x == 0
        assert bbox.max_x == 10
        assert bbox.min_y == 0
        assert bbox.max_y == 5
    
    def test_should_raise_error_given_invalid_x_range(self) -> None:
        """Should raise ValueError when min_x >= max_x."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            BoundingBox(10, 10, 0, 5)
    
    def test_should_raise_error_given_invalid_y_range(self) -> None:
        """Should raise ValueError when min_y >= max_y."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            BoundingBox(0, 10, 5, 5)
    
    def test_should_calculate_width_given_valid_bbox(self) -> None:
        """Should calculate correct width given valid bbox."""
        # Arrange
        bbox = BoundingBox(2, 8, 0, 5)
        
        # Act
        width = bbox.width
        
        # Assert
        assert width == 6
    
    def test_should_calculate_height_given_valid_bbox(self) -> None:
        """Should calculate correct height given valid bbox."""
        # Arrange
        bbox = BoundingBox(0, 10, 1, 6)
        
        # Act
        height = bbox.height
        
        # Assert
        assert height == 5
    
    def test_should_return_center_given_valid_bbox(self) -> None:
        """Should return correct center point given valid bbox."""
        # Arrange
        bbox = BoundingBox(0, 10, 0, 6)
        
        # Act
        center = bbox.center
        
        # Assert
        assert center.x == 5
        assert center.y == 3
    
    def test_should_contain_point_given_point_inside(self) -> None:
        """Should return True when checking point inside bbox."""
        # Arrange
        bbox = BoundingBox(0, 10, 0, 10)
        point = Point(5, 5)
        
        # Act
        result = bbox.contains(point)
        
        # Assert
        assert result is True
    
    def test_should_not_contain_point_given_point_outside(self) -> None:
        """Should return False when checking point outside bbox."""
        # Arrange
        bbox = BoundingBox(0, 10, 0, 10)
        point = Point(15, 5)
        
        # Act
        result = bbox.contains(point)
        
        # Assert
        assert result is False
    
    def test_should_contain_point_given_point_on_boundary(self) -> None:
        """Should return True when checking point on boundary."""
        # Arrange
        bbox = BoundingBox(0, 10, 0, 10)
        point = Point(0, 5)
        
        # Act
        result = bbox.contains(point)
        
        # Assert
        assert result is True
    
    def test_should_add_margin_given_bbox(self) -> None:
        """Should add margin when requested."""
        # Arrange
        bbox = BoundingBox(0, 10, 0, 10)
        
        # Act
        expanded = bbox.with_margin(0.1)
        
        # Assert
        assert expanded.min_x < 0
        assert expanded.max_x > 10
        assert expanded.min_y < 0
        assert expanded.max_y > 10
    
    def test_should_create_from_points_given_valid_list(self) -> None:
        """Should create bbox from points when given valid list."""
        # Arrange
        points = [Point(1, 2), Point(5, 8), Point(3, 1)]
        
        # Act
        bbox = BoundingBox.from_points(points)
        
        # Assert
        assert bbox.min_x <= 1
        assert bbox.max_x >= 5
        assert bbox.min_y <= 1
        assert bbox.max_y >= 8
    
    def test_should_raise_error_given_empty_list(self) -> None:
        """Should raise ValueError when given empty point list."""
        # Arrange & Act & Assert
        with pytest.raises(ValueError):
            BoundingBox.from_points([])


class TestVoronoiCell:
    """Tests for the VoronoiCell class."""
    
    def test_should_create_cell_given_valid_data(self) -> None:
        """Should create VoronoiCell when given valid data."""
        # Arrange
        seed = Point(0, 0)
        vertices = [Point(0, 1), Point(1, 0), Point(-1, 0)]
        
        # Act
        cell = VoronoiCell(seed, vertices, 0)
        
        # Assert
        assert cell.seed == seed
        assert len(cell.vertices) == 3
        assert cell.region_index == 0
    
    def test_should_raise_error_given_invalid_seed(self) -> None:
        """Should raise TypeError when given invalid seed."""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            VoronoiCell("invalid", [], 0)
    
    def test_should_raise_error_given_invalid_vertices(self) -> None:
        """Should raise TypeError when given invalid vertices."""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            VoronoiCell(Point(0, 0), "invalid", 0)
    
    def test_should_be_bounded_given_sufficient_vertices(self) -> None:
        """Should return True for bounded when given 3+ vertices."""
        # Arrange
        cell = VoronoiCell(
            Point(0, 0),
            [Point(0, 1), Point(1, 0), Point(-1, 0)],
            0
        )
        
        # Act
        result = cell.is_bounded()
        
        # Assert
        assert result is True
    
    def test_should_not_be_bounded_given_insufficient_vertices(self) -> None:
        """Should return False for bounded when given <3 vertices."""
        # Arrange
        cell = VoronoiCell(Point(0, 0), [Point(0, 1)], 0)
        
        # Act
        result = cell.is_bounded()
        
        # Assert
        assert result is False
    
    def test_should_calculate_area_given_triangle(self) -> None:
        """Should calculate correct area given triangular cell."""
        # Arrange
        cell = VoronoiCell(
            Point(0, 0),
            [Point(0, 0), Point(4, 0), Point(0, 3)],
            0
        )
        
        # Act
        area = cell.get_area()
        
        # Assert
        assert area == 6.0
    
    def test_should_return_zero_area_given_unbounded(self) -> None:
        """Should return zero area when cell is unbounded."""
        # Arrange
        cell = VoronoiCell(Point(0, 0), [], 0)
        
        # Act
        area = cell.get_area()
        
        # Assert
        assert area == 0.0


class TestVoronoiDiagram:
    """Tests for the VoronoiDiagram class."""
    
    def test_should_create_diagram_given_valid_data(self) -> None:
        """Should create VoronoiDiagram when given valid data."""
        # Arrange
        seed = Point(0, 0)
        cell = VoronoiCell(seed, [Point(0, 1), Point(1, 0), Point(-1, 0)], 0)
        bbox = BoundingBox(-2, 2, -2, 2)
        
        # Act
        diagram = VoronoiDiagram([cell], bbox, [seed])
        
        # Assert
        assert len(diagram.cells) == 1
        assert diagram.bounding_box == bbox
        assert len(diagram.seed_points) == 1
    
    def test_should_raise_error_given_cell_count_mismatch(self) -> None:
        """Should raise ValueError when cell count != seed count."""
        # Arrange
        bbox = BoundingBox(-2, 2, -2, 2)
        
        # Act & Assert
        with pytest.raises(ValueError):
            VoronoiDiagram([], bbox, [Point(0, 0)])
    
    def test_should_get_bounded_cells_given_mixed_cells(self) -> None:
        """Should return only bounded cells when given mixed cells."""
        # Arrange
        bbox = BoundingBox(-2, 2, -2, 2)
        bounded = VoronoiCell(
            Point(0, 0),
            [Point(0, 1), Point(1, 0), Point(-1, 0)],
            0
        )
        unbounded = VoronoiCell(Point(1, 1), [], 1)
        
        # Act
        diagram = VoronoiDiagram([bounded, unbounded], bbox, [Point(0, 0), Point(1, 1)])
        bounded_cells = diagram.get_bounded_cells()
        
        # Assert
        assert len(bounded_cells) == 1
        assert bounded_cells[0] == bounded
    
    def test_should_find_cell_at_point_given_point_inside(self) -> None:
        """Should find cell when given point inside a cell."""
        # Arrange
        bbox = BoundingBox(-2, 2, -2, 2)
        cell = VoronoiCell(
            Point(0, 0),
            [Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)],
            0
        )
        diagram = VoronoiDiagram([cell], bbox, [Point(0, 0)])
        
        # Act
        found = diagram.get_cell_at(Point(0, 0))
        
        # Assert
        assert found is not None
        assert found.seed == Point(0, 0)
    
    def test_should_not_find_cell_given_point_outside(self) -> None:
        """Should return None when given point outside all cells."""
        # Arrange
        bbox = BoundingBox(-2, 2, -2, 2)
        cell = VoronoiCell(
            Point(0, 0),
            [Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)],
            0
        )
        diagram = VoronoiDiagram([cell], bbox, [Point(0, 0)])
        
        # Act
        found = diagram.get_cell_at(Point(5, 5))
        
        # Assert
        assert found is None
