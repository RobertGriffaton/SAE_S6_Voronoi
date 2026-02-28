"""
Tkinter GUI module for the Voronoi diagram generator.

This module provides a graphical user interface for loading point files,
generating Voronoi diagrams, and exporting results.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import List, Optional, Callable
from pathlib import Path

from src.models import Point, VoronoiDiagram
from src.file_parser import PointFileParser, FileParserError
from src.voronoi_calculator import VoronoiCalculator
from src.exporters import (
    ExporterFactory, 
    ExportError,
    SVGExporter,
    ImageExporter
)


class CanvasConfig:
    """Configuration constants for the canvas."""
    DEFAULT_WIDTH: int = 800
    DEFAULT_HEIGHT: int = 600
    BACKGROUND_COLOR: str = "white"
    CELL_FILL_COLOR: str = "#e6f3ff"
    CELL_OUTLINE_COLOR: str = "#333333"
    CELL_OUTLINE_WIDTH: int = 1
    SEED_POINT_COLOR: str = "red"
    SEED_POINT_RADIUS: int = 4
    HOVER_HIGHLIGHT_COLOR: str = "#ffff99"
    MARGIN_PIXELS: int = 20


class VoronoiCanvas(tk.Canvas):
    """
    Custom canvas for displaying Voronoi diagrams.
    
    This canvas handles the rendering of Voronoi cells and seed points,
    including scaling and coordinate transformation.
    """
    
    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        """Initialize the canvas with default configuration."""
        super().__init__(
            parent,
            width=CanvasConfig.DEFAULT_WIDTH,
            height=CanvasConfig.DEFAULT_HEIGHT,
            bg=CanvasConfig.BACKGROUND_COLOR,
            **kwargs
        )
        
        self._diagram: Optional[VoronoiDiagram] = None
        self._scale: float = 1.0
        self._offset_x: float = 0.0
        self._offset_y: float = 0.0
        self._cell_items: List[int] = []
        self._point_items: List[int] = []
    
    def display_diagram(self, diagram: VoronoiDiagram) -> None:
        """
        Display a Voronoi diagram on the canvas.
        
        Args:
            diagram: The Voronoi diagram to display.
        """
        self.clear()
        self._diagram = diagram
        
        self._compute_transform()
        self._draw_cells()
        self._draw_seed_points()
    
    def clear(self) -> None:
        """Clear the canvas and reset state."""
        self.delete("all")
        self._cell_items.clear()
        self._point_items.clear()
        self._diagram = None
    
    def _compute_transform(self) -> None:
        """Compute scaling and offset to fit diagram in canvas."""
        if not self._diagram:
            return
        
        bbox = self._diagram.bounding_box
        canvas_width = self.winfo_width() or CanvasConfig.DEFAULT_WIDTH
        canvas_height = self.winfo_height() or CanvasConfig.DEFAULT_HEIGHT
        
        available_width = canvas_width - 2 * CanvasConfig.MARGIN_PIXELS
        available_height = canvas_height - 2 * CanvasConfig.MARGIN_PIXELS
        
        scale_x = available_width / bbox.width
        scale_y = available_height / bbox.height
        
        # Use same scale for both axes to preserve aspect ratio
        self._scale = min(scale_x, scale_y)
        
        # Center the diagram
        diagram_width = bbox.width * self._scale
        diagram_height = bbox.height * self._scale
        
        self._offset_x = (canvas_width - diagram_width) / 2 - bbox.min_x * self._scale
        self._offset_y = (canvas_height - diagram_height) / 2 - bbox.min_y * self._scale
    
    def _draw_cells(self) -> None:
        """Draw all Voronoi cells."""
        if not self._diagram:
            return
        
        for cell in self._diagram.cells:
            if cell.is_bounded():
                self._draw_cell(cell)
    
    def _draw_cell(self, cell: VoronoiDiagram) -> None:
        """
        Draw a single Voronoi cell.
        
        Args:
            cell: The cell to draw.
        """
        from src.models import VoronoiCell
        
        if not isinstance(cell, VoronoiCell) or len(cell.vertices) < 3:
            return
        
        # Transform vertices to canvas coordinates
        coords = []
        for vertex in cell.vertices:
            x = vertex.x * self._scale + self._offset_x
            y = vertex.y * self._scale + self._offset_y
            # Flip Y axis (canvas Y points down)
            y = (self.winfo_height() or CanvasConfig.DEFAULT_HEIGHT) - y
            coords.extend([x, y])
        
        item_id = self.create_polygon(
            coords,
            fill=CanvasConfig.CELL_FILL_COLOR,
            outline=CanvasConfig.CELL_OUTLINE_COLOR,
            width=CanvasConfig.CELL_OUTLINE_WIDTH,
            tags=("cell", f"cell_{cell.region_index}")
        )
        self._cell_items.append(item_id)
    
    def _draw_seed_points(self) -> None:
        """Draw all seed points."""
        if not self._diagram:
            return
        
        for point in self._diagram.seed_points:
            self._draw_seed_point(point)
    
    def _draw_seed_point(self, point: Point) -> None:
        """
        Draw a single seed point.
        
        Args:
            point: The point to draw.
        """
        x = point.x * self._scale + self._offset_x
        y = point.y * self._scale + self._offset_y
        # Flip Y axis
        y = (self.winfo_height() or CanvasConfig.DEFAULT_HEIGHT) - y
        
        radius = CanvasConfig.SEED_POINT_RADIUS
        item_id = self.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            fill=CanvasConfig.SEED_POINT_COLOR,
            outline="",
            tags=("seed",)
        )
        self._point_items.append(item_id)


class VoronoiApp:
    """
    Main application class for the Voronoi diagram generator.
    
    This class manages the GUI components, file handling, and
    coordinates between the parser, calculator, and exporters.
    """
    
    WINDOW_TITLE: str = "Voronoi Diagram Generator"
    WINDOW_MIN_WIDTH: int = 1000
    WINDOW_MIN_HEIGHT: int = 700
    DEFAULT_EXPORT_WIDTH: int = 800
    DEFAULT_EXPORT_HEIGHT: int = 600
    
    def __init__(self) -> None:
        """Initialize the application."""
        self._root = tk.Tk()
        self._root.title(self.WINDOW_TITLE)
        self._root.minsize(self.WINDOW_MIN_WIDTH, self.WINDOW_MIN_HEIGHT)
        
        self._parser = PointFileParser()
        self._calculator = VoronoiCalculator()
        self._current_points: List[Point] = []
        self._current_diagram: Optional[VoronoiDiagram] = None
        
        self._build_ui()
    
    def _build_ui(self) -> None:
        """Build the user interface."""
        # Main frame
        main_frame = ttk.Frame(self._root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self._root.columnconfigure(0, weight=1)
        self._root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        
        # Control panel (left side)
        control_panel = self._create_control_panel(main_frame)
        control_panel.grid(row=0, column=0, sticky=(tk.N, tk.S, tk.W), padx=(0, 10))
        
        # Canvas (right side)
        self._canvas = VoronoiCanvas(main_frame)
        self._canvas.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self._status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame, 
            textvariable=self._status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        status_bar.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_control_panel(self, parent: ttk.Frame) -> ttk.Frame:
        """
        Create the control panel with buttons.
        
        Args:
            parent: Parent widget.
            
        Returns:
            The control panel frame.
        """
        panel = ttk.LabelFrame(parent, text="Controls", padding="10")
        
        # File operations
        file_frame = ttk.LabelFrame(panel, text="File Operations", padding="5")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            file_frame,
            text="Load Points from File...",
            command=self._on_load_file
        ).pack(fill=tk.X, pady=2)
        
        # Generation
        gen_frame = ttk.LabelFrame(panel, text="Generation", padding="5")
        gen_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            gen_frame,
            text="Generate Voronoi Diagram",
            command=self._on_generate
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            gen_frame,
            text="Clear",
            command=self._on_clear
        ).pack(fill=tk.X, pady=2)
        
        # Export
        export_frame = ttk.LabelFrame(panel, text="Export", padding="5")
        export_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(
            export_frame,
            text="Export as SVG...",
            command=self._on_export_svg
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            export_frame,
            text="Export as Image...",
            command=self._on_export_image
        ).pack(fill=tk.X, pady=2)
        
        # Info
        info_frame = ttk.LabelFrame(panel, text="Information", padding="5")
        info_frame.pack(fill=tk.X)
        
        self._info_var = tk.StringVar(value="No points loaded")
        ttk.Label(info_frame, textvariable=self._info_var, wraplength=150).pack()
        
        return panel
    
    def _on_load_file(self) -> None:
        """Handle load file button click."""
        file_path = filedialog.askopenfilename(
            title="Select Point File",
            filetypes=[
                ("Text files", "*.txt"),
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            self._current_points = self._parser.parse(file_path)
            self._update_info(f"Loaded {len(self._current_points)} points")
            self._status_var.set(f"Loaded: {Path(file_path).name}")
            self._current_diagram = None
            self._canvas.clear()
        except FileParserError as e:
            messagebox.showerror("Error Loading File", str(e))
            self._status_var.set("Error loading file")
    
    def _on_generate(self) -> None:
        """Handle generate button click."""
        if len(self._current_points) < 2:
            messagebox.showwarning(
                "Not Enough Points",
                "Please load at least 2 points first."
            )
            return
        
        try:
            self._current_diagram = self._calculator.calculate(self._current_points)
            self._canvas.display_diagram(self._current_diagram)
            self._status_var.set(
                f"Generated diagram with {len(self._current_diagram.cells)} cells"
            )
        except Exception as e:
            messagebox.showerror("Generation Error", str(e))
            self._status_var.set("Error generating diagram")
    
    def _on_clear(self) -> None:
        """Handle clear button click."""
        self._current_points.clear()
        self._current_diagram = None
        self._canvas.clear()
        self._update_info("No points loaded")
        self._status_var.set("Cleared")
    
    def _on_export_svg(self) -> None:
        """Handle export SVG button click."""
        if not self._current_diagram:
            messagebox.showwarning(
                "No Diagram",
                "Please generate a diagram first."
            )
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export as SVG",
            defaultextension=".svg",
            filetypes=[("SVG files", "*.svg")]
        )
        
        if not file_path:
            return
        
        try:
            exporter = SVGExporter(
                width=self.DEFAULT_EXPORT_WIDTH,
                height=self.DEFAULT_EXPORT_HEIGHT
            )
            exporter.export(self._current_diagram, file_path)
            self._status_var.set(f"Exported to {Path(file_path).name}")
        except ExportError as e:
            messagebox.showerror("Export Error", str(e))
            self._status_var.set("Export failed")
    
    def _on_export_image(self) -> None:
        """Handle export image button click."""
        if not self._current_diagram:
            messagebox.showwarning(
                "No Diagram",
                "Please generate a diagram first."
            )
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export as Image",
            defaultextension=".png",
            filetypes=[
                ("PNG files", "*.png"),
                ("JPEG files", "*.jpg"),
                ("All images", "*.png *.jpg *.jpeg *.bmp *.gif")
            ]
        )
        
        if not file_path:
            return
        
        try:
            exporter = ImageExporter(
                width=self.DEFAULT_EXPORT_WIDTH,
                height=self.DEFAULT_EXPORT_HEIGHT
            )
            exporter.export(self._current_diagram, file_path)
            self._status_var.set(f"Exported to {Path(file_path).name}")
        except ExportError as e:
            messagebox.showerror("Export Error", str(e))
            self._status_var.set("Export failed")
    
    def _update_info(self, message: str) -> None:
        """Update the info label."""
        self._info_var.set(message)
    
    def run(self) -> None:
        """Start the application main loop."""
        self._root.mainloop()


def main() -> None:
    """Entry point for the GUI application."""
    app = VoronoiApp()
    app.run()


if __name__ == "__main__":
    main()
