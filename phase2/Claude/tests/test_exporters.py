"""
test_exporters.py — Unit tests for SVGExporter and ImageExporter.

Pattern: Arrange / Act / Assert (AAA).
Naming:  Should_<expected>_given_<context>
"""
from __future__ import annotations

from pathlib import Path

import pytest

from src.export.image_exporter import ImageExporter
from src.export.svg_exporter import SVGExporter
from tests.conftest import basic_diagram


class TestSVGExporter:

    @pytest.fixture
    def exporter(self) -> SVGExporter:
        return SVGExporter()

    def test_Should_have_svg_extension_given_default_instantiation(self, exporter):
        assert exporter.file_extension == ".svg"

    def test_Should_create_svg_file_given_valid_diagram(
        self, exporter, basic_diagram, tmp_path
    ):
        # Arrange
        output_path = tmp_path / "diagram.svg"
        # Act
        exporter.export(basic_diagram, output_path)
        # Assert
        assert output_path.exists()

    def test_Should_produce_valid_xml_given_valid_diagram(
    self, exporter, basic_diagram, tmp_path
    ):
        import xml.etree.ElementTree as ET
        SVG_NAMESPACE = "http://www.w3.org/2000/svg"
        output_path = tmp_path / "diagram.svg"
        exporter.export(basic_diagram, output_path)
        # Should not raise
        tree = ET.parse(str(output_path))
        root = tree.getroot()
        # ElementTree préfixe le tag avec le namespace : {http://...}svg
        assert root.tag in ("svg", f"{{{SVG_NAMESPACE}}}svg")

    def test_Should_contain_site_markers_given_four_sites(
        self, exporter, basic_diagram, tmp_path
    ):
        import xml.etree.ElementTree as ET
        output_path = tmp_path / "diagram.svg"
        exporter.export(basic_diagram, output_path)
        tree = ET.parse(str(output_path))
        circles = tree.findall(".//{http://www.w3.org/2000/svg}circle") or tree.findall(".//circle")
        assert len(circles) == len(basic_diagram.sites)

    def test_Should_contain_ridge_lines_given_valid_diagram(
        self, exporter, basic_diagram, tmp_path
    ):
        import xml.etree.ElementTree as ET
        output_path = tmp_path / "diagram.svg"
        exporter.export(basic_diagram, output_path)
        content = output_path.read_text()
        assert "<line" in content

    def test_Should_produce_non_empty_file_given_valid_diagram(
        self, exporter, basic_diagram, tmp_path
    ):
        output_path = tmp_path / "diagram.svg"
        exporter.export(basic_diagram, output_path)
        assert output_path.stat().st_size > 0


class TestImageExporter:

    @pytest.fixture
    def exporter(self) -> ImageExporter:
        return ImageExporter()

    def test_Should_have_png_extension_given_default_instantiation(self, exporter):
        assert exporter.file_extension == ".png"

    def test_Should_create_png_file_given_valid_diagram(
        self, exporter, basic_diagram, tmp_path
    ):
        output_path = tmp_path / "diagram.png"
        exporter.export(basic_diagram, output_path)
        assert output_path.exists()

    def test_Should_produce_valid_png_given_valid_diagram(
        self, exporter, basic_diagram, tmp_path
    ):
        from PIL import Image
        output_path = tmp_path / "diagram.png"
        exporter.export(basic_diagram, output_path)
        with Image.open(output_path) as img:
            assert img.format == "PNG"
            assert img.width > 0
            assert img.height > 0

    def test_Should_produce_non_empty_file_given_valid_diagram(
        self, exporter, basic_diagram, tmp_path
    ):
        output_path = tmp_path / "diagram.png"
        exporter.export(basic_diagram, output_path)
        assert output_path.stat().st_size > 0

    def test_Should_produce_larger_image_given_more_spread_out_points(
        self, exporter, basic_diagram, tmp_path
    ):
        """Spread-out points → larger bounding box → larger image."""
        from PIL import Image
        from src.core.models import Point
        from src.core.voronoi_engine import VoronoiEngine

        spread_points = [Point(0, 0), Point(100, 0), Point(0, 100), Point(100, 100)]
        spread_diagram = VoronoiEngine().compute(spread_points)

        small_path = tmp_path / "small.png"
        large_path = tmp_path / "large.png"

        exporter.export(basic_diagram, small_path)
        exporter.export(spread_diagram, large_path)

        with Image.open(small_path) as small, Image.open(large_path) as large:
            assert large.width > small.width or large.height > small.height
