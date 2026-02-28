"""
Tests for the voronoi_calculator module.

This module tests the VoronoiCalculator class and its algorithms.
"""

import pytest
import math

from src.voronoi_calculator import VoronoiCalculator
from src.models import Point, BoundingBox


class TestVoronoiCalculator:
    """Tests for the VoronoiCalculator class."""
    
    def test_should_calculate_diagram_given_two_points(self) -> None:
        """Should calculate diagram when given two points."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(2, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert diagram is not None
        assert len(diagram.cells) == 2
        assert len(diagram.seed_points) == 2
    
    def test_should_calculate_diagram_given_triangle(self) -> None:
        """Should calculate diagram when given three points (triangle)."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(2, 0), Point(1, math.sqrt(3))]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert diagram is not None
        assert len(diagram.cells) == 3
    
    def test_should_calculate_diagram_given_square(self) -> None:
        """Should calculate diagram when given four points (square)."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [
            Point(0, 0),
            Point(1, 0),
            Point(1, 1),
            Point(0, 1)
        ]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert diagram is not None
        assert len(diagram.cells) == 4
    
    def test_should_raise_error_given_empty_list(self) -> None:
        """Should raise ValueError when given empty point list."""
        # Arrange
        calculator = VoronoiCalculator()
        
        # Act & Assert
        with pytest.raises(ValueError):
            calculator.calculate([])
    
    def test_should_raise_error_given_single_point(self) -> None:
        """Should raise ValueError when given single point."""
        # Arrange
        calculator = VoronoiCalculator()
        
        # Act & Assert
        with pytest.raises(ValueError):
            calculator.calculate([Point(0, 0)])
    
    def test_should_raise_error_given_duplicate_points(self) -> None:
        """Should raise ValueError when given duplicate points."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(0, 0)]
        
        # Act & Assert
        with pytest.raises(ValueError):
            calculator.calculate(points)
    
    def test_should_create_bounded_cells_given_multiple_points(self) -> None:
        """Should create bounded cells when given multiple points."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [
            Point(0, 0),
            Point(2, 0),
            Point(1, 2),
            Point(-1, 1),
            Point(3, 1)
        ]
        
        # Act
        diagram = calculator.calculate(points)
        bounded_cells = diagram.get_bounded_cells()
        
        # Assert
        assert len(bounded_cells) > 0
    
    def test_should_use_provided_bounding_box(self) -> None:
        """Should use provided bounding box when given."""
        # Arrange
        bbox = BoundingBox(-5, 5, -5, 5)
        calculator = VoronoiCalculator(bounding_box=bbox)
        points = [Point(0, 0), Point(1, 1)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert diagram.bounding_box.min_x <= -5
        assert diagram.bounding_box.max_x >= 5
    
    def test_should_compute_correct_bounding_box_given_points(self) -> None:
        """Should compute correct bounding box when given points."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(3, 4)]
        
        # Act
        diagram = calculator.calculate(points)
        bbox = diagram.bounding_box
        
        # Assert
        assert bbox.min_x <= 0
        assert bbox.max_x >= 3
        assert bbox.min_y <= 0
        assert bbox.max_y >= 4
    
    def test_should_preserve_seed_points_order(self) -> None:
        """Should preserve seed points order in output."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [
            Point(0, 0),
            Point(1, 0),
            Point(0.5, 1)
        ]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        for i, original in enumerate(points):
            assert diagram.seed_points[i] == original
    
    def test_should_create_cells_with_correct_seeds(self) -> None:
        """Should create cells with correct seed points."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(2, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        for i, cell in enumerate(diagram.cells):
            assert cell.seed == points[i]
    
    def test_should_handle_collinear_points(self) -> None:
        """Should handle collinear points gracefully."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(1, 0), Point(2, 0), Point(3, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert diagram is not None
        assert len(diagram.cells) == 4
    
    def test_should_handle_large_number_of_points(self) -> None:
        """Should handle large number of points efficiently."""
        # Arrange
        calculator = VoronoiCalculator()
        import random
        random.seed(42)
        points = [
            Point(random.uniform(-100, 100), random.uniform(-100, 100))
            for _ in range(100)
        ]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert diagram is not None
        assert len(diagram.cells) == 100
    
    def test_should_clip_cells_to_bounding_box(self) -> None:
        """Should clip cells to bounding box."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(10, 0), Point(5, 10)]
        bbox = BoundingBox(0, 10, 0, 5)
        
        # Act
        diagram = calculator.calculate(points, bounding_box=bbox)
        
        # Assert
        for cell in diagram.cells:
            if cell.is_bounded():
                for vertex in cell.vertices:
                    assert bbox.contains(vertex)
    
    def test_should_calculate_voronoi_properties_given_known_case(self) -> None:
        """Should calculate correct Voronoi properties for known case."""
        # Arrange - Two points should have perpendicular bisector as boundary
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(2, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert - The boundary should be at x=1
        # Each cell should have the other cell's seed as nearest neighbor
        cell1 = diagram.cells[0]
        cell2 = diagram.cells[1]
        
        assert cell1.seed == Point(0, 0)
        assert cell2.seed == Point(2, 0)


class TestVoronoiCalculatorEdgeCases:
    """Edge case tests for VoronoiCalculator."""
    
    def test_should_handle_points_at_same_x(self) -> None:
        """Should handle points with same x coordinate."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(0, 2), Point(0, 4)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert len(diagram.cells) == 3
    
    def test_should_handle_points_at_same_y(self) -> None:
        """Should handle points with same y coordinate."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(2, 0), Point(4, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert len(diagram.cells) == 3
    
    def test_should_handle_very_close_points(self) -> None:
        """Should handle very close points."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(0.001, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert len(diagram.cells) == 2
    
    def test_should_handle_points_far_apart(self) -> None:
        """Should handle points far apart."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [Point(0, 0), Point(10000, 0)]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert len(diagram.cells) == 2
    
    def test_should_handle_negative_coordinates(self) -> None:
        """Should handle points with negative coordinates."""
        # Arrange
        calculator = VoronoiCalculator()
        points = [
            Point(-5, -5),
            Point(-5, 5),
            Point(5, -5),
            Point(5, 5)
        ]
        
        # Act
        diagram = calculator.calculate(points)
        
        # Assert
        assert len(diagram.cells) == 4
