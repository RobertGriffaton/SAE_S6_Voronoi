"""
conftest.py — Shared pytest fixtures.
"""
from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from src.core.models import Point
from src.core.voronoi_engine import VoronoiEngine


# ------------------------------------------------------------------
# Point fixtures
# ------------------------------------------------------------------

@pytest.fixture
def four_cardinal_points() -> list[Point]:
    """Four simple points forming a square — minimum for a meaningful diagram."""
    return [Point(0, 0), Point(1, 0), Point(0, 1), Point(1, 1)]


@pytest.fixture
def five_random_points() -> list[Point]:
    return [
        Point(2.0, 4.0),
        Point(5.3, 4.5),
        Point(18.0, 29.0),
        Point(12.5, 23.7),
        Point(7.0, 10.0),
    ]


@pytest.fixture
def basic_diagram(four_cardinal_points):
    engine = VoronoiEngine()
    return engine.compute(four_cardinal_points)


# ------------------------------------------------------------------
# File fixtures
# ------------------------------------------------------------------

@pytest.fixture
def valid_points_file(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\
        # Sample points file
        2,4
        5.3,4.5
        18,29
        12.5,23.7
        7,10
    """)
    file = tmp_path / "points.txt"
    file.write_text(content, encoding="utf-8")
    return file


@pytest.fixture
def file_with_blank_and_comment_lines(tmp_path: Path) -> Path:
    content = textwrap.dedent("""\

        # Header comment
        1,2

        3,4
        # another comment
        5,6
    """)
    file = tmp_path / "mixed.txt"
    file.write_text(content, encoding="utf-8")
    return file


@pytest.fixture
def file_with_malformed_line(tmp_path: Path) -> Path:
    content = "1,2\n3,4\nnot_a_number,5\n"
    file = tmp_path / "bad.txt"
    file.write_text(content, encoding="utf-8")
    return file


@pytest.fixture
def empty_file(tmp_path: Path) -> Path:
    file = tmp_path / "empty.txt"
    file.write_text("", encoding="utf-8")
    return file


@pytest.fixture
def file_only_comments(tmp_path: Path) -> Path:
    file = tmp_path / "comments.txt"
    file.write_text("# nothing here\n# still nothing\n", encoding="utf-8")
    return file
