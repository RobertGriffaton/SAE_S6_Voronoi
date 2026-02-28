"""
Export module for Voronoi diagrams.

This module provides exporters for saving Voronoi diagrams in various formats.
It uses the Strategy pattern to allow easy addition of new export formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Protocol

from src.models import VoronoiDiagram, Point, VoronoiCell


class ExportError(Exception):
    """Base exception for export errors."""
    pass


class Exporter(ABC):
    """
    Abstract base class for Voronoi diagram exporters.
    
    This class defines the interface for all exporters, following the
    Strategy pattern. New export formats can be added by implementing
    this interface.
    """
    
    DEFAULT_STROKE_WIDTH: float = 1.0
    DEFAULT_POINT_RADIUS: float = 3.0
    
    @abstractmethod
    def export(self, diagram: VoronoiDiagram, file_path: str) -> None:
        """
        Export the Voronoi diagram to a file.
        
        Args:
            diagram: The Voronoi diagram to export.
            file_path: Path to the output file.
            
        Raises:
            ExportError: If export fails.
        """
        pass
    
    @abstractmethod
    def get_supported_extension(self) -> str:
        """Return the file extension supported by this exporter."""
        pass


class SVGExporter(Exporter):
    """
    Exporter for SVG format.
    
    This exporter generates scalable vector graphics (SVG) files
    that can be viewed in web browsers and edited in vector graphics software.
    """
    
    SVG_NAMESPACE: str = "http://www.w3.org/2000/svg"
    DEFAULT_CELL_COLOR: str = "none"
    DEFAULT_STROKE_COLOR: str = "#333333"
    DEFAULT_POINT_COLOR: str = "#ff0000"
    DEFAULT_WIDTH: int = 800
    DEFAULT_HEIGHT: int = 600
    MARGIN_PIXELS: int = 20
    
    def __init__(
        self,
        cell_color: str = DEFAULT_CELL_COLOR,
        stroke_color: str = DEFAULT_STROKE_COLOR,
        point_color: str = DEFAULT_POINT_COLOR,
        stroke_width: float = Exporter.DEFAULT_STROKE_WIDTH,
        point_radius: float = Exporter.DEFAULT_POINT_RADIUS,
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT
    ):
        """
        Initialize SVG exporter with styling options.
        
        Args:
            cell_color: Fill color for cells (or "none" for transparent).
            stroke_color: Color for cell boundaries.
            point_color: Color for seed points.
            stroke_width: Width of cell boundary lines.
            point_radius: Radius of seed point markers.
            width: SVG canvas width in pixels.
            height: SVG canvas height in pixels.
        """
        self._cell_color = cell_color
        self._stroke_color = stroke_color
        self._point_color = point_color
        self._stroke_width = stroke_width
        self._point_radius = point_radius
        self._width = width
        self._height = height
    
    def get_supported_extension(self) -> str:
        """Return SVG file extension."""
        return ".svg"
    
    def export(self, diagram: VoronoiDiagram, file_path: str) -> None:
        """
        Export the Voronoi diagram to an SVG file.
        
        Args:
            diagram: The Voronoi diagram to export.
            file_path: Path to the output SVG file.
            
        Raises:
            ExportError: If export fails.
        """
        path = Path(file_path)
        
        try:
            svg_content = self._generate_svg(diagram)
            path.write_text(svg_content, encoding="utf-8")
        except IOError as e:
            raise ExportError(f"Failed to write SVG file: {e}") from e
    
    def _generate_svg(self, diagram: VoronoiDiagram) -> str:
        """
        Generate SVG content from the diagram.
        
        Args:
            diagram: The Voronoi diagram.
            
        Returns:
            SVG content as string.
        """
        # Compute scaling to fit diagram in canvas
        scale_x, scale_y, offset_x, offset_y = self._compute_transform(diagram)
        
        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="{self.SVG_NAMESPACE}" '
            f'width="{self._width}" height="{self._height}" '
            f'viewBox="0 0 {self._width} {self._height}">',
            '  <defs>',
            '    <style>',
            '      .cell { fill: ' + self._cell_color + '; }',
            '      .boundary { stroke: ' + self._stroke_color + 
            f'; stroke-width: {self._stroke_width}; fill: none; ' +
            'stroke-linejoin: round; }',
            '      .seed { fill: ' + self._point_color + '; }',
            '    </style>',
            '  </defs>',
            '  <g>',
        ]
        
        # Draw cells
        for cell in diagram.cells:
            if cell.is_bounded():
                path_data = self._vertices_to_path(
                    cell.vertices, scale_x, scale_y, offset_x, offset_y
                )
                lines.append(
                    f'    <path class="cell boundary" d="{path_data}"/>'
                )
        
        # Draw seed points
        for point in diagram.seed_points:
            svg_x = point.x * scale_x + offset_x
            svg_y = point.y * scale_y + offset_y
            lines.append(
                f'    <circle class="seed" cx="{svg_x:.2f}" cy="{svg_y:.2f}" '
                f'r="{self._point_radius}"/>'
            )
        
        lines.extend([
            '  </g>',
            '</svg>',
        ])
        
        return '\n'.join(lines)
    
    def _compute_transform(
        self, 
        diagram: VoronoiDiagram
    ) -> tuple[float, float, float, float]:
        """
        Compute scaling and translation for the diagram.
        
        Args:
            diagram: The Voronoi diagram.
            
        Returns:
            Tuple of (scale_x, scale_y, offset_x, offset_y).
        """
        bbox = diagram.bounding_box
        
        available_width = self._width - 2 * self.MARGIN_PIXELS
        available_height = self._height - 2 * self.MARGIN_PIXELS
        
        scale_x = available_width / bbox.width
        scale_y = available_height / bbox.height
        
        # Use same scale for both axes to preserve aspect ratio
        scale = min(scale_x, scale_y)
        
        # Center the diagram
        diagram_width = bbox.width * scale
        diagram_height = bbox.height * scale
        
        offset_x = (self._width - diagram_width) / 2 - bbox.min_x * scale
        offset_y = (self._height - diagram_height) / 2 - bbox.min_y * scale
        
        # Flip Y axis (SVG has Y pointing down)
        offset_y = self._height - offset_y
        scale_y = -scale
        
        return scale, scale_y, offset_x, offset_y
    
    def _vertices_to_path(
        self,
        vertices: List[Point],
        scale_x: float,
        scale_y: float,
        offset_x: float,
        offset_y: float
    ) -> str:
        """
        Convert vertices to SVG path data.
        
        Args:
            vertices: List of vertices.
            scale_x: X scaling factor.
            scale_y: Y scaling factor.
            offset_x: X offset.
            offset_y: Y offset.
            
        Returns:
            SVG path data string.
        """
        if not vertices:
            return ""
        
        commands = []
        for i, vertex in enumerate(vertices):
            x = vertex.x * scale_x + offset_x
            y = vertex.y * scale_y + offset_y
            
            if i == 0:
                commands.append(f"M {x:.2f} {y:.2f}")
            else:
                commands.append(f"L {x:.2f} {y:.2f}")
        
        commands.append("Z")  # Close path
        return " ".join(commands)


class ImageExporter(Exporter):
    """
    Exporter for raster image formats (PNG, JPEG, etc.).
    
    This exporter uses PIL/Pillow to generate raster images.
    """
    
    DEFAULT_BACKGROUND_COLOR: tuple[int, int, int] = (255, 255, 255)
    DEFAULT_CELL_COLOR_RGB: tuple[int, int, int] = (200, 220, 255)
    DEFAULT_STROKE_COLOR_RGB: tuple[int, int, int] = (50, 50, 50)
    DEFAULT_POINT_COLOR_RGB: tuple[int, int, int] = (255, 0, 0)
    DEFAULT_IMAGE_WIDTH: int = 800
    DEFAULT_IMAGE_HEIGHT: int = 600
    
    SUPPORTED_FORMATS: dict[str, str] = {
        ".png": "PNG",
        ".jpg": "JPEG",
        ".jpeg": "JPEG",
        ".bmp": "BMP",
        ".gif": "GIF",
        ".tiff": "TIFF",
        ".webp": "WEBP",
    }
    
    def __init__(
        self,
        background_color: tuple[int, int, int] = DEFAULT_BACKGROUND_COLOR,
        cell_color: tuple[int, int, int] = DEFAULT_CELL_COLOR_RGB,
        stroke_color: tuple[int, int, int] = DEFAULT_STROKE_COLOR_RGB,
        point_color: tuple[int, int, int] = DEFAULT_POINT_COLOR_RGB,
        stroke_width: int = 1,
        point_radius: int = 4,
        width: int = DEFAULT_IMAGE_WIDTH,
        height: int = DEFAULT_IMAGE_HEIGHT
    ):
        """
        Initialize image exporter with styling options.
        
        Args:
            background_color: RGB tuple for background.
            cell_color: RGB tuple for cell fill.
            stroke_color: RGB tuple for cell boundaries.
            point_color: RGB tuple for seed points.
            stroke_width: Width of cell boundary lines in pixels.
            point_radius: Radius of seed point markers in pixels.
            width: Image width in pixels.
            height: Image height in pixels.
        """
        self._background_color = background_color
        self._cell_color = cell_color
        self._stroke_color = stroke_color
        self._point_color = point_color
        self._stroke_width = stroke_width
        self._point_radius = point_radius
        self._width = width
        self._height = height
    
    def get_supported_extension(self) -> str:
        """Return default image extension."""
        return ".png"
    
    def export(self, diagram: VoronoiDiagram, file_path: str) -> None:
        """
        Export the Voronoi diagram to an image file.
        
        Args:
            diagram: The Voronoi diagram to export.
            file_path: Path to the output image file.
            
        Raises:
            ExportError: If export fails.
        """
        from PIL import Image, ImageDraw
        
        path = Path(file_path)
        file_format = self._get_format_from_extension(path.suffix)
        
        try:
            image = self._generate_image(diagram)
            image.save(file_path, format=file_format)
        except IOError as e:
            raise ExportError(f"Failed to write image file: {e}") from e
    
    def _get_format_from_extension(self, extension: str) -> str:
        """
        Get PIL format name from file extension.
        
        Args:
            extension: File extension (e.g., ".png").
            
        Returns:
            PIL format name.
            
        Raises:
            ExportError: If format is not supported.
        """
        ext_lower = extension.lower()
        if ext_lower in self.SUPPORTED_FORMATS:
            return self.SUPPORTED_FORMATS[ext_lower]
        raise ExportError(f"Unsupported image format: {extension}")
    
    def _generate_image(self, diagram: VoronoiDiagram) -> "Image.Image":
        """
        Generate PIL Image from the diagram.
        
        Args:
            diagram: The Voronoi diagram.
            
        Returns:
            PIL Image object.
        """
        from PIL import Image, ImageDraw
        
        image = Image.new(
            "RGB", 
            (self._width, self._height), 
            self._background_color
        )
        draw = ImageDraw.Draw(image)
        
        # Compute scaling
        scale, offset_x, offset_y = self._compute_transform(diagram)
        
        # Draw cells
        for cell in diagram.cells:
            if cell.is_bounded():
                polygon = self._vertices_to_polygon(
                    cell.vertices, scale, offset_x, offset_y
                )
                draw.polygon(polygon, fill=self._cell_color)
                draw.polygon(
                    polygon, 
                    outline=self._stroke_color, 
                    width=self._stroke_width
                )
        
        # Draw seed points
        for point in diagram.seed_points:
            x = int(point.x * scale + offset_x)
            y = int(point.y * scale + offset_y)
            bbox = [
                x - self._point_radius,
                y - self._point_radius,
                x + self._point_radius,
                y + self._point_radius,
            ]
            draw.ellipse(bbox, fill=self._point_color)
        
        return image
    
    def _compute_transform(
        self, 
        diagram: VoronoiDiagram
    ) -> tuple[float, float, float]:
        """
        Compute scaling and translation for the diagram.
        
        Args:
            diagram: The Voronoi diagram.
            
        Returns:
            Tuple of (scale, offset_x, offset_y).
        """
        bbox = diagram.bounding_box
        
        margin = 20
        available_width = self._width - 2 * margin
        available_height = self._height - 2 * margin
        
        scale_x = available_width / bbox.width
        scale_y = available_height / bbox.height
        
        # Use same scale for both axes
        scale = min(scale_x, scale_y)
        
        # Center the diagram
        diagram_width = bbox.width * scale
        diagram_height = bbox.height * scale
        
        offset_x = (self._width - diagram_width) / 2 - bbox.min_x * scale
        offset_y = (self._height - diagram_height) / 2 - bbox.min_y * scale
        
        return scale, offset_x, offset_y
    
    def _vertices_to_polygon(
        self,
        vertices: List[Point],
        scale: float,
        offset_x: float,
        offset_y: float
    ) -> List[tuple[int, int]]:
        """
        Convert vertices to polygon points.
        
        Args:
            vertices: List of vertices.
            scale: Scaling factor.
            offset_x: X offset.
            offset_y: Y offset.
            
        Returns:
            List of (x, y) tuples for PIL.
        """
        return [
            (
                int(v.x * scale + offset_x),
                int(v.y * scale + offset_y)
            )
            for v in vertices
        ]


class ExporterFactory:
    """
    Factory for creating appropriate exporters.
    
    This factory follows the Factory pattern to create exporters
    based on file extension or format type.
    """
    
    _exporters: dict[str, type[Exporter]] = {
        ".svg": SVGExporter,
        ".png": ImageExporter,
        ".jpg": ImageExporter,
        ".jpeg": ImageExporter,
        ".bmp": ImageExporter,
        ".gif": ImageExporter,
        ".tiff": ImageExporter,
        ".webp": ImageExporter,
    }
    
    @classmethod
    def create_exporter(cls, file_path: str) -> Exporter:
        """
        Create an appropriate exporter for the given file path.
        
        Args:
            file_path: Path to the output file.
            
        Returns:
            Configured exporter instance.
            
        Raises:
            ExportError: If format is not supported.
        """
        path = Path(file_path)
        extension = path.suffix.lower()
        
        if extension not in cls._exporters:
            supported = ", ".join(cls._exporters.keys())
            raise ExportError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {supported}"
            )
        
        exporter_class = cls._exporters[extension]
        return exporter_class()
    
    @classmethod
    def register_exporter(
        cls, 
        extension: str, 
        exporter_class: type[Exporter]
    ) -> None:
        """
        Register a new exporter for a file extension.
        
        Args:
            extension: File extension (e.g., ".pdf").
            exporter_class: Exporter class to register.
        """
        cls._exporters[extension.lower()] = exporter_class
    
    @classmethod
    def get_supported_formats(cls) -> List[str]:
        """
        Get list of supported file formats.
        
        Returns:
            List of supported file extensions.
        """
        return list(cls._exporters.keys())
