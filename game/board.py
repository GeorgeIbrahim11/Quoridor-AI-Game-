from typing import Set
from .constants import BOARD_SIZE, WallOrientation
from .wall import Wall

class Board:
    def __init__(self):
        self.walls: Set[Wall] = set()

    def copy(self) -> 'Board':
        new_board = Board()
        new_board.walls = self.walls.copy()
        return new_board

    def add_wall(self, wall: Wall) -> bool:
        """Adds a wall if valid structurally (doesn't check pathfinding). Returns True if added."""
        if not self.is_wall_valid(wall):
            return False
        self.walls.add(wall)
        return True
        
    def remove_wall(self, wall: Wall):
        if wall in self.walls:
            self.walls.remove(wall)

    def is_wall_valid(self, wall: Wall) -> bool:
        """Checks if a wall placement is structurally valid (bounds and intersections)."""
        if not (0 <= wall.x < BOARD_SIZE - 1 and 0 <= wall.y < BOARD_SIZE - 1):
            return False

        for w in self.walls:
            if w.x == wall.x and w.y == wall.y:
                return False # Crossing in the center or same wall completely overlapping
            if wall.orientation == WallOrientation.HORIZONTAL and w.orientation == WallOrientation.HORIZONTAL:
                if w.y == wall.y and abs(w.x - wall.x) == 1:
                    return False # Overlap horizontally
            if wall.orientation == WallOrientation.VERTICAL and w.orientation == WallOrientation.VERTICAL:
                if w.x == wall.x and abs(w.y - wall.y) == 1:
                    return False # Overlap vertically

        return True
    
    def blocks_movement(self, from_x: int, from_y: int, to_x: int, to_y: int) -> bool:
        """Check if a wall blocks movement between two adjacent cells."""
        if abs(from_x - to_x) + abs(from_y - to_y) != 1:
            return False
            
        if from_x == to_x: # Vertical movement (moving along y)
            min_y = min(from_y, to_y)
            wall1 = Wall(from_x, min_y, WallOrientation.HORIZONTAL)
            wall2 = Wall(from_x - 1, min_y, WallOrientation.HORIZONTAL)
            return wall1 in self.walls or wall2 in self.walls
        else: # Horizontal movement (moving along x)
            min_x = min(from_x, to_x)
            wall1 = Wall(min_x, from_y, WallOrientation.VERTICAL)
            wall2 = Wall(min_x, from_y - 1, WallOrientation.VERTICAL)
            return wall1 in self.walls or wall2 in self.walls
