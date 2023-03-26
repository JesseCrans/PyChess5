import pygame
import pyperclip
from copy import deepcopy
from typing import Tuple, List
from collections import defaultdict

from .settings import *
from .support import *
from .piece import Piece
from .move import Move


class Board:
    def __init__(self, fen: str) -> None:
        """Initializes an instance of the board class, with a given fen string.

        Args:
            fen (str): A FEN string (Forsyth-Edwards Notation)
        """
        self.fen = fen
        self.reset()

        self._move_functions = {
            0: self._get_king_moves,
            1: self._get_queen_moves,
            2: self._get_rook_moves,
            3: self._get_bishop_moves,
            4: self._get_knight_moves,
            5: self._get_pawn_moves
        }

        self._pinned = []
        self._checking = []

    def reset(self) -> None:
        """Resets the board by rereading the initial fen string and intializing the move, state and fen logs.
        """
        self.read_fen()
        self.fen_list = []
        self.move_log: List[Move] = []
        self.state_log = []

    def read_fen(self) -> None:
        """Reads the fen string given on creation and converts it to a position and game state.
        """
        self.position = [
            [None for _ in range(8)] for _ in range(8)]
        fen_pos, fen_turn, fen_castle, fen_enpassant_target_square, fen_halfturn, fen_fullturn = self.fen.split(
            ' ')

        # position
        rank = 0
        file = 0
        for char in fen_pos:
            if char.isalpha():
                if char.isupper():
                    color = 0
                    type = PIECE_NAME.index(char.lower())
                    if type == 0:
                        self.white_king = (rank, file)
                else:
                    color = 1
                    type = PIECE_NAME.index(char)
                    if type == 0:
                        self.black_king = (rank, file)

                self.position[rank][file] = Piece(rank, file, type, color)
                file += 1
            elif char.isnumeric():
                file += int(char)
            else:
                rank += 1
                file = 0

        # turn
        if fen_turn == 'w':
            self.turn = 0
        else:
            self.turn = 1

        # castle rights
        self.castle = [[False, False], [False, False]]
        if 'K' in fen_castle:
            self.castle[0][0] = True
        if 'Q' in fen_castle:
            self.castle[0][1] = True
        if 'k' in fen_castle:
            self.castle[1][0] = True
        if 'q' in fen_castle:
            self.castle[1][1] = True

        # en passant
        self.en_passant_target_square = ()
        if fen_enpassant_target_square != '-':
            rank, file = not_to_pos(fen_enpassant_target_square)
            self.en_passant_target_square = (rank, file)

        # half turn
        self.halfturn = int(fen_halfturn)

        # full turn
        self.fullturn = int(fen_fullturn)

    def get_fen(self) -> str:
        """Generates the fen string of the current board state.

        Returns:
            str: fen string of the current board state
        """
        fen = ''
        # position sequence
        for row in self.position:
            count = 0
            for piece in row:
                if not piece:
                    count += 1
                else:
                    if count != 0:
                        fen += str(count)
                        count = 0
                    if piece.color == 0:
                        fen += PIECE_NAME[piece.type].upper()
                    else:
                        fen += PIECE_NAME[piece.type]
            if count != 0:
                fen += str(count)
            fen += '/'

        fen = fen.rstrip('/')
        fen += ' '

        # turn
        if self.turn == 0:
            fen += 'w'
        else:
            fen += 'b'
        fen += ' '

        # castling rights
        if self.castle[0][0]:
            fen += 'K'
        if self.castle[0][1]:
            fen += 'Q'
        if self.castle[1][0]:
            fen += 'k'
        if self.castle[1][1]:
            fen += 'q'
        if (self.castle[0][0] is False and
            self.castle[0][1] is False and
            self.castle[1][0] is False and
                self.castle[1][1] is False):
            fen += '-'
        fen += ' '

        # en passant target square
        if self.en_passant_target_square:
            fen += pos_to_not(*self.en_passant_target_square)
        else:
            fen += '-'
        fen += ' '

        # half and full turns
        fen += str(self.halfturn)
        fen += ' '

        fen += str(self.fullturn)

        pyperclip.copy(fen)

        return fen

    def make_move(self, move: Move) -> None:
        """Makes a move on the board and handles all special move cases.

        Args:
            move (Move): the move to be executed
        """
        self.move_log.append(move)
        self.state_log.append([deepcopy(self.castle),
                               self.en_passant_target_square,
                               self.halfturn,
                               self.fullturn])

        self.position[move.start_rank][move.start_file], self.position[move.target_rank][
            move.target_file] = None, self.position[move.start_rank][move.start_file]

        # handles special pawn moves
        if move.piece.type == 5:
            if abs(move.start_rank - move.target_rank) == 2:
                self.en_passant_target_square = (
                    (move.start_rank + move.target_rank)//2, move.start_file)
            else:
                self.en_passant_target_square = ()

            # promotion move
            if move.is_promotion:
                move.piece.promote_to(move.promotion_choice)

            # en passant move, removes the captured pawn
            if move.is_enpassant:
                self.position[move.start_rank][move.target_file] = None

        elif move.piece.type == 0:
            # update king position
            if self.turn == 0:
                self.white_king = (move.target_rank, move.target_file)
            else:
                self.black_king = (move.target_rank, move.target_file)

            # update castling rights
            self.castle[self.turn] = [False, False]

            # handles castling move
            if move.is_castle:
                if move.start_file < move.target_file:
                    self.position[move.start_rank][7], self.position[move.start_rank][5] = None, move.castled_rook
                    move.castled_rook.move(move.start_rank, 5)
                else:
                    self.position[move.start_rank][0], self.position[move.start_rank][3] = None, move.castled_rook
                    move.castled_rook.move(move.start_rank, 3)

        # update castling rights for rook move
        elif move.piece.type == 2:
            # (0, 7) for black, (7, 7) for white
            if (move.start_rank, move.start_file) == (7 - 7*self.turn, 7):
                self.castle[self.turn][0] = False
            # (0, 0) for black, (7, 0) for white
            if (move.start_rank, move.start_file) == (7 - 7*self.turn, 0):
                self.castle[self.turn][1] = False

        if move.piece.type != 5:
            # updates en_passant_target_square
            self.en_passant_target_square = ()

        if move.captured and move.captured.type == 2:
            if move.captured.color == 0:
                if move.target_file == 7:
                    self.castle[0][0] = False
                if move.target_rank == 0:
                    self.castle[0][1] = False
            else:
                if move.target_file == 7:
                    self.castle[1][0] = False
                if move.target_rank == 0:
                    self.castle[1][1] = False

        # moves the piece object
        move.piece.move(move.target_rank, move.target_file)

        # updating the turn
        self.turn = (self.turn + 1) % 2

        if self.turn == 0:
            self.fullturn += 1

        if move.captured or move.piece.type == 5:
            self.halfturn = 0
        else:
            self.halfturn += 1

    def unmake_move(self) -> None:
        """Unmakes the last move made in the case that there is a last move.
        """
        if self.move_log:
            move = self.move_log.pop()
            self.castle, self.en_passant_target_square, self.halfturn, self.fullturn = self.state_log.pop()

            self.turn = (self.turn + 1) % 2

            self.position[move.start_rank][move.start_file], self.position[
                move.target_rank][move.target_file] = move.piece, move.captured

            if move.is_promotion:
                move.piece.promote_to(5)

            if move.piece.type == 5:
                if move.is_enpassant:
                    self.position[move.start_rank][move.target_file], self.position[
                        move.target_rank][move.target_file] = move.captured,  None

            elif move.piece.type == 0:
                if self.turn == 0:
                    self.white_king = (move.start_rank, move.start_file)
                else:
                    self.black_king = (move.start_rank, move.start_file)

                if move.is_castle:
                    if move.start_file < move.target_file:
                        self.position[move.start_rank][7], self.position[move.start_rank][5] = move.castled_rook, None
                        move.castled_rook.move(move.start_rank, 7)
                    else:
                        self.position[move.start_rank][0], self.position[move.start_rank][3] = move.castled_rook, None
                        move.castled_rook.move(move.start_rank, 0)

            move.piece.move(move.start_rank, move.start_file)

    def get_legal_moves(self) -> List[Move]:
        """Generates all legal moves in a position.

        Returns:
            List[Move]: list of legal moves
        """
        self._checked, self._pinned, self._checking = self._check_for_pins_and_checks()

        if self.turn == 0:
            king_rank, king_file = self.white_king
        else:
            king_rank, king_file = self.black_king

        moves = []
        if self._checked:
            if len(self._checking) == 1:
                moves = self._get_pseudo_moves()
                check = self._checking[0]
                check_rank, check_file = check[0], check[1]
                checking_piece = self.position[check_rank][check_file]
                valid_squares = []
                if checking_piece.type == 4:
                    valid_squares.append((check_rank, check_file))
                elif checking_piece.type == 5 and self.en_passant_target_square:
                    valid_squares.append((self.en_passant_target_square))
                    valid_squares.append((check_rank, check_file))
                else:
                    for i in range(1, 8):
                        valid_square = (
                            king_rank + check[2]*i, king_file + check[3]*i)
                        valid_squares.append(valid_square)
                        if valid_square == (check_rank, check_file):
                            break
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].piece.type != 0:
                        if not (moves[i].target_rank, moves[i].target_file) in valid_squares:
                            moves.pop(i)
                        elif ((moves[i].target_rank, moves[i].target_file) == self.en_passant_target_square and
                              moves[i].piece.type != 5):
                            moves.pop(i)
            else:
                self._get_king_moves(king_rank, king_file, moves)
        else:
            moves = self._get_pseudo_moves()

        return moves

    def _check_for_pins_and_checks(self) -> Tuple[bool, List[Piece], List[Piece]]:
        """Checks the current position for any checking or pinned pieces.

        Returns:
            Tuple[bool, List[Piece], List[Piece]]: tuple containing if the current player is in check, if there are any pinned pieces, if there are any checking pieces
        """
        pinned = []
        checking = []
        checked = False

        if self.turn == 0:
            start_rank, start_file = self.white_king
        else:
            start_rank, start_file = self.black_king

        directions = ((0, 1), (0, -1), (1, 0), (-1, 0),
                      (1, 1), (1, -1), (-1, 1), (-1, -1))

        for i, d in enumerate(directions):
            possible_pin = ()
            for j in range(1, 8):
                target_rank = start_rank + d[0] * j
                target_file = start_file + d[1] * j
                if 0 <= target_rank < 8 and 0 <= target_file < 8:
                    target = self.position[target_rank][target_file]

                    if target:
                        if target.color == self.turn and target.type != 0:
                            if not possible_pin:
                                possible_pin = (target_rank, target_file, *d)
                            else:
                                break
                        else:
                            if (target.type == 1 or
                                (0 <= i <= 3 and target.type == 2) or
                                (4 <= i <= 7 and target.type == 3) or
                                (j == 1 and target.type == 5 and ((self.turn == 0 and 6 <= i <= 7) or
                                                                  (self.turn == 1 and 4 <= i <= 5))) or
                                    (j == 1 and target.type == 0 and self.turn != target.color)):
                                if not possible_pin:
                                    checked = True
                                    checking.append(
                                        (target_rank, target_file, *d))
                                    break
                                else:
                                    pinned.append(possible_pin)
                                    break
                            elif target.type == 0 and self.turn == target.color:
                                continue
                            else:
                                break

                else:
                    break

        knight_moves = ((-1, -2), (-1, 2), (1, -2), (1, 2),
                        (-2, -1), (-2, 1), (2, -1), (2, 1))

        for move in knight_moves:
            target_rank, target_file = start_rank + \
                move[0], start_file + move[1]

            if 0 <= target_rank < 8 and 0 <= target_file < 8:
                target = self.position[target_rank][target_file]
                if target:
                    if target.color != self.turn and target.type == 4:
                        checked = True
                        checking.append((target_rank, target_file, *move))

        return checked, pinned, checking

    def _check_for_en_passant_pin(self, rank: int, file: int) -> bool:
        """Checks if the pawn on the specified square is incapable of making an en passant move due to the king being in check afterwards.

        Args:
            rank (int): rank of the pawn
            file (int): file of the pawn

        Returns:
            bool: wether the pawn can make the en passant move, if True the pawn is pinned
        """
        if self.turn == 0:
            king = self.white_king
        else:
            king = self.black_king

        possible_pin = (king[0] == rank)

        if possible_pin:
            pin_direction = 1 if king[1] < file else -1
            white_pawns = 0
            black_pawns = 0
            for i in range(1, 8):
                if white_pawns > 1 or black_pawns > 1:
                    return False
                target_rank = king[0]
                target_file = king[1] + pin_direction*i
                if 0 <= target_rank < 8 and 0 <= target_file < 8:
                    target = self.position[target_rank][target_file]
                    if target:
                        if target.type == 5:
                            if target.color == 0:
                                white_pawns += 1
                            else:
                                black_pawns += 1
                        elif (target.type == 3 or target.type == 4 or target.type == 0 or
                              ((target.type == 1 or target.type == 2) and target.color == self.turn)):
                            return False
                        elif ((target.type == 1 or target.type == 2) and target.color != self.turn and
                              white_pawns == 1 and black_pawns == 1):
                            return True

        return False

    def _get_pseudo_moves(self) -> List[Move]:
        """Gets all pseudo legal moves in the current position without doing all legality checks.

        Returns:
            List[Move]: list of pseudo legal moves
        """
        moves = []
        for rank in range(8):
            for file in range(8):
                piece = self.position[rank][file]
                if piece and piece.color == self.turn:
                    self._move_functions[piece.type](rank, file, moves)
        return moves

    def _get_pawn_moves(self, rank: int, file: int, move_list: list) -> None:
        """Generates all pseudo legal pawn moves in the current position and adds them to the given move list.

        Args:
            rank (int): rank of the pawn
            file (int): file of the pawn
            move_list (list): list the generated moves should be added to
        """
        pinned = False
        pin_direction = ()
        for i in range(len(self._pinned)-1, -1, -1):
            if self._pinned[i][0] == rank and self._pinned[i][1] == file:
                pinned = True
                pin_direction = (self._pinned[i][2], self._pinned[i][3])
                self._pinned.pop(i)
                break

        pawn_direction = -1 if self.turn == 0 else 1

        # single pawn push
        if self.position[rank + pawn_direction][file] is None:
            if not pinned or pin_direction == (-1, 0) or pin_direction == (1, 0):
                move_list.append(
                    Move(self.position, (rank, file), (rank + pawn_direction, file)))

                # add promtion moves
                if rank + pawn_direction == 0 or rank + pawn_direction == 7:
                    for i in range(2, 5):
                        move_list.append(
                            Move(self.position, (rank, file), (rank + pawn_direction, file), promotion_choice=i))

                # double pawn push
                start_rank = 6 if self.turn == 0 else 1
                if rank == start_rank and self.position[rank + 2*pawn_direction][file] is None:
                    move_list.append(
                        Move(self.position, (rank, file), (rank + 2*pawn_direction, file)))

        # if the pawn is not on the left edge it can move left
        if file > 0:
            if not pinned or pin_direction == (-1, -1) or pin_direction == (1, 1):
                target_rank, target_file = rank + pawn_direction, file - 1
                target_piece = self.position[target_rank][target_file]
                if target_piece and target_piece.color != self.turn:
                    move_list.append(
                        Move(self.position, (rank, file), (target_rank, target_file)))

                    # add promotion moves
                    if target_rank == 0:
                        for i in range(2, 5):
                            move_list.append(
                                Move(self.position, (rank, file), (target_rank, target_file), promotion_choice=i))

                # check for en passant possibility
                elif (target_rank, target_file) == self.en_passant_target_square:
                    if not self._check_for_en_passant_pin(rank, file):
                        move_list.append(
                            Move(self.position, (rank, file), (target_rank, target_file), enpassant=True))

        # if the pawn is not on the right edge it can move right
        if file < 7:
            if not pinned or pin_direction == (-1, 1) or pin_direction == (1, -1):
                target_rank, target_file = rank + pawn_direction, file + 1
                target_piece = self.position[target_rank][target_file]
                if target_piece and target_piece.color != self.turn:
                    move_list.append(
                        Move(self.position, (rank, file), (target_rank, target_file)))

                    # add promotion moves
                    if rank + pawn_direction == 0:
                        for i in range(2, 5):
                            move_list.append(
                                Move(self.position, (rank, file), (target_rank, target_file), promotion_choice=i))

                # check for en passant possibility
                elif (target_rank, target_file) == self.en_passant_target_square:
                    if not self._check_for_en_passant_pin(rank, file):
                        move_list.append(
                            Move(self.position, (rank, file), (target_rank, target_file), enpassant=True))

    def _get_king_moves(self, rank: int, file: int, move_list: list) -> None:
        """Generates all pseudo legal king moves in the current position and adds them to the given move list.

        Args:
            rank (int): rank of the king
            file (int): file of the king
            move_list (list): list the generated moves should be added to
        """
        moves = ((0, 1), (0, -1), (1, 0), (-1, 0),
                 (1, 1), (1, -1), (-1, 1), (-1, -1))
        for i in moves:
            target_rank, target_file = rank + i[0], file + i[1]
            if 0 <= target_rank < 8 and 0 <= target_file < 8:
                target = self.position[target_rank][target_file]
                if target == None or (target and target.color != self.turn):

                    if self.turn == 0:
                        self.white_king = (target_rank, target_file)
                    else:
                        self.black_king = (target_rank, target_file)

                    checked, _, _ = self._check_for_pins_and_checks()
                    if not checked:
                        move_list.append(
                            Move(self.position, (rank, file), (target_rank, target_file)))

                    if self.turn == 0:
                        self.white_king = (rank, file)
                    else:
                        self.black_king = (rank, file)

        if (self.castle[self.turn][0] and
            self.position[rank][file+1] is None and
            self.position[rank][file+2] is None and
                self.position[rank][7] is not None):
            for i in range(1, 3):
                target_rank, target_file = rank, file + i
                if self.turn == 0:
                    self.white_king = (target_rank, target_file)
                else:
                    self.black_king = (target_rank, target_file)
                checked, _, _ = self._check_for_pins_and_checks()
                if self.turn == 0:
                    self.white_king = (rank, file)
                else:
                    self.black_king = (rank, file)
                if checked:
                    break
                if not checked and i == 2:
                    move_list.append(
                        Move(self.position, (rank, file), (rank, file + 2), is_castle=True))
        if (self.castle[self.turn][1] and
            self.position[rank][file-1] is None and
            self.position[rank][file-2] is None and
            self.position[rank][file-3] is None and
                self.position[rank][0] is not None):
            for i in range(1, 3):
                target_rank, target_file = rank, file - i
                if self.turn == 0:
                    self.white_king = (target_rank, target_file)
                else:
                    self.black_king = (target_rank, target_file)
                checked, _, _ = self._check_for_pins_and_checks()
                if self.turn == 0:
                    self.white_king = (rank, file)
                else:
                    self.black_king = (rank, file)
                if checked:
                    break
                if not checked and i == 2:
                    move_list.append(
                        Move(self.position, (rank, file), (rank, file - 2), is_castle=True))

    def _get_queen_moves(self, rank: int, file: int, move_list: list) -> None:
        """Generates all pseudo legal queen moves in the current position and adds them to the given move list.

        Args:
            rank (int): rank of the queen
            file (int): file of the queen
            move_list (list): list the generated moves should be added to
        """
        self._get_bishop_moves(rank, file, move_list)
        self._get_rook_moves(rank, file, move_list)

    def _get_rook_moves(self, rank: int, file: int, move_list: list) -> None:
        """Generates all pseudo legal rook moves in the current position and adds them to the given move list.

        Args:
            rank (int): rank of the rook
            file (int): file of the rook
            move_list (list): list the generated moves should be added to
        """
        pinned = False
        pin_direction = ()
        for i in range(len(self._pinned)-1, -1, -1):
            if self._pinned[i][0] == rank and self._pinned[i][1] == file:
                pinned = True
                pin_direction = (self._pinned[i][2], self._pinned[i][3])
                if self.position[rank][file].type != 1:
                    self._pinned.pop(i)
                break

        directions = ((0, 1), (0, -1), (1, 0), (-1, 0))
        for i in directions:
            for j in range(1, 8):
                target_rank, target_file = rank + j*i[0], file + j*i[1]
                if 0 <= target_rank < 8 and 0 <= target_file < 8:
                    if not pinned or pin_direction == i or pin_direction == (-i[0], -i[1]):
                        piece = self.position[target_rank][target_file]
                        if piece == None:
                            move_list.append(
                                Move(self.position, (rank, file), (target_rank, target_file)))
                        elif piece and piece.color != self.turn:
                            move_list.append(
                                Move(self.position, (rank, file), (target_rank, target_file)))
                            break
                        else:
                            break

    def _get_bishop_moves(self, rank: int, file: int, move_list: list) -> None:
        """Generates all pseudo legal bishop moves in the current position and adds them to the given move list.

        Args:
            rank (int): rank of the bishop
            file (int): file of the bishop
            move_list (list): list the generated moves should be added to
        """
        pinned = False
        pin_direction = ()
        for i in range(len(self._pinned)-1, -1, -1):
            if self._pinned[i][0] == rank and self._pinned[i][1] == file:
                pinned = True
                pin_direction = (self._pinned[i][2], self._pinned[i][3])
                if self.position[rank][file].type != 1:
                    self._pinned.pop(i)
                break

        directions = ((1, 1), (-1, -1), (1, -1), (-1, 1))
        bishop = self.position[rank][file]
        for i in directions:
            for j in range(1, 8):
                target_rank, target_file = rank + j*i[0], file + j*i[1]
                if 0 <= target_rank < 8 and 0 <= target_file < 8:
                    if not pinned or pin_direction == i or pin_direction == (-i[0], -i[1]):
                        piece = self.position[target_rank][target_file]
                        if piece == None:
                            move_list.append(
                                Move(self.position, (rank, file), (target_rank, target_file)))
                        elif piece and piece.color != bishop.color:
                            move_list.append(
                                Move(self.position, (rank, file), (target_rank, target_file)))
                            break
                        else:
                            break

    def _get_knight_moves(self, rank: int, file: int, move_list: list) -> None:
        """Generates all pseudo legal knight moves in the current position and adds them to the given move list.

        Args:
            rank (int): rank of the knight
            file (int): file of the knight
            move_list (list): list the generated moves should be added to
        """
        pinned = False
        pin_direction = ()
        for i in range(len(self._pinned)-1, -1, -1):
            if self._pinned[i][0] == rank and self._pinned[i][1] == file:
                pinned = True
                self._pinned.pop(i)
                break

        knight = self.position[rank][file]
        moves = ((-1, -2), (-1, 2), (1, -2), (1, 2),
                 (-2, -1), (-2, 1), (2, -1), (2, 1))
        for i in moves:
            target_rank, target_file = rank + i[0], file + i[1]
            if 0 <= target_rank < 8 and 0 <= target_file < 8:
                piece = self.position[target_rank][target_file]
                if piece is None or (piece and piece.color != knight.color):
                    if not pinned:
                        move_list.append(
                            Move(self.position, (rank, file), (target_rank, target_file)))
