"""
Tests for the file_parser module.

This module tests the PointFileParser class and its error handling.
"""

import pytest
import tempfile
from pathlib import Path

from src.file_parser import (
    PointFileParser,
    FileParserError,
    InvalidFormatError,
    EmptyFileError,
    FileNotFoundErrorCustom
)
from src.models import Point


class TestPointFileParser:
    """Tests for the PointFileParser class."""
    
    def test_should_parse_file_given_valid_points(self) -> None:
        """Should parse file when given valid point data."""
        # Arrange
        parser = PointFileParser()
        content = "1.0,2.0\n3.0,4.0\n5.0,6.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 3
            assert points[0] == Point(1.0, 2.0)
            assert points[1] == Point(3.0, 4.0)
            assert points[2] == Point(5.0, 6.0)
        finally:
            Path(temp_path).unlink()
    
    def test_should_parse_file_given_whitespace(self) -> None:
        """Should parse file when given whitespace around coordinates."""
        # Arrange
        parser = PointFileParser()
        content = "  1.0  ,  2.0  \n  3.0  ,  4.0  "
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 2
            assert points[0] == Point(1.0, 2.0)
        finally:
            Path(temp_path).unlink()
    
    def test_should_parse_file_given_comments(self) -> None:
        """Should parse file when given comment lines."""
        # Arrange
        parser = PointFileParser()
        content = "# This is a comment\n1.0,2.0\n# Another comment\n3.0,4.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 2
        finally:
            Path(temp_path).unlink()
    
    def test_should_parse_file_given_inline_comments(self) -> None:
        """Should parse file when given inline comments."""
        # Arrange
        parser = PointFileParser()
        content = "1.0,2.0 # inline comment\n3.0,4.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 2
            assert points[0] == Point(1.0, 2.0)
        finally:
            Path(temp_path).unlink()
    
    def test_should_parse_file_given_empty_lines(self) -> None:
        """Should parse file when given empty lines."""
        # Arrange
        parser = PointFileParser()
        content = "1.0,2.0\n\n3.0,4.0\n\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 2
        finally:
            Path(temp_path).unlink()
    
    def test_should_raise_error_given_nonexistent_file(self) -> None:
        """Should raise FileNotFoundErrorCustom when given nonexistent file."""
        # Arrange
        parser = PointFileParser()
        nonexistent_path = "/path/that/does/not/exist.txt"
        
        # Act & Assert
        with pytest.raises(FileNotFoundErrorCustom):
            parser.parse(nonexistent_path)
    
    def test_should_raise_error_given_empty_file(self) -> None:
        """Should raise EmptyFileError when given empty file."""
        # Arrange
        parser = PointFileParser()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            # Act & Assert
            with pytest.raises(EmptyFileError):
                parser.parse(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_should_raise_error_given_file_with_only_comments(self) -> None:
        """Should raise EmptyFileError when given file with only comments."""
        # Arrange
        parser = PointFileParser()
        content = "# Comment 1\n# Comment 2\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act & Assert
            with pytest.raises(EmptyFileError):
                parser.parse(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_should_raise_error_given_missing_y_coordinate(self) -> None:
        """Should raise InvalidFormatError when given missing y coordinate."""
        # Arrange
        parser = PointFileParser()
        content = "1.0,2.0\n3.0\n5.0,6.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act & Assert
            with pytest.raises(InvalidFormatError) as exc_info:
                parser.parse(temp_path)
            assert "line 2" in str(exc_info.value).lower()
        finally:
            Path(temp_path).unlink()
    
    def test_should_raise_error_given_too_many_values(self) -> None:
        """Should raise InvalidFormatError when given too many values."""
        # Arrange
        parser = PointFileParser()
        content = "1.0,2.0,3.0\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act & Assert
            with pytest.raises(InvalidFormatError):
                parser.parse(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_should_raise_error_given_invalid_number(self) -> None:
        """Should raise InvalidFormatError when given invalid number format."""
        # Arrange
        parser = PointFileParser()
        content = "1.0,not_a_number\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act & Assert
            with pytest.raises(InvalidFormatError):
                parser.parse(temp_path)
        finally:
            Path(temp_path).unlink()
    
    def test_should_validate_points_given_valid_list(self) -> None:
        """Should validate successfully when given valid point list."""
        # Arrange
        parser = PointFileParser()
        points = [Point(0, 0), Point(1, 1), Point(2, 2)]
        
        # Act
        result = parser.validate_points(points)
        
        # Assert
        assert result is True
    
    def test_should_raise_error_given_insufficient_points(self) -> None:
        """Should raise InvalidFormatError when given insufficient points."""
        # Arrange
        parser = PointFileParser()
        points = [Point(0, 0)]
        
        # Act & Assert
        with pytest.raises(InvalidFormatError):
            parser.validate_points(points)
    
    def test_should_raise_error_given_duplicate_points(self) -> None:
        """Should raise InvalidFormatError when given duplicate points."""
        # Arrange
        parser = PointFileParser()
        points = [Point(0, 0), Point(1, 1), Point(0, 0)]
        
        # Act & Assert
        with pytest.raises(InvalidFormatError):
            parser.validate_points(points)
    
    def test_should_parse_file_given_negative_coordinates(self) -> None:
        """Should parse file when given negative coordinates."""
        # Arrange
        parser = PointFileParser()
        content = "-1.5,-2.5\n3.0,-4.0\n-5.0,6.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 3
            assert points[0] == Point(-1.5, -2.5)
            assert points[1] == Point(3.0, -4.0)
            assert points[2] == Point(-5.0, 6.0)
        finally:
            Path(temp_path).unlink()
    
    def test_should_parse_file_given_scientific_notation(self) -> None:
        """Should parse file when given scientific notation."""
        # Arrange
        parser = PointFileParser()
        content = "1.5e2,2.5e-1\n3.0E3,4.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_path = f.name
        
        try:
            # Act
            points = parser.parse(temp_path)
            
            # Assert
            assert len(points) == 2
            assert points[0].x == 150.0
            assert points[0].y == 0.25
        finally:
            Path(temp_path).unlink()
