"""
exporter_base.py — Strategy interface for diagram exporters.

The Strategy pattern lets the UI call exporter.export(diagram, path) without
knowing whether it's writing SVG, PNG, or any future format.  Adding a new
format requires only a new class — no changes to existing code (OCP).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from src.core.models import VoronoiDiagram


class DiagramExporter(ABC):
    """Abstract base class (Strategy) for exporting a VoronoiDiagram."""

    @abstractmethod
    def export(self, diagram: VoronoiDiagram, output_path: Path) -> None:
        """
        Write *diagram* to *output_path*.

        Parameters
        ----------
        diagram     : the computed Voronoi diagram
        output_path : destination file path (including extension)

        Raises
        ------
        IOError / OSError on write failure.
        """

    @property
    @abstractmethod
    def file_extension(self) -> str:
        """Return the canonical file extension for this format (e.g. '.svg')."""
