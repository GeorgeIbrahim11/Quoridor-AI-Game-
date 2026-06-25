import random
from game.game_state import GameState, Move, PawnMove, WallMove
from game.rules import get_valid_pawn_moves, is_wall_placement_valid
from game.constants import BOARD_SIZE, WallOrientation
from game.wall import Wall

def get_easy_ai_move(state: GameState) -> Move:
    """Random valid move. Prefers moving to placing walls randomly."""
    player = state.get_current_player()
    opponent = state.get_opponent()
    
    valid_moves = get_valid_pawn_moves(state.board, player, opponent)
    
    # 80% chance to just move, 20% to place a random valid wall
    if player.walls_left > 0 and random.random() < 0.2:
        # Try to find a valid wall
        for _ in range(50): # Try 50 random wall placements
            x = random.randint(0, BOARD_SIZE - 2)
            y = random.randint(0, BOARD_SIZE - 2)
            orientation = random.choice([WallOrientation.HORIZONTAL, WallOrientation.VERTICAL])
            wall = Wall(x, y, orientation)
            
            if is_wall_placement_valid(state.board, wall, state.p1, state.p2):
                return WallMove(player.id, wall)
                
    # Fallback to pawn move
    mx, my = random.choice(valid_moves)
    return PawnMove(player.id, mx, my)
