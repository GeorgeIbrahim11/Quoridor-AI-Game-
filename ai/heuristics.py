from game.game_state import GameState
from game.constants import PlayerId
from ai.pathfinding import get_shortest_path_length

def evaluate_state(state: GameState, maximizing_player: PlayerId) -> float:
    """
    Evaluates the board state.
    Positive score is good for maximizing_player, negative is bad.
    """
    if state.is_game_over():
        if state.winner == maximizing_player:
            return 100000.0
        else:
            return -100000.0
            
    p1 = state.p1
    p2 = state.p2
    
    p1_dist = get_shortest_path_length(state.board, p1.x, p1.y, p1.goal_y)
    p2_dist = get_shortest_path_length(state.board, p2.x, p2.y, p2.goal_y)
    
    # Base score: difference in shortest paths
    # We want our distance to be small and opponent's to be large
    if maximizing_player == PlayerId.PLAYER_1:
        # P1 wants to minimize p1_dist and maximize p2_dist
        path_score = (p2_dist - p1_dist) * 10.0
        wall_score = (p1.walls_left - p2.walls_left) * 5.0
    else:
        # P2 wants to minimize p2_dist and maximize p1_dist
        path_score = (p1_dist - p2_dist) * 10.0
        wall_score = (p2.walls_left - p1.walls_left) * 5.0
        
    return float(path_score + wall_score)
