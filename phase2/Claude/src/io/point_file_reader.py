"""
point_file_reader.py — Parses a text file into a list of Point objects.

Format: one coordinate pair per line, separated by a comma.
        Lines starting with '#' and blank lines are ignored.

Example:
    2,4
    5.3,4.5
    # this is a comment
    18,29
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List

from src.core.models import Point

# Regex: optional whitespace, a number, a comma, a number, optional whitespace
_COORDINATE_PATTERN = re.compile(
    r"^\s*(?P<x>[+-]?\d+(?:\.\d+)?)\s*,\s*(?P<y>[+-]?\d+(?:\.\d+)?)\s*$"
)

COMMENT_PREFIX: str = "#"


class PointParseError(ValueError):
    """Raised when a line cannot be interpreted as a valid coordinate pair."""


class PointFileReader:
    """
    Reads a plain-text file and returns a list of Point objects.

    Responsibilities (SRP):
      - Open and iterate the file
      - Skip blanks and comments
      - Delegate line parsing to _parse_line
      - Aggregate and return results
    """

    def read(self, file_path: Path) -> List[Point]:
        """
        Parse *file_path* and return all valid Point objects found.

        Parameters
        ----------
        file_path : path to the coordinate file

        Returns
        -------
        List[Point] — at least one point

        Raises
        ------
        FileNotFoundError : if the file does not exist
        PointParseError   : if any data line is malformed
        ValueError        : if the file contains no valid points
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        points: List[Point] = []

        with file_path.open(encoding="utf-8") as fh:
            for line_number, raw_line in enumerate(fh, start=1):
                stripped = raw_line.strip()
                if self._should_skip(stripped):
                    continue
                points.append(self._parse_line(stripped, line_number))

        if not points:
            raise ValueError(f"No valid points found in '{file_path}'.")

        return points

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _should_skip(line: str) -> bool:
        """Return True for blank lines and comment lines."""
        return not line or line.startswith(COMMENT_PREFIX)

    @staticmethod
    def _parse_line(line: str, line_number: int) -> Point:
        """
        Parse a single coordinate line and return a Point.

        Raises PointParseError on malformed input.
        """
        match = _COORDINATE_PATTERN.match(line)
        if not match:
            raise PointParseError(
                f"Line {line_number}: cannot parse '{line}' as a coordinate pair. "
                "Expected format: 'x,y' (e.g. '3.5,12')."
            )
        return Point(x=float(match.group("x")), y=float(match.group("y")))
