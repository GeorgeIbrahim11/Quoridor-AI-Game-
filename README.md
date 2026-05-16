# Quoridor — AI Strategy Board Game

A complete implementation of the abstract strategy board game **Quoridor**, built in Python with Pygame.  
Developed as a term project for **CSE472s: Artificial Intelligence — Spring 2026**.

---

## Team Members

| Member | Role |
|--------|------|
| Member 1 (Lead) | Game Engine — board state, pathfinding, move & wall validation |
| Member 2 | GUI & UX — board renderer, interaction, HUD, menus |
| Member 3 | AI Opponent — Easy / Medium / Hard difficulty levels |

---

## Game Description

Quoridor is a 2-player strategy board game invented by Mirko Marchesi (1997).  
Each player controls a pawn starting at the centre of their baseline. The goal is to be the first to reach the opposite side of the 9×9 board.

On each turn a player must either:
- **Move** their pawn one step orthogonally, or
- **Place a wall** (2 cells long) to block the opponent — but walls can never completely seal off a player's path.

Special movement rules include **jumping over** an adjacent opponent pawn, and **diagonal escape** when a straight jump is blocked by a wall.

---

## Screenshots

<img width="500" height="613" alt="image" src="https://github.com/user-attachments/assets/84fe8bf6-afeb-4ec7-8ea5-ab029bcc0cb3" />


---



## Installation & Running

### Requirements
- Python 3.10 or higher
- Pygame

### Install dependencies

```bash
pip install pygame
```

### Folder structure

```
quoridor/
├── engine/
│   ├── __init__.py
│   ├── board.py
│   ├── pathfinder.py
│   ├── move_validator.py
│   ├── wall_manager.py
│   └── game.py
├── gui.py
├── ai.py
├── test_engine.py
└── README.md
```

### Run the game

```bash
cd quoridor
python gui.py
```

### Run engine tests

```bash
python test_engine.py
```

---

## Controls

### In-game keyboard

| Key | Action |
|-----|--------|
| Click pawn | Select it |
| Click green cell | Move pawn there |
| `W` | Toggle wall placement mode |
| `H` | Switch to horizontal wall |
| `V` | Switch to vertical wall |
| `Ctrl + Z` | Undo last move |
| `Ctrl + Y` | Redo undone move |
| `ESC` | Return to main menu |

### On-screen buttons

| Button | Action |
|--------|--------|
| ↩ Undo | Undo last move (greyed out if nothing to undo) |
| ↪ Redo | Redo undone move (greyed out if nothing to redo) |
| Menu | Return to main menu |
| Quit | Exit the game |

### Wall placement
1. Press `W` to enter wall mode
2. Press `H` (horizontal) or `V` (vertical) to choose orientation
3. Hover over the board — **green preview** = valid, **red** = illegal
4. Click to place the wall
5. Wall mode automatically exits after a successful placement

---

## Game Modes

| Mode | Description |
|------|-------------|
| Human vs Human | Two players take turns on the same computer |
| Human vs AI (Easy) | AI picks random valid moves — good for beginners |
| Human vs AI (Medium) | AI uses a greedy heuristic — shortest path + strategic walls |
| Human vs AI (Hard) | AI uses Minimax with Alpha-Beta pruning — depth-3 search |

---

## Bonus Feature — Undo / Redo

The game supports unlimited undo and redo (up to 50 moves back):

- **Undo** restores the exact board state before the last move, including pawn positions, wall placements, wall counts, and whose turn it is.
- **Redo** re-applies a move that was undone.
- Any new move after an undo clears the redo history (standard behaviour).
- Works in both Human vs Human and Human vs AI modes.

---

## Project Architecture

```
engine/game.py          ← Single entry point (GUI & AI import only this)
    │
    ├── board.py        ← Board state: pawns, walls, turn, winner
    ├── pathfinder.py   ← BFS path checker + wall-block detection
    ├── move_validator  ← Orthogonal moves, jump-over, diagonal escape
    └── wall_manager    ← Wall legality: overlap, crossing, path check

gui.py                  ← Pygame interface (uses engine.Game only)
ai.py                   ← AI opponent (uses engine.Game only)
```

The engine, GUI, and AI are fully decoupled. The GUI and AI only call methods on the `Game` class — they never touch the board internals directly.

---

## AI Algorithm Details

### Easy
Picks a completely random valid pawn move. 10% chance to place a random wall.

### Medium (Bonus)
Greedy depth-1 search. Evaluates all pawn moves and a sample of wall placements. Chooses the move that maximises the evaluation function. Places walls when they score meaningfully better than any pawn move.

### Hard (Bonus)
**Minimax with Alpha-Beta Pruning** at depth 3.

- **Maximising player**: AI (Player 2)  
- **Minimising player**: Human (Player 1)  
- **Branching factor control**: All pawn moves + top 5 scored wall placements per node  
- **Loop detection**: Penalises revisiting recent positions to prevent back-and-forth  

### Evaluation Function

```
score = (human_path_length - ai_path_length) × 2.0   ← main signal
      + (ai_walls - human_walls)             × 0.5   ← wall advantage
      + (ai_row_progress - human_row_progress) × 0.3  ← position
```

Where `path_length` is the BFS shortest path to the goal row (ignoring pawns, walls only).

---

## References

- [Official Quoridor Rules](https://en.gigamic.com/files/media/fiche_pedagogique/educative-sheet_quoridor_english.pdf)
- [Quoridor on BoardGameGeek](https://boardgamegeek.com/boardgame/624/quoridor)
- [Minimax Algorithm with Alpha-Beta Pruning](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
- [BFS Pathfinding](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Pygame Documentation](https://www.pygame.org/docs/)
