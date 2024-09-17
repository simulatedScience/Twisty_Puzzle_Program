
import numpy as np

def binary_reward_factory(solved_state: np.ndarray) -> callable:
    def binary_reward(state: np.ndarray, truncated: bool) -> tuple[float, bool]:
        """
        Return a reward of 1 if the state is equal to the solved state, otherwise 0.

        Args:
            state (np.ndarray): The current state of the environment.
            truncated (bool): Whether the episode was truncated.

        Returns:
            (float): The reward in range [0, 1]. This will always be 0 or 1.
        """
        done: bool = np.all(state == solved_state, axis=-1)
        if isinstance(done, (bool, np.bool_)):
            reward: float = 1. if done else 0.
        elif isinstance(done, np.ndarray):
            reward: float = np.where(done, 1., 0.)
        else:
            raise ValueError(f"Unexpected type for done: {type(done)}")
        return reward, done
    return binary_reward

def correct_points_reward_factory(solved_state) -> callable:
    def correct_points_reward(state: np.ndarray, truncated: bool) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position.

        Args:
            state (np.ndarray): The current state of the environment.
            truncated (bool): Whether the episode was truncated.

        Returns:
            (float): The reward in range [0, 1].
        """
        correct_points = np.sum(state == solved_state, axis=-1)
        reward: float = correct_points/state.shape[-1]
        done: bool = 1-reward < 1e-5
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

def most_correct_points_reward_factory(solved_states: np.ndarray) -> callable:
    def most_correct_points_reward(state: np.ndarray, truncated: bool) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

        Args:
            state (np.ndarray): The current state of the environment.
            truncated (bool): Whether the episode was truncated.

        Returns:
            (float): The reward in range [0, 1].
        """
        max_correct_points: int = 0
        for solved_state in solved_states:
            correct_points: int = np.sum(state == solved_state, axis=-1)
            max_correct_points: int = np.max(max_correct_points, correct_points)
        reward: float = max_correct_points/state.shape[-1]
        done: bool = 1-reward < 1e-5
        if done:
            reward = 500.
        return reward, done
    return most_correct_points_reward

def sparse_most_correct_points_reward_factory(solved_states: np.ndarray) -> callable:
    def sparse_most_correct_points_reward(state: np.ndarray, truncated: bool) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

        Args:
            state (np.ndarray): The current state of the environment.
            # action

        Returns:
            (float): The reward in range [0, 1].
        """
        max_correct_points: int = 0
        for solved_state in solved_states:
            correct_points: int = np.sum(state == solved_state, axis=-1)
            max_correct_points: int = np.max(max_correct_points, correct_points)
        reward: float = max_correct_points/state.shape[-1]
        done: bool = 1-reward < 1e-5
        if not (truncated or done):
            reward = 0.
        elif done:
            reward = 100.
        return reward, done
    return sparse_most_correct_points_reward