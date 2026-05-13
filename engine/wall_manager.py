"""
wall_manager.py — Wall Placement & Legality for Quoridor
Member 1 (Lead) — Game Engine

Rules enforced:
  1. Player must have walls remaining
  2. Wall anchor must be within valid range
  3. No wall segment overlap with existing walls
  4. No wall crossing (H wall crosses V wall and vice-versa)
  5. After placement, BOTH players must still have a path to their goal
"""

from typing import TYPE_CHECKING
from .pathfinder import both_players_have_path

if TYPE_CHECKING:
    from .board import Board

BOARD_SIZE = 9


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def get_valid_wall_placements(board: "Board", player: int) -> list[tuple[str, int, int]]:
    """
    Return every legal wall placement as a list of
        ('h', row, col)  or  ('v', row, col)
    where (row, col) is the anchor cell.

    NOTE: This can be expensive (up to ~128 placements × BFS each).
    The AI should call this; the GUI can call is_valid_wall() on demand.
    """
    if board.walls_remaining[player] == 0:
        return []

    valid = []
    for row in range(BOARD_SIZE - 1):
        for col in range(BOARD_SIZE - 1):
            for orientation in ("h", "v"):
                if _placement_legal(board, orientation, row, col):
                    valid.append((orientation, row, col))
    return valid


def is_valid_wall(
    board: "Board", player: int, orientation: str, row: int, col: int
) -> bool:
    """
    Return True if *player* can legally place a wall of the given
    orientation with anchor at (row, col).

    orientation: 'h' (horizontal) or 'v' (vertical)
    """
    if board.walls_remaining[player] == 0:
        return False
    return _placement_legal(board, orientation, row, col)


def apply_wall(
    board: "Board", player: int, orientation: str, row: int, col: int
) -> bool:
    """
    Place a wall and switch turns if the move is legal.

    Returns True on success, False on any violation.
    """
    if not is_valid_wall(board, player, orientation, row, col):
        return False

    _place_wall(board, orientation, row, col)
    board.walls_remaining[player] -= 1
    board.switch_turn()
    return True


# ──────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────

def _placement_legal(board: "Board", orientation: str, row: int, col: int) -> bool:
    """
    Full legality check (no wall-count check — handled by callers).

    Steps:
      A. Anchor in valid range
      B. No segment overlap
      C. No crossing
      D. Both players still reachable after placement (BFS)
    """
    # A — valid anchor range: anchor + 1 must still be on the board
    if row < 0 or col < 0:
        return False
    if orientation == "h" and (row >= BOARD_SIZE - 1 or col >= BOARD_SIZE - 1):
        return False
    if orientation == "v" and (row >= BOARD_SIZE - 1 or col >= BOARD_SIZE - 1):
        return False

    # B & C — overlap / crossing check (cheap, no BFS)
    if _overlaps_or_crosses(board, orientation, row, col):
        return False

    # D — path check (expensive BFS — only reached if B/C pass)
    _place_wall(board, orientation, row, col)
    reachable = both_players_have_path(board)
    _remove_wall(board, orientation, row, col)

    return reachable


def _overlaps_or_crosses(
    board: "Board", orientation: str, row: int, col: int
) -> bool:
    """
    Return True if the proposed wall overlaps or crosses an existing wall.

    Horizontal wall at anchor (r, c) occupies segments:
        h_walls: (r, c) and (r, c+1)
    Vertical wall at anchor (r, c) occupies segments:
        v_walls: (r, c) and (r+1, c)

    Crossing:
        A horizontal wall at (r, c) crosses a vertical wall if both
        segments (r, c) and (r, c+1) lie at the shared crossing point.
        Specifically, an H wall at (r, c) crosses a V wall at (r, c)
        because they share the internal junction between the two cells.

    Simplified crossing rule:
        H wall at (r, c)  crosses  V wall at (r, c)  — same anchor.
    """
    if orientation == "h":
        # Overlap: another H wall uses (r,c) or (r,c+1)
        if (row, col) in board.h_walls or (row, col + 1) in board.h_walls:
            return True
        # Cross: a V wall at the same anchor occupies the same junction
        if (row, col) in board.v_walls and (row + 1, col) in board.v_walls:
            return True

    else:  # "v"
        # Overlap: another V wall uses (r,c) or (r+1,c)
        if (row, col) in board.v_walls or (row + 1, col) in board.v_walls:
            return True
        # Cross: an H wall at the same anchor
        if (row, col) in board.h_walls and (row, col + 1) in board.h_walls:
            return True

    return False


def _place_wall(board: "Board", orientation: str, row: int, col: int):
    """Add wall segments to the board (no validation)."""
    if orientation == "h":
        board.h_walls.add((row, col))
        board.h_walls.add((row, col + 1))
    else:
        board.v_walls.add((row, col))
        board.v_walls.add((row + 1, col))


def _remove_wall(board: "Board", orientation: str, row: int, col: int):
    """Remove wall segments (used to undo the temporary placement in BFS check)."""
    if orientation == "h":
        board.h_walls.discard((row, col))
        board.h_walls.discard((row, col + 1))
    else:
        board.v_walls.discard((row, col))
        board.v_walls.discard((row + 1, col))
