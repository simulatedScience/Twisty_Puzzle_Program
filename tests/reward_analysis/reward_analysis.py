"""
1. Scramble the puzzle randomly from a solved state using a given action set.
2. After each move, record the value of the reward function.
3. Repeat for many scrambles, averaging the results
4. Plot the average reward after each move in a grid.
"""
import random

import matplotlib.pyplot as plt
import numpy as np


import os, sys, inspect
# add grandparent directory "Twisty_Puzzle_Program" to path
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
grandparentdir = os.path.dirname(os.path.dirname(currentdir))
sys.path.insert(0, grandparentdir)

from src.puzzle_class import Twisty_Puzzle
from src.smart_scramble import smart_scramble
from src.ai_modules.twisty_puzzle_model import perform_action
from reward_factories import binary_reward_factory, correct_points_reward_factory, most_correct_points_reward_factory
from tests.nn_rl_stable_baselines.nn_rl_training import load_puzzle
    # except ModuleNotFoundError as e:
    #     print(f"Module not found: {e}")

def get_scramble_rewards(
        scramble_moves: list[str],
        reward_functions: dict[str, callable],
        solved_state: list[int],
        actions_dict: dict[str, list[list[int]]],
    ) -> tuple[dict[str, list[float]], dict[str, list[bool]]]:
    """
    Given a list of scramble moves and reward functions, calculate the reward at each step of the scramble for each reward function.

    Args:
        scramble_moves (list[str]): A list of moves to scramble the puzzle.
        reward_functions (dict[str, callable]): A dictionary of reward functions with name and callable functio with signature (state, action, solved_state) -> tuple[float, bool]
        solved_state (list[int]): A list of integers representing the solved state of the puzzle. Each int represents one color, each item one sticker.
        actions_dict (dict[str, list[list[int]]]): A dictionary of actions to perform given by their names and cycle representation

    Returns:
        dict[str, list[float]]: A dictionary of reward function names and their rewards at each step of the scramble.
        dict[str, list[bool]]: A dictionary of reward function names and their done flags at each step of the scramble.
    """
    current_state: list[int] = solved_state.copy()
    rewards: dict[str, list[float]] = {name: [] for name in reward_functions.keys()}
    dones: dict[str, list[bool]] = {name: [] for name in reward_functions.keys()}
    num_moves = len(scramble_moves)
    scramble_moves.append(scramble_moves[-1])  # Add an extra move to get the correct length (num_moves+1 states)
    for i, move in enumerate(scramble_moves):
        action = actions_dict[move]
        for name, reward_function in reward_functions.items():
            reward, done = reward_function(current_state)
            rewards[name].append(reward)
            dones[name].append(done)
        if i != num_moves-1:
            current_state = perform_action(current_state, action)
    return rewards, dones

def plot_rewards(
    rewards: dict[str, list[float]],
    dones: dict[str, list[bool]],
    min_max_rewards: dict[str, list[tuple[float, float]]],
    label_prefix: str = "",
    puzzle_name: str = None,
    show: bool = True,
):
    """
    Plot the rewards for each reward function at each step of the scramble.

    Args:
        rewards (dict[str, list[float]]): A dictionary of reward function names and their rewards at each step of the scramble.
        dones (dict[str, list[bool]]): A dictionary of reward function names and their done flags at each step of the scramble.
        min_max_rewards (dict[str, list[tuple[float, float]]): A dictionary of reward function names and their min and max rewards.
    """
    num_moves = len(rewards[list(rewards.keys())[0]])
    linestyles = ['-', '--', '-.', ':']
    
    # check if any rewards are nonpositive
    nonpositive = any(reward <= 0 for reward_list in rewards.values() for reward in reward_list)
    plt_func = plt.plot if nonpositive else plt.semilogy
    
    for i, (name, reward_list) in enumerate(rewards.items()):
        # plot done markers
        # plt.scatter(
        #     range(num_moves),
        #     reward_list,
        #     label=name + "done",
        #     # plot done flags with different marker
        #     marker=['p' if done else 'o' for done in dones[name]])
        plt_func(
            range(num_moves),
            reward_list,
            linestyle=linestyles[i % len(linestyles)],
            alpha=0.8,
            label="   ".join([name, label_prefix]),
            # color=color,
        )
        color = plt.gca().lines[-1].get_color()
        if name in min_max_rewards:
            # get last plot color
            min_rewards, max_rewards = zip(*min_max_rewards[name])
            plt.fill_between(
                x=range(num_moves),
                y1=min_rewards,
                y2=max_rewards,
                color=color,
                alpha=0.2,
            )
    if puzzle_name is not None:
        plt.title(f"Rewards for {puzzle_name}")
    plt.legend()
    if show:
        plt.show()

def filter_actions(
        actions_dict: dict[str, list[list[int]]],
        base_action_names: list[str],
        rotations_prefix: str = "rot_") -> tuple[set[str], set[str], set[str]]:
    """
    Split actions into base actions, whole puzzle rotations and algorithms based on their names.

    Args:
        actions_dict (dict[str, list[list[int]]]): A dictionary of actions to perform given by their names and cycle representation, including whole puzzle rotations and algorithms
        base_action_names (list[str]): A list of base action names.
        rotations_prefix (str, optional): The prefix for whole puzzle rotations. Defaults to "rot_".

    Returns:
        set[str]: A set of base action names.
        set[str]: A set of whole puzzle rotation names.
        set[str]: A set of algorithm names.
    """
    # split actions into base actions, whole puzzle rotations and algorithms
    # base actions
    base_actions = {name for name, action in actions_dict.items() if name in base_action_names}
    # whole puzzle rotations
    puzzle_rotations = {name for name, action in actions_dict.items() if name.startswith(rotations_prefix)}
    # algorithms
    algorithms = {name for name, action in actions_dict.items() if name not in base_action_names and not name.startswith(rotations_prefix)}
    return base_actions, puzzle_rotations, algorithms

def create_actions_dict_options(
        base_actions: set[str],
        algorithms: set[str],
        rotations: set[str],
    ):
    print("base actions:", base_actions)
    print("rotations:", rotations)
    print("algorithms:", algorithms)
    # create the most promising actions dict options
    actions_dict_options: dict[str, set[str]] = {
    # 1. only base actions
        "base_actions": base_actions,
    # 2. base actions + algorithms
        "base_actions + algorithms": base_actions | algorithms,
    # 3. algorithms + whole puzzle rotations
        "algorithms + rotations": algorithms | rotations,
    # 4. base actions + whole puzzle rotations + algorithms
        "base_actions + rotations + algorithms": base_actions | rotations | algorithms
    }
    return actions_dict_options

if __name__ == "__main__":
    # Set up the puzzle
    # puzzle: Twisty_Puzzle = Twisty_Puzzle()
    # puzzle_name = input("Enter a puzzle name: ")
    # puzzle_name = "square_two_algs"
    # puzzle_name = "skewb_sym_half"
    puzzle_name = "rubiks_algs"
    # puzzle.load_puzzle(puzzle_name)
    solved_state, moves_dict = load_puzzle(puzzle_name)
    # n = puzzle.state_space_size
    
    base_actions, rotations, algorithms = filter_actions(
        actions_dict=moves_dict,
        # base_action_names={"s", "t", "t'", "b", "b'"},
        # base_action_names={"wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"},
        base_action_names={"f", "f'", "r", "r'", "b", "b'", "t", "t'", "l", "l'", "d", "d'"},
        rotations_prefix="rot_",
    )
    actions_dict_options = create_actions_dict_options(
        base_actions=base_actions,
        algorithms=algorithms,
        rotations=rotations,
    )
    rotated_solved_states = [solved_state] + [perform_action(solved_state.copy(), moves_dict[rot]) for rot in rotations]
    
    binary_reward = binary_reward_factory(solved_state)
    correct_points_reward = correct_points_reward_factory(solved_state)
    most_correct_points_reward = most_correct_points_reward_factory(rotated_solved_states)

    for actions_dict_name, actions_dict in actions_dict_options.items():
        scramble_moves = [random.choice(list(actions_dict)) for _ in range(50)]
        print(f"\nScramble moves for {actions_dict_name}:")
        print(*scramble_moves)
        rewards, dones = get_scramble_rewards(
            scramble_moves=scramble_moves,
            reward_functions={
                # 'binary': binary_reward,
                'correct_points': correct_points_reward,
                'most_correct_points': most_correct_points_reward
            },
            solved_state=solved_state,
            actions_dict=moves_dict,
        )
        
        plot_rewards(
            puzzle_name=puzzle_name,
            rewards=rewards,
            dones=dones,
            min_max_rewards={},
            label_prefix=actions_dict_name,
            show=False,
        )
    plt.suptitle(
        "Action Sets:\n$\\quad$" + "\n$\\quad$".join(
            [f"{name}: {{{', '.join(actions)}}}" for name, actions in actions_dict_options.items()]
            ),
        ha="left",
        va="top",
        x=0.05,
        fontsize=9,
    )
    plt.show()