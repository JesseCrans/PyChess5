# PyChessFinal

A chess engine using pygame.
It uses a minimax alpha beta pruning algorithm to find the best move.
The legal move generation works as far as i know. I have tested on various positions for depths <= 6.
I am done with this project but a few things are missing/need improvements if i were to retry this ever.
1. Better interface, with a move display, timer etc.
2. faster search, maybe using numpy arrays instead of 2d lists or another board representation. and generally improving the legal move generation and search function.
3. Using some sort of threading/multiprocessing to run the calculations in the background. Now it freezes when the engine is thinking for a long time.
4. little rules like draw by insufficient material i have not added, but eventually this is covered by the 50 move rule so not strictly necessary.
