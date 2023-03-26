from .settings import *
from .support import *

class Piece:
    def __init__(self, rank: int, file: int, type: int, color: bool) -> None:
        """Initializes a piece object with a position, type and color.

        Args:
            rank (int): the rank on which the piece is placed
            file (int): the file on which the piece is placed
            type (int): the type of piece
            color (bool): what team the piece is on
        """
        self.rank, self.file = rank, file  # position on the board
        self.type, self.color = type, color  # what piece it is

        self.img = IMGS[self.type][self.color]

        self.pos()
        
    def __str__(self) -> str:
        """Generates a string representation of the piece object.

        Returns:
            str: string representation of object
        """
        string = f'{PIECE_COLORS[self.color]}{PIECE_NAME[self.type]}'
        return string

    def pos(self) -> None:
        """Calculates the position on screen based on the coordinates on the board.
        """
        self.x = SQUARE_SIZE*self.file + (SQUARE_SIZE - PIECE_SIZE)/2
        self.y = SQUARE_SIZE*self.rank + (SQUARE_SIZE - PIECE_SIZE)/2

    def move(self, rank: int, file: int) -> None:
        """Moves the piece to the specified coordinates.

        Args:
            row (int): row which the piece should move to
            col (int): column which the piece should move to
        """
        self.rank = rank
        self.file = file
        self.pos()

    def promote_to(self, promotion: int) -> None:
        """Promotes a piece to another type.

        Args:
            promotion (int): type to promote to
        """
        self.type = promotion
        self.img = IMGS[self.type][self.color]

    def draw(self, win: pygame.Surface) -> None:
        """Draws the piece on the screen.

        Args:
            win (pygame.Surface): the window the piece should be drawn on
        """
        win.blit(self.img, (self.x, self.y))

