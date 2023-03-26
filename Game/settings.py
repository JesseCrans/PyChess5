import pygame
import os

# This file is to store all the constant values in the chess program

# window settings
SCREEN_SIZE = 600
UI_WIDTH = 0  # BOARD_SIZE//2
WIN = pygame.display.set_mode((SCREEN_SIZE + UI_WIDTH, SCREEN_SIZE))
pygame.display.set_caption('PyChess')
FPS = 60

# game settings
SQUARE_SIZE = SCREEN_SIZE//8
PIECE_SIZE = SQUARE_SIZE * 0.8

# colors
WHITE = (255, 255, 220)
BLACK = (70, 161, 68)
RED = (255, 153, 153, 200)
YELLOW = (255, 255, 153, 200)
ORANGE = (255, 153, 51, 200)
DARK_RED = (153, 0, 0, 200)

BG = (192, 192, 192, 200)
BG_DARK = (128, 128, 128)

# images
white_king = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'king_w.png')), (PIECE_SIZE, PIECE_SIZE))
black_king = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'king_b.png')), (PIECE_SIZE, PIECE_SIZE))
white_queen = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'queen_w.png')), (PIECE_SIZE, PIECE_SIZE))
black_queen = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'queen_b.png')), (PIECE_SIZE, PIECE_SIZE))
white_pawn = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'pawn_w.png')), (PIECE_SIZE, PIECE_SIZE))
black_pawn = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'pawn_b.png')), (PIECE_SIZE, PIECE_SIZE))
white_horse = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'knight_w.png')), (PIECE_SIZE, PIECE_SIZE))
black_horse = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'knight_b.png')), (PIECE_SIZE, PIECE_SIZE))
white_bishop = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'bishop_w.png')), (PIECE_SIZE, PIECE_SIZE))
black_bishop = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'bishop_b.png')), (PIECE_SIZE, PIECE_SIZE))
white_rook = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'rook_w.png')), (PIECE_SIZE, PIECE_SIZE))
black_rook = pygame.transform.scale(pygame.image.load(
    os.path.join('Assets', 'rook_b.png')), (PIECE_SIZE, PIECE_SIZE))

IMGS = [
    [white_king, black_king],
    [white_queen, black_queen],
    [white_rook, black_rook],
    [white_bishop, black_bishop],
    [white_horse, black_horse],
    [white_pawn, black_pawn]
]

# other
BOARD_NOTATION = [
    [col+str(row) for col in ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']] for row in range(8, 0, -1)
]

COLORS = ['White', 'Black']
PIECE_NAME = ['k', 'q', 'r', 'b', 'n', 'p']
PIECE_NAME_FULL = ['king', 'queen', 'rook', 'bishop', 'knight', 'pawn']
PIECE_COLORS = ['w', 'b']
PIECE_COLORS_FULL = ['white', 'black']
PIECE_VALUE = [999999, 9, 5, 3, 3, 1]
