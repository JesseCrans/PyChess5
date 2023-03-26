from typing import Tuple, List
from .piece import Piece
from .support import *
from .settings import *

class Move:
    def __init__(self, position: List[List[Piece]], start_square: tuple, target_square: tuple, enpassant=False, promotion_choice=1, is_castle=False) -> None:
        """Initializes move object given the board position, the start and end square and special move parameters.

        Args:
            position (List[List[Piece]]): the position the move should be made in
            start_square (tuple): the starting position of the move
            target_square (tuple): the ending position of the move
            enpassant (bool, optional): wether the move is an en passant move. Defaults to False.
            promotion_choice (int, optional): what the piece should be promoted to incase of promotion. Defaults to 1.
            is_castle (bool, optional): wether the move is a castling move. Defaults to False.
        """
        self.start_rank, self.start_file = start_square
        self.target_rank, self.target_file = target_square
        self.piece: Piece = position[self.start_rank][self.start_file]
        self.captured: Piece = position[self.target_rank][self.target_file]

        # handles promotion
        self.is_promotion = False
        if self.piece and self.piece.type == 5 and (self.target_rank == 0 or self.target_rank == 7):
            self.is_promotion = True
        self.promotion_choice = promotion_choice

        # handles en passant
        self.is_enpassant = enpassant
        if self.is_enpassant:
            self.captured = position[self.start_rank][self.target_file]

        # handles castling
        self.is_castle = is_castle
        if self.is_castle:
            if self.start_file < self.target_file:  # king side
                self.castled_rook = position[self.start_rank][7]
            else:  # queen side
                self.castled_rook = position[self.start_rank][0]

        # gives every move a unique ID for comparing moves
        self.move_id = self.start_rank * 1000 + self.start_file * \
            100 + self.target_rank * 10 + self.target_file
        self.move_id_notation = f'{pos_to_not(self.start_rank, self.start_file)}{pos_to_not(self.target_rank, self.target_file)}'

    def __str__(self) -> str:
        """Returns the string representation of the object in the form of the start square and end square in chess notation.

        Returns:
            str: string representation of the object
        """
        return self.move_id_notation

    def __eq__(self, other) -> bool:
        """Compares move by move_id.

        Args:
            other (Move): move to compare to

        Returns:
            bool: equality of the moves
        """
        if isinstance(other, Move):
            return other.move_id == self.move_id
        return False