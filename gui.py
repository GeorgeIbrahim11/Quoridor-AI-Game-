"""
gui.py — Quoridor GUI & UX (Member 2)
Built with Pygame. Requires the engine/ package (Member 1).

Install:  pip install pygame
Run:      python gui.py

Features:
  - Menu & Quit buttons always visible in-game
  - AI runs in background thread (no lag on human moves)
  - Instructions panel on menu screen
  - Undo (Ctrl+Z) and Redo (Ctrl+Y) support
  - ESC returns to menu
"""

import pygame
import sys
import os
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from engine import Game
from engine.game import GameState
from engine.move_validator import get_valid_moves

pygame.init()

# ══════════════════════════════════════════════════════════════════════
# CONSTANTS & THEME
# ══════════════════════════════════════════════════════════════════════

BOARD_SIZE  = 9
CELL        = 64
WALL_THICK  = 10
GAP         = 4
BOARD_PX    = BOARD_SIZE * CELL + (BOARD_SIZE - 1) * GAP
MARGIN_LEFT = 60
MARGIN_TOP  = 130
WIN_W       = MARGIN_LEFT * 2 + BOARD_PX
WIN_H       = MARGIN_TOP + BOARD_PX + 70 + 30

C_BG         = (18,  18,  24)
C_CELL       = (36,  36,  48)
C_CELL_HOVER = (52,  52,  68)
C_GRID       = (50,  50,  66)
C_VALID      = (80, 180, 120, 160)
C_SELECTED   = (100, 140, 220)
C_P1         = (220,  80,  80)
C_P2         = (80,  160, 220)
C_P1_DARK    = (160,  40,  40)
C_P2_DARK    = (40,  110, 160)
C_TEXT       = (220, 220, 230)
C_TEXT_DIM   = (120, 120, 140)
C_WHITE      = (255, 255, 255)
C_BTN_UNDO   = (60,  90,  60)
C_BTN_UNDO_H = (80, 120,  80)
C_BTN_REDO   = (60,  60,  90)
C_BTN_REDO_H = (80,  80, 120)

FONT_LG = pygame.font.SysFont("segoeui", 26, bold=True)
FONT_MD = pygame.font.SysFont("segoeui", 17)
FONT_SM = pygame.font.SysFont("segoeui", 13)
FONT_XL = pygame.font.SysFont("segoeui", 46, bold=True)

MODE_MENU  = "menu"
MODE_HvH   = "hvh"
MODE_HvAI  = "hvai"
INPUT_PAWN = "pawn"
INPUT_WALL = "wall"

AI_MOVE_EVENT = pygame.USEREVENT + 1

# ══════════════════════════════════════════════════════════════════════
# COORDINATE HELPERS
# ══════════════════════════════════════════════════════════════════════

def cell_rect(row, col):
    return pygame.Rect(
        MARGIN_LEFT + col * (CELL + GAP),
        MARGIN_TOP  + row * (CELL + GAP),
        CELL, CELL
    )

def pixel_to_cell(px, py):
    ox, oy = px - MARGIN_LEFT, py - MARGIN_TOP
    if ox < 0 or oy < 0:
        return None
    col = int(ox / (CELL + GAP))
    row = int(oy / (CELL + GAP))
    if col >= BOARD_SIZE or row >= BOARD_SIZE:
        return None
    if (ox - col*(CELL+GAP)) > CELL or (oy - row*(CELL+GAP)) > CELL:
        return None
    return (row, col)

def pixel_to_wall_anchor(px, py, orientation):
    ox, oy = px - MARGIN_LEFT, py - MARGIN_TOP
    if orientation == "h":
        col = int(ox / (CELL + GAP))
        row = int(oy / (CELL + GAP) - 0.5)
        if 0 <= row < BOARD_SIZE-1 and 0 <= col < BOARD_SIZE-1:
            return (row, col)
    else:
        col = int(ox / (CELL + GAP) - 0.5)
        row = int(oy / (CELL + GAP))
        if 0 <= row < BOARD_SIZE-1 and 0 <= col < BOARD_SIZE-1:
            return (row, col)
    return None

def wall_segments_to_rects(state, orientation):
    rects = []
    drawn = set()
    if orientation == "h":
        segs = state.h_walls
        for (r, c) in segs:
            if ("h", r, c) in drawn: continue
            drawn.add(("h", r, c))
            x1 = MARGIN_LEFT + c * (CELL + GAP)
            y1 = MARGIN_TOP  + r * (CELL + GAP) + CELL + (GAP - WALL_THICK) // 2
            w  = (CELL + GAP + CELL) if (r, c+1) in segs else CELL
            if (r, c+1) in segs: drawn.add(("h", r, c+1))
            rects.append(pygame.Rect(x1, y1, w, WALL_THICK))
    else:
        segs = state.v_walls
        for (r, c) in segs:
            if ("v", r, c) in drawn: continue
            drawn.add(("v", r, c))
            x1 = MARGIN_LEFT + c * (CELL + GAP) + CELL + (GAP - WALL_THICK) // 2
            y1 = MARGIN_TOP  + r * (CELL + GAP)
            h  = (CELL + GAP + CELL) if (r+1, c) in segs else CELL
            if (r+1, c) in segs: drawn.add(("v", r+1, c))
            rects.append(pygame.Rect(x1, y1, WALL_THICK, h))
    return rects

# ══════════════════════════════════════════════════════════════════════
# DRAWING
# ══════════════════════════════════════════════════════════════════════

def draw_board(surf, state, selected_cell, valid_moves, hover_cell,
               input_mode, wall_orient, hover_wall_anchor, game, ai_thinking):

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            rect  = cell_rect(row, col)
            color = C_CELL_HOVER if ((row,col)==hover_cell and input_mode==INPUT_PAWN) else C_CELL
            pygame.draw.rect(surf, color, rect, border_radius=4)

    if input_mode == INPUT_PAWN and not ai_thinking:
        hl = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        hl.fill(C_VALID)
        for (r, c) in valid_moves:
            rect = cell_rect(r, c)
            surf.blit(hl, rect.topleft)
            pygame.draw.rect(surf, (80,200,120), rect, 2, border_radius=4)

    if selected_cell:
        pygame.draw.rect(surf, C_SELECTED, cell_rect(*selected_cell), 3, border_radius=4)

    for rect in wall_segments_to_rects(state, "h"):
        pygame.draw.rect(surf, (200,160,80), rect, border_radius=3)
    for rect in wall_segments_to_rects(state, "v"):
        pygame.draw.rect(surf, (200,160,80), rect, border_radius=3)

    if input_mode == INPUT_WALL and hover_wall_anchor and not ai_thinking:
        r, c  = hover_wall_anchor
        valid = game.is_valid_wall(state.current_turn, wall_orient, r, c)
        gc    = (100,220,140,140) if valid else (220,80,80,140)
        gs    = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
        if wall_orient == "h":
            x = MARGIN_LEFT + c*(CELL+GAP)
            y = MARGIN_TOP  + r*(CELL+GAP) + CELL + (GAP-WALL_THICK)//2
            pygame.draw.rect(gs, gc, pygame.Rect(x, y, CELL*2+GAP, WALL_THICK), border_radius=3)
        else:
            x = MARGIN_LEFT + c*(CELL+GAP) + CELL + (GAP-WALL_THICK)//2
            y = MARGIN_TOP  + r*(CELL+GAP)
            pygame.draw.rect(gs, gc, pygame.Rect(x, y, WALL_THICK, CELL*2+GAP), border_radius=3)
        surf.blit(gs, (0,0))

    for player, color, dark in [(1,C_P1,C_P1_DARK),(2,C_P2,C_P2_DARK)]:
        r, c   = state.pawns[player]
        rect   = cell_rect(r, c)
        cx, cy = rect.centerx, rect.centery
        radius = CELL//2 - 8
        pygame.draw.circle(surf, dark,    (cx+2, cy+3), radius)
        pygame.draw.circle(surf, color,   (cx,   cy),   radius)
        pygame.draw.circle(surf, C_WHITE, (cx-radius//3, cy-radius//3), radius//4)
        lbl = FONT_SM.render(str(player), True, C_WHITE)
        surf.blit(lbl, lbl.get_rect(center=(cx, cy)))

    if ai_thinking:
        txt = FONT_MD.render("AI is thinking...", True, C_P2)
        surf.blit(txt, txt.get_rect(centerx=WIN_W//2, y=MARGIN_TOP+BOARD_PX+16))


def draw_hud(surf, state, input_mode, wall_orient,
             btn_menu, btn_quit, btn_undo, btn_redo,
             ai_difficulty, mode, game):

    # Player panels
    for player, color, lx in [(1,C_P1,MARGIN_LEFT),(2,C_P2,WIN_W-MARGIN_LEFT-150)]:
        active = state.current_turn == player
        txt = FONT_LG.render(f"P{player}", True, color if active else C_TEXT_DIM)
        surf.blit(txt, (lx, 10))
        walls = state.walls_remaining[player]
        wt = FONT_SM.render(f"Walls: {walls}", True, C_TEXT if active else C_TEXT_DIM)
        surf.blit(wt, (lx, 40))
        for i in range(walls):
            pygame.draw.rect(surf, color if active else C_TEXT_DIM,
                             pygame.Rect(lx + i*9, 58, 6, 12), border_radius=1)

    # Center info
    label = ("Human"          if (mode==MODE_HvAI and state.current_turn==1)
             else f"AI ({ai_difficulty})" if (mode==MODE_HvAI and state.current_turn==2)
             else f"Player {state.current_turn}")
    t1 = FONT_MD.render(f"{label}'s Turn", True, C_TEXT)
    t2 = FONT_SM.render(
        "PAWN mode  —  W=wall  Ctrl+Z=undo  Ctrl+Y=redo"
        if input_mode == INPUT_PAWN
        else f"WALL [{wall_orient.upper()}]  —  H/V=orient  W=back  Ctrl+Z=undo",
        True, C_TEXT_DIM)
    surf.blit(t1, t1.get_rect(centerx=WIN_W//2, y=12))
    surf.blit(t2, t2.get_rect(centerx=WIN_W//2, y=40))

    # Buttons
    mx, my = pygame.mouse.get_pos()
    undo_available = game.can_undo()
    redo_available = game.can_redo()

    for btn, lbl, base_c, hov_c, enabled in [
        (btn_undo, "↩ Undo", C_BTN_UNDO,   C_BTN_UNDO_H, undo_available),
        (btn_redo, "↪ Redo", C_BTN_REDO,   C_BTN_REDO_H, redo_available),
        (btn_menu, "Menu",   (50,50,70),    (70,70,100),  True),
        (btn_quit, "Quit",   (140,40,40),   (190,60,60),  True),
    ]:
        hov  = btn.collidepoint(mx, my) and enabled
        dim  = not enabled
        col  = (40,40,40) if dim else (hov_c if hov else base_c)
        pygame.draw.rect(surf, col, btn, border_radius=7)
        pygame.draw.rect(surf, C_GRID, btn, 1, border_radius=7)
        tc   = C_TEXT_DIM if dim else (C_WHITE if hov else C_TEXT)
        t    = FONT_SM.render(lbl, True, tc)
        surf.blit(t, t.get_rect(center=btn.center))


def draw_winner_overlay(surf, winner):
    ov = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    ov.fill((10,10,20,200))
    surf.blit(ov, (0,0))
    color = C_P1 if winner == 1 else C_P2
    big = FONT_XL.render(f"Player {winner} Wins!", True, color)
    sub = FONT_SM.render("Click  Menu  to play again  |  Quit  to exit  |  Ctrl+Z  to undo", True, C_TEXT_DIM)
    surf.blit(big, big.get_rect(center=(WIN_W//2, WIN_H//2 - 30)))
    surf.blit(sub, sub.get_rect(center=(WIN_W//2, WIN_H//2 + 30)))

# ══════════════════════════════════════════════════════════════════════
# MENU SCREEN
# ══════════════════════════════════════════════════════════════════════

def draw_menu(surf, mouse_pos):
    surf.fill(C_BG)

    title = FONT_XL.render("QUORIDOR", True, C_TEXT)
    sub   = FONT_MD.render("Abstract Strategy Board Game", True, C_TEXT_DIM)
    surf.blit(title, title.get_rect(centerx=WIN_W//2, y=22))
    surf.blit(sub,   sub.get_rect(centerx=WIN_W//2,   y=78))

    btn_w, btn_h = 240, 46

    btn_hvh = pygame.Rect(WIN_W//2 - btn_w//2, 120, btn_w, btn_h)
    hov = btn_hvh.collidepoint(mouse_pos)
    pygame.draw.rect(surf, (60,60,90) if hov else (36,36,56), btn_hvh, border_radius=10)
    pygame.draw.rect(surf, C_P1 if hov else C_GRID, btn_hvh, 2, border_radius=10)
    t = FONT_MD.render("Human vs Human", True, C_WHITE if hov else C_TEXT)
    surf.blit(t, t.get_rect(center=btn_hvh.center))

    dl = FONT_SM.render("Human vs AI — pick difficulty:", True, C_TEXT_DIM)
    surf.blit(dl, dl.get_rect(centerx=WIN_W//2, y=184))

    sw, sg = 100, 12
    sx = WIN_W//2 - (sw*3+sg*2)//2
    btn_easy   = pygame.Rect(sx,           198, sw, btn_h)
    btn_medium = pygame.Rect(sx+sw+sg,     198, sw, btn_h)
    btn_hard   = pygame.Rect(sx+(sw+sg)*2, 198, sw, btn_h)

    for btn, lbl, accent in [
        (btn_easy,   "Easy",   (80,180,100)),
        (btn_medium, "Medium", (200,160,60)),
        (btn_hard,   "Hard",   (200,70,70)),
    ]:
        hov = btn.collidepoint(mouse_pos)
        pygame.draw.rect(surf, (55,70,55) if hov else (30,36,30), btn, border_radius=10)
        pygame.draw.rect(surf, accent, btn, 2, border_radius=10)
        t2 = FONT_MD.render(lbl, True, C_WHITE if hov else C_TEXT)
        surf.blit(t2, t2.get_rect(center=btn.center))

    # Instructions box
    box = pygame.Rect(MARGIN_LEFT-10, 264, WIN_W-(MARGIN_LEFT-10)*2, 226)
    pygame.draw.rect(surf, (26,26,36), box, border_radius=10)
    pygame.draw.rect(surf, C_GRID, box, 1, border_radius=10)
    ih = FONT_MD.render("How to Play", True, C_TEXT)
    surf.blit(ih, ih.get_rect(centerx=WIN_W//2, y=box.y+10))

    instructions = [
        ("Goal",      "Move your pawn to the opposite side of the board first"),
        ("Move",      "Click your pawn to select, then click a green highlighted cell"),
        ("Wall mode", "Press W — then click between cells to place a wall"),
        ("Orient",    "H = horizontal wall     V = vertical wall"),
        ("Preview",   "Green preview = valid placement   Red = illegal"),
        ("Wall rule", "Walls cannot fully block any player's path to goal"),
        ("Jump",      "Adjacent pawns: jump over — or diagonally if a wall blocks"),
        ("Undo/Redo", "Ctrl+Z = undo last move     Ctrl+Y = redo"),
        ("Keys",      "W = wall mode    ESC = back to menu    Quit button = exit"),
    ]
    y = box.y + 36
    for lbl, desc in instructions:
        ls = FONT_SM.render(lbl + ":", True, C_P2)
        ds = FONT_SM.render(desc, True, C_TEXT_DIM)
        surf.blit(ls, (box.x+12, y))
        surf.blit(ds, (box.x+96, y))
        y += 22

    return btn_hvh, btn_easy, btn_medium, btn_hard

# ══════════════════════════════════════════════════════════════════════
# AI THREADING
# ══════════════════════════════════════════════════════════════════════

_ai_result   = None
_ai_thinking = False

def _ai_thread_fn(board_clone, difficulty):
    global _ai_result, _ai_thinking
    try:
        from ai import get_ai_move
        proxy = _BoardProxy(board_clone)
        move  = get_ai_move(proxy, difficulty)
    except Exception as e:
        print(f"[AI error] {e}")
        move = None
    _ai_result   = move
    _ai_thinking = False
    pygame.event.post(pygame.event.Event(AI_MOVE_EVENT))


class _BoardProxy:
    def __init__(self, board):
        self._b = board
        from engine.move_validator import get_valid_moves, apply_pawn_move
        from engine.wall_manager   import get_valid_wall_placements, apply_wall, is_valid_wall
        self._gvm = get_valid_moves
        self._apm = apply_pawn_move
        self._gwp = get_valid_wall_placements
        self._aw  = apply_wall
        self._ivw = is_valid_wall

    def clone_board(self):                      return self._b.clone()
    def get_valid_moves(self, p):               return self._gvm(self._b, p)
    def get_valid_wall_placements(self, p):     return self._gwp(self._b, p)
    def is_valid_wall(self, p, o, r, c):        return self._ivw(self._b, p, o, r, c)
    def get_state(self):
        b = self._b
        return GameState(
            pawns=dict(b.pawns), walls_remaining=dict(b.walls_remaining),
            h_walls=frozenset(b.h_walls), v_walls=frozenset(b.v_walls),
            current_turn=b.current_turn, winner=b.winner,
            valid_pawn_moves=self._gvm(b, b.current_turn),
        )


def start_ai_thinking(game, difficulty):
    global _ai_thinking, _ai_result
    if _ai_thinking: return
    _ai_thinking = True
    _ai_result   = None
    clone = game.clone_board()
    threading.Thread(target=_ai_thread_fn, args=(clone, difficulty), daemon=True).start()

# ══════════════════════════════════════════════════════════════════════
# MAIN LOOP
# ══════════════════════════════════════════════════════════════════════

def main():
    global _ai_thinking, _ai_result

    screen = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Quoridor")
    clock  = pygame.time.Clock()

    game          = Game()
    mode          = MODE_MENU
    input_mode    = INPUT_PAWN
    wall_orient   = "h"
    selected      = None
    valid_moves   = []
    message       = "Click your pawn to select it, then click a destination."
    ai_player     = None
    ai_difficulty = "medium"
    ai_triggered  = False

    # HUD buttons — fixed positions
    btn_undo = pygame.Rect(4,        6, 70, 26)
    btn_redo = pygame.Rect(78,       6, 70, 26)
    btn_menu = pygame.Rect(WIN_W-130,6, 58, 26)
    btn_quit = pygame.Rect(WIN_W-66, 6, 56, 26)

    def reset_game():
        nonlocal selected, valid_moves, input_mode, wall_orient, message, ai_triggered
        global _ai_thinking, _ai_result
        game.reset()
        selected     = None
        valid_moves  = []
        input_mode   = INPUT_PAWN
        wall_orient  = "h"
        message      = "Click your pawn to select it, then click a destination."
        ai_triggered = False
        _ai_thinking = False
        _ai_result   = None

    def do_undo():
        nonlocal selected, valid_moves, message
        if game.can_undo():
            game.undo()
            selected    = None
            valid_moves = []
            message     = "Move undone."

    def do_redo():
        nonlocal selected, valid_moves, message
        if game.can_redo():
            game.redo()
            selected    = None
            valid_moves = []
            message     = "Move redone."

    while True:
        mx, my = pygame.mouse.get_pos()
        state  = game.get_state()

        # Trigger AI after human move
        if (mode == MODE_HvAI and not state.winner
                and state.current_turn == ai_player
                and not _ai_thinking and not ai_triggered):
            ai_triggered = True
            start_ai_thinking(game, ai_difficulty)

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # AI result ready
            if event.type == AI_MOVE_EVENT:
                move = _ai_result
                ai_triggered = False
                state = game.get_state()
                if move and not state.winner:
                    if move[0] == "pawn":
                        game.move_pawn(ai_player, move[1])
                        message = f"AI ({ai_difficulty}) moved to {move[1]}."
                    elif move[0] == "wall":
                        game.place_wall(ai_player, move[1], move[2], move[3])
                        message = f"AI ({ai_difficulty}) placed {move[1].upper()} wall."

            # MENU
            if mode == MODE_MENU:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    btn_hvh, btn_easy, btn_medium, btn_hard = draw_menu(screen, (mx,my))
                    if btn_hvh.collidepoint(mx,my):
                        mode=MODE_HvH; ai_player=None; reset_game()
                    elif btn_easy.collidepoint(mx,my):
                        mode=MODE_HvAI; ai_player=2; ai_difficulty="easy"; reset_game()
                    elif btn_medium.collidepoint(mx,my):
                        mode=MODE_HvAI; ai_player=2; ai_difficulty="medium"; reset_game()
                    elif btn_hard.collidepoint(mx,my):
                        mode=MODE_HvAI; ai_player=2; ai_difficulty="hard"; reset_game()

            # IN-GAME
            else:
                if event.type == pygame.KEYDOWN:
                    ctrl = pygame.key.get_mods() & pygame.KMOD_CTRL

                    if event.key == pygame.K_ESCAPE:
                        reset_game(); mode = MODE_MENU

                    # Undo: Ctrl+Z
                    if event.key == pygame.K_z and ctrl and not _ai_thinking:
                        do_undo()
                        ai_triggered = False

                    # Redo: Ctrl+Y
                    if event.key == pygame.K_y and ctrl and not _ai_thinking:
                        do_redo()
                        ai_triggered = False

                    if event.key == pygame.K_w and not state.winner and not _ai_thinking:
                        if state.walls_remaining[state.current_turn] > 0:
                            input_mode  = INPUT_WALL if input_mode==INPUT_PAWN else INPUT_PAWN
                            selected    = None
                            valid_moves = []
                            message     = "Wall mode. H/V = orientation. Click board to place."
                    if event.key == pygame.K_h: wall_orient = "h"
                    if event.key == pygame.K_v: wall_orient = "v"

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # HUD buttons
                    if btn_menu.collidepoint(mx,my):
                        reset_game(); mode = MODE_MENU; continue
                    if btn_quit.collidepoint(mx,my):
                        pygame.quit(); sys.exit()
                    if btn_undo.collidepoint(mx,my) and not _ai_thinking:
                        do_undo(); ai_triggered = False; continue
                    if btn_redo.collidepoint(mx,my) and not _ai_thinking:
                        do_redo(); ai_triggered = False; continue

                    if _ai_thinking or state.winner: continue
                    if mode == MODE_HvAI and state.current_turn == ai_player: continue

                    # Pawn mode
                    if input_mode == INPUT_PAWN:
                        cell = pixel_to_cell(mx, my)
                        if cell is None: continue
                        current = state.current_turn
                        if selected is None:
                            if cell == state.pawns[current]:
                                selected    = cell
                                valid_moves = game.get_valid_moves(current)
                                message     = "Select destination. W = wall mode."
                        else:
                            if cell in valid_moves:
                                game.move_pawn(current, cell)
                                message      = f"Player {current} moved to {cell}."
                                selected     = None
                                valid_moves  = []
                                ai_triggered = False
                            elif cell == state.pawns[current]:
                                selected    = None
                                valid_moves = []
                                message     = "Deselected."
                            else:
                                message     = "Invalid move — click your pawn to try again."
                                selected    = None
                                valid_moves = []

                    # Wall mode
                    else:
                        anchor = pixel_to_wall_anchor(mx, my, wall_orient)
                        if anchor:
                            r, c    = anchor
                            current = state.current_turn
                            ok      = game.place_wall(current, wall_orient, r, c)
                            if ok:
                                message      = f"Player {current} placed {wall_orient.upper()} wall."
                                input_mode   = INPUT_PAWN
                                ai_triggered = False
                            else:
                                message = "Invalid wall — try another spot."

        # DRAWING
        state = game.get_state()
        screen.fill(C_BG)

        if mode == MODE_MENU:
            draw_menu(screen, (mx, my))
        else:
            hover_cell        = pixel_to_cell(mx, my)
            hover_wall_anchor = (pixel_to_wall_anchor(mx, my, wall_orient)
                                 if input_mode == INPUT_WALL else None)

            draw_hud(screen, state, input_mode, wall_orient,
                     btn_menu, btn_quit, btn_undo, btn_redo,
                     ai_difficulty, mode, game)
            draw_board(screen, state, selected, valid_moves,
                       hover_cell, input_mode, wall_orient,
                       hover_wall_anchor, game, _ai_thinking)

            if not _ai_thinking:
                msg_surf = FONT_SM.render(message, True, C_TEXT_DIM)
                screen.blit(msg_surf, msg_surf.get_rect(
                    centerx=WIN_W//2, y=MARGIN_TOP+BOARD_PX+16))

            if state.winner:
                draw_winner_overlay(screen, state.winner)

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()
