This is a list of all hyperparameters for the RL agent:

- action set of agent  
  *Which actions are available to the agent*
- scamble action set  
  *Which actions can be used for scambling the puzzle during training*
- start scramble depth  
  *Number of scramble moves at the beginning of training. These will be increased based on agent's success*
- success threshold for increasing scramble depth  
  *Percentage of successful episodes of the last `stw` to increase scramble depth by 1.*
- success threshold window (`stw`)
  *Number of episodes to average over to determine when to increase scramble depth. This is also the minimum number of episodes between increases in scramble depth.*

- reward function  
  *How to reward each state. Either dense of sparse, binary rewards.*

- RL Algorithm (e.g. PPO)
- learning rate for Q-Learning (in range [0,1], close to 0)
- discount factor for Q-learning (in rabge [0,1], close to 1)
- 