# import torch

def reward_01(state: "torch.tensor", goal: "torch.tensor") -> "torch.tensor":
  """
  Compute the 0-1 reward for the state and the goal (1 if state == goal, 0 otherwise).

  Args:
      state (torch.tensor): the current state
      goal (torch.tensor): the goal state

  Returns:
      torch.tensor: 1 if state == goal, 0 otherwise
  """
  return torch.tensor(1.0 if torch.equal(state, goal) else 0.0)


def reward_mse(state: "torch.tensor", goal: "torch.tensor"):
  """
  Reward is the negative mean squared error between state and goal.

  Args:
      state (torch.tensor): Current state.
      goal (torch.tensor): Goal state.

  Returns:
      (torch.tensor): Reward
  """
  return -torch.norm(state - goal, p=2)


def reward_mae(state: "torch.tensor", goal: "torch.tensor"):
  """
  Reward is the negative mean absolute error between state and goal.

  Args:
      state (torch.tensor): Current state.
      goal (torch.tensor): Goal state.

  Returns:
      (torch.tensor): Reward
  """
  return -torch.norm(state - goal, p=1)


def reward_euclidean(state: "torch.tensor", goal: "torch.tensor"):
  """
  Compute the negative euclidean distance between the state and the goal.

  Args:
      state (torch.tensor): the current state
      goal (torch.tensor): the goal state

  Returns:
      torch.tensor: the euclidean distance between the state and the goal
  """
  return -torch.norm(state - goal)


def reward_manhattan(state: "torch.tensor", goal: "torch.tensor"):
  """
  Compute the negative manhattan distance between the state and the goal.

  Args:
      state (torch.tensor): the current state
      goal (torch.tensor): the goal state

  Returns:
      torch.tensor: the manhattan distance between the state and the goal
  """
  return -torch.sum(torch.abs(state - goal))
