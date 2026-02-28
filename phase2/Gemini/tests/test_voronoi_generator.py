import pytest
from src.models.point import Point
from src.services.voronoi_generator import VoronoiGenerator

def test_should_generate_voronoi_given_valid_points():
    # Arrange
    points = [Point(0, 0), Point(0, 1), Point(1, 0), Point(1, 1)]
    
    # Act
    result = VoronoiGenerator.generate(points)
    
    # Assert
    assert len(result.vertices) > 0
    assert len(result.regions) > 0
    assert len(result.point_region) == 4

def test_should_raise_value_error_given_too_few_points():
    # Arrange
    points = [Point(0, 0), Point(1, 1)]
    
    # Act & Assert
    with pytest.raises(ValueError, match="At least 3 points are required to generate a Voronoi diagram."):
        VoronoiGenerator.generate(points)

def test_should_raise_value_error_given_collinear_points():
    # Arrange
    points = [Point(0, 0), Point(1, 1), Point(2, 2)]
    
    # Act & Assert
    with pytest.raises(ValueError, match="Could not generate Voronoi diagram. Points might be collinear or coincident."):
        VoronoiGenerator.generate(points)
