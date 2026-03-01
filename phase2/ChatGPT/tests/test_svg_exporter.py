from pathlib import Path

from voronoi_app.algorithms.half_plane import HalfPlaneVoronoiAlgorithm
from voronoi_app.exporters.svg_exporter import SvgExporter
from voronoi_app.models import Point
from voronoi_app.services.diagram_service import VoronoiDiagramService


def test_Should_given_diagram_exportSvgFile(tmp_path: Path) -> None:
    # Arrange
    service = VoronoiDiagramService(HalfPlaneVoronoiAlgorithm())
    exporter = SvgExporter()
    diagram = service.build_diagram([Point(0.0, 0.0), Point(10.0, 0.0), Point(5.0, 10.0)])
    output_file = tmp_path / "diagram.svg"

    # Act
    exporter.export(diagram, output_file)

    # Assert
    content = output_file.read_text(encoding="utf-8")
    assert output_file.exists()
    assert "<svg" in content
    assert "<line" in content
    assert "<circle" in content
