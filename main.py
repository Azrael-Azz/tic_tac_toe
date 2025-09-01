import pygame
import sys
import random

# Initialize pygame
pygame.init()

# Game configuration
WIDTH, HEIGHT = 600, 750
BOARD_ROWS, BOARD_COLS = 3, 3
SQUARE_SIZE = WIDTH // BOARD_COLS
LINE_WIDTH = 8
CIRCLE_RADIUS = SQUARE_SIZE // 3
CIRCLE_WIDTH = 12
CROSS_WIDTH = 18
SPACE = 50
PANEL_HEIGHT = 180

# Colors
GRID_COLOR = (220, 220, 220)       # Grid lines
CIRCLE_COLOR = (41, 128, 185)      # Player 1 color
CROSS_COLOR = (192, 57, 43)        # Player 2 color
TEXT_COLOR = (44, 62, 80)          # Text
PANEL_BORDER = (127, 140, 141)     # Panel border
BTN_COLOR = (52, 73, 94)           # Button default
BTN_HOVER = (26, 82, 118)          # Button hover
BTN_TEXT = (255, 255, 255)         # Button text

# Fonts
FONT = pygame.font.SysFont("Verdana", 34, bold=True)
SMALL_FONT = pygame.font.SysFont("Verdana", 22, bold=True)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe")

# Gradient colors
GRADIENT_TOP = (52, 152, 219)       # Light blue
GRADIENT_BOTTOM = (236, 240, 241)   # White-gray
PANEL_TOP = (52, 73, 94)            # Dark gray-blue
PANEL_BOTTOM = (34, 49, 63)         # Darker gray-blue


# Draw vertical gradient onto a surface
def draw_gradient_background(surface, top_color, bottom_color):
    height = surface.get_height()
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (surface.get_width(), y))


# Pre-rendered gradient backgrounds (optimization)
background_surface = pygame.Surface((WIDTH, HEIGHT))
draw_gradient_background(background_surface, GRADIENT_TOP, GRADIENT_BOTTOM)

panel_surface = pygame.Surface((WIDTH, PANEL_HEIGHT))
draw_gradient_background(panel_surface, PANEL_TOP, PANEL_BOTTOM)


# Board Class
class Board:
    def __init__(self):
        self.grid = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]

    def draw_lines(self):
        """Draws grid with shadows for depth."""
        shadow_offset = 6
        # Shadow grid
        for row in range(1, BOARD_ROWS):
            pygame.draw.line(screen, (180, 180, 180),
                             (0 + shadow_offset, row * SQUARE_SIZE + shadow_offset),
                             (WIDTH + shadow_offset, row * SQUARE_SIZE + shadow_offset), LINE_WIDTH)
        for col in range(1, BOARD_COLS):
            pygame.draw.line(screen, (180, 180, 180),
                             (col * SQUARE_SIZE + shadow_offset, 0 + shadow_offset),
                             (col * SQUARE_SIZE + shadow_offset, BOARD_ROWS * SQUARE_SIZE + shadow_offset), LINE_WIDTH)
        # Main grid
        for row in range(1, BOARD_ROWS):
            pygame.draw.line(screen, GRID_COLOR, (0, row * SQUARE_SIZE),
                             (WIDTH, row * SQUARE_SIZE), LINE_WIDTH)
        for col in range(1, BOARD_COLS):
            pygame.draw.line(screen, GRID_COLOR, (col * SQUARE_SIZE, 0),
                             (col * SQUARE_SIZE, BOARD_ROWS * SQUARE_SIZE), LINE_WIDTH)

    def draw_figures(self):
        """Draws circles (player 1) and crosses (player 2)."""
        for row in range(BOARD_ROWS):
            for col in range(BOARD_COLS):
                if self.grid[row][col] == 1:  # Circle
                    pygame.draw.circle(
                        screen, CIRCLE_COLOR,
                        (col * SQUARE_SIZE + SQUARE_SIZE // 2,
                         row * SQUARE_SIZE + SQUARE_SIZE // 2),
                        CIRCLE_RADIUS, CIRCLE_WIDTH
                    )
                elif self.grid[row][col] == 2:  # Cross
                    pygame.draw.line(
                        screen, CROSS_COLOR,
                        (col * SQUARE_SIZE + SPACE, row *
                         SQUARE_SIZE + SQUARE_SIZE - SPACE),
                        (col * SQUARE_SIZE + SQUARE_SIZE -
                         SPACE, row * SQUARE_SIZE + SPACE),
                        CROSS_WIDTH
                    )
                    pygame.draw.line(
                        screen, CROSS_COLOR,
                        (col * SQUARE_SIZE + SPACE, row * SQUARE_SIZE + SPACE),
                        (col * SQUARE_SIZE + SQUARE_SIZE - SPACE,
                         row * SQUARE_SIZE + SQUARE_SIZE - SPACE),
                        CROSS_WIDTH
                    )

    def mark_square(self, row, col, player):
        self.grid[row][col] = player

    def available_square(self, row, col):
        return self.grid[row][col] == 0

    def empty_squares(self):
        return [(r, c) for r in range(BOARD_ROWS) for c in range(BOARD_COLS) if self.grid[r][c] == 0]

    def is_full(self):
        return not self.empty_squares()

    def restart(self):
        self.grid = [[0] * BOARD_COLS for _ in range(BOARD_ROWS)]


# Button Class
class Button:
    def __init__(self, rect, text, callback):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback

    def draw(self, mouse_pos):
        """Draw button with hover effect."""
        color = BTN_HOVER if self.rect.collidepoint(mouse_pos) else BTN_COLOR
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        label = SMALL_FONT.render(self.text, True, BTN_TEXT)
        label_rect = label.get_rect(center=self.rect.center)
        screen.blit(label, label_rect)

    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.callback()


# Game Class
class Game:
    def __init__(self, vs_ai=False):
        self.board = Board()
        self.player = 1
        self.game_over = False
        self.vs_ai = vs_ai
        self.winner = None
        self.board.draw_lines()

        # Buttons for in-game menu
        self.buttons = [
            Button((50, HEIGHT - 70, 200, 50), "Restart",
                   lambda: start_game(self.vs_ai)),
            Button((350, HEIGHT - 70, 200, 50),
                   "Mode Select", self.reset_to_menu)
        ]

    def switch_player(self):
        self.player = 2 if self.player == 1 else 1

    def check_win(self, player):
        """Check if a player has won and draw a winning line."""
        for col in range(BOARD_COLS):
            if all(self.board.grid[row][col] == player for row in range(BOARD_ROWS)):
                self._draw_win_line((col * SQUARE_SIZE + SQUARE_SIZE // 2, 15),
                                    (col * SQUARE_SIZE + SQUARE_SIZE // 2, BOARD_ROWS * SQUARE_SIZE - 15))
                return True
        for row in range(BOARD_ROWS):
            if all(self.board.grid[row][c] == player for c in range(BOARD_COLS)):
                self._draw_win_line((15, row * SQUARE_SIZE + SQUARE_SIZE // 2),
                                    (WIDTH - 15, row * SQUARE_SIZE + SQUARE_SIZE // 2))
                return True
        if all(self.board.grid[i][i] == player for i in range(BOARD_ROWS)):
            self._draw_win_line(
                (15, 15), (WIDTH - 15, BOARD_ROWS * SQUARE_SIZE - 15))
            return True
        if all(self.board.grid[i][BOARD_ROWS - i - 1] == player for i in range(BOARD_ROWS)):
            self._draw_win_line(
                (15, BOARD_ROWS * SQUARE_SIZE - 15), (WIDTH - 15, 15))
            return True
        return False

    def _draw_win_line(self, start_pos, end_pos):
        """Draws winning line in the winner's color."""
        color = CIRCLE_COLOR if self.player == 1 else CROSS_COLOR
        pygame.draw.line(screen, color, start_pos, end_pos, LINE_WIDTH + 2)

    def show_winner(self):
        """Display winner or draw message."""
        text = f"Player {self.winner} Wins!" if self.winner else "Draw!"
        label = FONT.render(text, True, (255, 255, 255))
        rect = label.get_rect(center=(WIDTH // 2, HEIGHT - PANEL_HEIGHT // 2))
        screen.blit(label, rect)

    def ai_move(self):
        """Simple AI: chooses random move."""
        if not self.game_over:
            move = random.choice(self.board.empty_squares())
            self.board.mark_square(move[0], move[1], 2)
            if self.check_win(2):
                self.game_over = True
                self.winner = 2
            else:
                self.switch_player()

    def reset_to_menu(self):
        main()


# Mode Selection Screen
def choose_mode():
    btn1 = Button((150, 200, 300, 60), "Player vs Player",
                  lambda: start_game(False))
    btn2 = Button((150, 300, 300, 60), "Player vs Computer",
                  lambda: start_game(True))

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_surface, (0, 0))  # Use pre-rendered background
        btn1.draw(mouse_pos)
        btn2.draw(mouse_pos)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn1.check_click(event.pos)
                btn2.check_click(event.pos)


# Game Loop
def start_game(vs_ai):
    game = Game(vs_ai=vs_ai)

    while True:
        mouse_pos = pygame.mouse.get_pos()
        screen.blit(background_surface, (0, 0))  # Pre-rendered background
        game.board.draw_lines()
        game.board.draw_figures()

        # Draw bottom panel
        screen.blit(panel_surface, (0, HEIGHT - PANEL_HEIGHT))
        pygame.draw.line(screen, PANEL_BORDER, (0, HEIGHT -
                         PANEL_HEIGHT), (WIDTH, HEIGHT - PANEL_HEIGHT), 3)

        if game.game_over:
            game.show_winner()

        for btn in game.buttons:
            btn.draw(mouse_pos)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.pos[1] < BOARD_ROWS * SQUARE_SIZE and not game.game_over:
                    col = event.pos[0] // SQUARE_SIZE
                    row = event.pos[1] // SQUARE_SIZE
                    if game.board.available_square(row, col):
                        game.board.mark_square(row, col, game.player)
                        if game.check_win(game.player):
                            game.game_over = True
                            game.winner = game.player
                        elif game.board.is_full():
                            game.game_over = True
                        else:
                            game.switch_player()
                            if game.vs_ai and not game.game_over and game.player == 2:
                                pygame.time.delay(300)
                                game.ai_move()

                for btn in game.buttons:
                    btn.check_click(event.pos)


# Main Entry Point
def main():
    choose_mode()


if __name__ == "__main__":
    main()
