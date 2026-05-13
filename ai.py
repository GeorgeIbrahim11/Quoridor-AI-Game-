"""
ai.py — Quoridor AI Opponent (Member 3)
Difficulty levels: Easy, Medium, Hard

Called by gui.py:
    get_ai_move(game, difficulty="medium") -> tuple

Returns:
    ("pawn", (row, col))
    ("wall", "h"/"v", row, col)
"""

import random
import math
import sys, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine.board import Board
from engine.move_validator import apply_pawn_move, get_valid_moves
from engine.wall_manager import apply_wall, get_valid_wall_placements
from engine.pathfinder import shortest_path_length

AI_PLAYER    = 2
HUMAN_PLAYER = 1
DEPTH_HARD   = 3

# Track recent AI positions to detect and break loops
_position_history = []
MAX_HISTORY = 6


# ══════════════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════════════

def get_ai_move(game, difficulty: str = "medium") -> tuple:
    board = game.clone_board()
    if difficulty == "easy":
        return _easy_move(board)
    elif difficulty == "hard":
        return _hard_move(board)
    else:
        return _medium_move(board)


# ══════════════════════════════════════════════════════════════════════
# EASY — Random moves, occasional random wall
# ══════════════════════════════════════════════════════════════════════

def _easy_move(board: Board) -> tuple:
    if board.walls_remaining[AI_PLAYER] > 0 and random.random() < 0.10:
        walls = get_valid_wall_placements(board, AI_PLAYER)
        if walls:
            o, r, c = random.choice(walls)
            return ("wall", o, r, c)
    moves = get_valid_moves(board, AI_PLAYER)
    if moves:
        return ("pawn", random.choice(moves))
    walls = get_valid_wall_placements(board, AI_PLAYER)
    if walls:
        o, r, c = random.choice(walls)
        return ("wall", o, r, c)
    return ("pawn", board.pawns[AI_PLAYER])


# ══════════════════════════════════════════════════════════════════════
# MEDIUM — Greedy with wall usage
# ══════════════════════════════════════════════════════════════════════

def _medium_move(board: Board) -> tuple:
    """
    Greedy depth-1 search.
    Uses walls when they meaningfully lengthen the human's path.
    """
    best_score = -math.inf
    best_move  = None

    # Evaluate pawn moves
    for dest in get_valid_moves(board, AI_PLAYER):
        clone = board.clone()
        apply_pawn_move(clone, AI_PLAYER, dest)
        score = _evaluate(clone)
        if score > best_score:
            best_score = score
            best_move  = ("pawn", dest)

    # Evaluate walls — use them if they score better than best pawn move
    if board.walls_remaining[AI_PLAYER] > 0:
        walls = get_valid_wall_placements(board, AI_PLAYER)
        # Score all walls, pick top candidates
        scored = []
        for o, r, c in walls:
            clone = board.clone()
            apply_wall(clone, AI_PLAYER, o, r, c)
            score = _evaluate(clone)
            scored.append((score, o, r, c))
        scored.sort(reverse=True)
        # Only use a wall if it's clearly better than moving (threshold: +0.5)
        if scored and scored[0][0] > best_score + 0.5:
            s, o, r, c = scored[0]
            best_score = s
            best_move  = ("wall", o, r, c)

    return best_move if best_move else ("pawn", board.pawns[AI_PLAYER])


# ══════════════════════════════════════════════════════════════════════
# HARD — Minimax + Alpha-Beta + Loop detection
# ══════════════════════════════════════════════════════════════════════

def _hard_move(board: Board) -> tuple:
    global _position_history

    best_score = -math.inf
    best_move  = None
    alpha      = -math.inf
    beta       = math.inf

    # Get all candidate moves
    candidates = _generate_moves(board, AI_PLAYER)

    # Penalise moves that revisit recent positions (loop prevention)
    recent = set(_position_history[-MAX_HISTORY:])

    scored_candidates = []
    for move in candidates:
        penalty = 0
        if move[0] == "pawn" and move[1] in recent:
            penalty = -1.5   # discourage revisiting
        scored_candidates.append((move, penalty))

    for move, penalty in scored_candidates:
        clone = board.clone()
        _apply_move(clone, AI_PLAYER, move)
        score = _minimax(clone, DEPTH_HARD - 1, alpha, beta, maximising=False) + penalty
        if score > best_score:
            best_score = score
            best_move  = move
        alpha = max(alpha, best_score)

    # Record AI's chosen position
    if best_move and best_move[0] == "pawn":
        _position_history.append(best_move[1])
        if len(_position_history) > MAX_HISTORY * 2:
            _position_history = _position_history[-MAX_HISTORY:]

    return best_move if best_move else ("pawn", board.pawns[AI_PLAYER])


def _minimax(board: Board, depth: int, alpha: float, beta: float,
             maximising: bool) -> float:
    if board.winner == AI_PLAYER:
        return 10000 + depth
    if board.winner == HUMAN_PLAYER:
        return -10000 - depth
    if depth == 0:
        return _evaluate(board)

    player = AI_PLAYER if maximising else HUMAN_PLAYER
    moves  = _generate_moves(board, player)
    if not moves:
        return _evaluate(board)

    if maximising:
        value = -math.inf
        for move in moves:
            clone = board.clone()
            _apply_move(clone, player, move)
            value = max(value, _minimax(clone, depth-1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:
        value = math.inf
        for move in moves:
            clone = board.clone()
            _apply_move(clone, player, move)
            value = min(value, _minimax(clone, depth-1, alpha, beta, True))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


# ══════════════════════════════════════════════════════════════════════
# EVALUATION FUNCTION
# ══════════════════════════════════════════════════════════════════════

def _evaluate(board: Board) -> float:
    """
    Score from AI's perspective (higher = better for AI).

    Components:
      1. Path delta      — AI needs fewer steps than human (main signal)
      2. Walls remaining — having walls is future power
      3. Row progress    — closer to goal = better
    """
    ai_path    = shortest_path_length(board, AI_PLAYER)
    human_path = shortest_path_length(board, HUMAN_PLAYER)

    path_score     = (human_path - ai_path) * 2.0
    wall_score     = (board.walls_remaining[AI_PLAYER]
                      - board.walls_remaining[HUMAN_PLAYER]) * 0.5
    # AI (P2) starts row 8, moves toward row 0 — lower row = more progress
    ai_progress    = (8 - board.pawns[AI_PLAYER][0])
    human_progress = board.pawns[HUMAN_PLAYER][0]
    progress_score = (ai_progress - human_progress) * 0.3

    return path_score + wall_score + progress_score


# ══════════════════════════════════════════════════════════════════════
# MOVE GENERATION
# ══════════════════════════════════════════════════════════════════════

def _generate_moves(board: Board, player: int) -> list:
    """
    All pawn moves + top-scored wall placements.
    Limits branching factor for minimax speed.
    """
    moves = [("pawn", dest) for dest in get_valid_moves(board, player)]

    if board.walls_remaining[player] > 0:
        walls = get_valid_wall_placements(board, player)
        scored = []
        for o, r, c in walls:
            clone = board.clone()
            apply_wall(clone, player, o, r, c)
            score = _evaluate(clone) if player == AI_PLAYER else -_evaluate(clone)
            scored.append((score, o, r, c))
        scored.sort(reverse=True)
        for score, o, r, c in scored[:5]:   # top 5 walls only
            moves.append(("wall", o, r, c))

    return moves


def _apply_move(board: Board, player: int, move: tuple):
    if move[0] == "pawn":
        apply_pawn_move(board, player, move[1])
    elif move[0] == "wall":
        apply_wall(board, player, move[1], move[2], move[3])
