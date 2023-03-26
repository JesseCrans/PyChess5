from .settings import *
from typing import Tuple


def pos_to_not(rank: int, file: int) -> str:
    """Takes in a row and col and returns the corresponding chess notation.

    Args:
        row (int): the row of the square
        col (int): the column of the square

    Returns:
        str: the standard chess notation of the square
    """
    return BOARD_NOTATION[rank][file]


def not_to_pos(notation: str) -> Tuple[int, int]:
    """Takes in square notation and returns the corresponding position.

    Args:
        notation (str): standard chess notation for a square

    Returns:
        tuple: (rank, file) of the specified square
    """
    for i, rank in enumerate(BOARD_NOTATION):
        if notation in rank:
            return i, rank.index(notation)


def get_row_col_from_mouse(pos: Tuple[float, float]) -> Tuple[int, int]:
    """Takes in a position from the mouse and gives the corresponding row and column.

    Args:
        pos (Tuple[float, float]): mouse position

    Returns:
        Tuple[int, int]: row and column
    """
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col
