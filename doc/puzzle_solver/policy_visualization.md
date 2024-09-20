# Policy Visualization

After training an RL agent to solve a puzzle, we want to understand how it does so. Given the goal of training agents to solve puzzles in a way that is understandable to humans we will investigate this in particular.
We want to evaluate how general the solution strategy is by comparing the solves for different scrambles.

- **clustering of solves**  
  Use a clustering algorithm to group similar solves together. We can then visualize the clusters to see if the agent uses different strategies for different scrambles.

- **perturbation analysis**  
  small perturbations in the start state should only lead to small perturbations in the solution

- **action analysis**  
  To understand if the agent uses the available algorithms, we use historgrams showing how often each action is taken during an average solve.  
  Importantly, include histograms how often base actions, rotations or algorithms are chosen.
  Early observations (as of 2024-09-20) show that curriculum learning leads to agents favoring base actions. The lower the initial scramble depth, the less likely the agent seems to be to use algorithms. Adding the algorithms and rotations to the action space seems to affect binary agent's training time very little (see _2024-09-20 dino_cube_plus_ experiments)

- **reward evolution**  
  We can plot how the reward changes during each solve. We might expect similar curves for similar scrambles?

- **Rotation invariance**
  For humans, rotating a puzzle in 3D space doesn't change the solution strategy. We can investigate if the agent is rotation invariant by comparing the solves for different rotations of the same scramble. This is particularly interesting since the actions to rotate the puzzle to a default rotation are easily accessible to the agent. So it would be easy for the agent to learn a strategy that prefers a certain orientation.

- **Solution length**
  Most other ML solvers aim and often achieve the shortest possible solutions (minimal number of moves). This is something we specifically did not want here and by investigating solution lengths, we can quite easily check this.


## Show the order in which pieces are solved on average:
1. Let the agent solve many different scrambles and record all solves.
2. for each solves, analyse when each pieces is moved to its correct position and orientation (all piece points in correct place).
3. Average over all solves  to get a heatmap of the order in which pieces are solved.
4. color the puzzle pieces according to the heatmap

**Thoughts/ Optional features:**
- a piece being first moved to its correct position may not be a good metric, as pieces that are not currently being solved, may accidentally be moved to their correct position while solving other pieces.  
  -> instead of recording when pieces first reach their final position, record after which point they remain in the correct place for most of the remaining solve (e.g. in correct place after >50% of the remaining moves) => add parameter `correct_position_threshold`.
- Implement various human solvers or record many human solves to compare the agent's strategy to human strategies.