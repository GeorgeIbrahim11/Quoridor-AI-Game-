import random
from game.game_state import GameState, Move, PawnMove, WallMove
from game.rules import get_valid_pawn_moves, is_wall_placement_valid
from game.constants import BOARD_SIZE, WallOrientation
from game.wall import Wall
from ai.pathfinding import get_shortest_path_length

def get_medium_ai_move(state: GameState) -> Move:
    """Heuristic-based AI: Always takes the shortest path. Places a wall if opponent is getting too close."""
    player = state.get_current_player()
    opponent = state.get_opponent()
    
    p_dist = get_shortest_path_length(state.board, player.x, player.y, player.goal_y)
    o_dist = get_shortest_path_length(state.board, opponent.x, opponent.y, opponent.goal_y)
    
    # If opponent is closer to their goal, try to block them
    if o_dist < p_dist and player.walls_left > 0 and random.random() < 0.6:
        # Try to find a wall that increases opponent's path length
        best_wall = None
        max_increase = 0
        
        # Simple heuristic: try walls around the opponent
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x = opponent.x + dx
                y = opponent.y + dy
                for orientation in [WallOrientation.HORIZONTAL, WallOrientation.VERTICAL]:
                    wall = Wall(x, y, orientation)
                    if 0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1:
                        if is_wall_placement_valid(state.board, wall, state.p1, state.p2):
                            # Test the wall
                            state.board.walls.add(wall)
                            new_o_dist = get_shortest_path_length(state.board, opponent.x, opponent.y, opponent.goal_y)
                            state.board.walls.remove(wall)
                            
                            increase = new_o_dist - o_dist
                            if increase > max_increase:
                                max_increase = increase
                                best_wall = wall
                                
        if best_wall and max_increase > 0:
            return WallMove(player.id, best_wall)
            
    # Otherwise, move along the shortest path
    valid_moves = get_valid_pawn_moves(state.board, player, opponent)
    best_move = None
    min_dist = float('inf')
    
    for mx, my in valid_moves:
        dist = get_shortest_path_length(state.board, mx, my, player.goal_y)
        if dist < min_dist:
            min_dist = dist
            best_move = (mx, my)
            
    if best_move:
        return PawnMove(player.id, best_move[0], best_move[1])
        
    # Fallback
    mx, my = random.choice(valid_moves)
    return PawnMove(player.id, mx, my)
