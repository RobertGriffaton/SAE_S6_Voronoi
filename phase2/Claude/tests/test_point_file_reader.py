"""
test_point_file_reader.py — Unit tests for PointFileReader.

Pattern: Arrange / Act / Assert (AAA).
Naming:  Should_<expected>_given_<context>
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.core.models import Point
from src.io.point_file_reader import PointFileReader, PointParseError


@pytest.fixture
def reader() -> PointFileReader:
    return PointFileReader()


class TestPointFileReader:

    def test_Should_return_correct_points_given_valid_file(self, reader, valid_points_file):
        # Act
        points = reader.read(valid_points_file)
        # Assert
        assert len(points) == 5
        assert points[0] == Point(2.0, 4.0)
        assert points[1] == Point(5.3, 4.5)

    def test_Should_skip_blank_lines_and_comments_given_mixed_file(
        self, reader, file_with_blank_and_comment_lines
    ):
        points = reader.read(file_with_blank_and_comment_lines)
        assert len(points) == 3
        assert points[0] == Point(1.0, 2.0)

    def test_Should_raise_FileNotFoundError_given_nonexistent_path(self, reader, tmp_path):
        with pytest.raises(FileNotFoundError):
            reader.read(tmp_path / "does_not_exist.txt")

    def test_Should_raise_PointParseError_given_malformed_line(
        self, reader, file_with_malformed_line
    ):
        with pytest.raises(PointParseError, match="Line 3"):
            reader.read(file_with_malformed_line)

    def test_Should_raise_ValueError_given_empty_file(self, reader, empty_file):
        with pytest.raises(ValueError, match="No valid points"):
            reader.read(empty_file)

    def test_Should_raise_ValueError_given_file_with_only_comments(
        self, reader, file_only_comments
    ):
        with pytest.raises(ValueError, match="No valid points"):
            reader.read(file_only_comments)

    def test_Should_parse_integer_coordinates_given_no_decimal_points(
        self, reader, tmp_path
    ):
        f = tmp_path / "ints.txt"
        f.write_text("10,20\n30,40\n")
        points = reader.read(f)
        assert points == [Point(10.0, 20.0), Point(30.0, 40.0)]

    def test_Should_parse_negative_coordinates_given_negative_values(
        self, reader, tmp_path
    ):
        f = tmp_path / "neg.txt"
        f.write_text("-1.5,2.5\n3,-4\n")
        points = reader.read(f)
        assert points[0] == Point(-1.5, 2.5)
        assert points[1] == Point(3.0, -4.0)

    def test_Should_tolerate_extra_whitespace_around_coordinates(
        self, reader, tmp_path
    ):
        f = tmp_path / "spaces.txt"
        f.write_text("  1 , 2  \n 3.5 , 4.5 \n")
        points = reader.read(f)
        assert points[0] == Point(1.0, 2.0)

    def test_Should_raise_PointParseError_given_line_with_too_many_values(
        self, reader, tmp_path
    ):
        f = tmp_path / "toomany.txt"
        f.write_text("1,2,3\n")
        with pytest.raises(PointParseError):
            reader.read(f)

    def test_Should_raise_PointParseError_given_line_with_non_numeric_value(
        self, reader, tmp_path
    ):
        f = tmp_path / "alpha.txt"
        f.write_text("abc,def\n")
        with pytest.raises(PointParseError):
            reader.read(f)
