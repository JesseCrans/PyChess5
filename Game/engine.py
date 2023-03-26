from time import time
from random import choice
from typing import Tuple, List

from .settings import *
from .support import *
from .board import Board
from .piece import Piece
from .move import Move

class Engine:
    def __init__(self, board: Board, depth=1) -> None:
        """Initializes the engine object with a given board and search depth.       

        Args:
            board (Board): the board object that the engine uses to generate legal moves
            depth (int, optional): the search depth used to find the best move. Defaults to 1.
        """
        self.board = board
        self.depth = depth

    def perft(self, depth: int) -> int:
        """Generates all legal moves recursivly to count the number of possible positions up to a given depth

        Args:
            depth (int): search depth

        Returns:
            int: the total number of positions at the given depth
        """
        if depth == 0:
            return 1

        number_of_positions = 0

        moves = self.board.get_legal_moves()
        for move in moves:
            self.board.make_move(move)
            number_of_positions += self.perft(depth - 1)
            self.board.unmake_move()

        return number_of_positions

    def perft_range(self, depth: int) -> None:
        """Does the perft test for every value from 1 to the given depth and prints it to the console

        Args:
            depth (int): search depth
        """
        test = []
        for d in range(1, depth+1):
            t0 = time()
            new_nop = self.perft(d)
            t1 = time()
            total_time = round(t1 - t0, 3)
            print(f'depth: {d} \n\t nodes: {new_nop}, time: {total_time}s')

    def perft_divide(self, depth: int) -> None:
        """Generates all legal moves, then for every move does the perft test for the given depth.

        Args:
            depth (int): search depth
        """
        moves = self.board.get_legal_moves()

        moves_per_move = {}
        for move in moves:
            self.board.make_move(move)
            moves_per_move[move.move_id_notation] = self.perft(depth-1)
            self.board.unmake_move()

        for key in moves_per_move:
            print(f'{key}: {moves_per_move[key]}')
            
        print(f'Nodes searched: {self.perft(depth)}')

    def score(self) -> int:
        """Gives a score based on the pieces on the board and their given value.

        Returns:
            int: the score of the current position
        """
        score = 0
        for rank in self.board.position:
            for piece in rank:
                if piece:
                    if piece.color == 0:
                        score += PIECE_VALUE[piece.type]
                    else:
                        score -= PIECE_VALUE[piece.type]

        return score

    def knight_score(self) -> int:
        """Gives a score based on the placement of knight pieces in the current position.

        Returns:
            int: knight based score of the current position
        """
        white_knight_heatmap = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 0, 1, 2, 2, 1, 0, -1],
            [-1, 0, 1, 2, 2, 1, 0, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 0, 0, 1, 1, 0, 0, -1],
            [-1, -1, -1, -1, -1, -1, -1, -1]
        ]
        black_knight_heatmap = [
            [-1, -1, -1, -1, -1, -1, -1, -1],
            [-1, 0, 0, 1, 1, 0, 0, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 0, 1, 2, 2, 1, 0, -1],
            [-1, 0, 1, 2, 2, 1, 0, -1],
            [-1, 0, 1, 1, 1, 1, 0, -1],
            [-1, 0, 0, 0, 0, 0, 0, -1],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        score = 0
        for i, rank in enumerate(self.board.position):
            for j, piece in enumerate(rank):
                if piece and piece.type == 4:
                    if piece.color == 0:
                        score += white_knight_heatmap[i][j]
                    else:
                        score -= black_knight_heatmap[i][j]

        return score

    def bishop_score(self) -> int:
        """Gives a score based on the placement of bishop pieces in the current position.

        Returns:
            int: bishop based score of the current position
        """
        white_bishop_heatmap = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 1, 2, 1, 1, 2, 1, 0],
            [0, 2, 1, 0, 0, 1, 2, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        black_bishop_heatmap = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 2, 1, 0, 0, 1, 2, 0],
            [0, 1, 2, 1, 1, 2, 1, 0],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        score = 0
        for i, rank in enumerate(self.board.position):
            for j, piece in enumerate(rank):
                if piece and piece.type == 3:
                    if piece.color == 0:
                        score += white_bishop_heatmap[i][j]
                    else:
                        score -= black_bishop_heatmap[i][j]

        return score

    def king_score(self) -> int:
        """Gives a score based on the placement of king pieces in the current position.

        Returns:
            int: king based score of the current position
        """
        white_king_heatmap = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [2, 2, 2, 0, 0, 0, 2, 2]
        ]
        black_king_heatmap = [
            [2, 2, 2, 0, 0, 0, 2, 2],
            [1, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        score = 0
        for i, rank in enumerate(self.board.position):
            for j, piece in enumerate(rank):
                if piece and piece.type == 0:
                    if piece.color == 0:
                        score += white_king_heatmap[i][j]
                    else:
                        score -= black_king_heatmap[i][j]

        return score

    def pawn_score(self) -> int:
        """Gives a score based on the placement of pawn pieces in the current position.

        Returns:
            int: pawn based score of the current position
        """
        pawn_heatmap = [
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 0, 1, 2, 2, 1, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0]
        ]
        score = 0
        for i, rank in enumerate(self.board.position):
            for j, piece in enumerate(rank):
                if piece and piece.type == 5:
                    if piece.color == 0:
                        score += pawn_heatmap[i][j]
                    else:
                        score -= pawn_heatmap[i][j]

        return score

    def evaluate(self) -> float:
        """Gives an evaluation score of the current position based on all the seperate score functions.

        Returns:
            float: the evaluation score given to the current position
        """
        evaluation = self.score()

        total_pieces = 0
        for rank in self.board.position:
            for piece in rank:
                if piece:
                    total_pieces += 1

        evaluation += 0.1 * self.knight_score()
        evaluation += 0.2 * self.bishop_score()
        evaluation += 0.4 * self.king_score()
        evaluation += 0.3 * self.pawn_score()

        # perspective
        if self.board.turn == 0:
            return evaluation
        else:
            return -evaluation

    def evaluate_move(self, move: Move) -> int:
        """Gives a score to a move by estimating how good it is.

        Args:
            move (Move): Move to be scored

        Returns:
            int: estimated score of the move
        """
        score = 0
        if move.captured:
            score += PIECE_VALUE[move.captured.type] - \
                PIECE_VALUE[move.piece.type]
        
        if move.is_promotion:
            score += 100

        return score

    def order_moves(self) -> List[Move]:
        """Orders the move based on their score.    

        Returns:
            List[Move]: ordered list of moves
        """
        moves = self.board.get_legal_moves()
        moves = sorted(moves, key=self.evaluate_move)
        return moves

    def prune_search(self, depth: int, alpha: int =-999999, beta: int=999999) -> float:
        """Finds the best possible evaluation for a given depth using the minimax algorithm with alpha-beta-pruning.

        Args:
            depth (int): search depth
            alpha (int, optional): initial alpha value. Defaults to -999999.
            beta (int, optional): initial beta value. Defaults to 999999.

        Returns:
            float: the best evaluation found
        """
        if depth == 0:
            self.positions_evaluated += 1
            return self.evaluate()
        
        if self.board.halfturn >= 50:
            return 0

        moves = self.order_moves()
        if not moves:
            checked, _, _ = self.board._check_for_pins_and_checks()
            if checked:
                return -999999
            else:
                return 0

        for move in moves:
            self.board.make_move(move)
            evaluation = -self.prune_search(depth - 1, -beta, -alpha)
            self.board.unmake_move()
            if evaluation >= beta:
                return beta
            alpha = max(alpha, evaluation)

        return alpha

    def prune_search_move(self, depth: int) -> List[Move]:
        """Uses the prune_search function to find a list of the best move for a given depth.

        Args:
            depth (int): search depth

        Returns:
            List[Move]: list of best moves, with the highest found evaluation
        """
        t0 = time()

        moves = self.order_moves()
        if not moves:
            return None

        best_moves = []
        best_eval = -1000000

        alpha = -1000000
        beta = 1000000
        
        self.positions_evaluated = 0

        for move in moves:
            self.board.make_move(move)
            current_eval = -self.prune_search(depth-1, -beta, -alpha)
            self.board.unmake_move()
            if current_eval > best_eval:
                best_eval = current_eval
                best_moves = [move]
            if current_eval == best_eval:
                best_moves.append(move)

        t1 = time()
        print(f'Time: {round(t1 - t0, 3)}s')
        print(f'Evaluated: {self.positions_evaluated}')

        return best_moves
    
    def find_best_move(self) -> Move:
        """Generates a best move by randomly picking a move from the list of best moves generated by the prune_search_move function.

        Returns:
            Move: random best move
        """
        best_moves = self.prune_search_move(self.depth)
        if best_moves:
            random_best_move = choice(best_moves)
            return random_best_move

        return None
 