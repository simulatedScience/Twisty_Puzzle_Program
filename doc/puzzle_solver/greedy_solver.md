# Greedy Puzzle solver

We implement a greedy puzzle solver that uses the RL-agent's reward function as a heuristic to guide the solver. The CLI command `solve_greedy` implements weighted A* search with this reward function as the heuristic.

Reward function:
- Reward 500 if puzzle is exactly solved
- Reward 100 if puzzle is solved but not in the correct orientation
- Reward 0-1 as the maximum percentage of points in the correct position, considering any rotation of the puzzle.

Without algorithms in the action set, we expect this solver to get stuck in local optima very quickly, as it often requires complex move sequences to make progress in this metric once many pieces are already correct.

An action set with algorithms can help in this regard, making monotone reward progress more likely. However, if not all situations are covered by the algorithms, we expect this solver to still get stuck in local optima.

## Results:
Testing `move_greedy` on a few puzzles, we see exactly what we expected: At first, the solver quickly makes progress, gaining new correct points with each move. However it encounters many plateaus due to the spatial rotations not affecting the reward. The solver then gets stuck in local optima, where it can't make any progress without undoing previous moves, which the greedy policy doesn't allow.

Using the `solve_greedy` command, we see that the solver can solve some states of more complec puzzles without any RL training being necessary, but there are also many states, from which it can't find solutions.

We test the greedy solver for: `rubiks_2x2`, `rubiks_2x2_ai`, `rubiks_2x2_sym` (including algs)
Without Algorithms, `move_greedy` often gets stuck almost immediately, alternating between a move and its inverse, going back and forth between two reward values. Without algorihtms, `solve_greedy` can't solve most states either, as the heuristic is very bad at estimating the distance to the solved state with just base moves available.

With some manually chosen algorithms available, `move_greedy` already gets very close to the solved state most of the time, with `solve_greedy` being able to solve some, but far from all scrambles.

Notably, we observe some situations (e.g. scramble `f t l r'` on `rubiks_3x3`), where `solve_greedy` can solve the state without algorithms but cannot do so with the algorithms in `rubiks_algs`. This is because the algorithms allow the solver to move to a local optimum that isn't accessible with just base moves.