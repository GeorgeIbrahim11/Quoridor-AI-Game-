from typing import List, Optional
from .game_state import GameState, Move

class HistoryManager:
    def __init__(self, initial_state: GameState):
        self.history: List[GameState] = [initial_state.copy()]
        self.current_index = 0

    def get_current_state(self) -> GameState:
        return self.history[self.current_index].copy()

    def add_state(self, state: GameState):
        """Adds a new state, clearing any redo history."""
        # Truncate history if we are not at the end (clears redo)
        self.history = self.history[:self.current_index + 1]
        self.history.append(state.copy())
        self.current_index += 1

    def undo(self) -> Optional[GameState]:
        if self.current_index > 0:
            self.current_index -= 1
            return self.get_current_state()
        return None

    def redo(self) -> Optional[GameState]:
        if self.current_index < len(self.history) - 1:
            self.current_index += 1
            return self.get_current_state()
        return None
