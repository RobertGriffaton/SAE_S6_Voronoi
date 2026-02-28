from abc import ABC, abstractmethod
from PIL import Image, ImageDraw
from src.models.voronoi_result import VoronoiResult

class ExportStrategy(ABC):
    """
    Abstract Base Class representing an export strategy for Voronoi diagrams.
    """
    @abstractmethod
    def export(self, voronoi: VoronoiResult, file_path: str, width: int = 800, height: int = 600) -> None:
        """
        Exports the given VoronoiResult to the given file path.
        """
        pass

class SvgExportStrategy(ExportStrategy):
    """
    Concete strategy for exporting Voronoi vectorively to SVG.
    """
    def export(self, voronoi: VoronoiResult, file_path: str, width: int = 800, height: int = 600) -> None:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
            f.write(f'  <rect width="100%" height="100%" fill="white"/>\n')
            
            for region in voronoi.regions:
                # We only draw finite regions for simplicity
                if not region or -1 in region:
                    continue
                
                polygon_pts = " ".join([f"{voronoi.vertices[i].x},{voronoi.vertices[i].y}" for i in region])
                f.write(f'  <polygon points="{polygon_pts}" fill="none" stroke="black" stroke-width="2"/>\n')
                
            f.write('</svg>')

class ImageExportStrategy(ExportStrategy):
    """
    Concrete strategy for exporting Voronoi to a raster image (PNG, JPEG).
    """
    def export(self, voronoi: VoronoiResult, file_path: str, width: int = 800, height: int = 600) -> None:
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        
        for region in voronoi.regions:
            # We only draw finite regions for simplicity
            if not region or -1 in region:
                continue
                
            polygon_pts = [(voronoi.vertices[i].x, voronoi.vertices[i].y) for i in region]
            draw.polygon(polygon_pts, outline="black", fill=None)
            
        img.save(file_path)
