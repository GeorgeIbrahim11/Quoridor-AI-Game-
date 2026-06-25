from dataclasses import dataclass
from .constants import PlayerId, NUM_WALLS, BOARD_SIZE

@dataclass
class Player:
    id: PlayerId
    x: int
    y: int
    walls_left: int = NUM_WALLS

    def copy(self) -> 'Player':
        return Player(self.id, self.x, self.y, self.walls_left)
    
    @property
    def goal_y(self) -> int:
        if self.id == PlayerId.PLAYER_1:
            return 0  # Player 1 aims for the top row (y=0)
        else:
            return BOARD_SIZE - 1  # Player 2 aims for the bottom row (y=8)
