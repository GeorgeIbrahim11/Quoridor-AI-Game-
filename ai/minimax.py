import time
from typing import Tuple, List, Optional
from game.game_state import GameState, Move, PawnMove, WallMove
from game.constants import PlayerId, BOARD_SIZE, WallOrientation
from game.rules import get_valid_pawn_moves, is_wall_placement_valid
from game.wall import Wall
from .heuristics import evaluate_state
import random

def get_all_possible_moves(state: GameState) -> List[Move]:
    moves: List[Move] = []
    player = state.get_current_player()
    opponent = state.get_opponent()
    
    # Pawn moves
    valid_pawn_moves = get_valid_pawn_moves(state.board, player, opponent)
    for mx, my in valid_pawn_moves:
        moves.append(PawnMove(player.id, mx, my))
        
    # Wall moves
    if player.walls_left > 0:
        # Heuristic: only consider walls near both players to either block or protect
        wall_candidates = []
        # Focus on areas around both players
        for p in [player, opponent]:
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    x, y = p.x + dx, p.y + dy
                    if 0 <= x < BOARD_SIZE - 1 and 0 <= y < BOARD_SIZE - 1:
                        wall_candidates.append(Wall(x, y, WallOrientation.HORIZONTAL))
                        wall_candidates.append(Wall(x, y, WallOrientation.VERTICAL))
        
        valid_walls = []
        for w in set(wall_candidates):
            if is_wall_placement_valid(state.board, w, state.p1, state.p2):
                valid_walls.append(w)
                
        # Shuffle to avoid deterministic bias in truncated search
        random.shuffle(valid_walls)
        # Consider up to 12 walls to balance branching factor and defensive play
        for w in valid_walls[:12]:
            moves.append(WallMove(player.id, w))
            
    return moves

def order_moves(state: GameState, moves: List[Move], maximizing_player: PlayerId) -> List[Move]:
    """Basic move ordering: pawn moves first, then walls."""
    # In a more advanced version, we could use the previous depth's best move (PV)
    pawn_moves = [m for m in moves if isinstance(m, PawnMove)]
    wall_moves = [m for m in moves if isinstance(m, WallMove)]
    return pawn_moves + wall_moves

def minimax(state: GameState, depth: int, alpha: float, beta: float, maximizing_player: PlayerId, start_time: float, time_limit: float) -> Tuple[float, Optional[Move]]:
    # Check time limit
    if time.time() - start_time > time_limit:
        raise TimeoutError()

    if depth == 0 or state.is_game_over():
        return evaluate_state(state, maximizing_player), None
        
    is_maximizing = state.current_turn == maximizing_player
    best_move = None
    
    moves = get_all_possible_moves(state)
    if not moves:
        return evaluate_state(state, maximizing_player), None
        
    moves = order_moves(state, moves, maximizing_player)
    
    if is_maximizing:
        max_eval = float('-inf')
        for move in moves:
            next_state = state.copy()
            next_state.execute_move(move)
            
            try:
                eval_score, _ = minimax(next_state, depth - 1, alpha, beta, maximizing_player, start_time, time_limit)
            except TimeoutError:
                raise TimeoutError()
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in moves:
            next_state = state.copy()
            next_state.execute_move(move)
            
            try:
                eval_score, _ = minimax(next_state, depth - 1, alpha, beta, maximizing_player, start_time, time_limit)
            except TimeoutError:
                raise TimeoutError()
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def iterative_deepening(state: GameState, time_limit: float) -> Optional[Move]:
    start_time = time.time()
    best_move = None
    maximizing_player = state.current_turn
    
    # Try increasing depths
    for depth in range(1, 10): # Depth 10 is more than enough for Quoridor with this branching
        try:
            _, move = minimax(state, depth, float('-inf'), float('inf'), maximizing_player, start_time, time_limit)
            if move:
                best_move = move
        except TimeoutError:
            break
            
    return best_move
