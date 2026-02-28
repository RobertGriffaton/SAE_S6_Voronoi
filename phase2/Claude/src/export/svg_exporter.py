"""
svg_exporter.py — Exports a VoronoiDiagram to an SVG file.

Generates plain SVG (no external libraries required beyond the standard
library).  Infinite ridges are clipped to the diagram's bounding box so
the output is always bounded and viewable.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, Tuple
import xml.etree.ElementTree as ET

import numpy as np

from src.core.models import BoundingBox, VoronoiDiagram
from src.export.exporter_base import DiagramExporter

# Visual constants ─ no magic numbers
SVG_BACKGROUND_COLOR: str = "#ffffff"
RIDGE_COLOR: str = "#3a7bd5"
RIDGE_WIDTH: float = 1.0
SITE_COLOR: str = "#e74c3c"
SITE_RADIUS: float = 3.0
VIEWPORT_PADDING: float = 5.0  # pixels of white-space around the bounding box


class SVGExporter(DiagramExporter):
    """Concrete Strategy: writes Voronoi diagram as an SVG file."""

    @property
    def file_extension(self) -> str:
        return ".svg"

    def export(self, diagram: VoronoiDiagram, output_path: Path) -> None:
        bb = diagram.bounding_box
        vp_width = bb.width + 2 * VIEWPORT_PADDING
        vp_height = bb.height + 2 * VIEWPORT_PADDING

        svg = ET.Element(
            "svg",
            xmlns="http://www.w3.org/2000/svg",
            width=str(round(vp_width, 2)),
            height=str(round(vp_height, 2)),
            viewBox=f"0 0 {round(vp_width, 2)} {round(vp_height, 2)}",
        )

        # Background
        ET.SubElement(svg, "rect", width="100%", height="100%", fill=SVG_BACKGROUND_COLOR)

        # Ridges
        for rv, rp in zip(diagram.ridge_vertices, diagram.ridge_points):
            segment = self._compute_ridge_segment(rv, rp, diagram)
            if segment is None:
                continue
            p1, p2 = segment
            ET.SubElement(
                svg,
                "line",
                x1=str(round(self._to_vp_x(p1[0], bb), 2)),
                y1=str(round(self._to_vp_y(p1[1], bb), 2)),
                x2=str(round(self._to_vp_x(p2[0], bb), 2)),
                y2=str(round(self._to_vp_y(p2[1], bb), 2)),
                stroke=RIDGE_COLOR,
                **{"stroke-width": str(RIDGE_WIDTH)},
            )

        # Site markers
        for site in diagram.sites:
            ET.SubElement(
                svg,
                "circle",
                cx=str(round(self._to_vp_x(site.x, bb), 2)),
                cy=str(round(self._to_vp_y(site.y, bb), 2)),
                r=str(SITE_RADIUS),
                fill=SITE_COLOR,
            )

        tree = ET.ElementTree(svg)
        ET.indent(tree, space="  ")
        tree.write(str(output_path), encoding="unicode", xml_declaration=False)

    # ------------------------------------------------------------------
    # Coordinate helpers
    # ------------------------------------------------------------------

    def _to_vp_x(self, x: float, bb: BoundingBox) -> float:
        """Convert world-x to viewport-x (flip not needed for x)."""
        return x - bb.x_min + VIEWPORT_PADDING

    def _to_vp_y(self, y: float, bb: BoundingBox) -> float:
        """Convert world-y to viewport-y (SVG y-axis is flipped)."""
        return bb.y_max - y + VIEWPORT_PADDING

    # ------------------------------------------------------------------
    # Infinite ridge clipping
    # ------------------------------------------------------------------

    def _compute_ridge_segment(
        self,
        ridge_vertex_indices: List[int],
        ridge_point_indices: List[int],
        diagram: VoronoiDiagram,
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Return (p1, p2) world coordinates for the ridge, or None if outside bbox.

        For infinite ridges (one index == -1) the far endpoint is computed by
        projecting outward from the finite vertex along the perpendicular
        bisector of the two generating sites.
        """
        bb = diagram.bounding_box
        i, j = ridge_vertex_indices

        if i >= 0 and j >= 0:
            # Finite ridge
            return diagram.vertices[i], diagram.vertices[j]

        # Infinite ridge — find the finite vertex
        finite_idx = i if i >= 0 else j
        if finite_idx < 0:
            return None  # both endpoints at infinity — skip

        finite_vertex = diagram.vertices[finite_idx]

        # Direction = perpendicular to the segment joining the two sites
        p_idx, q_idx = ridge_point_indices
        p = diagram.sites[p_idx].to_array()
        q = diagram.sites[q_idx].to_array()
        midpoint = (p + q) / 2.0
        direction = np.array([-(q[1] - p[1]), q[0] - p[0]])

        # Ensure the direction points away from the interior of the diagram
        center = np.mean([[s.x, s.y] for s in diagram.sites], axis=0)
        if np.dot(midpoint - center, direction) < 0:
            direction = -direction

        # Normalise and scale to a length guaranteed to exit the bounding box
        norm = np.linalg.norm(direction)
        if norm == 0:
            return None
        far_length = max(bb.width, bb.height) * 2
        far_point = finite_vertex + (direction / norm) * far_length

        return finite_vertex, far_point
