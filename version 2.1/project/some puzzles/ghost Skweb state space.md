# Ghost Skewb

## Setting

Ein Skewb basiert auf einem Tetraeder. Das heißt es gibt vier Ecken, ihre Positionen relativ zueinander nie ändern, sondern nur ihre relative Ausrichtung.

These four corners and four center pieces have three neighbouring pieces each. Therefor every one of those pieces has three possible orientations.

There are also six edge pieces with four neighbouring pieces each, so they have four possible orientations.

### move center pieces
The centerpieces can only be swapped as two pairs simultaniously. A single pair of center pieces cannot be swapped without changing the rest of the puzzle.

### rotate center pieces
The sum of all rotations of center pieces must be a multiple of $360$°.

### rotate corner pieces
The sum of all rotations of center pieces must be a multiple of $360$°.

(Corner and center pieces behave identically but cannot be interchanged.)

### rotate edges
The sum of all rotations of edge pieces must be a multiple of $360$°. Every There is no legal move that rotates an edge piece by $90$°. So every edge must be rotated by either $180$° or $0$° (=correct orientation).

### move edges
Edges cannot be swapped pairwise. They can only be moved in cycles with three edge pieces. This can look like a single corner is rotated by $120$° but when the corner is rotated correctly it oftten gets obvious that the three edges around it are permuted in a cycle.

## Derivation
By permuting the center pieces we get $4!$ possible arrangements. Due to the restriction mentioned above (we can only swap to pairs, not just one), we have to divide by $2$.

Each center piece can have $3$ orientations, so there are $3^4$ possible arrangements. But again, this is counting more than we can achieve with legal moves, so we have to divide by $3$.

The exact same counts for corner pieces: There are $3^4$ possible arrangements, $3^3$ of them are achievable with valid moves.

There are $6$ edge pieces which can be permuted in $6!$ ways. But similar to the normal rubik's cube this is counting twice as many options as we actually have. $\implies$ divide by $2$.

Finally we can rotate edge pieces in $2^6$ ways but only $2^5$ of these states are actually possible without dissassembling the puzzle.

## Results
So overall we have $\frac{4! \cdot 3^4 \cdot 3^4 \cdot 6! \cdot 2^6}{2 \cdot 3 \cdot 3 \cdot 2 \cdot 2} = \frac{4! \cdot 6! \cdot 3^6 \cdot 2^5}{2 \cdot 2} = 3! \cdot  6! \cdot 2^5 = 138240$ possible arrangements of a Ghost Skewb.

In a regular Skewb, the orientation of the edges is not visible. Therefor that has only $3! \cdot 6! = 4320$ possible states.
