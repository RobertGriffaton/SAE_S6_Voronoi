"""Application entry point."""

from __future__ import annotations

import tkinter as tk

from voronoi_app.algorithms.half_plane import HalfPlaneVoronoiAlgorithm
from voronoi_app.exporters.image_exporter import ImageExporter
from voronoi_app.exporters.svg_exporter import SvgExporter
from voronoi_app.parsing import PointFileParser
from voronoi_app.services.diagram_service import VoronoiDiagramService
from voronoi_app.ui.app import VoronoiApp


def main() -> None:
    parser = PointFileParser()
    algorithm = HalfPlaneVoronoiAlgorithm()
    service = VoronoiDiagramService(algorithm)
    svg_exporter = SvgExporter()
    image_exporter = ImageExporter()

    root = tk.Tk()
    VoronoiApp(
        root=root,
        parser=parser,
        diagram_service=service,
        svg_exporter=svg_exporter,
        image_exporter=image_exporter,
    )
    root.mainloop()


if __name__ == "__main__":
    main()
