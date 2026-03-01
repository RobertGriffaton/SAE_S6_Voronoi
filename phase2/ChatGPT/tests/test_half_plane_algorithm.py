from voronoi_app.algorithms.half_plane import HalfPlaneVoronoiAlgorithm
from voronoi_app.models import Point


def test_Should_given_twoPoints_createTwoNonEmptyCells() -> None:
    # Arrange
    algorithm = HalfPlaneVoronoiAlgorithm()
    points = [Point(0.0, 0.0), Point(10.0, 0.0)]

    # Act
    cells = algorithm.compute_cells(points)

    # Assert
    assert len(cells) == 2
    assert all(len(polygon) >= 3 for polygon in cells.values())


def test_Should_given_twoPoints_keepCellPointsCloserToOwnSite() -> None:
    # Arrange
    algorithm = HalfPlaneVoronoiAlgorithm()
    left_site = Point(0.0, 0.0)
    right_site = Point(10.0, 0.0)

    # Act
    cells = algorithm.compute_cells([left_site, right_site])

    # Assert
    left_cell = cells[left_site]
    for vertex in left_cell:
        left_distance = (vertex.x - left_site.x) ** 2 + (vertex.y - left_site.y) ** 2
        right_distance = (vertex.x - right_site.x) ** 2 + (vertex.y - right_site.y) ** 2
        assert left_distance <= right_distance + 1e-8


def test_Should_given_threePoints_createThreeCells() -> None:
    # Arrange
    algorithm = HalfPlaneVoronoiAlgorithm()
    points = [Point(0.0, 0.0), Point(10.0, 0.0), Point(5.0, 8.0)]

    # Act
    cells = algorithm.compute_cells(points)

    # Assert
    assert len(cells) == 3
    assert all(len(polygon) >= 3 for polygon in cells.values())
