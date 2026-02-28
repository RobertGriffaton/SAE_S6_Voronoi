import os
import pytest
from src.models.point import Point
from src.models.voronoi_result import VoronoiResult
from src.services.export_strategy import SvgExportStrategy, ImageExportStrategy

@pytest.fixture
def mock_voronoi():
    vertices = [Point(10, 10), Point(20, 10), Point(20, 20), Point(10, 20)]
    # One finite square region and one infinite region
    regions = [[0, 1, 2, 3], [-1, 0, 1]]
    point_region = [0]
    return VoronoiResult(vertices=vertices, regions=regions, point_region=point_region)

def test_should_export_svg_given_valid_voronoi(mock_voronoi, tmp_path):
    # Arrange
    strategy = SvgExportStrategy()
    file_path = tmp_path / "test.svg"
    
    # Act
    strategy.export(mock_voronoi, str(file_path))
    
    # Assert
    assert file_path.exists()
    content = file_path.read_text(encoding="utf-8")
    assert "<svg" in content
    assert "<polygon" in content
    # Should have stroke black
    assert "stroke=\"black\"" in content

def test_should_export_image_given_valid_voronoi(mock_voronoi, tmp_path):
    # Arrange
    strategy = ImageExportStrategy()
    file_path = tmp_path / "test.png"
    
    # Act
    strategy.export(mock_voronoi, str(file_path))
    
    # Assert
    assert file_path.exists()
    assert os.path.getsize(str(file_path)) > 0
