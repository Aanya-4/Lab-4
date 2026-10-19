"""
renderer: all pygame drawing lives here, kept separate from game logic.
"""

import pygame

WIDTH, HEIGHT = 400, 600
BOARD_SIZE = 360
CELL_SIZE = BOARD_SIZE // 3
BOARD_TOP = 100
WINDOW_SIZE = (WIDTH, HEIGHT)

COLOR_BG = (245, 245, 245)
COLOR_LINE = (60, 60, 60)
COLOR_X = (200, 60, 60)
COLOR_O = (60, 100, 200)
COLOR_TEXT = (30, 30, 30)
COLOR_BTN = (225, 225, 225)
COLOR_BTN_HOVER = (205, 215, 235)
COLOR_BTN_BORDER = (60, 60, 60)

# On-screen buttons, below the board and the win/draw banner (banner is centred at y=500).
# Two on the first row, one full-width on the second; the last row ends at y=594 (window is 600 high).
BUTTON_RECTS = {
    'new_round':    pygame.Rect(10, 524, 185, 32),
    'reset_match':  pygame.Rect(205, 524, 185, 32),
    'first_player': pygame.Rect(10, 562, 380, 32),
}

_button_font = None


def board_pos_to_cell(pos):
    x, y = pos
    y -= BOARD_TOP
    if not (0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE):
        return None
    col = x // CELL_SIZE
    row = y // CELL_SIZE
    return int(row), int(col)


def draw_board(surface, board):
    surface.fill(COLOR_BG)
    for i in range(1, 3):
        pygame.draw.line(surface, COLOR_LINE, (i * CELL_SIZE, BOARD_TOP), (i * CELL_SIZE, BOARD_TOP + BOARD_SIZE), 3)
        pygame.draw.line(surface, COLOR_LINE, (0, BOARD_TOP + i * CELL_SIZE), (BOARD_SIZE, BOARD_TOP + i * CELL_SIZE), 3)

    for r in range(3):
        for c in range(3):
            symbol = board[r][c]
            if symbol is None:
                continue
            center = (c * CELL_SIZE + CELL_SIZE // 2, BOARD_TOP + r * CELL_SIZE + CELL_SIZE // 2)
            if symbol == 'X':
                offset = CELL_SIZE // 3
                pygame.draw.line(surface, COLOR_X, (center[0]-offset, center[1]-offset), (center[0]+offset, center[1]+offset), 6)
                pygame.draw.line(surface, COLOR_X, (center[0]+offset, center[1]-offset), (center[0]-offset, center[1]+offset), 6)
            else:
                pygame.draw.circle(surface, COLOR_O, center, CELL_SIZE // 3, 6)


def draw_text(surface, font, text, pos, color=COLOR_TEXT):
    surface.blit(font.render(text, True, color), pos)


def draw_banner(surface, font, text):
    surf = font.render(text, True, (180, 40, 40))
    rect = surf.get_rect(center=(surface.get_width() // 2, BOARD_TOP + BOARD_SIZE + 40))
    surface.blit(surf, rect)


def button_at(pos):
    """Return the name of the button under pos, or None."""
    for name, rect in BUTTON_RECTS.items():
        if rect.collidepoint(pos):
            return name
    return None


def draw_button(surface, name, label, hover=False):
    global _button_font
    if _button_font is None:
        _button_font = pygame.font.SysFont("consolas", 18)
    rect = BUTTON_RECTS[name]
    pygame.draw.rect(surface, COLOR_BTN_HOVER if hover else COLOR_BTN, rect, border_radius=6)
    pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, 2, border_radius=6)
    text = _button_font.render(label, True, COLOR_TEXT)
    surface.blit(text, text.get_rect(center=rect.center))
