"""
Voronoi diagram computation module.

This module provides algorithms for computing Voronoi diagrams from a set of points.
It uses scipy.spatial.Voronoi which implements Fortune's sweep line algorithm.

Algorithm choice:
- Fortune's algorithm is chosen for its O(n log n) time complexity
- It is more efficient than naive approaches (O(n²)) for large datasets
- scipy's implementation is well-tested and optimized
"""

from typing import List, Optional
import numpy as np
from scipy.spatial import Voronoi as SciPyVoronoi

from src.models import Point, VoronoiCell, VoronoiDiagram, BoundingBox


class VoronoiCalculator:
    """
    Calculator for Voronoi diagrams using Fortune's sweep line algorithm.
    
    This class encapsulates the Voronoi computation logic and provides
    a clean interface for generating diagrams from point sets.
    
    Design note: This class follows the Single Responsibility Principle (SRP)
    by focusing solely on Voronoi computation.
    """
    
    DEFAULT_BOUNDING_BOX_MARGIN: float = 0.1
    MIN_POINTS_REQUIRED: int = 2
    
    def __init__(self, bounding_box: Optional[BoundingBox] = None):
        """
        Initialize the calculator with optional bounding box.
        
        Args:
            bounding_box: Optional bounding box for the diagram.
                         If not provided, it will be computed from points.
        """
        self._bounding_box = bounding_box
    
    def calculate(
        self, 
        points: List[Point],
        bounding_box: Optional[BoundingBox] = None
    ) -> VoronoiDiagram:
        """
        Calculate the Voronoi diagram for a set of points.
        
        Args:
            points: List of seed points for the diagram.
            bounding_box: Optional bounding box to clip the diagram.
                         If not provided, it will be computed from points.
        
        Returns:
            A VoronoiDiagram containing all cells.
        
        Raises:
            ValueError: If fewer than 2 points are provided.
        """
        self._validate_points(points)
        
        effective_bbox = bounding_box or self._bounding_box
        if effective_bbox is None:
            effective_bbox = BoundingBox.from_points(
                points, 
                self.DEFAULT_BOUNDING_BOX_MARGIN
            )
        
        # Add far points to bound infinite regions
        points_with_far_points = self._add_far_points(points, effective_bbox)
        
        # Compute Voronoi diagram using scipy (Fortune's algorithm)
        scipy_voronoi = self._compute_scipy_voronoi(points_with_far_points)
        
        # Build cells from scipy result
        cells = self._build_cells(scipy_voronoi, points, effective_bbox)
        
        return VoronoiDiagram(
            cells=cells,
            bounding_box=effective_bbox,
            seed_points=points.copy()
        )
    
    def _validate_points(self, points: List[Point]) -> None:
        """
        Validate the input points.
        
        Args:
            points: List of points to validate.
            
        Raises:
            ValueError: If points are invalid.
        """
        if not points:
            raise ValueError("At least one point is required")
        if len(points) < self.MIN_POINTS_REQUIRED:
            raise ValueError(
                f"At least {self.MIN_POINTS_REQUIRED} points are required "
                f"to create a Voronoi diagram"
            )
        
        # Check for duplicate points
        point_tuples = [(p.x, p.y) for p in points]
        if len(point_tuples) != len(set(point_tuples)):
            raise ValueError("Duplicate points are not allowed")
    
    def _add_far_points(
        self, 
        points: List[Point], 
        bounding_box: BoundingBox
    ) -> List[Point]:
        """
        Add far points outside the bounding box to bound infinite regions.
        
        Fortune's algorithm produces infinite regions for points on the convex hull.
        By adding far points, we ensure all original points have bounded regions.
        
        Args:
            points: Original seed points.
            bounding_box: The bounding box.
            
        Returns:
            Points list with far points added.
        """
        margin = max(bounding_box.width, bounding_box.height) * 2
        
        far_points = [
            Point(bounding_box.min_x - margin, bounding_box.min_y - margin),
            Point(bounding_box.max_x + margin, bounding_box.min_y - margin),
            Point(bounding_box.max_x + margin, bounding_box.max_y + margin),
            Point(bounding_box.min_x - margin, bounding_box.max_y + margin),
        ]
        
        return points + far_points
    
    def _compute_scipy_voronoi(self, points: List[Point]) -> SciPyVoronoi:
        """
        Compute Voronoi diagram using scipy.
        
        Args:
            points: List of points (including far points).
            
        Returns:
            scipy.spatial.Voronoi result.
        """
        coordinates = np.array([[p.x, p.y] for p in points])
        return SciPyVoronoi(coordinates)
    
    def _build_cells(
        self,
        scipy_voronoi: SciPyVoronoi,
        original_points: List[Point],
        bounding_box: BoundingBox
    ) -> List[VoronoiCell]:
        """
        Build VoronoiCell objects from scipy result.
        
        Args:
            scipy_voronoi: Result from scipy Voronoi computation.
            original_points: Original seed points (without far points).
            bounding_box: Bounding box for clipping.
            
        Returns:
            List of VoronoiCell objects.
        """
        cells = []
        num_original = len(original_points)
        
        for i, point in enumerate(original_points):
            region_index = scipy_voronoi.point_region[i]
            region = scipy_voronoi.regions[region_index]
            
            # Skip if region is empty
            if not region or -1 in region:
                # Create empty cell for unbounded region
                cells.append(VoronoiCell(
                    seed=point,
                    vertices=[],
                    region_index=region_index
                ))
                continue
            
            # Build vertices list
            vertices = [
                Point(scipy_voronoi.vertices[vertex_idx][0],
                      scipy_voronoi.vertices[vertex_idx][1])
                for vertex_idx in region
            ]
            
            # Clip to bounding box
            vertices = self._clip_to_bounding_box(vertices, bounding_box)
            
            cells.append(VoronoiCell(
                seed=point,
                vertices=vertices,
                region_index=region_index
            ))
        
        return cells
    
    def _clip_to_bounding_box(
        self, 
        vertices: List[Point], 
        bounding_box: BoundingBox
    ) -> List[Point]:
        """
        Clip polygon vertices to the bounding box using Sutherland-Hodgman.
        
        Args:
            vertices: Polygon vertices.
            bounding_box: Bounding box to clip to.
            
        Returns:
            Clipped vertices.
        """
        if len(vertices) < 3:
            return vertices
        
        # Define bounding box edges (as lines)
        edges = [
            (Point(bounding_box.min_x, bounding_box.min_y),
             Point(bounding_box.max_x, bounding_box.min_y)),  # bottom
            (Point(bounding_box.max_x, bounding_box.min_y),
             Point(bounding_box.max_x, bounding_box.max_y)),  # right
            (Point(bounding_box.max_x, bounding_box.max_y),
             Point(bounding_box.min_x, bounding_box.max_y)),  # top
            (Point(bounding_box.min_x, bounding_box.max_y),
             Point(bounding_box.min_x, bounding_box.min_y)),  # left
        ]
        
        output_list = vertices
        
        for edge_start, edge_end in edges:
            input_list = output_list
            output_list = []
            
            if not input_list:
                break
            
            s = input_list[-1]  # previous point
            
            for e in input_list:
                if self._is_inside(e, edge_start, edge_end):
                    if not self._is_inside(s, edge_start, edge_end):
                        # Crossing in
                        intersection = self._compute_intersection(
                            s, e, edge_start, edge_end
                        )
                        if intersection:
                            output_list.append(intersection)
                    output_list.append(e)
                elif self._is_inside(s, edge_start, edge_end):
                    # Crossing out
                    intersection = self._compute_intersection(
                        s, e, edge_start, edge_end
                    )
                    if intersection:
                        output_list.append(intersection)
                s = e
        
        return output_list
    
    def _is_inside(
        self, 
        point: Point, 
        edge_start: Point, 
        edge_end: Point
    ) -> bool:
        """
        Check if a point is inside the clipping edge (left side).
        
        Args:
            point: Point to check.
            edge_start: Start of edge.
            edge_end: End of edge.
            
        Returns:
            True if point is inside.
        """
        # Cross product: positive means point is to the left of edge
        cross = (edge_end.x - edge_start.x) * (point.y - edge_start.y) - \
                (edge_end.y - edge_start.y) * (point.x - edge_start.x)
        return cross >= 0
    
    def _compute_intersection(
        self,
        p1: Point,
        p2: Point,
        edge_start: Point,
        edge_end: Point
    ) -> Optional[Point]:
        """
        Compute intersection of line segment with clipping edge.
        
        Args:
            p1: First point of segment.
            p2: Second point of segment.
            edge_start: Start of clipping edge.
            edge_end: End of clipping edge.
            
        Returns:
            Intersection point or None if parallel.
        """
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = edge_start.x, edge_start.y
        x4, y4 = edge_end.x, edge_end.y
        
        denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        
        if abs(denom) < 1e-10:
            return None  # Lines are parallel
        
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
        
        x = x1 + t * (x2 - x1)
        y = y1 + t * (y2 - y1)
        
        return Point(x, y)
