import pygame
from pygame import gfxdraw
from typing import List, Tuple

from .settings import *
from .support import *
from .board import Board
from .piece import Piece
from .move import Move

pygame.font.init()
font = pygame.font.SysFont('monospace', SQUARE_SIZE//4)
font_text = pygame.font.SysFont('monospace', SQUARE_SIZE//3)


class Interface:
    def __init__(self, win: pygame.Surface, board: Board) -> None:
        """Initializes the interface object with a pygame window and a board object.

        Args:
            win (pygame.Surface): pygame window the interface interacts with
            board (Board): the board that the interface has to display
        """
        self.win = win
        self.board = board
        self.reset()

    def reset(self) -> None:
        """Resets the interface object to start a new game.
        """
        self.board.reset()

        self.player = 0
        self.selected = None
        self.legal_moves = self.board.get_legal_moves()
        self.selected_moves = self.get_selected_legal_moves()
        self.fen_list = []

        self.draw()

    def select(self, target: Tuple[int, int]) -> bool:
        """Handles player clicking on squares to select pieces and make moves.

        Args:
            target (Tuple[int, int]): the clicked square

        Returns:
            bool: if the selection was successfull, a selection is successfull when a move is made
        """
        if True:
            if self.selected:
                piece = self.board.position[self.selected[0]][self.selected[1]]
                if piece and piece.color == self.board.turn:
                    result = self.move(self.selected, target)
                    if result:
                        self.selected = None
                        self.get_selected_legal_moves()
                        return True
                    else:
                        self.selected = None
                        self.select(target)
                        self.get_selected_legal_moves()

                self.selected = target
                self.get_selected_legal_moves()

            self.selected = target
            self.get_selected_legal_moves()

        return False

    def move(self, selected: Tuple[int, int], clicked: Tuple[int, int]) -> bool:
        """Executes a move that is tried by the select function. If it isnt a legal move it returns false.

        Args:
            selected (Tuple[int, int]): selected square, 1st clicked
            clicked (Tuple[int, int]): clicked square, 2nd clicked

        Returns:
            bool: success of the tried move
        """
        move = Move(self.board.position, selected, clicked)
        move_made = False
        for legal_move in self.legal_moves:
            if move == legal_move:
                if legal_move.is_promotion:
                    legal_move.promotion_choice = self.ask_promotion()
                self.make_move(legal_move)
                return True

        return False

    def make_move(self, move: Move) -> None:
        """Executes a given move on the board object and updates the legal moves and the fen string list.

        Args:
            move (Move): the move to be made
        """
        self.board.make_move(move)
        self.fen_list.append(self.board.get_fen().split(' ')[0:4])
        self.legal_moves = self.board.get_legal_moves()

    def unmake_move(self) -> None:
        """Unmakes the last move made on the board object, updatest the legal moves and the fen list.
        """
        self.board.unmake_move()
        self.fen_list.pop()
        self.legal_moves = self.board.get_legal_moves()

    def ask_promotion(self) -> int:
        """Ask for promotion choice from the player.

        Returns:
            int: promotion choice made by player
        """
        for rank in (3, 4):
            for file in (3, 4):
                gfxdraw.box(
                    self.win, (file*SQUARE_SIZE, rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), BG)
                x = SQUARE_SIZE*file + (SQUARE_SIZE - PIECE_SIZE)/2
                y = SQUARE_SIZE*rank + (SQUARE_SIZE - PIECE_SIZE)/2
                if rank == 3 and file == 3:
                    self.win.blit(IMGS[1][self.board.turn], (x, y))
                elif rank == 3 and file == 4:
                    self.win.blit(IMGS[2][self.board.turn], (x, y))
                elif rank == 4 and file == 3:
                    self.win.blit(IMGS[3][self.board.turn], (x, y))
                elif rank == 4 and file == 4:
                    self.win.blit(IMGS[4][self.board.turn], (x, y))
        pygame.display.update()

        clock = pygame.time.Clock()
        while True:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    x, y = pos
                    rank, file = get_row_col_from_mouse(pos)
                    if rank == 3 and file == 3:
                        return 1
                    elif rank == 3 and file == 4:
                        return 2
                    elif rank == 4 and file == 3:
                        return 3
                    elif rank == 4 and file == 4:
                        return
                    else:  # if no piece was selected, ask again until a selection is made
                        return self.ask_promotion()

    def draw(self) -> None:
        """Draw the board and pieces on screen along with the selected square, legal moves, the last move made and the end game message in case the game is over.
        """
        self.draw_squares()
        self.draw_pieces(self.board.position)
        self.highlight_selected()
        self.highlight_legal_moves()
        self.highlight_last_move()
        self.end_game()
        pygame.display.update()

    def draw_squares(self) -> None:
        """Draws the squares of the board including notation along the edges.
        """
        for rank in range(8):
            for file in range(rank % 2, 8, 2):
                pygame.draw.rect(
                    self.win, WHITE, (file*SQUARE_SIZE, rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            for file in range((rank+1) % 2, 8, 2):
                pygame.draw.rect(
                    self.win, BLACK, (file*SQUARE_SIZE, rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        for i in range(8):
            img = font.render(f'{pos_to_not(i, 0)}', True, (0, 0, 0))
            self.win.blit(img, (0*SQUARE_SIZE + 0.71 *
                                SQUARE_SIZE, i*SQUARE_SIZE + 0.77*SQUARE_SIZE))
            img = font.render(f'{pos_to_not(7, i)}', True, (0, 0, 0))
            self.win.blit(img, (i*SQUARE_SIZE + 0.71 *
                                SQUARE_SIZE, 7*SQUARE_SIZE + 0.77*SQUARE_SIZE))

    def draw_pieces(self, position: List[List[Piece]]) -> None:
        """Draws all the pieces in the current position.

        Args:
            position (List[List[Piece]]): current board position
        """
        for rank in range(8):
            for file in range(8):
                piece: Piece = position[rank][file]
                if piece:
                    piece.draw(self.win)

    def end_game(self) -> bool:
        """Checks if the game has ended and displays a corresponding message if it has ended.

        Returns:
            bool: wether the game has ended
        """

        # no moves
        if not self.legal_moves:
            background_rect = pygame.Rect(
                1*SQUARE_SIZE, 1*SQUARE_SIZE, 6*SQUARE_SIZE, 6*SQUARE_SIZE)
            gfxdraw.box(self.win, background_rect, BG)

            checked, _, _ = self.board._check_for_pins_and_checks()
            if checked:
                img = font_text.render(
                    f'{COLORS[(self.board.turn + 1) % 2]} has won', True, (0, 0, 0))
                self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                              SCREEN_SIZE//2 - 0.5*img.get_height()))
            else:
                img = font_text.render(f'Stalemate', True, (0, 0, 0))
                self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                              SCREEN_SIZE//2 - 0.5*img.get_height()))

            img = font_text.render(
                f'Press "r" to reset the game', True, (0, 0, 0))
            self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                          SCREEN_SIZE//2 - 0.5*img.get_height() + SQUARE_SIZE))
            return True

        # 50 move rule
        if self.board.halfturn >= 50:
            background_rect = pygame.Rect(
                1*SQUARE_SIZE, 1*SQUARE_SIZE, 6*SQUARE_SIZE, 6*SQUARE_SIZE)
            gfxdraw.box(self.win, background_rect, BG)

            img = font_text.render(f'Draw by 50 move rule', True, (0, 0, 0))
            self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                          SCREEN_SIZE//2 - 0.5*img.get_height()))

            img = font_text.render(
                f'Press "r" to reset the game', True, (0, 0, 0))
            self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                          SCREEN_SIZE//2 - 0.5*img.get_height() + SQUARE_SIZE))
            return True

        # 3 fold repetition
        if any([self.fen_list.count(i) > 2 for i in self.fen_list]):
            background_rect = pygame.Rect(
                1*SQUARE_SIZE, 1*SQUARE_SIZE, 6*SQUARE_SIZE, 6*SQUARE_SIZE)
            gfxdraw.box(self.win, background_rect, BG)

            img = font_text.render(f'Draw by repetition', True, (0, 0, 0))
            self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                          SCREEN_SIZE//2 - 0.5*img.get_height()))

            img = font_text.render(
                f'Press "r" to reset the game', True, (0, 0, 0))
            self.win.blit(img, (SCREEN_SIZE//2 - 0.5*img.get_width(),
                          SCREEN_SIZE//2 - 0.5*img.get_height() + SQUARE_SIZE))
            return True

        return False

    def highlight_selected(self) -> None:
        """Highlights the selected square
        """
        if self.selected:
            rank, file = self.selected
            gfxdraw.box(
                self.win, (file*SQUARE_SIZE, rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), YELLOW)
            piece = self.board.position[rank][file]
            if piece:
                piece.draw(self.win)

    def highlight_legal_moves(self) -> None:
        """Highlights the legal moves possible by the piece on the selected square.
        """
        if self.legal_moves_piece:
            for move in self.legal_moves_piece:
                gfxdraw.box(self.win, (move.target_file*SQUARE_SIZE,
                                       move.target_rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), RED)
                piece = self.board.position[move.target_rank][move.target_file]
                if piece:
                    piece.draw(self.win)

    def highlight_last_move(self) -> None:
        """Highlights the last move made.
        """
        if self.board.move_log:
            last_move: Move = self.board.move_log[-1]
            gfxdraw.box(self.win, (last_move.start_file*SQUARE_SIZE,
                                   last_move.start_rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), ORANGE)
            gfxdraw.box(self.win, (last_move.target_file*SQUARE_SIZE,
                                   last_move.target_rank*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), ORANGE)

            last_move.piece.draw(self.win)

    def get_selected_legal_moves(self) -> None:
        """Generates a list of all legal moves for the selected piece.
        """
        self.legal_moves_piece = [move for move in self.legal_moves if (
            move.start_rank, move.start_file) == self.selected]
