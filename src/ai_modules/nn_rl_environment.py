"""
This module implements a gymnasium environment to train neural network-based twisty puzzle agents using reinforcement learning.

This implementation uses numpy in the entire environment to enable efficient parallelization on a GPU.

Author: Sebastian Jost
"""
import gymnasium as gym
import numpy as np
from gymnasium.spaces import MultiDiscrete, Discrete
from stable_baselines3.common.callbacks import BaseCallback


# STICKER_DTYPE: np.int32 = np.int32
STICKER_DTYPE: np.dtype = np.uint16


class Twisty_Puzzle_Env(gym.Env):
    def __init__(self,
            solved_state: list[int],
            actions: dict[str, list[tuple[int, ...]]],
            base_actions: list[str] = None,
            max_moves: int = 50,
            initial_scramble_length=1, # 1 seems to work best
            success_threshold=0.9,
            reward_func: callable = None,
            # exp_identifier: str | None = None,
            ):
        self.solved_state, self.actions, self.base_actions = puzzle_info_to_np(solved_state, actions, base_actions)
        # initialize other parameters
        self.num_base_actions: int = len(self.base_actions)
        self.max_moves: int = max_moves
        self.episode_counter: int = 0
        self.scramble_length: int = initial_scramble_length
        self.reward_func: callable = reward_func
        self.success_threshold: float = success_threshold
        # parameters for tracking success rate
        self.last_n_episodes: int = 1000
        # self.episode_success_history: np.ndarray = np.zeros(self.last_n_episodes, dtype=np.bool_)
        
        self.scramble_actions: np.ndarray = np.zeros((0,), dtype=np.int32) # stores the most recent scramble actions

        # define variables for gym environment (Observation and Action Space)
        self.observation_space = MultiDiscrete([len(set(solved_state))] * len(solved_state))
        self.action_space = Discrete(len(actions))

    def is_terminated(self) -> bool:
        """
        Check if the episode was terminated.

        Returns:
            bool: True if the episode was terminated
        """
        return self.terminated

    # def reset_terminated(self) -> None:
    #     self.terminated = False

    def set_scramble_length(self, scramble_length: int) -> None:
        """
        Set the scramble length for all future episodes to the given value.  
        Note: This method is required to update the scramble depth when using a vectorized version of this environment for sb3-based rl-training.

        Args:
            scramble_length (int): number of moves to scramble the puzzle with. (positive integer)
        """
        self.scramble_length: int = scramble_length

    def get_scramble_length(self) -> int:
        """
        Get the current scramble length.

        Returns:
            int: the current scramble length
        """
        return self.scramble_length

    def reset(self, seed = None, options=None) -> tuple[np.ndarray, dict]:
        """
        Reset the environment to a random scrambled state. First, reset to solved, then apply `self.scramble_length` random base moves.

        Args:
            seed (int?, optional): unused parameter expected for gym environments. Defaults to None.
            options (dict?, optional): unused parameter expected for gym environments. Defaults to None.

        Returns:
            np.ndarray: a random scrambled state of the puzzle (start state for RL episode)
            dict: options dictionary (empty) (return value expected for gym environments)
        """
        self.state: np.ndarray = self.solved_state.copy()
        self.episode_counter += 1
        self.move_counter: np.ndarray = STICKER_DTYPE(0)
        self.terminated: bool = False
        # Access the monitor wrapper to get episode rewards
        # if self.episode_counter%1000 == 0: # and hasattr(self, 'monitor'):
        #     self.mean_success_rate = np.mean(self.episode_success_history)
        #     if self.mean_success_rate >= self.success_threshold:
        #         self.scramble_length += 1
        #         # results = self.monitor.get_episode_rewards()
        #         # # last_n_episodes = len(self.episode_success_history)  # Or any desired number of episodes
        #         # mean_reward = np.mean(results[-self.last_n_episodes:]) if len(results) > 0 else 0
        #         # if self.scramble_length < 25 or self.scramble_length % 25 == 0:
        #         #     print(f"[{self.exp_identifier}] Increased scramble length to {self.scramble_length} after {self.episode_counter} episodes.")
        #         #     print(f"[{self.exp_identifier}] Mean reward over last {self.last_n_episodes} episodes: {mean_reward:.2f}")
        #         #     print(f"[{self.exp_identifier}] Current success rate: {self.mean_success_rate:.2%}")
        self.state = self.scramble_puzzle(self.scramble_length)
        return self.state, {}

    def step(self, action_index):
        
        permutation: np.ndarray = self.actions[action_index]
        self.state: np.ndarray = self.state[permutation]
        
        self.move_counter += 1
        
        # terminated = np.all(self.state == self.solved_state)
        truncated = self.move_counter >= self.max_moves

        reward, self.terminated = self.reward_func(self.state, truncated)

        # if truncated or self.terminated:
        #     self.episode_success_history[self.episode_counter % self.last_n_episodes] = self.terminated
        
        return self.state, reward, self.terminated, truncated, {'terminated': self.terminated}

    def scramble_puzzle(self, scramble_length: int) -> np.ndarray:
        """
        Scrample the puzzle by applying `scrable_length` random moves.

        Args:
            scramble_length (int): number of random moves to apply

        Returns:
            np.ndarray: the scrambled state
        """
        self.scramble_actions = self.base_actions[np.random.random_integers(0, self.num_base_actions-1, (scramble_length,))]
        for action in self.scramble_actions:
            self.state = self.state[action]
        return self.state

class EarlyStopCallback(BaseCallback):
    def __init__(self, env: Twisty_Puzzle_Env, max_difficulty: int=100, verbose=0):
        super(EarlyStopCallback, self).__init__(verbose)
        self.env: Twisty_Puzzle_Env = env.unwrapped
        self.max_difficulty: int = max_difficulty

    def _on_step(self):
        if self.env.scramble_length > self.max_difficulty and self.env.mean_success_rate >= 1.:
            print(f"Early stopping: Difficulty {self.env.scramble_length} > {self.max_difficulty} reached. Last success rate: {np.mean(self.env.episode_success_history):.2%}")
            return False
        return True
    
class Update_Scramble_Length_Callback(BaseCallback):
    """
    This callback updates the scramble length of the environment whenever the past n episodes reach a given success rate.
    """
    def __init__(self, success_threshold: float = 0.1, last_n_episodes: int = 1000, verbose=0):
        super().__init__(verbose)
        # self.terminated_array: np.ndarray = np.zeros(last_n_episodes, dtype=np.bool_)
        self.last_n_episodes: int = last_n_episodes
        self.success_threshold: float = success_threshold
        # manually track episode success
        self.episode_success_history: np.ndarray = np.zeros(last_n_episodes, dtype=np.bool_)
        self.episode_index: int = 0

    # def _on_rollout_start(self) -> None:
    #     self.terminated_array: np.ndarray = np.zeros(self.last_n_episodes, dtype=np.bool_)
        # reset terminated flag in all envs
        # self.training_env.env_method("reset_terminated")

    def _on_step(self) -> bool:
        """
        Store the information if the episode was terminated.
        """
        for i, done in enumerate(self.locals["dones"]):
            if done:
                # self.episode_success_history[self.episode_index % self.last_n_episodes] = \
                #         self.training_env.env_method("is_terminated")[i]
                self.episode_success_history[self.episode_index % self.last_n_episodes] = \
                    self.locals["infos"][i].get("terminated", False)
                self.episode_index = (self.episode_index + 1) % self.last_n_episodes
        # for i, terminated in enumerate(self.training_env.env_method("is_terminated")):
        #     self.terminated_array[i] = terminated# if not self.terminated_array[i] else self.terminated_array[i]
        return True

    def _on_rollout_end(self) -> None:
        """
        Measure the success rate over the last n episodes and update the scramble length if the success rate is above the threshold.
        """
        # in locals['infos'] get the envs that have key 'terminal_observation'. From those, count how many have 'TimeLimit.truncated' == True and == False to calculate the success rate
        
        # count True in last `self.last_n_episodes` values in `dones`
        # mean_success_rate: float = 1 - self.locals["dones"][-self.last_n_episodes:].sum() / self.last_n_episodes
        mean_success_rate: float = np.mean(self.training_env.env_method("is_terminated")[-self.last_n_episodes:])
        old_scramble_length: int = self.training_env.env_method("get_scramble_length")[0]
        # print(f"n_calls: {self.n_calls}")
        print(f"Mean reward over {len(self.locals['rewards'])} eps: {np.mean(self.locals['rewards']):.2}")
        print(f"Current success rate: {mean_success_rate:6.1%}, old scramble length: {old_scramble_length}")
        print(f"Manual terminated mean: {np.mean(self.episode_success_history):6.1%}")
        if mean_success_rate >= self.success_threshold:
            self.training_env.env_method("set_scramble_length", old_scramble_length + 1)
            if self.verbose > 0:
                n_episodes: int = self.n_calls * self.training_env.n_envs
                print(f"Increased scramble length to {old_scramble_length + 1} after {self.num_timesteps} timesteps ({n_episodes} episodes).")
                print(f"Current success rate: {mean_success_rate:6.1%}")
        elif self.num_timesteps % 1_000_000 == 0 and self.verbose > 0:
            print(f"Current success rate: {mean_success_rate:6.1%}")


def puzzle_info_to_np(
        state: list[int],
        actions: dict[str, list[tuple[int, ...]]],
        base_actions: list[str] = None,
        ) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert the puzzle's state and actions to numpy arrays.
    
    Args:
        state (list[int]): the puzzle's state as a list of sticker indizes
        actions (dict[str, list[tuple[int, ...]]]): the puzzle's actions given as names and permutations in cyclic form
        base_actions (list[str]): the base actions to use for scrambling the puzzle as list of names

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: the puzzle's state and actions as numpy arrays
    """
    # uint16 is sufficient for puzzles with up to 65535 stickers (e.g. 100^3 cube).
    #   World record puzzle in 2024 has 49^2*6 = 14406 stickers (49^3 cube)
    np_state: np.ndarray = np.array(state, dtype=STICKER_DTYPE)
    state_length: int = len(state)
    actions_list = [permutation_cycles_to_tensor(state_length, actions[movename]) for movename in sorted(actions.keys())]
    np_actions: np.ndarray = np.stack(actions_list)

    if base_actions is None:
        base_actions = np_actions
    else:
        sorted_actions: list[str] = sorted(actions.keys())
        base_actions = np.stack(
            [actions_list[sorted_actions.index(base_action)] for base_action in base_actions],
        )
        del sorted_actions

    return (
        np_state,
        np_actions,
        base_actions,
        )

def permutation_cycles_to_tensor(state_length: int, action: list[list[int]]) -> np.ndarray:
    """
    Convert a permutation in cycle notation to a tensor.

    Args:
        action (list[list[int]]): permutation in cycle notation

    Returns:
        np.ndarray: permutation as a tensor
    """
    permutation = np.arange(state_length, dtype=STICKER_DTYPE)
    for i, cycle in enumerate(action):
        for j, element in enumerate(cycle):
            permutation[element] = cycle[(j+1) % len(cycle)]
    return permutation


if __name__ == "__main__":
    # check environment with gym environment checker
    from stable_baselines3.common.env_checker import check_env
    check_env(Twisty_Puzzle_Env(
        solved_state=[0, 1, 2, 3, 4, 5],
        actions={"U": [[0, 1, 2], [3, 4, 5]]},
        base_actions=["U"],
        max_moves=10,
        initial_scramble_length=1,
        success_threshold=0.9,
        reward_func=lambda state, truncated: (0., truncated),
        ))
