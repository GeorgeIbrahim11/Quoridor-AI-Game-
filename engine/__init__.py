"""
engine/ — Quoridor Game Engine
Member 1 (Lead)

Public surface (what GUI & AI teams import):
    from engine import Game, GameState
"""

from .game import Game, GameState

__all__ = ["Game", "GameState"]
