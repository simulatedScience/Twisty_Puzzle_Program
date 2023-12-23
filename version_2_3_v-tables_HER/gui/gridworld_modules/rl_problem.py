"""
this module implements an interface for the RL problems expected by the RLExperiments class.
"""
# import torch


class RLProblem:
  def __init__(self, problem_size: int, reward_type: str = "01"):
    pass

  def get_num_actions(self):
    """
    get the number of actions available in the environment.
    This is used to create the policy network.
    """
    pass

  def get_state_size(self):
    """
    get the size of the state vector including the goal (which is assumed to be the same length as the state).
    This is used to create the policy network.
    """
    pass

  def get_max_steps(self):
    """
    get the maximum number of steps allowed in the environment. This usually depends on the problem size.
    """
    pass

  def reset(self):
    """
    reset the environment to the initial state. This may be any random state from which the goal can be reached.
    """
    pass

  def step(self, action: int):
    """
    take a step in the environment

    Args:
        action (int): the action to take
    """
    pass

  def compute_reward(self, state: "torch.tensor", goal: "torch.tensor") -> float:
    """
    compute the reward for the given state and goal

    Args:
        state (torch.tensor): the current state
        goal (torch.tensor): the goal state
    """
    pass

  def __str__(self):
    """
    print a very short string representation of the problem and it's size
    """
    pass