# Policy Visualization

After training an RL agent to solve a puzzle, we want to understand how it does so. Given the goal of training agents to solve puzzles in a way that is understandable to humans we will investigate this in particular.
We want to evaluate how general the solution strategy is by comparing the solves for different scrambles.

- **clustering of solves**  
  Use a clustering algorithm to group similar solves together. We can then visualize the clusters to see if the agent uses different strategies for different scrambles.

- **perturbation analysis**  
  small perturbations in the start state should only lead to small perturbations in the solution

- **action analysis**  
  To understand if the agent uses the available algorithms, we use historgrams showing how often each action is taken during an average solve.

- **reward evolution**  
  We can plot how the reward changes during each solve. We might expect similar curves for similar scrambles?

- **Rotation invariance**
  For humans, rotating a puzzle in 3D space doesn't change the solution strategy. We can investigate if the agent is rotation invariant by comparing the solves for different rotations of the same scramble. This is particularly interesting since the actions to rotate the puzzle to a default rotation are easily accessible to the agent. So it would be easy for the agent to learn a strategy that prefers a certain orientation.

- **Solution length**
  Most other ML solvers aim and often achieve the shortest possible solutions (minimal number of moves). This is something we specifically did not want here and by investigating solution lengths, we can quite easily check this.


