"""Color palette and visual theme helpers."""

from __future__ import annotations

import colorsys

APP_BACKGROUND_COLOR = "#f4f6fb"
PANEL_BACKGROUND_COLOR = "#e7ecf7"
CANVAS_BACKGROUND_COLOR = "#fbfcff"
CANVAS_BORDER_COLOR = "#b2bfd6"
BUTTON_BACKGROUND_COLOR = "#314e89"
BUTTON_TEXT_COLOR = "#ffffff"
BUTTON_ACTIVE_COLOR = "#4766a6"
STATUS_TEXT_COLOR = "#233252"
EDGE_COLOR = "#223047"
SITE_COLOR = "#d7263d"

MIN_CELL_SATURATION = 0.45
MIN_CELL_VALUE = 0.85
GOLDEN_ANGLE_RATIO = 0.61803398875


def get_cell_color(index: int) -> str:
    """Returns a deterministic, visually distinct color for a cell index."""
    hue = (index * GOLDEN_ANGLE_RATIO) % 1.0
    red, green, blue = colorsys.hsv_to_rgb(hue, MIN_CELL_SATURATION, MIN_CELL_VALUE)
    return _rgb_to_hex(red, green, blue)


def _rgb_to_hex(red: float, green: float, blue: float) -> str:
    red_255 = _to_channel(red)
    green_255 = _to_channel(green)
    blue_255 = _to_channel(blue)
    return f"#{red_255:02x}{green_255:02x}{blue_255:02x}"


def _to_channel(value: float) -> int:
    bounded = max(0.0, min(1.0, value))
    return int(round(bounded * 255))
