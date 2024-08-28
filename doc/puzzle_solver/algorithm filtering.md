# Alghorithm filtering
We generate algorithms (useful move sequences) automatically to then train RL agents to use these. Due to this two-step process, some of the most important decisions are when to stop generating algorithms and which algorithms to accept in the action set.

## Algorithm generation

### Number of pieces changed by the algorithm
As explained in the RL solver introduction, algorithms are only beneficial to an RL agent if they shorten sufficiently many solutions or enable the use of denser rewards (other options might exist too). We concluded there, that the use of dense, intuitive rewards would be useful to make the reward function more monotonic, reducing the depth/ height of local optima.
Algorithms that affect many pieces don't help with that, as they are much more likely to lead to large reward jumps with each action. Algorithms affecting only a few points (=> few pieces) can also only lead to small reward jumps, leading to more smaller steps towards a solution instead of a few large leaps.

Algorithms affecting only a few pieces are also desirable for humans using them, as their affect on the puzzle is much easier to predict and understand than the effect of algorithms affecting many pieces at once.


### Order of the algorithm
We want algorithms to have a low order, meaning that after only a few repetitions of the algorithm, we get back to the initial state. A low algorithm order is necessary for the algorithm to only affect few pieces because an algorithm affecting $n$ points can have at most order $n!$. These cases are very rare though, as that would require the algorithm to go through all possible permutations of these points. In practice, the order of an algorithm is usually much lower than $n!$. Therefore a high order usually means many affected pieces.

<!-- To generate algorithms with low order, we exploit the permutation-group structure of the investigated twisty puzzles: any move sequence $s$ has a finite order $ord(s)$. After $ord(s)$ repetitions of the sequence, we always reach the initial position again. Using the prime factorization of $ord(s)$, we can generate new move sequences as repetitions of $s$ with a known, reduced order. If $k$ divides $ord(s)$, then $s^{ord(s)/k}$ has order $k$. This way we can rather efficiently find all move sequences that have low order. -->
To generate algorithms with low order, we exploit the permutation-group structure of the investigated twisty puzzles: any move sequence $s$ has a finite order $ord(s)$.
We can decompose any move sequence into the cycles making up its permutation. Given a cylce $c$ in $s$, repeating the move sequence $ord(c)$ times, is guaranteed to reduce the number of affected points IF none of the cycles has full algorithm order $ord(s)$.

### Feasibility for human use
One of the main goals of this work is to create AI puzzle solvers that can help humans solve twisty puzzles. Therefore, algorithms that require many thousands or millions of moves are not practical. These would take too long to execute on a physical puzzle and are highly prone to errors. To ensure that the generated algorithms are feasible for human use, we limit the number of moves a generated algorithm can have as well as the length of the base sequence it is generated from. While the former is a limit on the total time it takes to execute an algorithm, the latter makes the algorithms easier to memorize for humans. Memorizing move sequences of lengths 100 or more without any useful patterns would be very difficult.

Algorithms used in speedcubing often also consider how the puzzle would be held in the hand and only use moves that can be performed in quick succession with efficient movements. We do not take this into account in this work, due to the wide variety of puzzle shapes supported by the framework, each needing different considerations. The focus of this work is also explicitly not on speedcubing, as we are not searching for short solutions but instead prefer longer ones that are easier to generalize.

