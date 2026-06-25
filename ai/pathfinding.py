from collections import deque
from game.board import Board
from game.player import Player
from game.constants import BOARD_SIZE, Direction

def has_path(board: Board, player: Player) -> bool:
    """Uses BFS to check if a player can reach their goal row."""
    visited = set()
    queue = deque([(player.x, player.y)])
    visited.add((player.x, player.y))
    
    goal_y = player.goal_y
    
    while queue:
        cx, cy = queue.popleft()
        
        if cy == goal_y:
            return True
            
        for direction in Direction:
            nx, ny = cx + direction.value[0], cy + direction.value[1]
            
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if (nx, ny) not in visited:
                    if not board.blocks_movement(cx, cy, nx, ny):
                        visited.add((nx, ny))
                        queue.append((nx, ny))
                        
    return False

def get_shortest_path_length(board: Board, start_x: int, start_y: int, goal_y: int) -> int:
    """Returns the shortest path length to the goal row using BFS. Returns float('inf') if no path."""
    visited = set()
    queue = deque([(start_x, start_y, 0)]) # x, y, distance
    visited.add((start_x, start_y))
    
    while queue:
        cx, cy, dist = queue.popleft()
        
        if cy == goal_y:
            return dist
            
        for direction in Direction:
            nx, ny = cx + direction.value[0], cy + direction.value[1]
            
            if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                if (nx, ny) not in visited:
                    if not board.blocks_movement(cx, cy, nx, ny):
                        visited.add((nx, ny))
                        queue.append((nx, ny, dist + 1))
                        
    return float('inf')
