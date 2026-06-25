import pygame
from game.constants import *
from game.game_state import GameState
from game.wall import Wall

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("Verdana", 18)
        self.bold_font = pygame.font.SysFont("Verdana", 20, bold=True)
        self.title_font = pygame.font.SysFont("Verdana", 32, bold=True)
        
        board_pixel_size = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE - 1) * WALL_THICKNESS
        self.board_x = (WIDTH - board_pixel_size) // 2
        self.board_y = 140

    def draw_board(self, state: GameState, game_mode_name: str):
        # Draw Top Header
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(self.screen, (20, 20, 25), header_rect)
        pygame.draw.line(self.screen, (60, 60, 70), (0, 100), (WIDTH, 100), 2)
        
        # P1 Info (Pinned Left)
        p1_active = state.current_turn == PlayerId.PLAYER_1
        p1_color = COLOR_P1 if p1_active else (100, 100, 110)
        p1_name = self.bold_font.render("PLAYER 1", True, p1_color)
        p1_walls = self.font.render(f"Walls: {state.p1.walls_left}", True, (180, 180, 190))
        self.screen.blit(p1_name, (50, 20))
        self.screen.blit(p1_walls, (50, 50))
        if p1_active:
            pygame.draw.circle(self.screen, COLOR_P1, (30, 33), 7)

        # Title (Centered)
        title_surf = self.title_font.render("QUORIDOR", True, COLOR_TEXT)
        title_rect = title_surf.get_rect(center=(WIDTH//2, 35))
        self.screen.blit(title_surf, title_rect)
        
        mode_surf = self.font.render(game_mode_name, True, (100, 180, 255))
        mode_rect = mode_surf.get_rect(center=(WIDTH//2, 75))
        self.screen.blit(mode_surf, mode_rect)

        # P2 Info (Pinned Right)
        p2_active = state.current_turn == PlayerId.PLAYER_2
        p2_color = COLOR_P2 if p2_active else (100, 100, 110)
        p2_name = self.bold_font.render("PLAYER 2", True, p2_color)
        p2_walls = self.font.render(f"Walls: {state.p2.walls_left}", True, (180, 180, 190))
        
        p2_name_x = WIDTH - p2_name.get_width() - 50
        p2_walls_x = WIDTH - p2_walls.get_width() - 50
        self.screen.blit(p2_name, (p2_name_x, 20))
        self.screen.blit(p2_walls, (p2_walls_x, 50))
        if p2_active:
            pygame.draw.circle(self.screen, COLOR_P2, (p2_name_x - 20, 33), 7)

        # Draw Board
        board_width = BOARD_SIZE * CELL_SIZE + (BOARD_SIZE - 1) * WALL_THICKNESS
        board_rect = pygame.Rect(self.board_x, self.board_y, board_width, board_width)
        pygame.draw.rect(self.screen, COLOR_BOARD, board_rect, border_radius=8)
        
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                cell_rect = self.get_cell_rect(x, y)
                pygame.draw.rect(self.screen, COLOR_GRID, cell_rect, border_radius=4)
                
        for wall in state.board.walls:
            self.draw_wall(wall, COLOR_WALL)
            
        # Draw players
        p1_rect = self.get_cell_rect(state.p1.x, state.p1.y)
        pygame.draw.circle(self.screen, COLOR_P1, p1_rect.center, CELL_SIZE // 2 - 6)
        pygame.draw.circle(self.screen, (255, 255, 255, 80), p1_rect.center, CELL_SIZE // 2 - 8, width=2)
        
        p2_rect = self.get_cell_rect(state.p2.x, state.p2.y)
        pygame.draw.circle(self.screen, COLOR_P2, p2_rect.center, CELL_SIZE // 2 - 6)
        pygame.draw.circle(self.screen, (255, 255, 255, 80), p2_rect.center, CELL_SIZE // 2 - 8, width=2)
        
        if state.is_game_over():
            self._draw_overlay(f"PLAYER {state.winner.value} WINS!")

    def _draw_overlay(self, message):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        text_surf = self.title_font.render(message, True, (255, 215, 0))
        text_rect = text_surf.get_rect(center=(WIDTH//2, HEIGHT//2 - 50))
        self.screen.blit(text_surf, text_rect)

    def draw_wall(self, wall: Wall, color):
        rect = self.get_wall_rect(wall.x, wall.y, wall.orientation)
        if len(color) == 4:
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill(color)
            self.screen.blit(s, rect)
        else:
            pygame.draw.rect(self.screen, color, rect, border_radius=3)

    def draw_valid_moves(self, moves):
        for (x, y) in moves:
            rect = self.get_cell_rect(x, y)
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            s.fill(COLOR_MOVE_HOVER)
            self.screen.blit(s, rect)

    def draw_wall_hover(self, wall: Wall, is_valid: bool):
        color = COLOR_WALL_HOVER_VALID if is_valid else COLOR_WALL_HOVER_INVALID
        self.draw_wall(wall, color)

    def get_cell_rect(self, x, y):
        cx = self.board_x + x * (CELL_SIZE + WALL_THICKNESS)
        cy = self.board_y + y * (CELL_SIZE + WALL_THICKNESS)
        return pygame.Rect(cx, cy, CELL_SIZE, CELL_SIZE)

    def get_wall_rect(self, x, y, orientation):
        cx = self.board_x + x * (CELL_SIZE + WALL_THICKNESS) + CELL_SIZE
        cy = self.board_y + y * (CELL_SIZE + WALL_THICKNESS) + CELL_SIZE
        if orientation == WallOrientation.VERTICAL:
            return pygame.Rect(cx, cy - CELL_SIZE, WALL_THICKNESS, CELL_SIZE * 2 + WALL_THICKNESS)
        else:
            return pygame.Rect(cx - CELL_SIZE, cy, CELL_SIZE * 2 + WALL_THICKNESS, WALL_THICKNESS)
            
    def get_board_pos_from_mouse(self, mx, my):
        bx, by = mx - self.board_x, my - self.board_y
        if bx < 0 or by < 0: return None
        step = CELL_SIZE + WALL_THICKNESS
        cx, cy = bx // step, by // step
        rem_x, rem_y = bx % step, by % step
        if cx < BOARD_SIZE and cy < BOARD_SIZE and rem_x < CELL_SIZE and rem_y < CELL_SIZE:
            return ("CELL", int(cx), int(cy))
        if bx < BOARD_SIZE * step and by < BOARD_SIZE * step:
            if rem_x >= CELL_SIZE and rem_y < CELL_SIZE and cx < BOARD_SIZE - 1:
                return ("WALL", int(cx), int(cy), WallOrientation.VERTICAL)
            if rem_y >= CELL_SIZE and rem_x < CELL_SIZE and cy < BOARD_SIZE - 1:
                return ("WALL", int(cx), int(cy), WallOrientation.HORIZONTAL)
            if rem_x >= CELL_SIZE and rem_y >= CELL_SIZE and cx < BOARD_SIZE - 1 and cy < BOARD_SIZE - 1:
                return ("WALL", int(cx), int(cy), WallOrientation.HORIZONTAL)
        return None
