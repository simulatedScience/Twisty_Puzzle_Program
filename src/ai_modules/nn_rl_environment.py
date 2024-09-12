"""
This module implements a gymnasium environment to train neural network-based twisty puzzle agents using reinforcement learning.

This implementation uses pytorch in the entire environment to enable parallelization on a GPU.

Author: Sebastian Jost
"""


import gymnasium as gym
import torch
from stable_baselines3.common.callbacks import BaseCallback


STICKER_DTYPE: torch.dtype = torch.uint16

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
            device: str = "cuda",
            ):
        self.device: str = device
        self.solved_state, self.actions, self.base_actions = puzzle_info_to_torch(solved_state, actions, base_actions, device=device)

        self.num_base_actions = torch.uint16(len(self.base_actions))
        self.max_moves = torch.uint16(max_moves, device=self.device)
        self.episode_counter = torch.uint16(0)
        self.scramble_length = torch.uint16(initial_scramble_length)
        self.reward_func = reward_func
        self.success_threshold = torch.float16(success_threshold)
        
        self.last_n_episodes = torch.uint16(1000)
        self.episode_success_history = torch.zeros(self.last_n_episodes, dtype=torch.bool, device=self.device)

    def reset(self, seed = None, options=None) -> torch.Tensor:
        self.state: torch.Tensor = self.solved_state.clone()
        self.episode_counter += 1
        self.move_counter: torch.Tensor = torch.tensor(0, dtype=STICKER_DTYPE, device=self.device)
        # Access the monitor wrapper to get episode rewards
        if self.episode_counter%1000 == 0: # and hasattr(self, 'monitor'):
            self.mean_success_rate = torch.mean(self.episode_success_history)
            if self.mean_success_rate >= self.success_threshold:
                self.scramble_length += 1
                # results = self.monitor.get_episode_rewards()
                # # last_n_episodes = len(self.episode_success_history)  # Or any desired number of episodes
                # mean_reward = torch.mean(results[-self.last_n_episodes:]) if len(results) > 0 else 0
                # if self.scramble_length < 25 or self.scramble_length % 25 == 0:
                #     print(f"[{self.exp_identifier}] Increased scramble length to {self.scramble_length} after {self.episode_counter} episodes.")
                #     print(f"[{self.exp_identifier}] Mean reward over last {self.last_n_episodes} episodes: {mean_reward:.2f}")
                #     print(f"[{self.exp_identifier}] Current success rate: {self.mean_success_rate:.2%}")
        self.state = self.scramble_puzzle(self.scramble_length)
        return self.state, {}

    def step(self, action_index):
        permutation: torch.Tensor = self.actions[action_index]
        self.state: torch.Tensor = self.state[permutation]
        
        self.move_counter += 1
        
        # terminated = np.all(self.state == self.solved_state)
        truncated = self.move_counter >= self.max_moves

        reward, terminated = self.reward_func(self.state, truncated)

        if truncated or terminated:
            self.episode_success_history[self.episode_counter % self.last_n_episodes] = terminated
        
        return self.state, reward, terminated, truncated, {}

    def scramble_puzzle(self, scramble_length: "torch.uint16") -> torch.Tensor:
        """
        Scrample the puzzle by applying `scrable_length` random moves.

        Args:
            scramble_length (torch.uint16): number of random moves to apply

        Returns:
            torch.Tensor: the scrambled state
        """
        random_actions = self.base_actions[torch.randint(self.num_base_actions, (scramble_length,))]
        for action in random_actions:
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


def puzzle_info_to_torch(
        state: list[int],
        actions: dict[str, list[tuple[int, ...]]],
        base_actions: list[str] = None,
        device: str = "cuda",
        ) -> tuple[torch.Tensor, torch.Tensor]:
    """
    Convert the puzzle's state and actions to torch tensors.
    
    Args:
        state (list[int]): the puzzle's state as a list of sticker indizes
        actions (dict[str, list[tuple[int, ...]]]): the puzzle's actions given as names and permutations in cyclic form
        base_actions (list[str]): the base actions to use for scrambling the puzzle as list of names
        device (str): the device to use for computations (e.g. "cuda" or "cpu")
    """
    # uint16 is sufficient for puzzles with up to 65535 stickers (e.g. 100^3 cube).
    #   World record puzzle in 2024 has 49^2*6 = 14406 stickers (49^3 cube)
    torch_state: torch.Tensor = torch.tensor(state, dtype=STICKER_DTYPE, device=device)
    state_length: int = len(state)
    actions_list = [permutation_cycles_to_tensor(state_length, actions[movename]) for movename in sorted(actions.keys())]
    torch_actions: torch.Tensor = torch.tensor(actions_list, dtype=STICKER_DTYPE, device=device)

    if base_actions is None:
        base_actions = torch_actions
    else:
        sorted_actions: list[str] = sorted(actions.keys())
        base_actions = torch.tensor(
            [actions[sorted_actions.index(base_action)] for base_action in base_actions],
            dtype=STICKER_DTYPE,
            device=device
        )
        del sorted_actions

    return (
        torch_state,
        torch_actions,
        base_actions,
        )

def permutation_cycles_to_tensor(state_length: int, action: list[list[int]]) -> torch.Tensor:
    """
    Convert a permutation in cycle notation to a tensor.

    Args:
        action (list[list[int]]): permutation in cycle notation

    Returns:
        torch.Tensor: permutation as a tensor
    """
    permutation = torch.arange(state_length, dtype=STICKER_DTYPE)
    for i, cycle in enumerate(action):
        for j, element in enumerate(cycle):
            permutation[element] = cycle[(j+1) % len(cycle)]
    return permutation


