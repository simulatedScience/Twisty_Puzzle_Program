# Puzzle Solver - Reward Functions
Reinforcement Learning requires a reward function to evaluate the agent's actions. This document describes options for reward functions for the puzzle solver.

### Binary 0-1 Reward
This is the most basic reward function: reward 1 if the puzzle is solved, 0 otherwise. While this is easy to define and doesn't force any possibly imperfect human-knowledge on the agent, it is a very sparse reward that RL-agents have a hard time learning from.

### Number of Correct Points
For most humans, an intuitive measure of how close to the goal a current state is, is counting how many puzzle pieces are in the correct position and orientation.

#### Implementation notes:
- There are many choices how to implement this. Consider using one-hot encodings for point colors combined with standard norm functions. Alternatively, count number of matching points directly.

### Rotation invariant number of correct points
Some puzzles can be rotated as a whole in 3D space (especially when specifically adding moves to do so). These puzzles can still be considered as solved in any spatial orientation, even if the colors don't exactly match the one defined solved state.

Therefore, episodes can be ended early when the current state matches any orientation of the solved state.

#### Implementation notes:
For efficient comparison, precompute a list of all possible orientations of the solved state. Then, when calculating the number of correct points, compare the current state with all possible orientations of the solved statel, stopping if a match is found.