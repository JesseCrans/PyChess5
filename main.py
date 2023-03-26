import pygame
import threading

from Game.support import *
from Game.interface import Interface
from Game.board import Board
from Game.engine import Engine

DEPTH = 4  # default depth

# r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1
# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1


def main() -> None:
    """Responsible for the main game loop and handles player key and mouse button clicks.
    """
    run = True
    clock = pygame.time.Clock()
    board = Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
    interface = Interface(WIN, board)
    engine = Engine(board, DEPTH)
    engine_move_made = True

    while run:
        clock.tick(FPS)
        ended = interface.draw()
        pygame.display.update()

        if not engine_move_made and not ended:
            best_move = engine.find_best_move()
            if best_move:
                interface.make_move(best_move)
            engine_move_made = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if not ended:
                    pos = pygame.mouse.get_pos()
                    rank, file = get_row_col_from_mouse(pos)
                    if 0 <= rank < 8 and 0 <= file < 8:
                        result = interface.select((rank, file))
                        if result:
                            engine_move_made = False
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()

                if event.key == pygame.K_r:
                    interface.reset()

                elif event.key == pygame.K_f:
                    print(interface.board.get_fen())

                elif event.key == pygame.K_z:
                    interface.board.unmake_move()

                # perft tests
                elif keys[pygame.K_p] and keys[pygame.K_r] and keys[pygame.K_1]:
                    engine.perft_range(1)
                elif keys[pygame.K_p] and keys[pygame.K_r] and keys[pygame.K_2]:
                    engine.perft_range(2)
                elif keys[pygame.K_p] and keys[pygame.K_r] and keys[pygame.K_3]:
                    engine.perft_range(3)
                elif keys[pygame.K_p] and keys[pygame.K_r] and keys[pygame.K_4]:
                    engine.perft_range(4)
                elif keys[pygame.K_p] and keys[pygame.K_r] and keys[pygame.K_5]:
                    engine.perft_range(5)
                elif keys[pygame.K_p] and keys[pygame.K_r] and keys[pygame.K_6]:
                    engine.perft_range(6)

                elif keys[pygame.K_p] and keys[pygame.K_d] and keys[pygame.K_1]:
                    engine.perft_divide(1)
                elif keys[pygame.K_p] and keys[pygame.K_d] and keys[pygame.K_2]:
                    engine.perft_divide(2)
                elif keys[pygame.K_p] and keys[pygame.K_d] and keys[pygame.K_2]:
                    engine.perft_divide(3)
                elif keys[pygame.K_p] and keys[pygame.K_d] and keys[pygame.K_3]:
                    engine.perft_divide(4)
                elif keys[pygame.K_p] and keys[pygame.K_d] and keys[pygame.K_4]:
                    engine.perft_divide(5)
                elif keys[pygame.K_p] and keys[pygame.K_d] and keys[pygame.K_5]:
                    engine.perft_divide(6)

    pygame.quit()


if __name__ == '__main__':
    main()
