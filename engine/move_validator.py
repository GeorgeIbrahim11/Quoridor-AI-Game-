"""
move_validator.py — Pawn Move Validation for Quoridor
Member 1 (Lead) — Game Engine

Handles:
  1. Basic orthogonal moves
  2. Wall collision detection
  3. Jump-over (when pawns are adjacent)
  4. Diagonal escape (jump blocked by wall or board edge)
"""

from typing import TYPE_CHECKING
from .pathfinder import wall_blocks

if TYPE_CHECKING:
    from .board import Board

BOARD_SIZE = 9

# Cardinal directions as (delta_row, delta_col)
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def get_valid_moves(board: "Board", player: int) -> list[tuple[int, int]]:
    """
    Return a list of all valid destination squares for *player*'s pawn
    on the current board state.

    Returns list of (row, col) tuples the pawn can legally move to.
    """
    row, col = board.get_pawn_pos(player)
    opponent = board.opponent(player)
    opp_pos  = board.get_pawn_pos(opponent)

    moves: list[tuple[int, int]] = []

    for dr, dc in DIRECTIONS:
        nr, nc = row + dr, col + dc

        # Out of bounds
        if not _in_bounds(nr, nc):
            continue

        # Wall blocks this direction
        if wall_blocks(board, row, col, nr, nc):
            continue

        # Is the opponent pawn in that square?
        if (nr, nc) == opp_pos:
            jump_moves = _get_jump_moves(board, row, col, dr, dc, opp_pos)
            moves.extend(jump_moves)
        else:
            moves.append((nr, nc))

    return moves


def is_valid_move(board: "Board", player: int, dest: tuple[int, int]) -> bool:
    """Return True if moving *player*'s pawn to *dest* is legal."""
    return dest in get_valid_moves(board, player)


def apply_pawn_move(board: "Board", player: int, dest: tuple[int, int]) -> bool:
    """
    Move *player*'s pawn to *dest* and switch turns.

    Returns True on success, False if the move is illegal.
    """
    if not is_valid_move(board, player, dest):
        return False

    board.pawns[player] = dest

    # Check win condition
    if board.is_winner(player):
        board.winner = player

    board.switch_turn()
    return True


# ──────────────────────────────────────────────────────────────────────
# Jump logic
# ──────────────────────────────────────────────────────────────────────

def _get_jump_moves(
    board: "Board",
    row: int, col: int,
    dr: int, dc: int,
    opp_pos: tuple[int, int],
) -> list[tuple[int, int]]:
    """
    The moving pawn is at (row, col); opponent pawn is at opp_pos.
    Determine valid jump destinations.

    Rules:
      1. If straight jump (continue same direction past opponent) is
         clear of walls AND in bounds → straight jump only.
      2. Otherwise → diagonal escape in perpendicular directions
         that are not wall-blocked.
    """
    opp_r, opp_c = opp_pos
    jump_r, jump_c = opp_r + dr, opp_c + dc

    # Can we jump straight over?
    straight_ok = (
        _in_bounds(jump_r, jump_c)
        and not wall_blocks(board, opp_r, opp_c, jump_r, jump_c)
    )

    if straight_ok:
        return [(jump_r, jump_c)]

    # Diagonal escape — try the two perpendicular directions from opp cell
    escape: list[tuple[int, int]] = []
    for pdr, pdc in _perpendicular(dr, dc):
        er, ec = opp_r + pdr, opp_c + pdc
        if _in_bounds(er, ec) and not wall_blocks(board, opp_r, opp_c, er, ec):
            escape.append((er, ec))

    return escape


def _perpendicular(dr: int, dc: int) -> list[tuple[int, int]]:
    """Return the two directions perpendicular to (dr, dc)."""
    if dr != 0:
        return [(0, -1), (0, 1)]
    else:
        return [(-1, 0), (1, 0)]


def _in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE
