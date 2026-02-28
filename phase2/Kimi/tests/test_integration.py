"""
Integration tests for the Voronoi diagram generator.

These tests verify the complete workflow from file parsing to export.
"""

import pytest
import tempfile
from pathlib import Path

from src.file_parser import PointFileParser
from src.voronoi_calculator import VoronoiCalculator
from src.exporters import ExporterFactory


class TestCompleteWorkflow:
    """Integration tests for the complete workflow."""
    
    def test_should_complete_workflow_given_valid_input_file(self) -> None:
        """Should complete full workflow when given valid input file."""
        # Arrange - Create input file
        content = """# Test points
0,0
2,0
1,1.732
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = f.name
        
        try:
            # Act - Parse, calculate, export
            parser = PointFileParser()
            points = parser.parse(input_path)
            
            calculator = VoronoiCalculator()
            diagram = calculator.calculate(points)
            
            exporter = ExporterFactory.create_exporter(output_path)
            exporter.export(diagram, output_path)
            
            # Assert
            assert Path(output_path).exists()
            assert Path(output_path).stat().st_size > 0
        finally:
            Path(input_path).unlink()
            Path(output_path).unlink()
    
    def test_should_export_multiple_formats_given_same_diagram(self) -> None:
        """Should export to multiple formats when given same diagram."""
        # Arrange
        content = "0,0\n2,0\n1,1.732\n"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        svg_path = input_path.replace('.txt', '.svg')
        png_path = input_path.replace('.txt', '.png')
        
        try:
            # Act
            parser = PointFileParser()
            points = parser.parse(input_path)
            
            calculator = VoronoiCalculator()
            diagram = calculator.calculate(points)
            
            svg_exporter = ExporterFactory.create_exporter(svg_path)
            svg_exporter.export(diagram, svg_path)
            
            png_exporter = ExporterFactory.create_exporter(png_path)
            png_exporter.export(diagram, png_path)
            
            # Assert
            assert Path(svg_path).exists()
            assert Path(png_path).exists()
        finally:
            Path(input_path).unlink(missing_ok=True)
            Path(svg_path).unlink(missing_ok=True)
            Path(png_path).unlink(missing_ok=True)
    
    def test_should_handle_large_dataset_given_many_points(self) -> None:
        """Should handle large dataset when given many points."""
        # Arrange
        import random
        random.seed(42)
        
        lines = [f"{random.uniform(-100, 100)},{random.uniform(-100, 100)}" 
                 for _ in range(50)]
        content = "\n".join(lines)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix='.svg', delete=False) as f:
            output_path = f.name
        
        try:
            # Act
            parser = PointFileParser()
            points = parser.parse(input_path)
            
            calculator = VoronoiCalculator()
            diagram = calculator.calculate(points)
            
            exporter = ExporterFactory.create_exporter(output_path)
            exporter.export(diagram, output_path)
            
            # Assert
            assert len(points) == 50
            assert len(diagram.cells) == 50
            assert Path(output_path).exists()
        finally:
            Path(input_path).unlink()
            Path(output_path).unlink()
    
    def test_should_preserve_point_coordinates_given_round_trip(self) -> None:
        """Should preserve point coordinates through round trip."""
        # Arrange
        original_points = [
            (1.5, 2.5),
            (-3.5, 4.5),
            (0.0, -1.5),
        ]
        content = "\n".join(f"{x},{y}" for x, y in original_points)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        try:
            # Act
            parser = PointFileParser()
            points = parser.parse(input_path)
            
            calculator = VoronoiCalculator()
            diagram = calculator.calculate(points)
            
            # Assert
            for i, (expected_x, expected_y) in enumerate(original_points):
                assert diagram.seed_points[i].x == expected_x
                assert diagram.seed_points[i].y == expected_y
        finally:
            Path(input_path).unlink()


class TestErrorHandling:
    """Tests for error handling in the complete workflow."""
    
    def test_should_fail_gracefully_given_malformed_input(self) -> None:
        """Should fail gracefully when given malformed input."""
        # Arrange
        content = "1,2\ninvalid_line\n3,4"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        try:
            # Act & Assert
            parser = PointFileParser()
            with pytest.raises(Exception):
                parser.parse(input_path)
        finally:
            Path(input_path).unlink()
    
    def test_should_fail_gracefully_given_insufficient_points(self) -> None:
        """Should fail gracefully when given insufficient points."""
        # Arrange
        content = "1,2"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        try:
            # Act
            parser = PointFileParser()
            points = parser.parse(input_path)
            
            # Assert
            calculator = VoronoiCalculator()
            with pytest.raises(ValueError):
                calculator.calculate(points)
        finally:
            Path(input_path).unlink()
    
    def test_should_fail_gracefully_given_duplicate_points(self) -> None:
        """Should fail gracefully when given duplicate points."""
        # Arrange
        content = "1,2\n1,2\n3,4"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            input_path = f.name
        
        try:
            # Act
            parser = PointFileParser()
            points = parser.parse(input_path)
            
            # Assert
            calculator = VoronoiCalculator()
            with pytest.raises(ValueError):
                calculator.calculate(points)
        finally:
            Path(input_path).unlink()
