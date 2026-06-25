from dataclasses import dataclass
from typing import Optional, Union
from .board import Board
from .player import Player
from .constants import PlayerId, BOARD_SIZE
from .wall import Wall
from .rules import get_valid_pawn_moves, is_wall_placement_valid

@dataclass
class PawnMove:
    player_id: PlayerId
    to_x: int
    to_y: int

@dataclass
class WallMove:
    player_id: PlayerId
    wall: Wall

Move = Union[PawnMove, WallMove]

class GameState:
    def __init__(self):
        self.board = Board()
        # Player 1 starts at bottom (x=4, y=8)
        self.p1 = Player(PlayerId.PLAYER_1, BOARD_SIZE // 2, BOARD_SIZE - 1)
        # Player 2 starts at top (x=4, y=0)
        self.p2 = Player(PlayerId.PLAYER_2, BOARD_SIZE // 2, 0)
        self.current_turn = PlayerId.PLAYER_1
        self.winner: Optional[PlayerId] = None

    def copy(self) -> 'GameState':
        new_state = GameState()
        new_state.board = self.board.copy()
        new_state.p1 = self.p1.copy()
        new_state.p2 = self.p2.copy()
        new_state.current_turn = self.current_turn
        new_state.winner = self.winner
        return new_state
        
    def get_current_player(self) -> Player:
        return self.p1 if self.current_turn == PlayerId.PLAYER_1 else self.p2
        
    def get_opponent(self) -> Player:
        return self.p2 if self.current_turn == PlayerId.PLAYER_1 else self.p1

    def get_player(self, player_id: PlayerId) -> Player:
        return self.p1 if player_id == PlayerId.PLAYER_1 else self.p2

    def is_game_over(self) -> bool:
        return self.winner is not None

    def execute_move(self, move: Move) -> bool:
        if self.is_game_over():
            return False
            
        current_player = self.get_current_player()
        if current_player.id != move.player_id:
            return False

        if isinstance(move, PawnMove):
            valid_moves = get_valid_pawn_moves(self.board, current_player, self.get_opponent())
            if (move.to_x, move.to_y) not in valid_moves:
                return False
            
            # Apply move
            current_player.x = move.to_x
            current_player.y = move.to_y
            
            # Check win condition
            if current_player.y == current_player.goal_y:
                self.winner = current_player.id

        elif isinstance(move, WallMove):
            if current_player.walls_left <= 0:
                return False
                
            if not is_wall_placement_valid(self.board, move.wall, self.p1, self.p2):
                return False
                
            # Apply wall placement
            self.board.add_wall(move.wall)
            current_player.walls_left -= 1

        # Switch turn
        if not self.is_game_over():
            self.current_turn = PlayerId.PLAYER_2 if self.current_turn == PlayerId.PLAYER_1 else PlayerId.PLAYER_1
            
        return True
