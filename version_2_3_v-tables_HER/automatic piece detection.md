# Automatic piece detection

## Why piece detection is useful

1. If puzzles are represented as nothing more but colored points in $\mathbb{R}^3$ it is sometimes hard to understand the geometry of the puzzle. By connecting points of the same piece, this gets more obvious.

2. To check whether or not a given state of a puzzle is valid, we need to figure out the exact permutation that leads from the solved state to the current state. However since we only know the color of each point and not their exact index, we are missing some important information. But knowing the pieces and how the points are different from each other can help reconstruct that missing information.

3. Knowing the pieces could improve performance by treating several color points as one object. In case of 3D polyhedra representing the points, it could also help by not having to render the faces connecting points of the same piece, as they will never be visible.

4. Knowing the pieces could also help in the visualisation of the 3D polyhedra. If the edges of the polyhedra are drawn, the edges that are shared by two polyhedra of the same piece could be hidden to show the pieces in this visualisation.

    These shared edges can be obtained using the `vor.ridge_points` attribute of the `scipy.spatial.Voronoi` class used to create the polyhedra. If two points defining a ridge (face) are part of the same piece: hide all edges of that ridge (face).

-----

## Requirements for pieces

A piece is a collection of points representing one physical object. Points of one piece should not be able to move relative to each other.

-----

## How to detect pieces

1. ***Two points are not part of the same piece if there exists a move that moves just one of them.***

This first rule alone results in a problem for gear cubes:

The rotating edge pieces sit on top of the inner edge pieces and can therefor never move completely independently. But they can move relative to the other color stickers on the same piece. This issue can be resolved with the second rule:

2. ***Two points are not on the same piece if there exists a cycle in a move, that contains at least two but not all of the points on that piece.***

This second rule only needs to be checked for pieces with at least three points in them.

Most puzzles don't require the second rule but some geared puzzles do.

3. ***Two points are not on the same piece if there exists a sequence of moves such that the last move only moves one of them.***

This is a computationally expensive but necessary rule. It is possible that seperable pieces can only be seperated with a sequence of moves, not with a single one.

This sequence can definitely be as long as the sum of the orders of all moves.

-----

## Additional Thoughts
### a)
There is still one small problem though:

Assume a piece that has at least three points where there exists a move which only moves several of them around another one. This could happen in form of an additional point in the center of each gear cube edge piece or for any number of points on the rotation axis of the other points.

_This case is left up to the user because it is not clear how to handle it:_

1. Assume the point $P$ has orientation that matters. Then the other points would move around $P$ without $P$ itself rotating. That would imply that they are on different pieces as otherwise the pieces would be deformed.

2. If the orientation of $P$ does not matter, it should be rotated too.

This problem would require additional computational effort while not necessarily providing expected behavior in all cases. If the point $P$ should rotate with the other points, the user can simply add bandaging to do that.

### b) _(covered by rule 2)_
Points are also not on the same piece if within any move that moves both points, their cycles have different orders.

However this rule is not required as all cases where it would be useful are also covered by the second rule mentioned above.

-----

## Implementation of rule 1

1. ***Two points are not part of the same piece if there exists a move that moves just one of them.***

### Idea
We start by assuming the whole puzzle is one piece. Then we iteratively check for every move whether or not it would split any piece. If that is the case, we replace the old piece with two new ones.

### Preparation
In preparation for the algorithm we convert every move into the set of points it changes. That way we can check the piece separation more easily.

### Considerations
If we apply a move $m$ to the puzzle and consider a piece $A$, then there are three possible cases:

1. every point of $A$ is in the move $m$. We don't split the piece. $\iff A \subseteq m \iff A \cap m = A$
2. no point of $A$ is in the move $m$. We don't split the piece. $\iff A \cap m = \emptyset = \{\,\}$
3. some points of $A$ are in the move, some aren't. We split the piece. $\iff A \cap m \neq A$ or $\emptyset$

### Algorithm
As explained before we start by assuming the whole puzzle is just one piece and keep track of all pieces in a list `pieces`.

Until we reach the last element of that list, we check for every piece whether or not it can be split into more pieces.

To do that we loop over all possible moves and determine the intersection of that move with the current piece $A$.

If this intersection is neither empty not the whole piece ($\implies$ case 3), we add the intersection $A \cap m$ as a new element to `pieces` and delete all point in the intersection from $A$.

Once we are done with all moves, we consider the next piece, if one exists.

This algorithm yields all pieces in one run.

-----

## Implementation of rule 2

2. ***Two points are not on the same piece if there exists a cycle in a move, that contains at least two but not all of the points on that piece.***

### Preparations
It is common that different moves of a puzzle contain some of the same cycles. Therefor we won't loop over the moves but only over the distinct cycles. So we need some list of all cycles.

To get that we store them as frozensets in a set.

### Algorithm
We loop over all pieces determined by the algorithm for the first rule.

If the piece contains at least three points, we loop over all cycles and calculate the intersection of the cycle and the current piece.

If this intersection has at least two elements but is not the whole piece, the piece gets split up.

Similar to above the intersection is added to the list of pieces and the current piece is shortend accordingly.

-----

## Implementation of rule 3
The above algorithm does not work for all puzzles. One example is the square two. Currently only seperations occurring after one move can be detected. However it is possible for seperable pieces to remain together for a larger number of moves before they can be seperated.

The maximum number of moves required to seperate two points can be calculated though:

Let a puzzle have $N \in \mathbb{N}$ moves. We order these moves such that the first $n$ moves are not an inverse of oneanother ($\implies 1 \leq n \leq N$).
Let each move $m_i$ have the order $k_i$.

Then the maximum number of moves required to seperate two points should be:

$\eta_{\max} = \sum\limits_{i=1}^{n} a_i \quad$ where $\quad a_i = \begin{cases}k_i & \text{if move } i \text{ has no inverse} \\ \lceil k_i / 2 \rceil & \text{if move } i \text{ has an inverse} \end{cases}$

If there are no inverse moves ($\implies n = N$), this simplifies to $\eta_{\max} = \sum\limits_{i=1}^{N} k_i$. If every move has an inverse, it simplifies to $\eta_{\max} = \sum\limits_{i=1}^{N/2} \lceil k_i/2 \rceil$.

### the variables in programming
In the implementation we could get the variables as:
- $m_i =$ `move` 
- $k_i =$ `lcm([len(cycle) for cycle in move])`
- $N =$ `len(moves)`