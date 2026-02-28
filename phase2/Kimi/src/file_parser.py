"""
File parsing module for reading point data.

This module handles reading and parsing input files containing point coordinates.
It supports the format: x,y (one point per line).
"""

from pathlib import Path
from typing import List

from src.models import Point


class FileParserError(Exception):
    """Base exception for file parsing errors."""
    pass


class InvalidFormatError(FileParserError):
    """Raised when the file format is invalid."""
    pass


class EmptyFileError(FileParserError):
    """Raised when the file is empty or contains no valid points."""
    pass


class FileNotFoundErrorCustom(FileParserError):
    """Raised when the specified file does not exist."""
    pass


class PointFileParser:
    """
    Parser for point data files.
    
    This class handles reading and parsing files containing 2D point coordinates.
    It follows the Single Responsibility Principle by focusing solely on file parsing.
    
    Supported format:
        - One point per line: "x,y"
        - Coordinates are decimal numbers
        - Lines starting with # are treated as comments
        - Empty lines are ignored
    """
    
    COMMENT_CHAR: str = "#"
    COORDINATE_SEPARATOR: str = ","
    MIN_COORDINATES_PER_LINE: int = 2
    MAX_COORDINATES_PER_LINE: int = 2
    
    def parse(self, file_path: str) -> List[Point]:
        """
        Parse a file and extract points.
        
        Args:
            file_path: Path to the input file.
            
        Returns:
            List of parsed points.
            
        Raises:
            FileNotFoundErrorCustom: If the file does not exist.
            InvalidFormatError: If the file format is invalid.
            EmptyFileError: If the file contains no valid points.
        """
        path = Path(file_path)
        self._validate_file_exists(path)
        
        content = self._read_file(path)
        points = self._parse_content(content)
        
        if not points:
            raise EmptyFileError(
                f"File '{file_path}' contains no valid points"
            )
        
        return points
    
    def _validate_file_exists(self, path: Path) -> None:
        """
        Validate that the file exists.
        
        Args:
            path: Path to validate.
            
        Raises:
            FileNotFoundErrorCustom: If the file does not exist.
        """
        if not path.exists():
            raise FileNotFoundErrorCustom(
                f"File not found: {path}"
            )
        if not path.is_file():
            raise FileNotFoundErrorCustom(
                f"Path is not a file: {path}"
            )
    
    def _read_file(self, path: Path) -> str:
        """
        Read the file content.
        
        Args:
            path: Path to the file.
            
        Returns:
            File content as string.
            
        Raises:
            FileParserError: If reading fails.
        """
        try:
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError as e:
            raise InvalidFormatError(
                f"File encoding error: {e}"
            ) from e
        except IOError as e:
            raise FileParserError(
                f"Cannot read file: {e}"
            ) from e
    
    def _parse_content(self, content: str) -> List[Point]:
        """
        Parse file content and extract points.
        
        Args:
            content: File content as string.
            
        Returns:
            List of parsed points.
            
        Raises:
            InvalidFormatError: If a line has invalid format.
        """
        points = []
        lines = content.splitlines()
        
        for line_number, line in enumerate(lines, start=1):
            point = self._parse_line(line, line_number)
            if point is not None:
                points.append(point)
        
        return points
    
    def _parse_line(self, line: str, line_number: int) -> Point | None:
        """
        Parse a single line and return a Point or None.
        
        Args:
            line: Line content.
            line_number: Line number for error reporting.
            
        Returns:
            Point if valid, None if line should be skipped.
            
        Raises:
            InvalidFormatError: If the line format is invalid.
        """
        stripped = line.strip()
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith(self.COMMENT_CHAR):
            return None
        
        # Remove inline comments
        if self.COMMENT_CHAR in stripped:
            stripped = stripped.split(self.COMMENT_CHAR)[0].strip()
        
        return self._extract_coordinates(stripped, line_number)
    
    def _extract_coordinates(self, content: str, line_number: int) -> Point:
        """
        Extract coordinates from a line.
        
        Args:
            content: Line content (without comments).
            line_number: Line number for error reporting.
            
        Returns:
            Point with extracted coordinates.
            
        Raises:
            InvalidFormatError: If coordinates cannot be extracted.
        """
        parts = content.split(self.COORDINATE_SEPARATOR)
        
        if len(parts) < self.MIN_COORDINATES_PER_LINE:
            raise InvalidFormatError(
                f"Line {line_number}: Expected {self.MIN_COORDINATES_PER_LINE} "
                f"coordinates, found {len(parts)}"
            )
        
        if len(parts) > self.MAX_COORDINATES_PER_LINE:
            raise InvalidFormatError(
                f"Line {line_number}: Too many values. "
                f"Expected format: 'x,y'"
            )
        
        try:
            x = float(parts[0].strip())
            y = float(parts[1].strip())
        except ValueError as e:
            raise InvalidFormatError(
                f"Line {line_number}: Invalid numeric format"
            ) from e
        
        try:
            return Point(x, y)
        except (ValueError, TypeError) as e:
            raise InvalidFormatError(
                f"Line {line_number}: {e}"
            ) from e
    
    def validate_points(self, points: List[Point]) -> bool:
        """
        Validate that points can be used for Voronoi computation.
        
        Args:
            points: List of points to validate.
            
        Returns:
            True if points are valid.
            
        Raises:
            InvalidFormatError: If points are invalid.
        """
        if len(points) < 2:
            raise InvalidFormatError(
                f"At least 2 points are required, found {len(points)}"
            )
        
        # Check for duplicates
        coordinates = [(p.x, p.y) for p in points]
        if len(coordinates) != len(set(coordinates)):
            raise InvalidFormatError("Duplicate points found in input")
        
        return True
