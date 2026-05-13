"""
test_engine.py — Full Test Suite for the Quoridor Engine
Run with:  python test_engine.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import Game
from engine.board import Board
from engine.pathfinder import has_path, shortest_path_length, wall_blocks
from engine.move_validator import get_valid_moves, is_valid_move
from engine.wall_manager import is_valid_wall, apply_wall

PASS = "✅ PASS"
FAIL = "❌ FAIL"

results = []

def check(name, condition):
    status = PASS if condition else FAIL
    results.append((name, condition))
    print(f"  {status}  {name}")


# ══════════════════════════════════════════════════════════════════════
print("\n── Board Initialisation ──")
# ══════════════════════════════════════════════════════════════════════

game = Game()
state = game.get_state()

check("P1 starts at (0,4)",   state.pawns[1] == (0, 4))
check("P2 starts at (8,4)",   state.pawns[2] == (8, 4))
check("P1 has 10 walls",      state.walls_remaining[1] == 10)
check("P2 has 10 walls",      state.walls_remaining[2] == 10)
check("Player 1 goes first",  state.current_turn == 1)
check("No winner at start",   state.winner is None)
check("No walls at start",    len(state.h_walls) == 0 and len(state.v_walls) == 0)


# ══════════════════════════════════════════════════════════════════════
print("\n── Basic Pawn Movement ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()

# P1 valid moves from (0,4): down(1,4), left(0,3), right(0,5) — NOT up (out of bounds)
moves = game.get_valid_moves(1)
check("P1 can move down",    (1, 4) in moves)
check("P1 can move left",    (0, 3) in moves)
check("P1 can move right",   (0, 5) in moves)
check("P1 cannot move up",   (-1, 4) not in moves)
check("P1 has 3 moves",      len(moves) == 3)

ok = game.move_pawn(1, (1, 4))
check("P1 moves to (1,4)",   ok)
check("Turn switches to P2", game.get_state().current_turn == 2)
check("P1 position updated", game.get_state().pawns[1] == (1, 4))

# Wrong turn
check("P1 can't move on P2's turn", not game.move_pawn(1, (2, 4)))


# ══════════════════════════════════════════════════════════════════════
print("\n── Wall Placement Basics ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()

# Place a horizontal wall at (3, 3) — blocks movement between row 3 and 4
ok = game.place_wall(1, "h", 3, 3)
check("H wall placed at (3,3)",  ok)
check("Turn switches after wall", game.get_state().current_turn == 2)
check("P1 wall count decreases", game.get_state().walls_remaining[1] == 9)
check("h_walls has 2 segments",  len(game.get_state().h_walls) == 2)

# Wall segments should block vertical movement
b = game.board
check("Wall blocks (3,3)->(4,3)", wall_blocks(b, 3, 3, 4, 3))
check("Wall blocks (3,4)->(4,4)", wall_blocks(b, 3, 4, 4, 4))
check("Wall does NOT block (3,2)->(4,2)", not wall_blocks(b, 3, 2, 4, 2))


# ══════════════════════════════════════════════════════════════════════
print("\n── Wall Overlap / Cross Prevention ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
game.place_wall(1, "h", 3, 3)   # P1 places H wall at (3,3)

# P2's turn — try to overlap same H wall
check("Cannot place overlapping H wall (same anchor)",
      not game.place_wall(2, "h", 3, 3))

check("Cannot place overlapping H wall (shifted by 1)",
      not game.place_wall(2, "h", 3, 4))

# Crossing: V wall at same anchor should be blocked
check("Cannot place crossing V wall at (3,3)",
      not game.place_wall(2, "v", 3, 3))


# ══════════════════════════════════════════════════════════════════════
print("\n── Path Blocking Prevention ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()

# Build a wall that would completely seal off P1's path
# Fill columns 0-6 bottom edge of row 4
# (This simulates a near-complete blockade)
b = game.board
# Manually add walls to simulate attempted blockade
# Place 4 H walls across most of row 4
# anchor at (4,0),(4,2),(4,4),(4,6) — each covers 2 cells → covers cols 0-7
for anchor_col in [0, 2, 4, 6]:
    apply_wall(b, 1, "h", 4, anchor_col)
    b.walls_remaining[1] -= 1

# Now try to place last wall that would block col 7-8 fully
# and seal P1 completely — this should be REJECTED
check("Cannot place wall that fully blocks P1's path",
      not is_valid_wall(b, 1, "h", 4, 7))

# But P1 should still have a path around the existing walls
check("P1 still has a path after partial blockade",
      has_path(b, 1))


# ══════════════════════════════════════════════════════════════════════
print("\n── Pathfinder ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
b = game.board

check("P1 has path at start",  has_path(b, 1))
check("P2 has path at start",  has_path(b, 2))
check("P1 path length ~8",     shortest_path_length(b, 1) == 8)
check("P2 path length ~8",     shortest_path_length(b, 2) == 8)


# ══════════════════════════════════════════════════════════════════════
print("\n── Jump Over Opponent ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
b = game.board

# Manually position pawns adjacent to each other
b.pawns[1] = (4, 4)
b.pawns[2] = (5, 4)
b.current_turn = 1

moves = get_valid_moves(b, 1)
check("P1 can jump over P2 to (6,4)", (6, 4) in moves)
check("P1 cannot land ON P2 at (5,4)", (5, 4) not in moves)


# ══════════════════════════════════════════════════════════════════════
print("\n── Diagonal Escape (Jump Blocked by Wall) ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
b = game.board

# P1 at (4,4), P2 at (5,4), wall below P2 at row 5 blocks straight jump
b.pawns[1] = (4, 4)
b.pawns[2] = (5, 4)
b.current_turn = 1
b.h_walls.add((5, 4))   # wall below P2 — blocks (5,4)->(6,4)

moves = get_valid_moves(b, 1)
check("P1 cannot straight-jump (wall blocks)",  (6, 4) not in moves)
check("P1 can escape diagonally to (5,3)",       (5, 3) in moves)
check("P1 can escape diagonally to (5,5)",       (5, 5) in moves)


# ══════════════════════════════════════════════════════════════════════
print("\n── Win Condition ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
b = game.board

# Move P1 to one step before goal, P2 out of the way
b.pawns[1] = (7, 4)
b.pawns[2] = (8, 0)   # move P2 off the goal cell
b.current_turn = 1

ok = game.move_pawn(1, (8, 4))
state = game.get_state()
check("P1 moves to goal row (8,4)",  ok)
check("Winner is Player 1",          state.winner == 1)
check("Game is over",                game.board.is_game_over())
check("No further moves accepted",   not game.move_pawn(2, (7, 4)))


# ══════════════════════════════════════════════════════════════════════
print("\n── Reset ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
state = game.get_state()
check("After reset: P1 back to (0,4)",    state.pawns[1] == (0, 4))
check("After reset: no winner",           state.winner is None)
check("After reset: walls restored",      state.walls_remaining[1] == 10)
check("After reset: P1 goes first",       state.current_turn == 1)


# ══════════════════════════════════════════════════════════════════════
print("\n── Board Clone (for AI) ──")
# ══════════════════════════════════════════════════════════════════════

game.reset()
game.move_pawn(1, (1, 4))   # P1 moves

clone = game.clone_board()
# Mutate clone — original should be unchanged
clone.pawns[2] = (6, 4)
clone.h_walls.add((3, 3))

check("Clone mutation doesn't affect original pawn",  game.board.pawns[2] == (8, 4))
check("Clone mutation doesn't affect original walls", (3, 3) not in game.board.h_walls)


# ══════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════

total   = len(results)
passed  = sum(1 for _, ok in results if ok)
failed  = total - passed

print(f"\n{'═'*45}")
print(f"  Results: {passed}/{total} passed   {failed} failed")
print(f"{'═'*45}\n")

if failed:
    print("Failed tests:")
    for name, ok in results:
        if not ok:
            print(f"  ❌ {name}")
    sys.exit(1)
else:
    print("All tests passed! ✅")
