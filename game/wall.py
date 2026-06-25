from dataclasses import dataclass
from .constants import WallOrientation

@dataclass(frozen=True)
class Wall:
    x: int
    y: int
    orientation: WallOrientation
