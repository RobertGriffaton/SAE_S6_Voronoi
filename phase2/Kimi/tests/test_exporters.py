"""
Tests for the exporters module.

This module tests all exporter classes including SVGExporter,
ImageExporter, and ExporterFactory.
"""

import pytest
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from src.exporters import (
    SVGExporter,
    ImageExporter,
    ExporterFactory,
    ExportError
)
from src.models import Point, VoronoiCell, VoronoiDiagram, BoundingBox


class TestSVGExporter:
    """Tests for the SVGExporter class."""
    
    def test_should_export_svg_given_valid_diagram(self) -> None:
        """Should export valid SVG when given valid diagram."""
        # Arrange
        exporter = SVGExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            
            # Assert
            content = Path(temp_path).read_text()
            assert '<svg' in content
            assert '</svg>' in content
        finally:
            Path(temp_path).unlink()
    
    def test_should_create_valid_xml_given_valid_diagram(self) -> None:
        """Should create valid XML structure when given valid diagram."""
        # Arrange
        exporter = SVGExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            
            # Assert - Should parse without error
            tree = ET.parse(temp_path)
            root = tree.getroot()
            assert root.tag.endswith('svg')
        finally:
            Path(temp_path).unlink()
    
    def test_should_include_seed_points_given_valid_diagram(self) -> None:
        """Should include seed points in SVG when given valid diagram."""
        # Arrange
        exporter = SVGExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            content = Path(temp_path).read_text()
            
            # Assert
            assert '<circle' in content
            assert 'class="seed"' in content
        finally:
            Path(temp_path).unlink()
    
    def test_should_include_cell_paths_given_valid_diagram(self) -> None:
        """Should include cell paths in SVG when given valid diagram."""
        # Arrange
        exporter = SVGExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            content = Path(temp_path).read_text()
            
            # Assert
            assert '<path' in content
            assert 'class="cell' in content
        finally:
            Path(temp_path).unlink()
    
    def test_should_return_svg_extension(self) -> None:
        """Should return .svg as supported extension."""
        # Arrange
        exporter = SVGExporter()
        
        # Act
        ext = exporter.get_supported_extension()
        
        # Assert
        assert ext == ".svg"
    
    def test_should_apply_custom_colors_given_custom_config(self) -> None:
        """Should apply custom colors when given custom configuration."""
        # Arrange
        exporter = SVGExporter(
            cell_color="#ff0000",
            stroke_color="#00ff00",
            point_color="#0000ff"
        )
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            content = Path(temp_path).read_text()
            
            # Assert
            assert '#ff0000' in content
            assert '#00ff00' in content
            assert '#0000ff' in content
        finally:
            Path(temp_path).unlink()
    
    def test_should_set_canvas_size_given_custom_dimensions(self) -> None:
        """Should set canvas size when given custom dimensions."""
        # Arrange
        exporter = SVGExporter(width=1200, height=800)
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            content = Path(temp_path).read_text()
            
            # Assert
            assert 'width="1200"' in content
            assert 'height="800"' in content
        finally:
            Path(temp_path).unlink()
    
    def _create_simple_diagram(self) -> VoronoiDiagram:
        """Helper to create a simple Voronoi diagram for testing."""
        seed1 = Point(0, 0)
        seed2 = Point(2, 0)
        cell1 = VoronoiCell(
            seed1,
            [Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)],
            0
        )
        cell2 = VoronoiCell(
            seed2,
            [Point(1, -1), Point(3, -1), Point(3, 1), Point(1, 1)],
            1
        )
        bbox = BoundingBox(-2, 4, -2, 2)
        return VoronoiDiagram([cell1, cell2], bbox, [seed1, seed2])


class TestImageExporter:
    """Tests for the ImageExporter class."""
    
    def test_should_export_png_given_valid_diagram(self) -> None:
        """Should export valid PNG when given valid diagram."""
        # Arrange
        exporter = ImageExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            
            # Assert
            from PIL import Image
            img = Image.open(temp_path)
            assert img.format == 'PNG'
        finally:
            Path(temp_path).unlink()
    
    def test_should_export_jpeg_given_valid_diagram(self) -> None:
        """Should export valid JPEG when given valid diagram."""
        # Arrange
        exporter = ImageExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            
            # Assert
            from PIL import Image
            img = Image.open(temp_path)
            assert img.format == 'JPEG'
        finally:
            Path(temp_path).unlink()
    
    def test_should_set_image_size_given_custom_dimensions(self) -> None:
        """Should set image size when given custom dimensions."""
        # Arrange
        exporter = ImageExporter(width=400, height=300)
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act
            exporter.export(diagram, temp_path)
            
            # Assert
            from PIL import Image
            img = Image.open(temp_path)
            assert img.size == (400, 300)
        finally:
            Path(temp_path).unlink()
    
    def test_should_return_png_extension(self) -> None:
        """Should return .png as supported extension."""
        # Arrange
        exporter = ImageExporter()
        
        # Act
        ext = exporter.get_supported_extension()
        
        # Assert
        assert ext == ".png"
    
    def test_should_raise_error_given_unsupported_format(self) -> None:
        """Should raise ExportError when given unsupported format."""
        # Arrange
        exporter = ImageExporter()
        diagram = self._create_simple_diagram()
        
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = f.name
        
        try:
            # Act & Assert
            with pytest.raises(ExportError):
                exporter.export(diagram, temp_path)
        finally:
            Path(temp_path).unlink()
    
    def _create_simple_diagram(self) -> VoronoiDiagram:
        """Helper to create a simple Voronoi diagram for testing."""
        seed1 = Point(0, 0)
        seed2 = Point(2, 0)
        cell1 = VoronoiCell(
            seed1,
            [Point(-1, -1), Point(1, -1), Point(1, 1), Point(-1, 1)],
            0
        )
        cell2 = VoronoiCell(
            seed2,
            [Point(1, -1), Point(3, -1), Point(3, 1), Point(1, 1)],
            1
        )
        bbox = BoundingBox(-2, 4, -2, 2)
        return VoronoiDiagram([cell1, cell2], bbox, [seed1, seed2])


class TestExporterFactory:
    """Tests for the ExporterFactory class."""
    
    def test_should_create_svg_exporter_given_svg_extension(self) -> None:
        """Should create SVGExporter when given .svg extension."""
        # Arrange & Act
        exporter = ExporterFactory.create_exporter("output.svg")
        
        # Assert
        assert isinstance(exporter, SVGExporter)
    
    def test_should_create_image_exporter_given_png_extension(self) -> None:
        """Should create ImageExporter when given .png extension."""
        # Arrange & Act
        exporter = ExporterFactory.create_exporter("output.png")
        
        # Assert
        assert isinstance(exporter, ImageExporter)
    
    def test_should_create_image_exporter_given_jpg_extension(self) -> None:
        """Should create ImageExporter when given .jpg extension."""
        # Arrange & Act
        exporter = ExporterFactory.create_exporter("output.jpg")
        
        # Assert
        assert isinstance(exporter, ImageExporter)
    
    def test_should_create_image_exporter_given_jpeg_extension(self) -> None:
        """Should create ImageExporter when given .jpeg extension."""
        # Arrange & Act
        exporter = ExporterFactory.create_exporter("output.jpeg")
        
        # Assert
        assert isinstance(exporter, ImageExporter)
    
    def test_should_raise_error_given_unsupported_extension(self) -> None:
        """Should raise ExportError when given unsupported extension."""
        # Arrange & Act & Assert
        with pytest.raises(ExportError):
            ExporterFactory.create_exporter("output.pdf")
    
    def test_should_return_supported_formats(self) -> None:
        """Should return list of supported formats."""
        # Arrange & Act
        formats = ExporterFactory.get_supported_formats()
        
        # Assert
        assert ".svg" in formats
        assert ".png" in formats
        assert ".jpg" in formats
    
    def test_should_handle_uppercase_extension(self) -> None:
        """Should handle uppercase file extensions."""
        # Arrange & Act
        exporter = ExporterFactory.create_exporter("output.SVG")
        
        # Assert
        assert isinstance(exporter, SVGExporter)
    
    def test_should_register_new_exporter_given_custom_class(self) -> None:
        """Should register new exporter when given custom class."""
        # Arrange
        class CustomExporter(SVGExporter):
            pass
        
        # Act
        ExporterFactory.register_exporter(".custom", CustomExporter)
        exporter = ExporterFactory.create_exporter("output.custom")
        
        # Assert
        assert isinstance(exporter, CustomExporter)
