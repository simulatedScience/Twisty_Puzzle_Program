"""
This module implements a basic training routine for training a NN to solve a twisty puzzle using Reinforcement Learning.
Here, we use stable baselines to simplify training.

observations (tuple[int]):
    state of the puzzle as a list of integers
        each int roughly represents one colored sticker of the puzzle (e.g. 0 = white, 1 = yellow, ..., 5=blue)
actions (dict[str, list[tuple[int, ...]]]):
    dictionary of actions
        key: name of the action
        value: permutation applied to the puzzle's state given in cycle notation.

        Example entry: {'U': [(0, 1, 2, 3), (4, 5, 6, 7)]} represents the action U that cyclically permutes the first 4 stickers and the next set of 4 stickers of the puzzle. All other stickers (indices >7) remain unchanged.
"""
import os
import random

import numpy as np

from gymnasium import Env
from gymnasium.spaces import MultiDiscrete, Discrete
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from tqdm.auto import tqdm
import logging

# Disable Stable Baselines3 Logging
logging.getLogger("stable_baselines3").setLevel(logging.WARNING)

class Twisty_Puzzle_Env(Env):
    def __init__(self, solved_state: list[int], actions: dict[str, list[tuple[int, ...]]], max_moves=50):
        super(Twisty_Puzzle_Env, self).__init__()
        self.solved_state = solved_state
        self.actions = actions
        self.max_moves = max_moves
        self.current_step = 0
        self.scramble_length = 1
        self.episode_counter = 0
        
        # Observation space: MultiDiscrete for the stickers, each can be one of the colors
        self.observation_space = MultiDiscrete([6] * len(solved_state))
        
        # Action space: Discrete, each action corresponds to a named move
        self.action_space = Discrete(len(actions))
        self.action_index_to_name = {i: name for i, name in enumerate(actions.keys())}
        self.name_to_action_index = {name: i for i, name in self.action_index_to_name.items()}
        
        # Initialize the state
        self.state = list(solved_state)

    def reset(self, seed=None, options=None, print_scramble=False):
        self.state = list(self.solved_state)
        self.current_step = 0
        self.episode_counter += 1
        if self.episode_counter % 1000 == 0:
            self.scramble_length += 1
        self.state = self.scramble_puzzle(self.scramble_length, print_scramble=print_scramble)
        return self.state, {}

    def scramble_puzzle(self, n, print_scramble=False):
        state = list(self.solved_state)
        if print_scramble:
            scramble = [0]*n
        for i in range(n):
            action_name = random.choice(list(self.actions.keys()))
            if print_scramble:
                scramble[i] = action_name
            permutation = self.actions[action_name]
            state = self.apply_permutation(state, permutation)
        if print_scramble:
            print(f"Scramble: {' '.join(scramble)}")
        return state

    def step(self, action):
        action_name = self.action_index_to_name[action]
        permutation = self.actions[action_name]
        self.state = self.apply_permutation(self.state, permutation)
        
        self.current_step += 1
        
        terminated = np.all(self.state == self.solved_state)
        truncated = self.current_step >= self.max_moves
        
        reward = 1 if terminated else 0
        
        return self.state, reward, terminated, truncated, {}
    
    def apply_permutation(self, state, permutation):
        new_state = np.array(state)
        for cycle in permutation:
            if len(cycle) > 1:
                first_element = new_state[cycle[0]]
                new_state[cycle[:-1]] = new_state[cycle[1:]]
                new_state[cycle[-1]] = first_element
        return new_state

    def render(self, mode='human'):
        # Simple render function
        print(self.state)


class ProgressBarCallback(BaseCallback):
    def __init__(self, total_timesteps):
        super().__init__()
        self.pbar = tqdm(total=total_timesteps, desc="Training Progress")
    def _on_step(self):
        self.pbar.update(self.locals["self"].num_timesteps - self.pbar.n)
        # self.pbar.set_postfix(
        #     time_elapsed=self.num_timesteps,  # or calculate a more accurate time remaining
        # )
        return True

def load_puzzle(puzzle_name: str):
    """
    Load solved state and actions from puzzle definition file
    
    Args:
        puzzle_name (str): name of the puzzle
        
    Returns:
        list[int]: solved state of the puzzle
        dict[str, list[tuple[int, ...]]]: dictionary of actions (name -> permutation in cycle notation)
    """
    try:
        from src.interaction_modules.load_from_xml import load_puzzle
    except ImportError:
        import sys
        import os
        # Get the absolute path to the project's root directory (A)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
        # Add the project root and the C directory to the Python path
        sys.path.insert(0, project_root)
        from src.interaction_modules.load_from_xml import load_puzzle
    try:
        point_dicts, moves_dict, state_space_size = load_puzzle(puzzle_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the puzzle '{puzzle_name}'.")
    # convert point colors to solved state for the environment
    # point_dicts: list[dict[str, tuple[vpy.vector, vpy.vector, float]]]
    #     list includes position, color and size (for visualization) of each point
    #     convert to color index for each point
    point_colors = [point["vpy_color"] for point in point_dicts]
    point_colors = [(color.x, color.y, color.z) for color in point_colors]
    colors = list(set(point_colors))
    solved_state: np.ndarray[int] = np.array([colors.index(color) for color in point_colors])
    return solved_state, moves_dict


def test_agent(
        model,
        env,
        num_tests: int = 5,
        scramble_length: int = 5
    ):
    env.scramble_length = scramble_length
    for i in range(num_tests):
        obs, _ = env.reset(print_scramble=True)
        done = False
        action_sequence = []
        while not done:
            action, _ = model.predict(obs, deterministic=True)
            obs, _, terminated, truncated, _ = env.step(int(action))
            done = terminated or truncated
            action_sequence.append(env.action_index_to_name[int(action)])
        print(f"Test {i+1} solve: {' '.join(action_sequence)}")
        print(f"{'Solved' if terminated else 'Failed'} after {env.current_step} steps")

def main(
        puzzle_name: str = "rubiks_2x2_ai",
        train_new: bool = False,
        n_episodes: int = 500_000,
    ):
    solved_state, actions_dict = load_puzzle(puzzle_name)
    env = Twisty_Puzzle_Env(solved_state, actions_dict)
    model = PPO("MlpPolicy", env, verbose=1)
    # print model summary
    print(model.policy)
    # look for existing model
    model_path = os.path.join("models", f"{puzzle_name}_model_{n_episodes}.zip")
    if not train_new and os.path.exists(model_path):
        print("Loading existing model...")
        model = model.load(model_path)
    else: # train a new model
        print("Training new model...")
        callback = ProgressBarCallback(total_timesteps=n_episodes)
        model.learn(
            total_timesteps=n_episodes,
            callback=callback,
            log_interval=5000)
    os.makedirs("models", exist_ok=True)
    model.save(os.path.join("models", f"{puzzle_name}_model_{n_episodes}.zip"))
    test_agent(model, env)


if __name__ == "__main__":
    main(
        train_new=False,
    )
