"""
pathfinder.py — BFS Pathfinding for Quoridor
Member 1 (Lead) — Game Engine

Responsibilities:
  - Verify that every wall placement leaves a valid path to goal
    for BOTH players (mandatory by game rules).
  - Provide shortest-path length (used by AI heuristics).
"""

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .board import Board

BOARD_SIZE = 9


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def has_path(board: "Board", player: int) -> bool:
    """
    Return True if *player* has at least one reachable path to their
    goal row given the current wall configuration.

    Uses BFS — O(N²) worst case which is fast on a 9×9 board.
    """
    start = board.get_pawn_pos(player)
    goal  = board.goal_row(player)
    return _bfs(board, start, goal) is not None


def shortest_path_length(board: "Board", player: int) -> int:
    """
    Return the fewest steps needed for *player* to reach their goal
    row, ignoring the opponent's pawn position (walls only).

    Returns a very large number if no path exists (shouldn't happen in
    a legal game state, but guards against edge cases).
    """
    start = board.get_pawn_pos(player)
    goal  = board.goal_row(player)
    result = _bfs(board, start, goal)
    return result if result is not None else 9999


def both_players_have_path(board: "Board") -> bool:
    """
    Convenience check — True only if BOTH players can reach their
    respective goals.  Called after every attempted wall placement.
    """
    return has_path(board, 1) and has_path(board, 2)


# ──────────────────────────────────────────────────────────────────────
# Core BFS
# ──────────────────────────────────────────────────────────────────────

def _bfs(board: "Board", start: tuple[int, int], goal_row: int):
    """
    BFS from *start* toward *goal_row*.

    Returns the number of steps to the nearest goal cell, or None if
    the goal is unreachable.

    NOTE: We deliberately ignore pawn positions here — pathfinding is
    purely about walls, because pawns can move out of the way.
    """
    visited: set[tuple[int, int]] = set()
    queue: deque[tuple[tuple[int, int], int]] = deque()
    queue.append((start, 0))

    while queue:
        (row, col), steps = queue.popleft()

        if row == goal_row:
            return steps

        if (row, col) in visited:
            continue
        visited.add((row, col))

        for nr, nc in _passable_neighbours(board, row, col):
            if (nr, nc) not in visited:
                queue.append(((nr, nc), steps + 1))

    return None


def _passable_neighbours(
    board: "Board", row: int, col: int
) -> list[tuple[int, int]]:
    """
    Return all grid cells reachable from (row, col) in one step,
    respecting walls but NOT pawn positions.
    """
    neighbours = []

    # UP — row-1
    if row > 0 and not _wall_blocks(board, row, col, row - 1, col):
        neighbours.append((row - 1, col))

    # DOWN — row+1
    if row < BOARD_SIZE - 1 and not _wall_blocks(board, row, col, row + 1, col):
        neighbours.append((row + 1, col))

    # LEFT — col-1
    if col > 0 and not _wall_blocks(board, row, col, row, col - 1):
        neighbours.append((row, col - 1))

    # RIGHT — col+1
    if col < BOARD_SIZE - 1 and not _wall_blocks(board, row, col, row, col + 1):
        neighbours.append((row, col + 1))

    return neighbours


# ──────────────────────────────────────────────────────────────────────
# Wall-blocking logic  (shared with move_validator)
# ──────────────────────────────────────────────────────────────────────

def _wall_blocks(
    board: "Board",
    r1: int, c1: int,
    r2: int, c2: int,
) -> bool:
    """
    Return True if a wall prevents movement from (r1,c1) to (r2,c2).

    Movement direction is determined by the difference:
      - Vertical move   (r changes): check horizontal walls
      - Horizontal move (c changes): check vertical walls

    Horizontal wall encoding:
        h_walls contains (row, col) meaning there is a wall segment
        on the BOTTOM edge of (row, col).  So movement from row r
        to row r+1 is blocked if (r, col) is in h_walls where col is
        either c1 or c2 (they are the same for vertical movement, but
        we need to check the cell on the upper side).

    Vertical wall encoding:
        v_walls contains (row, col) meaning there is a wall segment
        on the RIGHT edge of (row, col).  Movement from col c to c+1
        is blocked if (row, c) is in v_walls.
    """
    if r2 == r1 + 1:
        # Moving DOWN: blocked by h_wall on bottom of (r1, c1)
        return board.has_h_wall_below(r1, c1)

    if r2 == r1 - 1:
        # Moving UP: blocked by h_wall on bottom of (r2, c1)
        return board.has_h_wall_below(r2, c1)

    if c2 == c1 + 1:
        # Moving RIGHT: blocked by v_wall on right of (r1, c1)
        return board.has_v_wall_right(r1, c1)

    if c2 == c1 - 1:
        # Moving LEFT: blocked by v_wall on right of (r1, c2)
        return board.has_v_wall_right(r1, c2)

    return False  # same cell or diagonal — no wall check needed


# Export the helper so other modules can import it without duplication
wall_blocks = _wall_blocks
