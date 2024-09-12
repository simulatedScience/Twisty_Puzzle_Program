
# import numpy as np
import torch

def binary_reward_factory(solved_state: torch.tensor) -> callable:
    def binary_reward(state: torch.Tensor, truncated: bool) -> tuple[float, bool]:
        done = torch.all(state == solved_state, axis=-1)
        if isinstance(done, (bool, torch.bool)):
            reward = 1. if done else 0.
        elif isinstance(done, torch.Tensor):
            reward = torch.where(done, 1., 0.)
        else:
            raise ValueError(f"Unexpected type for done: {type(done)}")
        return reward, done
    return binary_reward

def correct_points_reward_factory(solved_state) -> callable:
    def correct_points_reward(state: torch.Tensor, truncated: bool) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position.

        Args:
            state (torch.Tensor): The current state of the environment.
            # action
            solved_state (torch.Tensor): The solved state of the environment.

        Returns:
            (float): The reward in range [0, 1].
        """
        correct_points = torch.sum(state == solved_state, axis=-1)
        reward = correct_points/state.shape[-1]
        done = 1-reward < 1e-5
        if done:
            reward = 500.
        # print("correct points reward: ",
        #       state,
        #       solved_state,
        #       f"reward = {reward}",
        #       sep="\n",
        #       end="\n\n")
        return reward, done
    return correct_points_reward

def most_correct_points_reward_factory(solved_states: torch.Tensor) -> callable:
    def most_correct_points_reward(state: torch.Tensor, truncated: bool) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

        Args:
            state (torch.Tensor): The current state of the environment.
            # action
            solved_states (torch.Tensor): The solved states of the environment as rows in a matrix.

        Returns:
            (float): The reward in range [0, 1].
        """
        max_correct_points: int = 0
        for solved_state in solved_states:
            correct_points = torch.sum(state == solved_state, axis=-1)
            max_correct_points = torch.max(max_correct_points, correct_points)
        reward = max_correct_points/state.shape[-1]
        done = 1-reward < 1e-5
        if done:
            reward = 500.
        return reward, done
    return most_correct_points_reward

def sparse_most_correct_points_reward_factory(solved_states: torch.Tensor) -> callable:
    def sparse_most_correct_points_reward(state: torch.Tensor, truncated: bool) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

        Args:
            state (torch.Tensor): The current state of the environment.
            # action
            solved_states (torch.Tensor): The solved states of the environment as rows in a matrix.

        Returns:
            (float): The reward in range [0, 1].
        """
        max_correct_points: int = 0
        for solved_state in solved_states:
            correct_points = torch.sum(state == solved_state, axis=-1)
            max_correct_points = torch.max(max_correct_points, correct_points)
        reward = max_correct_points/state.shape[-1]
        done = 1-reward < 1e-5
        if not (truncated or done):
            reward = 0.
        elif done:
            reward = 100.
        return reward, done
    return sparse_most_correct_points_reward