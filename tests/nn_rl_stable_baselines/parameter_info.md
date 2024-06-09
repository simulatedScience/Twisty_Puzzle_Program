# Training parameters for NNs

### `initial_scramble_length` (`int`) (Default: `1`)
During training, puzzles are randomly scrambled for each episode with the agent's goal being to solve the puzzle. This parameter determines the number of scrmable moves at the beginning of training.
The scramble length is then automatically increased by 1 every 1000 episodes if from the last 500 episodes, the agent's success rate was greater than `success_threshold`.

Experiments training Agents to solve the Skewb have shown that `initial_scramble_length` = 1 yields the best results. Too high values completely prevent the agent from learning anything (when given binary rewards) as it almost never encounters a positive reward Using HER or denser rewards may allow for higher values of `initial_scramble_length`, but setting it to 1 has almost no disadvantages known to us.

Even compared to initial scramble lengths 2, 3 and 4, the agent trained with `initial_scramble_length` = 1 learns faster and achieves higher difficulties (higher `scramble_length`) earlier - presumably because it initialy has more successfull episodes and thus gets less noisy rewards early on. Later, this benefits the agent as it had time to better learn to solve the states close to the goal, so in new states it can more easily find a path to states from which it knows a solution.

![Initial scramble length comparison for Skewb: 1, 2, 4, 8, 16](initial_scramble_length_comparison_skewb.png)

### `success_threshold` (`float`) (Default: `0.8`)
Determines how many of the past 500 episodes must have been successful to increase the scramble length by 1.

There is an interesting analogy to teaching in schools with this parameter. It acts similar to a grade a student needs to pass a course or school year to then learn new material in upcoming courses.

### `max_moves` (`int`) (Default: `50`)
The maximum number of moves the agent can make before the episode is terminated.


### `reward_type` (`str`) (Default: `'binary'`)
Determines the type of reward the agent receives. The following reward types are available:
- `'binary'`: The agent receives a reward of 1 if it solves the puzzle and 0 otherwise.
- `'euclidean'`: The agent receives a reward of $1 - ||s - s*||$ where s is the current state vector and s* is the goal state vector. Currently, this reward is not normalized, so with a lot of points in the puzzle, it can get very negative (For Skewb: -600)

### Learning algorithm (`sb3.BaseAlgorithm`) (Default: `PPO`)

# Default parameters used by Stable Baselines 3
### optimizer: _Adam_
### learning_rate: _1e-3_
### NN architecture: _MlpPolicy_
- two fully connected hidden layers with 64 units each
- tanh activation function everywhere except the output layer
- output layer
- input and output size depend on the puzzle
