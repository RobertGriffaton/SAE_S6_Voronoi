import pytest
from unittest.mock import mock_open, patch
from src.utils.file_reader import FileReader
from src.models.point import Point

def test_should_read_points_given_valid_file():
    # Arrange
    file_content = "10.5,20.0\n30,40.1"
    expected_points = [Point(10.5, 20.0), Point(30.0, 40.1)]
    
    # Act
    with patch("builtins.open", mock_open(read_data=file_content)):
        points = FileReader.read_points("dummy_path.txt")
        
    # Assert
    assert points == expected_points

def test_should_raise_exception_given_file_not_found():
    # Arrange
    # Act & Assert
    with patch("builtins.open", side_effect=FileNotFoundError):
        with pytest.raises(FileNotFoundError):
            FileReader.read_points("non_existent.txt")

def test_should_raise_value_error_given_invalid_coordinate_format():
    # Arrange
    file_content = "10.5,20.0\ninvalid,40.1"
    
    # Act & Assert
    with patch("builtins.open", mock_open(read_data=file_content)):
        with pytest.raises(ValueError, match="Invalid coordinate format at line 2. Expected two numbers separated by a comma."):
            FileReader.read_points("dummy_path.txt")

def test_should_skip_empty_lines_given_file_with_empty_lines():
    # Arrange
    file_content = "10.5,20.0\n\n30,40.1\n"
    expected_points = [Point(10.5, 20.0), Point(30.0, 40.1)]
    
    # Act
    with patch("builtins.open", mock_open(read_data=file_content)):
        points = FileReader.read_points("dummy_path.txt")
        
    # Assert
    assert points == expected_points
