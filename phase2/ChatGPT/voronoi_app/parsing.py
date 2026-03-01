"""Input file parsing utilities."""

from __future__ import annotations

from pathlib import Path

from voronoi_app.models import Point


class PointFileParser:
    """Parses point files where each non-empty line is `x,y`."""

    def parse_file(self, file_path: str | Path) -> list[Point]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Input file not found: {path}")

        points: list[Point] = []
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            points.append(self._parse_line(line, line_number))

        if len(points) < 2:
            raise ValueError("At least two points are required to compute a Voronoi diagram.")

        self._ensure_unique_points(points)
        return points

    def _parse_line(self, line: str, line_number: int) -> Point:
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2:
            raise ValueError(f"Invalid format at line {line_number}: expected 'x,y'.")

        try:
            x = float(parts[0])
            y = float(parts[1])
        except ValueError as exception:
            raise ValueError(
                f"Invalid numeric values at line {line_number}: '{line}'."
            ) from exception

        return Point(x=x, y=y)

    def _ensure_unique_points(self, points: list[Point]) -> None:
        if len(set(points)) != len(points):
            raise ValueError("Duplicate points are not allowed.")
