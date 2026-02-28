from dataclasses import dataclass

@dataclass(frozen=True)
class Point:
    """
    Represents a 2D point with x and y coordinates.
    Immutable due to frozen=True.
    """
    x: float
    y: float
