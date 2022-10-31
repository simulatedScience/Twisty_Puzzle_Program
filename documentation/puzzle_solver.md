# A* algorithm used for solving the puzzles

## Availiable information
Using Q-Learning we assign a value ($Q(s,a) \in \mathbb{R}$) to each visited state-action pair $(s,a)$. A high value (currently $1$) means that the action is considered to be good in the given state, a low value (currently $0$) represents bad actions.

In older Q-tables (before 31.08.2020) the maximum high and low values are still very different.

From the neural network or Q-table we only get a value for a given state-action pair, not a value for just the state, but we want the search algorithm to terminate once it finds a sequence of actions that leads to the solved state.


## Variables for the algorithm
We always keep two dictionaries:
* `open_dict` stores all so far explored action sequences.
  * **keys:** `(tuple)` with all the consecutive action names
  * **values:** `(tuple)` consisting of:
    * `(float)` - value of this action
    * `(list)` - state after performing the actions in the key to the start state
* `closed_dict` stores all states that have been seen so far
  * **keys:** `(tuple)` representing the state of the puzzle (not including any action)
  * **values:** `(float)` best value of an action sequence that resulted in this state so far

Additionally we of course need a bit of information about the puzzle:
* `ACTIONS_DICT` - `(dict)` - a dictionary containing all movenames and the corresponding permutations
* `SOLVED_STATE` - `(list)` - the solved state

_____

## The actual algorithm
### The idea of A*
Beginning from the start state, consider all possible actions from the current state and the states they lead to. The new states get evaluated based on the number of moves they are away from the start state and based on a heuristic that approximates how far they are from the solved state.

This is expressed in the equation $f(s) = g(s) + h(s)$, where $g(s)$ is the cost for the moves since the start state and $h(s)$ is the approximate cost to the goal.

We can also implement a scaling factor $\lambda \in [1,0]$ to make this weighted A* search, which simply changes the equation to $f(s) = \lambda \, g(s) + h(s)$

Since it may take a very long time to check every possible state, at each time step only the state with the best current value is expanded. "Expanded" meaning that we consider all actions possible from that state and add them with their corresponding values to the `open_dict`.

What the "best" value is depends on the functions $g(s)$ and $h(s)$.

The algorithm terminates once the solved state is reached.

### Our implementation
Our Q-table and neural network both approximate Q-values and therefor only evaluate state-action pairs, not just states. So we have to adapt the algorithm a little bit:

Instead of storing states we store sequences of actions that are applied to the starting state.

$g(s)$ then counts the number of actions performed in that sequence. Let $s'$ be a successor of $s$, then $g(s') = g(s) -1$

When using weighted A* search, we get $f(s') = \lambda g(s') \, h(s) = (\lambda g(s) - \lambda) h(s)$. The weight factor $\lambda$ scales down the cost of past moves.

$h(s)$ evaluates the last taken action using the Q-table or neural network. The action $a$ is part of the state $s$ since we store action sequences as states.
$$h(s) = \begin{cases}1 & , s=solved\\Q(s) & , else \end{cases}$$

Our Q-values are in the range $[0,1]$ where close to $1$ is good and close to $0$ is bad. A value of exactly $0$ means that the action has not yet been explored.

_____

## Reevaluating states visited before
It is possible to reach the same state with different moves. In that case, if the current way to reach that state is better than a previous way, the following states are also evaluated suboptimally. Therefore it is beneficial to re-add that state to the *open list* in order to increase the chance of finding an optimal solution.

This can also help to find any solution. To understand how, consider the following example:

> ### Example:
> Let $S_e$ be the solved state (end), $S_{T_1}$ the first state that is visited twice and $S_{T_2}$ the deepest state that was calculated using the moves that lead to state $S_{T_1}$.
>
> Assume that the moves leading from $S_{T_1}$ to $S_{T_2}$ were desireable to get to a solution, but the heuristic happened to estimate $S_{T_2}$'s value badly, which led to another node being considered. When $S_{T_1}$ value improves, so does the value for $S_{T_2}$ as the same path will be chosen again. But this time, due to the improvement to the evaluation of $S_{T_1}$, the states following $S_{T_2}$ are explored further because the value improved the priority.

In practice, it's necessary to test whether or not this reevaluation is worth the extra computation time, but if we want an optimal solution, this step is necessary.