import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, List

from src.models.point import Point
from src.models.voronoi_result import VoronoiResult
from src.utils.file_reader import FileReader
from src.services.voronoi_generator import VoronoiGenerator
from src.services.export_strategy import SvgExportStrategy, ImageExportStrategy

class MainWindow(tk.Tk):
    """
    Main application window (View and Controller).
    """
    
    def __init__(self):
        super().__init__()
        self.title("Voronoi Diagram Generator")
        self.geometry("850x700")
        
        # Application context state
        self.points: List[Point] = []
        self.voronoi: Optional[VoronoiResult] = None
        
        self.canvas_width = 800
        self.canvas_height = 600
        
        self._setup_ui()
        
    def _setup_ui(self):
        # Top Frame for controls
        control_frame = tk.Frame(self, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        self.btn_load = tk.Button(control_frame, text="Load Points File", command=self._load_file)
        self.btn_load.pack(side=tk.LEFT, padx=10)
        
        self.btn_export_svg = tk.Button(control_frame, text="Export SVG", command=self._export_svg, state=tk.DISABLED)
        self.btn_export_svg.pack(side=tk.LEFT, padx=10)
        
        self.btn_export_img = tk.Button(control_frame, text="Export Image", command=self._export_img, state=tk.DISABLED)
        self.btn_export_img.pack(side=tk.LEFT, padx=10)
        
        # Canvas for drawing
        self.canvas = tk.Canvas(self, width=self.canvas_width, height=self.canvas_height, bg="white", relief=tk.SUNKEN, borderwidth=2)
        self.canvas.pack(side=tk.TOP, pady=10)
        
    def _load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select points file",
            filetypes=(("Text Files", "*.txt"), ("All Files", "*.*"))
        )
        if not file_path:
            return
            
        try:
            self.points = FileReader.read_points(file_path)
            self.voronoi = VoronoiGenerator.generate(self.points)
            self._draw_diagram()
            
            # Enable exports
            self.btn_export_svg.config(state=tk.NORMAL)
            self.btn_export_img.config(state=tk.NORMAL)
            messagebox.showinfo("Success", f"Loaded {len(self.points)} points and generated Voronoi diagram.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load or generate diagram:\n{e}")
            
    def _draw_diagram(self):
        self.canvas.delete("all")
        if not self.voronoi:
            return
            
        # Draw Voronoi regions (polygons)
        for region in self.voronoi.regions:
            # Skip empty regions or those pointing to infinity
            if not region or -1 in region:
                continue
            
            polygon_pts = []
            for idx in region:
                v = self.voronoi.vertices[idx]
                polygon_pts.extend([v.x, v.y])
                
            self.canvas.create_polygon(polygon_pts, outline="blue", fill="", width=2)
            
        # Draw original points as small red circles
        point_radius = 4
        for p in self.points:
            self.canvas.create_oval(
                p.x - point_radius, p.y - point_radius, 
                p.x + point_radius, p.y + point_radius, 
                fill="red", outline="red"
            )
            
    def _export_svg(self):
        if not self.voronoi:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".svg", filetypes=(("SVG Files", "*.svg"),))
        if file_path:
            try:
                strategy = SvgExportStrategy()
                strategy.export(self.voronoi, file_path, self.canvas_width, self.canvas_height)
                messagebox.showinfo("Success", "Exported SVG successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export SVG:\n{e}")
                
    def _export_img(self):
        if not self.voronoi:
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=(("PNG Files", "*.png"),))
        if file_path:
            try:
                strategy = ImageExportStrategy()
                strategy.export(self.voronoi, file_path, self.canvas_width, self.canvas_height)
                messagebox.showinfo("Success", "Exported Image successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export Image:\n{e}")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()
