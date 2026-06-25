import pygame
import sys
from game.constants import *
from game.game_state import GameState, PawnMove, WallMove
from game.history_manager import HistoryManager
from game.rules import get_valid_pawn_moves, is_wall_placement_valid
from game.wall import Wall
from ui.renderer import Renderer
from ui.button import Button
from ai.easy_ai import get_easy_ai_move
from ai.medium_ai import get_medium_ai_move
from ai.hard_ai import get_hard_ai_move

pygame.init()

def main():
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Quoridor AI - Premium Edition")
    clock = pygame.time.Clock()
    
    renderer = Renderer(screen)
    
    ui_state = "MENU"
    game_state = GameState()
    history = HistoryManager(game_state)
    
    font = pygame.font.SysFont("Verdana", 18)
    bold_font = pygame.font.SysFont("Verdana", 20, bold=True)
    title_font = pygame.font.SysFont("Verdana", 48, bold=True)
    
    game_mode = 3 
    mode_buttons = [
        Button(350, 250, 300, 45, "Player vs Player", font, COLOR_BTN, COLOR_TEXT, "MODE_0"),
        Button(350, 310, 300, 45, "Player vs AI (Easy)", font, COLOR_BTN, COLOR_TEXT, "MODE_1"),
        Button(350, 370, 300, 45, "Player vs AI (Med)", font, COLOR_BTN, COLOR_TEXT, "MODE_2"),
        Button(350, 430, 300, 45, "Player vs AI (Hard)", font, COLOR_BTN, COLOR_TEXT, "MODE_3"),
        Button(350, 520, 300, 60, "START GAME", bold_font, (100, 200, 100), (255, 255, 255), "START"),
    ]

    # Stacking UNDO and REDO on the LEFT
    side_undo_btn = Button(30, 370, 110, 60, "UNDO", bold_font, (45, 45, 55), (200, 200, 210), "UNDO", is_secondary=True)
    side_redo_btn = Button(30, 440, 110, 60, "REDO", bold_font, (45, 45, 55), (200, 200, 210), "REDO", is_secondary=True)

    # Putting MENU button on the RIGHT side of the board
    game_menu_btn = Button(WIDTH - 140, 400, 110, 60, "MENU", bold_font, (60, 60, 75), COLOR_TEXT, "PAUSE")

    # PAUSE Menu Buttons
    ctrl_buttons = [
        Button(375, 220, 250, 45, "RESUME", bold_font, (100, 200, 100), (255, 255, 255), "RESUME"),
        Button(375, 280, 250, 45, "UNDO", font, COLOR_BTN, COLOR_TEXT, "UNDO"),
        Button(375, 340, 250, 45, "REDO", font, COLOR_BTN, COLOR_TEXT, "REDO"),
        Button(375, 400, 250, 45, "HOW TO PLAY", font, (100, 150, 200), (255, 255, 255), "SHOW_CONTROLS"),
        Button(375, 460, 250, 45, "Restart", font, (180, 100, 100), COLOR_TEXT, "RESTART"),
        Button(375, 520, 250, 45, "Main Menu", font, (80, 80, 90), COLOR_TEXT, "GOTO_MENU"),
    ]
    
    back_btn = Button(400, 600, 200, 45, "BACK", bold_font, COLOR_BTN, COLOR_TEXT, "RESUME_PAUSE")

    def handle_undo():
        history.undo()
        if game_mode > 0 and history.current_index > 0:
            if history.get_current_state().current_turn == PlayerId.PLAYER_2:
                history.undo()

    def handle_redo():
        history.redo()
        if game_mode > 0 and history.current_index < len(history.history) - 1:
            if history.get_current_state().current_turn == PlayerId.PLAYER_2:
                history.redo()

    def update_mode_buttons():
        for b in mode_buttons:
            if b.action_value.startswith("MODE_"):
                m_val = int(b.action_value.split("_")[1])
                b.current_color = COLOR_BTN_ACCENT if game_mode == m_val else COLOR_BTN

    update_mode_buttons()
    mode_names = {0: "PvP", 1: "Easy AI", 2: "Medium AI", 3: "Hard AI"}

    running = True
    while running:
        current_state = history.get_current_state()
        
        # AI Turn
        if ui_state == "PLAYING" and not current_state.is_game_over():
            if game_mode > 0 and current_state.current_turn == PlayerId.PLAYER_2:
                pygame.time.delay(300)
                if game_mode == 1: move = get_easy_ai_move(current_state)
                elif game_mode == 2: move = get_medium_ai_move(current_state)
                else: move = get_hard_ai_move(current_state)
                if current_state.execute_move(move):
                    history.add_state(current_state)
                    continue

        # Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False
            if ui_state == "MENU":
                for btn in mode_buttons:
                    action = btn.handle_event(event)
                    if action:
                        if action.startswith("MODE_"): game_mode = int(action.split("_")[1]); update_mode_buttons()
                        elif action == "START": game_state = GameState(); history = HistoryManager(game_state); ui_state = "PLAYING"
            elif ui_state == "PLAYING":
                if game_menu_btn.handle_event(event) == "PAUSE": ui_state = "PAUSE"
                if side_undo_btn.handle_event(event) == "UNDO": handle_undo()
                if side_redo_btn.handle_event(event) == "REDO": handle_redo()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL): handle_undo()
                    if event.key == pygame.K_y and (pygame.key.get_mods() & pygame.KMOD_CTRL): handle_redo()
                    if event.key == pygame.K_ESCAPE: ui_state = "PAUSE"
                is_human = (current_state.current_turn == PlayerId.PLAYER_1 or game_mode == 0)
                if not current_state.is_game_over() and is_human:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if not (side_undo_btn.is_hovered or side_redo_btn.is_hovered or game_menu_btn.is_hovered):
                            pos = renderer.get_board_pos_from_mouse(event.pos[0], event.pos[1])
                            if pos:
                                move = None
                                if pos[0] == "CELL": move = PawnMove(current_state.current_turn, pos[1], pos[2])
                                elif pos[0] == "WALL":
                                    if current_state.get_current_player().walls_left > 0:
                                        wall = Wall(pos[1], pos[2], pos[3])
                                        if is_wall_placement_valid(current_state.board, wall, current_state.p1, current_state.p2):
                                            move = WallMove(current_state.current_turn, wall)
                                if move and current_state.execute_move(move): history.add_state(current_state)
            elif ui_state == "PAUSE":
                for btn in ctrl_buttons:
                    action = btn.handle_event(event)
                    if action == "RESUME": ui_state = "PLAYING"
                    elif action == "UNDO": handle_undo(); ui_state = "PLAYING"
                    elif action == "REDO": handle_redo(); ui_state = "PLAYING"
                    elif action == "SHOW_CONTROLS": ui_state = "HOW_TO_PLAY"
                    elif action == "RESTART": game_state = GameState(); history = HistoryManager(game_state); ui_state = "PLAYING"
                    elif action == "GOTO_MENU": ui_state = "MENU"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: ui_state = "PLAYING"
            elif ui_state == "HOW_TO_PLAY":
                if back_btn.handle_event(event) == "RESUME_PAUSE" or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE): ui_state = "PAUSE"

        # Drawing
        screen.fill(COLOR_BG)
        if ui_state == "MENU":
            title_surf = title_font.render("QUORIDOR AI", True, (255, 255, 255))
            screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 120)))
            sub_surf = font.render("Choose Your Challenge", True, (150, 150, 160))
            screen.blit(sub_surf, sub_surf.get_rect(center=(WIDTH//2, 180)))
            for btn in mode_buttons: btn.draw(screen)
        elif ui_state in ["PLAYING", "PAUSE", "HOW_TO_PLAY"]:
            renderer.draw_board(current_state, mode_names[game_mode])
            game_menu_btn.draw(screen)
            side_undo_btn.draw(screen)
            side_redo_btn.draw(screen)
            if ui_state == "PLAYING" and not current_state.is_game_over():
                is_human = (current_state.current_turn == PlayerId.PLAYER_1 or game_mode == 0)
                if is_human and not (side_undo_btn.is_hovered or side_redo_btn.is_hovered or game_menu_btn.is_hovered):
                    mx, my = pygame.mouse.get_pos()
                    pos = renderer.get_board_pos_from_mouse(mx, my)
                    player = current_state.get_current_player()
                    renderer.draw_valid_moves(get_valid_pawn_moves(current_state.board, player, current_state.get_opponent()))
                    if pos and pos[0] == "WALL":
                        wall = Wall(pos[1], pos[2], pos[3])
                        valid = player.walls_left > 0 and is_wall_placement_valid(current_state.board, wall, current_state.p1, current_state.p2)
                        renderer.draw_wall_hover(wall, valid)
            if ui_state == "PAUSE":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 180)); screen.blit(overlay, (0, 0))
                menu_rect = pygame.Rect(WIDTH//2 - 150, 180, 300, 440)
                pygame.draw.rect(screen, (40, 40, 50), menu_rect, border_radius=20)
                pygame.draw.rect(screen, (80, 80, 100), menu_rect, width=2, border_radius=20)
                p_title = bold_font.render("PAUSE MENU", True, (255, 255, 255))
                screen.blit(p_title, p_title.get_rect(center=(WIDTH//2, 205)))
                for btn in ctrl_buttons: btn.draw(screen)
            if ui_state == "HOW_TO_PLAY":
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA); overlay.fill((0, 0, 0, 220)); screen.blit(overlay, (0, 0))
                help_rect = pygame.Rect(WIDTH//2 - 250, 100, 500, 550)
                pygame.draw.rect(screen, (40, 40, 50), help_rect, border_radius=20)
                pygame.draw.rect(screen, (100, 180, 255), help_rect, width=2, border_radius=20)
                h_title = bold_font.render("HOW TO PLAY", True, (100, 180, 255))
                screen.blit(h_title, h_title.get_rect(center=(WIDTH//2, 140)))
                instructions = ["• Objective: Reach the opposite baseline.", "• Movement: Click on highlighted cells.", "• Jump: Overleap adjacent opponents.", "• Walls: Click between cells to block paths.", "• Wall Limit: Don't trap anyone completely!", "", "--- CONTROLS ---", "• UNDO / Ctrl+Z: Go back a turn", "• REDO / Ctrl+Y: Go forward", "• ESC / MENU: Options & Restart"]
                y_off = 190
                for line in instructions:
                    line_surf = font.render(line, True, COLOR_TEXT)
                    screen.blit(line_surf, (WIDTH//2 - 220, y_off)); y_off += 35
                back_btn.draw(screen)

        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit(); sys.exit()

if __name__ == "__main__":
    main()
