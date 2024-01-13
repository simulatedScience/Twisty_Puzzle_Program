# Automatic piece detection

-----

## Requirements for pieces

A piece is a collection of points representing one physical object. Points of one piece should not be able to move relative to each other.

-----

1. ***Two points are not on the same piece if there exists a sequence of moves such that the last move only moves one of them.***

2. ***Two points are not on the same piece if they are part of two cycles with different orders within the same move***

-----

# implementation

1. create a cutting template for each move (except inverse moves) according to the first two rules.
2. apply all templates to the puzzle
3. make a move
4. repeat steps 2-4 until one of the following conditions applys
   1. the number of pieces is equal to the number of points
   2. all move combinations that could seperate pieces are checked
   3. a maximum time is reached

Condition 4.1 only applies in rare cases, where every piece only has one sticker.
Condition 4.2 may require a lot of computational effort and may not cause a stop within reasonable runtime.
Therefor a timeout condition 4.3 is strongly recommended.

Instead of 4.2 and 4.3 one could also choose moves randomly and set a fixed number of moves after which to terminate. This is unreliable in calculating all pieces correctly though.