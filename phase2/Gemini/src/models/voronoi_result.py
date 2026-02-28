from dataclasses import dataclass
from typing import List
from src.models.point import Point

@dataclass(frozen=True)
class VoronoiResult:
    """
    Encapsulates the result of a Voronoi diagram generation.
    - vertices: The coordinates of the Voronoi vertices.
    - regions: A list of regions, where each region is a list of vertex indices.
      A negative index (-1) indicates a vertex outside the Voronoi diagram (infinity).
    - point_region: Array of region indices for each input point.
    """
    vertices: List[Point]
    regions: List[List[int]]
    point_region: List[int]
