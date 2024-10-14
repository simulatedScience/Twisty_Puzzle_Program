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


## Problem
Points like center pieces, that can be changed by some moves but never actually move relative to each other are considered separate pieces with this algorithm.
-> rule 1 is incorrect. Points that are on the rotation axis of the move can be part of either the piece that is moved or the rest of the puzzle. However, the piece detection algorithm is unaware of rotation axes, using only the permutations for all calculations.

A potential fix has been implemented in `tests/piece detection/piece_detection_v2_tests.py`, but that breaks the piece templates almost entirely.

## Old algorithm, new explanation
Let X be the set of points.
1. generate cutting templates:
   1. for each move, split the puzzle into pieces according to this single move, using rules 1 and 2. `get_piece_template()`  
     For most non-geared moves, this results in two pieces: the moved piece and the rest of the puzzle. Geared moves may have more pieces due to rule 2.
   2. Now that we have a list of partitions of X, we calculate the "largest" partition $\Pi$, such that all other partitions can be formed by joining elements of $\Pi$. (`intersect_pieces()`)

`split_moves()` 