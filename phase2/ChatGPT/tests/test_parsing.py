from pathlib import Path

import pytest

from voronoi_app.models import Point
from voronoi_app.parsing import PointFileParser


def test_Should_given_validPointFile_returnParsedPoints(tmp_path: Path) -> None:
    # Arrange
    parser = PointFileParser()
    file_path = tmp_path / "points.txt"
    file_path.write_text("1,2\n3.5,4\n", encoding="utf-8")

    # Act
    points = parser.parse_file(file_path)

    # Assert
    assert points == [Point(1.0, 2.0), Point(3.5, 4.0)]


def test_Should_given_duplicatePoint_raiseValueError(tmp_path: Path) -> None:
    # Arrange
    parser = PointFileParser()
    file_path = tmp_path / "points.txt"
    file_path.write_text("1,2\n1,2\n", encoding="utf-8")

    # Act / Assert
    with pytest.raises(ValueError, match="Duplicate points"):
        parser.parse_file(file_path)


def test_Should_given_invalidFormat_raiseValueError(tmp_path: Path) -> None:
    # Arrange
    parser = PointFileParser()
    file_path = tmp_path / "points.txt"
    file_path.write_text("1;2\n3,4\n", encoding="utf-8")

    # Act / Assert
    with pytest.raises(ValueError, match="Invalid format"):
        parser.parse_file(file_path)
