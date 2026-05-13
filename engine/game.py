"""
game.py — Game Controller for Quoridor
Member 1 (Lead) — Game Engine

Added: Undo / Redo support via snapshot history.
"""

from dataclasses import dataclass, field
from .board import Board
from .move_validator import get_valid_moves, apply_pawn_move
from .wall_manager import get_valid_wall_placements, apply_wall, is_valid_wall
from .pathfinder import shortest_path_length

MAX_HISTORY = 50   # maximum undo steps stored


@dataclass
class GameState:
    pawns:            dict
    walls_remaining:  dict
    h_walls:          set
    v_walls:          set
    current_turn:     int
    winner:           "int | None"
    valid_pawn_moves: list
    valid_walls:      list = field(default_factory=list)


class Game:
    """
    High-level controller.  One instance per game session.

    Undo/Redo:
        game.can_undo()  → bool
        game.can_redo()  → bool
        game.undo()      → bool   (True if successful)
        game.redo()      → bool   (True if successful)

    Every move_pawn / place_wall call saves a snapshot first.
    Undo restores the previous snapshot; redo re-applies it.
    """

    def __init__(self):
        self.board        = Board()
        self._undo_stack  = []   # list of Board clones (past states)
        self._redo_stack  = []   # list of Board clones (future states)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def reset(self):
        self.board.reset()
        self._undo_stack.clear()
        self._redo_stack.clear()

    def move_pawn(self, player: int, dest: tuple) -> bool:
        if self._wrong_turn(player) or self.board.is_game_over():
            return False
        self._save_snapshot()
        ok = apply_pawn_move(self.board, player, dest)
        if not ok:
            self._undo_stack.pop()   # discard — nothing changed
        return ok

    def place_wall(self, player: int, orientation: str, row: int, col: int) -> bool:
        if self._wrong_turn(player) or self.board.is_game_over():
            return False
        self._save_snapshot()
        ok = apply_wall(self.board, player, orientation, row, col)
        if not ok:
            self._undo_stack.pop()
        return ok

    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def undo(self) -> bool:
        """Restore the previous game state."""
        if not self.can_undo():
            return False
        self._redo_stack.append(self.board.clone())   # save current for redo
        self.board = self._undo_stack.pop()
        return True

    def redo(self) -> bool:
        """Re-apply the move that was just undone."""
        if not self.can_redo():
            return False
        self._undo_stack.append(self.board.clone())   # save current for undo
        self.board = self._redo_stack.pop()
        return True

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_valid_moves(self, player: int) -> list:
        return get_valid_moves(self.board, player)

    def get_valid_wall_placements(self, player: int) -> list:
        return get_valid_wall_placements(self.board, player)

    def is_valid_wall(self, player: int, orientation: str, row: int, col: int) -> bool:
        return is_valid_wall(self.board, player, orientation, row, col)

    def get_path_length(self, player: int) -> int:
        return shortest_path_length(self.board, player)

    def get_state(self, include_valid_walls: bool = False) -> GameState:
        b       = self.board
        current = b.current_turn
        valid_walls = get_valid_wall_placements(b, current) if include_valid_walls else []
        return GameState(
            pawns            = dict(b.pawns),
            walls_remaining  = dict(b.walls_remaining),
            h_walls          = frozenset(b.h_walls),
            v_walls          = frozenset(b.v_walls),
            current_turn     = current,
            winner           = b.winner,
            valid_pawn_moves = get_valid_moves(b, current),
            valid_walls      = valid_walls,
        )

    def clone_board(self) -> Board:
        return self.board.clone()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _wrong_turn(self, player: int) -> bool:
        return self.board.current_turn != player

    def _save_snapshot(self):
        self._undo_stack.append(self.board.clone())
        self._redo_stack.clear()          # new move wipes redo history
        if len(self._undo_stack) > MAX_HISTORY:
            self._undo_stack.pop(0)
