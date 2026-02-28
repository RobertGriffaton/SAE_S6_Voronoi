"""
Data models for the Voronoi diagram generator.

This module defines the core data structures used throughout the application,
including points, Voronoi cells, and diagram boundaries.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class Point:
    """
    Represents a 2D point with x and y coordinates.
    
    Attributes:
        x: The x-coordinate of the point.
        y: The y-coordinate of the point.
    """
    x: float
    y: float
    
    def __post_init__(self) -> None:
        """Validate coordinates are finite numbers."""
        if not isinstance(self.x, (int, float)) or not isinstance(self.y, (int, float)):
            raise TypeError("Coordinates must be numeric")
        if not self._is_finite(self.x) or not self._is_finite(self.y):
            raise ValueError("Coordinates must be finite numbers")
    
    @staticmethod
    def _is_finite(value: float) -> bool:
        """Check if a value is finite (not NaN or infinity)."""
        import math
        return math.isfinite(value)
    
    def to_tuple(self) -> Tuple[float, float]:
        """Convert point to a tuple (x, y)."""
        return (self.x, self.y)
    
    def distance_to(self, other: Point) -> float:
        """
        Calculate Euclidean distance to another point.
        
        Args:
            other: The other point.
            
        Returns:
            The Euclidean distance between the two points.
        """
        import math
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)


@dataclass
class VoronoiCell:
    """
    Represents a single cell in a Voronoi diagram.
    
    A Voronoi cell consists of a seed point and the polygon vertices
    that form the cell boundary.
    
    Attributes:
        seed: The seed point (site) of this cell.
        vertices: List of vertices forming the cell polygon in order.
        region_index: Index of the region in the original Voronoi computation.
    """
    seed: Point
    vertices: List[Point]
    region_index: int
    
    def __post_init__(self) -> None:
        """Validate cell data."""
        if not isinstance(self.seed, Point):
            raise TypeError("Seed must be a Point instance")
        if not isinstance(self.vertices, list):
            raise TypeError("Vertices must be a list")
        if not all(isinstance(v, Point) for v in self.vertices):
            raise TypeError("All vertices must be Point instances")
    
    def is_bounded(self) -> bool:
        """
        Check if the cell is bounded (finite).
        
        Returns:
            True if the cell has vertices and forms a closed polygon.
        """
        return len(self.vertices) >= 3
    
    def get_area(self) -> float:
        """
        Calculate the area of the cell using the shoelace formula.
        
        Returns:
            The area of the cell. Returns 0 for unbounded cells.
        """
        if not self.is_bounded():
            return 0.0
        
        area = 0.0
        n = len(self.vertices)
        for i in range(n):
            j = (i + 1) % n
            area += self.vertices[i].x * self.vertices[j].y
            area -= self.vertices[j].x * self.vertices[i].y
        
        return abs(area) / 2.0


@dataclass
class BoundingBox:
    """
    Represents a rectangular bounding box.
    
    Attributes:
        min_x: Minimum x-coordinate.
        max_x: Maximum x-coordinate.
        min_y: Minimum y-coordinate.
        max_y: Maximum y-coordinate.
    """
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    
    DEFAULT_MARGIN: float = 0.1  # 10% margin
    
    def __post_init__(self) -> None:
        """Validate bounding box coordinates."""
        if self.min_x >= self.max_x:
            raise ValueError("min_x must be less than max_x")
        if self.min_y >= self.max_y:
            raise ValueError("min_y must be less than max_y")
    
    @property
    def width(self) -> float:
        """Return the width of the bounding box."""
        return self.max_x - self.min_x
    
    @property
    def height(self) -> float:
        """Return the height of the bounding box."""
        return self.max_y - self.min_y
    
    @property
    def center(self) -> Point:
        """Return the center point of the bounding box."""
        return Point(
            (self.min_x + self.max_x) / 2,
            (self.min_y + self.max_y) / 2
        )
    
    def contains(self, point: Point) -> bool:
        """
        Check if a point is inside the bounding box.
        
        Args:
            point: The point to check.
            
        Returns:
            True if the point is inside or on the boundary.
        """
        return (
            self.min_x <= point.x <= self.max_x and
            self.min_y <= point.y <= self.max_y
        )
    
    def with_margin(self, margin_ratio: float = DEFAULT_MARGIN) -> BoundingBox:
        """
        Create a new bounding box with added margin.
        
        Args:
            margin_ratio: The margin ratio to add (default 10%).
            
        Returns:
            A new bounding box with margin applied.
        """
        margin_x = self.width * margin_ratio
        margin_y = self.height * margin_ratio
        return BoundingBox(
            min_x=self.min_x - margin_x,
            max_x=self.max_x + margin_x,
            min_y=self.min_y - margin_y,
            max_y=self.max_y + margin_y
        )
    
    MIN_SIZE: float = 1.0  # Minimum size to handle degenerate cases
    
    @classmethod
    def from_points(
        cls, 
        points: List[Point], 
        margin_ratio: float = DEFAULT_MARGIN
    ) -> BoundingBox:
        """
        Create a bounding box from a list of points.
        
        Args:
            points: List of points to include in the bounding box.
            margin_ratio: Optional margin to add around the points.
            
        Returns:
            A bounding box containing all points.
            
        Raises:
            ValueError: If the points list is empty.
        """
        if not points:
            raise ValueError("Cannot create bounding box from empty point list")
        
        min_x = min(p.x for p in points)
        max_x = max(p.x for p in points)
        min_y = min(p.y for p in points)
        max_y = max(p.y for p in points)
        
        # Ensure minimum size to handle degenerate cases (collinear points)
        if max_x - min_x < cls.MIN_SIZE:
            center_x = (min_x + max_x) / 2
            min_x = center_x - cls.MIN_SIZE / 2
            max_x = center_x + cls.MIN_SIZE / 2
        
        if max_y - min_y < cls.MIN_SIZE:
            center_y = (min_y + max_y) / 2
            min_y = center_y - cls.MIN_SIZE / 2
            max_y = center_y + cls.MIN_SIZE / 2
        
        bbox = cls(min_x=min_x, max_x=max_x, min_y=min_y, max_y=max_y)
        return bbox.with_margin(margin_ratio)


@dataclass
class VoronoiDiagram:
    """
    Represents a complete Voronoi diagram.
    
    Attributes:
        cells: List of Voronoi cells.
        bounding_box: The bounding box used for computation.
        seed_points: The original seed points used to generate the diagram.
    """
    cells: List[VoronoiCell]
    bounding_box: BoundingBox
    seed_points: List[Point]
    
    def __post_init__(self) -> None:
        """Validate diagram data."""
        if not isinstance(self.cells, list):
            raise TypeError("Cells must be a list")
        if not isinstance(self.seed_points, list):
            raise TypeError("Seed points must be a list")
        if len(self.cells) != len(self.seed_points):
            raise ValueError("Number of cells must match number of seed points")
    
    def get_bounded_cells(self) -> List[VoronoiCell]:
        """
        Get only the bounded (finite) cells.
        
        Returns:
            List of bounded cells.
        """
        return [cell for cell in self.cells if cell.is_bounded()]
    
    def get_cell_at(self, point: Point) -> Optional[VoronoiCell]:
        """
        Find the cell containing a given point.
        
        Args:
            point: The point to locate.
            
        Returns:
            The cell containing the point, or None if not found.
        """
        for cell in self.cells:
            if self._point_in_polygon(point, cell.vertices):
                return cell
        return None
    
    @staticmethod
    def _point_in_polygon(point: Point, vertices: List[Point]) -> bool:
        """
        Check if a point is inside a polygon using ray casting.
        
        Args:
            point: The point to check.
            vertices: Polygon vertices in order.
            
        Returns:
            True if the point is inside the polygon.
        """
        if len(vertices) < 3:
            return False
        
        inside = False
        n = len(vertices)
        j = n - 1
        
        for i in range(n):
            if (
                (vertices[i].y > point.y) != (vertices[j].y > point.y) and
                point.x < (vertices[j].x - vertices[i].x) * 
                         (point.y - vertices[i].y) / 
                         (vertices[j].y - vertices[i].y + 1e-10) + vertices[i].x
            ):
                inside = not inside
            j = i
        
        return inside
