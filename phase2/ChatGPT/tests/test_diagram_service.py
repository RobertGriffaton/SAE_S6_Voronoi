from voronoi_app.algorithms.half_plane import HalfPlaneVoronoiAlgorithm
from voronoi_app.models import Point
from voronoi_app.services.diagram_service import VoronoiDiagramService


def test_Should_given_points_buildDiagramWithSegments() -> None:
    # Arrange
    service = VoronoiDiagramService(HalfPlaneVoronoiAlgorithm())
    points = [Point(0.0, 0.0), Point(10.0, 0.0), Point(5.0, 10.0)]

    # Act
    diagram = service.build_diagram(points)

    # Assert
    assert diagram.sites == points
    assert len(diagram.cells) == 3
    assert len(diagram.segments) > 0
