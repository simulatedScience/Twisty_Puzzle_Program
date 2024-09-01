# Piece classification

When generating new algorithms for a puzzle, a major challenge is deciding which ones to accept and which ones to reject. To prevent bloating the action set with many, almost identical algorithms, we developed an "algorithm signature", that records some important properties of an algorithm. If these signatures are different, the algorithms are guaranteed to be different. If they are the same, the algorithms are likely to be similar. Making the algorithm signature as informative as possible is helpful to tell apart more algorithms to make the decision whether to accept or reject them easier.

An important part of the algorithm signature is recording which cycles in the algorithm affect which pieces. Two algorithms that affect completely different pieces (e.g. one affects only corners, the other edges) are  almost certainly both beneficial to keep. If two algorithms affect the same pieces, the decision is more nuanced. For example, the edges of a rubik's 3x3x3 cube cannot be efficiently solved with only one algorithm that cycles four edges. Another algorithm that cycles 2 or 3 edges might still be benefial, possibly even another 4-cycle affecting different edges. This shows, that properly classifying pieces is very helpful in telling apart different algorithms.

A naive approach to classify pieces is to count the number of points in a piece. This can be very inaccuracte though.
Here's a better way:

Calculate the orbit of each piece using the base moves of the puzzle. Two pieces are equivalent, if they are in the same orbit. By keeping a list of all orbits, we can still classify each piece with a single integer, representing the index of the piece's orbit in that list. This way, we can easily compare pieces by comparing their orbit index.

<!-- ## 
Using the order of piece orbits might allow us to know when we have found sufficient algorithms to reach all valid permutations of pieces in that orbit.
Due to Lagrange's theorem, any orbit with prime order can be reached with a single algorithm. (Consider the orbit as a permutation group. In groups with prime order, every element is a generator of the entire group. So any permutation ) -->