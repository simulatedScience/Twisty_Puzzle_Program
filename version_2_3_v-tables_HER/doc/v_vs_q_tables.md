# V-Learning
V-learning describes the process of learning the state-value-function $V: S \to \mathbb{R}$, where $S$ is the set of all possible states.

Actions are then chosen to optimize the value $V(s')$ of the expected next state $s'$.

For example, assume the agent is in state $s \in S$ and $A_s$ is the set of all actions that are available in state $s$. Then in V-learning the agent tries every possible action and scores them according to the followup state $s'_a$ that is reached by performing action $a\in A$ in state $s$.

This requires a model that predicts the future state $s'_a$ before the agent actually performs that action in the environment.

Therefore V-learning falls into the category of model-based reinforcement learning.

# Q-Learning
Q-learning on the other hand describes the process of learning the action-value-function $Q: S \times A \to \mathbb{R}$, where $S$ is the set of all possible states and $A$ is the set of all possible actions.

Actions are chosen to optimize the value $Q(s,a)$ of the action $a \in A$.

To choose an action in a given state $s \in S$, evaluate $Q$ for all possible actions $a\in A_s$ and choose the action $\hat a$ with the best value $Q(s,\hat a)$.

In conrast to V-learning this requires no model of the environment, which is why Q-learning falls into the category of model-free reinforcement learning.

# Comparison: Q- vs. V-learning

### Similarities
- both methods require the same number of model evaluations ($V(s)$ or $Q(s,a)$ respectively) to choose an action.

### Pros Q-Learning
- Q-learning's lack of an environment model makes it ***much faster*** in choosing actions because predicting the next state is usually slow.
- Q-learning is ***easier to implement*** because it doesn't require an environment model.

### Pros V-Learning
- V-learning ensures that actions that lead to the ***same state*** get the ***same value*** assigned. This can be especially helpful in deterministic environments.
- The ***input space*** $S$ is ***much smaller*** than the state-action space $S\times A$, that is required for Q-learning. When using tables instead of neural networks, this can same huge amounts of storage space. However when using neural networks, the benefit is much smaller.