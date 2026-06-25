from game.game_state import GameState, Move
from .minimax import iterative_deepening

def get_hard_ai_move(state: GameState) -> Move:
    """Uses Iterative Deepening Minimax with Alpha-Beta pruning to find the best move."""
    # 3.0 seconds is a good balance for a "Hard" AI in a typical project
    TIME_LIMIT = 3.0
    best_move = iterative_deepening(state, time_limit=TIME_LIMIT)
    
    if best_move is None:
        # Fallback to medium AI if something goes wrong (e.g. timeout on depth 1)
        from .medium_ai import get_medium_ai_move
        return get_medium_ai_move(state)
        
    return best_move
