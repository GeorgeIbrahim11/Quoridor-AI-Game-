"""
board.py — Quoridor Board State & Data Model
Member 1 (Lead) — Game Engine
"""

BOARD_SIZE = 9


class Board:
    """
    Represents the full state of a Quoridor game.

    Coordinate system:
        - (row, col) where row 0 is Player 1's starting side (top)
        - row 8 is Player 2's starting side (bottom)
        - Player 1 moves toward row 8, Player 2 moves toward row 0

    Wall storage:
        - h_walls: set of (row, col) meaning a horizontal wall exists
          on the BOTTOM edge of cell (row, col), blocking movement
          between row <-> row+1 across columns col and col+1.
        - v_walls: set of (row, col) meaning a vertical wall exists
          on the RIGHT edge of cell (row, col), blocking movement
          between col <-> col+1 across rows row and row+1.

    Each wall occupies TWO cells.  When you place a horizontal wall
    at anchor (r, c) it registers (r, c) AND (r, c+1) in h_walls.
    Likewise a vertical wall at anchor (r, c) registers (r, c) AND
    (r+1, c) in v_walls.
    """

    def __init__(self):
        self.reset()

    # ------------------------------------------------------------------
    # Initialisation / Reset
    # ------------------------------------------------------------------

    def reset(self):
        """Restore the board to its starting state."""
        # Pawn positions: player_id -> (row, col)
        self.pawns = {
            1: (0, 4),   # top centre
            2: (8, 4),   # bottom centre
        }

        # Walls remaining for each player
        self.walls_remaining = {1: 10, 2: 10}

        # Wall registries (see class docstring for semantics)
        self.h_walls: set[tuple[int, int]] = set()
        self.v_walls: set[tuple[int, int]] = set()

        # Whose turn it is (1 or 2)
        self.current_turn = 1

        # Winner (None until someone wins)
        self.winner: int | None = None

    # ------------------------------------------------------------------
    # Basic Queries
    # ------------------------------------------------------------------

    def get_pawn_pos(self, player: int) -> tuple[int, int]:
        """Return (row, col) for the given player's pawn."""
        return self.pawns[player]

    def opponent(self, player: int) -> int:
        """Return the opponent's player id."""
        return 2 if player == 1 else 1

    def goal_row(self, player: int) -> int:
        """Return the row a player must reach to win."""
        return 8 if player == 1 else 0

    def is_winner(self, player: int) -> bool:
        """Return True if the player has reached their goal row."""
        row, _ = self.pawns[player]
        return row == self.goal_row(player)

    def is_game_over(self) -> bool:
        return self.winner is not None

    # ------------------------------------------------------------------
    # Turn management
    # ------------------------------------------------------------------

    def switch_turn(self):
        self.current_turn = self.opponent(self.current_turn)

    # ------------------------------------------------------------------
    # Wall helpers (used by wall_manager and pathfinder)
    # ------------------------------------------------------------------

    def has_h_wall_below(self, row: int, col: int) -> bool:
        """
        True if there is a horizontal wall segment on the bottom edge
        of cell (row, col) — i.e. it blocks movement from row to row+1.
        """
        return (row, col) in self.h_walls

    def has_v_wall_right(self, row: int, col: int) -> bool:
        """
        True if there is a vertical wall segment on the right edge of
        cell (row, col) — i.e. it blocks movement from col to col+1.
        """
        return (row, col) in self.v_walls

    # ------------------------------------------------------------------
    # State snapshot (useful for AI search)
    # ------------------------------------------------------------------

    def clone(self) -> "Board":
        """Return a deep copy of the board."""
        b = Board.__new__(Board)
        b.pawns = dict(self.pawns)
        b.walls_remaining = dict(self.walls_remaining)
        b.h_walls = set(self.h_walls)
        b.v_walls = set(self.v_walls)
        b.current_turn = self.current_turn
        b.winner = self.winner
        return b

    # ------------------------------------------------------------------
    # Debug / display
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Simple ASCII representation for testing."""
        lines = []
        p1r, p1c = self.pawns[1]
        p2r, p2c = self.pawns[2]

        for row in range(BOARD_SIZE):
            # Cell row
            row_str = ""
            for col in range(BOARD_SIZE):
                if (row, col) == (p1r, p1c):
                    cell = "1"
                elif (row, col) == (p2r, p2c):
                    cell = "2"
                else:
                    cell = "."

                row_str += cell

                # Vertical wall on the right edge?
                if col < BOARD_SIZE - 1:
                    row_str += "|" if self.has_v_wall_right(row, col) else " "

            lines.append(row_str)

            # Horizontal wall row below
            if row < BOARD_SIZE - 1:
                wall_row = ""
                for col in range(BOARD_SIZE):
                    wall_row += "—" if self.has_h_wall_below(row, col) else " "
                    if col < BOARD_SIZE - 1:
                        wall_row += " "
                lines.append(wall_row)

        header = f"Turn: Player {self.current_turn} | " \
                 f"Walls — P1:{self.walls_remaining[1]}  P2:{self.walls_remaining[2]}"
        return header + "\n" + "\n".join(lines)
