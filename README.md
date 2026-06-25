# Quoridor AI Project

A complete, production-quality implementation of the classic board game **Quoridor**, featuring multiple AI difficulty levels, robust pathfinding, and full Undo/Redo capabilities. Developed in Python using Pygame for a university AI course project.

![Quoridor Gameplay](https://via.placeholder.com/800x450.png?text=Quoridor+Gameplay+Screenshot)

## 🌟 Features

- **Full Game Logic:** 100% accurate implementation of Quoridor rules, including diagonal pawn jumping, wall collision, and path verification.
- **Advanced AI Opponents:**
  - **Easy:** Makes random, valid moves with occasional wall placements.
  - **Medium:** Heuristic-driven logic that greedily follows the shortest path and blocks the player when threatened.
  - **Hard:** Sophisticated AI using **Iterative Deepening Minimax** with **Alpha-Beta Pruning**. It utilizes a time-limited search (default 3s) and an advanced evaluation heuristic that balances goal proximity, wall conservation, and opponent disruption.
- **Robust Pathfinding:** BFS-based pathfinding ensures walls can never completely box in any player.
- **Full Undo/Redo Stack:** Mistakes happen! Use the UI buttons or standard keyboard shortcuts (`Ctrl+Z` / `Ctrl+Y`) to traverse the game state history seamlessly.
- **Modern GUI:** Clean, visually appealing Pygame interface with valid move highlighting, wall placement preview colors, and turn indicators.
- **Game Modes:** Support for Human vs Human (PvP) and Human vs AI.

## 🛠 Project Structure

```
/
├── main.py                 # Game entry point and event loop
├── game/                   # Core game logic
│   ├── board.py            # Board state and wall management
│   ├── constants.py        # System-wide configuration
│   ├── game_state.py       # Centralized immutable-safe state manager
│   ├── history_manager.py  # Undo/Redo logic using a state-history stack
│   ├── player.py           # Player dataclass and goals
│   ├── rules.py            # Movement validation and pawn jump logic
│   └── wall.py             # Wall dataclass
├── ai/                     # Artificial Intelligence logic
│   ├── easy_ai.py          # Random valid moves
│   ├── medium_ai.py        # Shortest path heuristics
│   ├── hard_ai.py          # Iterative Deepening entry point
│   ├── heuristics.py       # Weighted board evaluation functions
│   ├── minimax.py          # Minimax algorithm with Move Ordering
│   └── pathfinding.py      # BFS graph traversal
├── ui/                     # Presentation layer
│   ├── button.py           # Pygame interactive button component
│   └── renderer.py         # Pygame drawing routines
├── requirements.txt        # Python dependencies
└── README.md               # You are here
```

## 🚀 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/quoridor-ai.git
   cd quoridor-ai
   ```

2. **Set up a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 🎮 How to Play

Run the main game file to launch the GUI:
```bash
python main.py
```

### Controls

- **Move Pawn:** Click on any highlighted adjacent cell.
- **Place Wall:** Hover your mouse between cells. If the preview is green, click to place a wall. The orientation (horizontal/vertical) is determined by where you hover within the cell intersection.
- **Undo Move:** Press `Ctrl+Z` or click the `Undo` button.
- **Redo Move:** Press `Ctrl+Y` or click the `Redo` button.
- **Change Game Mode:** Use the mode selectors on the right to toggle between PvP and various AI difficulties.
- **Restart Game:** Click the `Restart` button to reset the board instantly.

## 🧠 AI & Architecture Highlights

- **State Management:** The game operates on a centralized `GameState` object. Rather than mutating a single board and attempting to reverse commands, every move creates a deep copy of the state, ensuring that the Undo/Redo system (`history_manager.py`) is completely bug-free and mathematically sound.
- **Iterative Deepening Minimax:** The Hard AI uses a time-limited iterative search. It explores increasingly deeper levels of the game tree until the time limit (3 seconds) is reached, ensuring it always makes the most informed move possible within its budget.
- **Alpha-Beta Pruning & Move Ordering:** To optimize search efficiency, the engine uses Alpha-Beta pruning combined with move ordering (prioritizing pawn moves). This allows the AI to skip evaluating millions of disadvantageous branches.
- **Advanced Heuristics:** The evaluation function considers path length differences, wall counts, and strategic positioning to evaluate board states beyond simple greedy movements.
- **Pathfinding:** Before any wall is placed, the board uses a Breadth-First Search (BFS) to guarantee that a path still exists for all players.

## 🎥 Demo Video

https://drive.google.com/drive/folders/1nYU3eqwbxcQQmac2rx8zOhbes0KwEReY?usp=sharing

## 👥 Contributors
- David Amir Mahrous 2300228
- Manuel Gamal Aziz 2300526
- Mariam Emad Ibrahim 2300450
- George Wanis Ayed 2300280
- Maria Samy Ibrahim 2300812
- George Ibrahim Abdo 2300285

