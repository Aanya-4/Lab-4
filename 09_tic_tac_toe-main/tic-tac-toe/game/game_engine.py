"""
GameEngine: owns the board, turn state, and round-end logic.

You (the player) always play X and click to move. The computer always
plays O and moves automatically right after you, using a simple
random-move AI (see game/ai.py) - this is given infrastructure, not
something you need to build.

Current features:
  - Scoreboard: X wins, O wins and draws are tracked across rounds.
  - Win/draw detection: all 8 lines count (rows, columns, both
    diagonals); a win is always reported as a win, even if it fills
    the last cell. Once a round has ended, further clicks are ignored.
  - Move validation: clicking an occupied cell is rejected entirely,
    leaving the board and the current turn unchanged.
  - First-player choice: X or O can start; the choice applies from the
    next round. If O starts, the computer opens the round.

Controls:
  - Click   place X in a cell
  - R       restart the round (scoreboard is kept)
  - M       reset the whole match (scoreboard is cleared)
  - F       switch who starts the next round (X / O)

The same three actions are also available as on-screen buttons below
the board (see renderer.BUTTON_RECTS).
"""

from game.rules import check_winner, is_board_full
from game.renderer import board_pos_to_cell, button_at
from game.ai import choose_move

HUMAN_SYMBOL = 'X'
COMPUTER_SYMBOL = 'O'


class GameEngine:
    def __init__(self):
        self.scores = {'X': 0, 'O': 0, 'draw': 0}   # persists across rounds
        self.first_player = HUMAN_SYMBOL            # who starts the NEXT round (setting survives resets)
        self.new_round()

    def new_round(self):
        """Reset the board for a fresh round; the scoreboard is kept."""
        self.board = [[None] * 3 for _ in range(3)]
        self.current_player = self.first_player
        self.round_over = False
        self.winner = None   # 'X', 'O', or None (meaning draw, only valid when round_over)
        self._maybe_take_computer_turn()   # if O starts, the computer opens the round

    def reset_match(self):
        """Clear the scoreboard and start a fresh round."""
        self.scores = {'X': 0, 'O': 0, 'draw': 0}
        self.new_round()

    def toggle_first_player(self):
        """Switch who starts the next round; the current round is left untouched."""
        self.first_player = COMPUTER_SYMBOL if self.first_player == HUMAN_SYMBOL else HUMAN_SYMBOL

    def _press_button(self, name):
        if name == 'new_round':
            self.new_round()
        elif name == 'reset_match':
            self.reset_match()
        elif name == 'first_player':
            self.toggle_first_player()

    def handle_click(self, pos):
        button = button_at(pos)
        if button is not None:
            self._press_button(button)   # buttons work even after the round has ended
            return
        if self.round_over:
            return   # round has ended - ignore further moves
        if self.current_player != HUMAN_SYMBOL:
            return   # not your turn - the computer is about to move (or already has)
        cell = board_pos_to_cell(pos)
        if cell is None:
            return
        row, col = cell
        if self.board[row][col] is not None:
            return   # occupied cell - reject entirely; board and turn stay unchanged
        self.board[row][col] = self.current_player
        self.check_round_end()
        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self._maybe_take_computer_turn()

    def _maybe_take_computer_turn(self):
        if self.round_over or self.current_player != COMPUTER_SYMBOL:
            return
        move = choose_move(self.board)
        if move is None:
            return
        row, col = move
        self.board[row][col] = self.current_player
        self.check_round_end()
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    def handle_keydown(self, key):
        import pygame
        if key == pygame.K_r:
            self.new_round()
        elif key == pygame.K_m:
            self.reset_match()
        elif key == pygame.K_f:
            self.toggle_first_player()

    def check_round_end(self):
        # Check for a winner first so a winning move on the last cell is a win, not a draw.
        winner = check_winner(self.board)
        if winner:
            self.round_over = True
            self.winner = winner
            self.scores[winner] += 1
            return
        if is_board_full(self.board):
            self.round_over = True
            self.winner = None
            self.scores['draw'] += 1

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_board(surface, self.board)
        if self.round_over:
            turn_label = "Round over"
        else:
            turn_label = "Your turn (X)" if self.current_player == HUMAN_SYMBOL else "Computer's turn (O)"
        renderer.draw_text(surface, font, turn_label, (10, 15))
        score_label = f"X: {self.scores['X']}  O: {self.scores['O']}  Draws: {self.scores['draw']}"
        renderer.draw_text(surface, font, score_label, (10, 45))
        renderer.draw_text(surface, font, f"Next round: {self.first_player} starts", (10, 72))
        import pygame
        hovered = renderer.button_at(pygame.mouse.get_pos())
        labels = {
            'new_round': "New Round (R)",
            'reset_match': "Reset Match (M)",
            'first_player': f"First: {self.first_player} (F)",
        }
        for name, label in labels.items():
            renderer.draw_button(surface, name, label, hover=(name == hovered))

        if self.round_over:
            text = f"{self.winner} wins!" if self.winner else "Draw!"
            renderer.draw_banner(surface, font, f"{text} R: new round")
