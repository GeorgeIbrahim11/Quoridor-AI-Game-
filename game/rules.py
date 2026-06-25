from typing import List, Tuple
from .board import Board
from .player import Player
from .constants import Direction, BOARD_SIZE
from ai.pathfinding import has_path
from .wall import Wall

def get_valid_pawn_moves(board: Board, current_player: Player, opponent: Player) -> List[Tuple[int, int]]:
    """Returns a list of valid (x, y) coordinates the current player can move to."""
    valid_moves = []
    cx, cy = current_player.x, current_player.y
    ox, oy = opponent.x, opponent.y

    for d in Direction:
        dx, dy = d.value
        nx, ny = cx + dx, cy + dy

        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
            if not board.blocks_movement(cx, cy, nx, ny):
                # Normal move
                if (nx, ny) != (ox, oy):
                    valid_moves.append((nx, ny))
                else:
                    # Jump over opponent
                    jump_x, jump_y = nx + dx, ny + dy
                    # Check if straight jump is possible
                    can_straight_jump = False
                    if 0 <= jump_x < BOARD_SIZE and 0 <= jump_y < BOARD_SIZE:
                        if not board.blocks_movement(nx, ny, jump_x, jump_y):
                            valid_moves.append((jump_x, jump_y))
                            can_straight_jump = True
                    
                    # If straight jump is blocked by a wall or board edge, diagonal jump is allowed
                    if not can_straight_jump:
                        # Check diagonals from the opponent's position
                        # If moving vertically (dx=0), diagonals are at x-1 and x+1
                        # If moving horizontally (dy=0), diagonals are at y-1 and y+1
                        if dx == 0: # Moved vertically
                            for ddx in [-1, 1]:
                                diag_x, diag_y = nx + ddx, ny
                                if 0 <= diag_x < BOARD_SIZE and 0 <= diag_y < BOARD_SIZE:
                                    if not board.blocks_movement(nx, ny, diag_x, diag_y):
                                        valid_moves.append((diag_x, diag_y))
                        else: # Moved horizontally
                            for ddy in [-1, 1]:
                                diag_x, diag_y = nx, ny + ddy
                                if 0 <= diag_x < BOARD_SIZE and 0 <= diag_y < BOARD_SIZE:
                                    if not board.blocks_movement(nx, ny, diag_x, diag_y):
                                        valid_moves.append((diag_x, diag_y))
    return valid_moves

def is_wall_placement_valid(board: Board, wall: Wall, p1: Player, p2: Player) -> bool:
    """Checks if a wall placement is valid and doesn't block any player from reaching their goal."""
    if not board.is_wall_valid(wall):
        return False
        
    # Temporarily add the wall
    board.walls.add(wall)
    
    # Check paths
    p1_can_reach = has_path(board, p1)
    p2_can_reach = has_path(board, p2)
    
    # Remove the wall
    board.walls.remove(wall)
    
    return p1_can_reach and p2_can_reach
