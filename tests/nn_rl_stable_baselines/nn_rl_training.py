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
import sys
import time

import numpy as np
import matplotlib.pyplot as plt

print(sys.version)
from gymnasium import Env
from gymnasium.spaces import MultiDiscrete, Discrete
from stable_baselines3 import PPO

class Twisty_Puzzle_Env(Env):
    def __init__(self, solved_state: list[int], actions: dict[str, list[tuple[int, ...]]]):
        super(Twisty_Puzzle_Env, self).__init__()
        self.solved_state = solved_state
        self.actions = actions
        
        # Observation space: MultiDiscrete for the stickers, each can be one of the colors
        self.observation_space = MultiDiscrete([6] * len(solved_state))
        
        # Action space: Discrete, each action corresponds to a named move
        self.action_space = Discrete(len(actions))
        self.action_index_to_name = {i: name for i, name in enumerate(actions.keys())}
        self.name_to_action_index = {name: i for i, name in self.action_index_to_name.items()}
        
        # Initialize the state
        self.state = list(solved_state)

    def reset(self, seed=None):
        self.state = list(self.solved_state)
        return self.state
    
    def step(self, action):
        action_name = self.action_index_to_name[action]
        permutation = self.actions[action_name]
        self.state = self.apply_permutation(self.state, permutation)
        
        done = self.state == self.solved_state
        reward = 1 if done else -1
        
        return self.state, reward, done, {}
    
    def apply_permutation(self, state, permutation):
        new_state = list(state)
        for cycle in permutation:
            if len(cycle) > 1:
                first_element = new_state[cycle[0]]
                for i in range(len(cycle) - 1):
                    new_state[cycle[i]] = new_state[cycle[i + 1]]
                new_state[cycle[-1]] = first_element
        return new_state

    def render(self, mode='human'):
        # Simple render function
        print(self.state)


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
    


solved_state, actions_dict = load_puzzle("rubiks_2x2_ai")
env = Twisty_Puzzle_Env(solved_state, actions_dict)
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=1000)