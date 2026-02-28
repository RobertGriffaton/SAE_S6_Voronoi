import numpy as np
from scipy.spatial import Voronoi, QhullError
from typing import List
from src.models.point import Point
from src.models.voronoi_result import VoronoiResult

class VoronoiGenerator:
    """
    Service responsible for generating a Voronoi diagram from a set of points.
    """
    
    @staticmethod
    def generate(points: List[Point]) -> VoronoiResult:
        """
        Generates a Voronoi diagram.
        
        Args:
            points: A list of at least 3 non-collinear Point objects.
            
        Returns:
            A VoronoiResult object containing vertices and regions.
            
        Raises:
            ValueError: If fewer than 3 points are provided, or if points are collinear/invalid.
        """
        if len(points) < 3:
            raise ValueError("At least 3 points are required to generate a Voronoi diagram.")
            
        # Convert points to numpy array
        points_array = np.array([[p.x, p.y] for p in points])
        
        try:
            vor = Voronoi(points_array)
        except QhullError:
            raise ValueError("Could not generate Voronoi diagram. Points might be collinear or coincident.")
            
        # Convert scipy Voronoi result to our domain models
        vertices = [Point(float(v[0]), float(v[1])) for v in vor.vertices]
        
        # vor.regions includes empty list for empty regions
        regions = [list(region) for region in vor.regions]
        point_region = list(vor.point_region)
        
        return VoronoiResult(vertices=vertices, regions=regions, point_region=point_region)
