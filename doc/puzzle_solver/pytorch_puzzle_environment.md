# Twisty Puzzle Environment for RL

To train NN-based RL agents to solve twisty puzzles, we use stable baselines 3 with a custom gymnasium environment. This environment is implemented with pytorch to enable parallelization on a GPU.

## Notation
n = number of stickers in the puzzle = length of state vector  
|A| = number of actions defined the puzzle (including rotations, algorithms and inverses)


| Information | Usual format | Pytorch format | Explanation | 
| --- | --- | --- | --- |
| State | list[int] | torch.Tensor[torch.uint16], shape=n | The state of the puzzle represented by the permutation of the integers. `uint16` is sufficient for puzzles with 65536 stickers (~104³ cube). The world record largest puzzle in 2024 has 14406 stickers ([49³ cube](https://twistypuzzles.com/forum/viewtopic.php?p=430466#p430466)) |
| Actions | dict[str, list[list[int]]] | torch.Tensor[torch.uint16], shape=(n,\|A\|) | Usually actions are stored as names mapped to permutations in cycle notation. We convert this to a tensor of integers, where each row is an action describing the full permutation explicitly to ensure equal length of all actions. |