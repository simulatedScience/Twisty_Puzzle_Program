
import numpy as np

def binary_reward_factory(solved_state) -> callable:
    def binary_reward(state: np.ndarray) -> tuple[float, bool]:
        done = np.all(state == solved_state, axis=-1)
        if isinstance(done, (bool, np.bool_)):
            reward = 1. if done else 0.
        elif isinstance(done, np.ndarray):
            reward = np.where(done, 1., 0.)
        else:
            raise ValueError(f"Unexpected type for done: {type(done)}")
        return reward, done
    return binary_reward

def correct_points_reward_factory(solved_state) -> callable:
    def correct_points_reward(state: np.ndarray) -> tuple[float, bool]:
        """
        Count the number of points that are in the correct position.

        Args:
            state (np.ndarray): The current state of the environment.
            # action
            solved_state (np.ndarray): The solved state of the environment.

        Returns:
            (float): The reward in range [0, 1].
        """
        correct_points = np.sum(state == solved_state, axis=-1)
        reward = correct_points/state.shape[-1]
        done = 1-reward < 1e-5
        if done:
            reward = 100.
        # print("correct points reward: ",
        #       state,
        #       solved_state,
        #       f"reward = {reward}",
        #       sep="\n",
        #       end="\n\n")
        return reward, done
    return correct_points_reward

def most_correct_points_reward_factory(solved_states: list[np.ndarray]) -> callable:
    def most_correct_points_reward(state):
        """
        Count the number of points that are in the correct position considering several possible solved states. This is especially useful when considering any rotation of the solved state as solved.

        Args:
            state (np.ndarray): The current state of the environment.
            # action
            solved_states (list[np.ndarray]): The solved states of the environment.

        Returns:
            (float): The reward in range [0, 1].
        """
        max_correct_points = 0
        for solved_state in solved_states:
            correct_points = np.sum(state == solved_state, axis=-1)
            max_correct_points = max(max_correct_points, correct_points)
        reward = max_correct_points/state.shape[-1]
        done = 1-reward < 1e-5
        if done:
            reward = 100.
        # print("most correct points reward: ",
        #       state,
        #       solved_states,
        #       f"reward = {reward}",
        #       sep="\n",
        #       end="\n\n")
        return reward, done
    return most_correct_points_reward