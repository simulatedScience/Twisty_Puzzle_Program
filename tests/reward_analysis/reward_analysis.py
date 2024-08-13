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
    ) -> list[tuple]:
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
    # plt_func = plt.semilogy
    # plt_func = plt.plot

    artists = []

    for i, (name, reward_list) in enumerate(rewards.items()):
        # plot done markers
        # plt.scatter(
        #     range(num_moves),
        #     reward_list,
        #     label=name + "done",
        #     # plot done flags with different marker
        #     marker=['p' if done else 'o' for done in dones[name]])
        ax_line, = plt_func(
            range(num_moves),
            reward_list,
            linestyle=linestyles[i % len(linestyles)],
            alpha=0.8,
            label="   ".join([name, label_prefix]),
            # color=color,
        )
        map_legend_to_ax
        color = plt.gca().lines[-1].get_color()
        if name in min_max_rewards:
            # get last plot color
            min_rewards, max_rewards = min_max_rewards[name]
            ax_poly = plt.fill_between(
                x=range(num_moves),
                y1=min_rewards,
                y2=max_rewards,
                color=color,
                alpha=0.2,
            )
        else:
            ax_poly = None
        artists.append((ax_line, ax_poly))
    if puzzle_name is not None:
        plt.title(f"Rewards for {puzzle_name}")
    # plt.legend()
    if show:
        plt.show()
    return artists

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
        # "base_actions + algorithms": base_actions | algorithms,
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
    puzzle_name = "rubiks_2x2_sym"
    # puzzle.load_puzzle(puzzle_name)
    solved_state, moves_dict = load_puzzle(puzzle_name)
    # n = puzzle.state_space_size
    
    n_repetitions: int = 1
    
    base_actions, rotations, algorithms = filter_actions(
        actions_dict=moves_dict,
        # base_action_names={"s", "t", "t'", "b", "b'"}, # square_two
        # base_action_names={"wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"}, # skewb_sym_half
        # base_action_names={"f", "f'", "r", "r'", "b", "b'", "t", "t'", "l", "l'", "d", "d'"}, # rubiks_algs
        base_action_names={"f", "f'", "r", "r'", "b", "b'", "t", "t'", "l", "l'", "d", "d'"}, # rubiks_2x2_sym
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

    map_legend_to_ax = {}
    all_artists = []
    for actions_dict_name, actions_dict in actions_dict_options.items():
        reward_data: dict[str, list[list[float]]] = {}
        # dones_data: dict[str, list[list[bool]]] = {}
        for rep in range(n_repetitions):
            scramble_moves = [random.choice(list(actions_dict)) for _ in range(100)]
            # print(f"\nScramble moves for {actions_dict_name}:")
            # print(*scramble_moves)
            rewards, dones = get_scramble_rewards(
                scramble_moves=scramble_moves,
                reward_functions={
                    'binary': binary_reward,
                    'correct_points': correct_points_reward,
                    'most_correct_points': most_correct_points_reward
                },
                solved_state=solved_state,
                actions_dict=moves_dict,
            )
            for name, reward_list in rewards.items():
                if name not in reward_data:
                    reward_data[name] = []
                reward_data[name].append(reward_list)

        reward_data = {name: np.array(reward_lists) for name, reward_lists in reward_data.items()}
        # average the rewards over all repetitions
        reward_data_mean: dict[str, np.ndarray] = {}
        reward_data_std: dict[str, np.ndarray] = {}
        reward_data_min_max: dict[str, list[tuple[float, float]]] = {}
        for name, reward_lists in reward_data.items():
            reward_data_mean[name] = np.mean(reward_lists, axis=0)
            reward_data_std[name] = np.std(reward_lists, axis=0) if n_repetitions > 1 else np.zeros_like(reward_data_mean[name])
            # reward_data_min_max[name] = [np.max(reward_lists, axis=0), np.min(reward_lists, axis=0)]
            # get min max by adding +-std
            reward_data_min_max[name] = [reward_data_mean[name] + reward_data_std[name], reward_data_mean[name] - reward_data_std[name]]


        artists = plot_rewards(
            puzzle_name=puzzle_name,
            rewards=reward_data_mean,
            dones=dones,
            min_max_rewards=reward_data_min_max,
            label_prefix=actions_dict_name,
            show=False,
        )
        all_artists = all_artists + artists
        # new_legend_lines = legend.get_lines()#[:len(artists)]
        # print(f"{new_legend_lines = }")
    # plt.plot((0, 100), (0, 0), label="0", color="#000")
    legend = plt.legend(fancybox=True)
    pickradius = 10  # Points (Pt). How close the click needs to be to trigger an event.
    for legend_line, (ax_line, ax_poly) in zip(legend.get_lines(), all_artists):
        legend_line.set_picker(pickradius)  # Enable picking on the legend line.
        map_legend_to_ax[legend_line] = ax_line, ax_poly
    plt.suptitle(
        "Action Sets:\n$\\quad$" + "\n$\\quad$".join(
            [f"{name}: {{{', '.join(actions)}}}" for name, actions in actions_dict_options.items()]
            ),
        ha="left",
        va="top",
        x=0.05,
        fontsize=9,
    )
    # for legend_line, ax_line, polygon in zip(legend.get_lines(), plt.gca().lines, plt.gca().artists):
    #     legend_line.set_picker(pickradius)  # Enable picking on the legend line.
    #     map_legend_to_ax[legend_line] = ax_line, polygon
        
    
    def legend_on_pick(event):
        """
        copied from mpl legend picking demo: https://matplotlib.org/stable/gallery/event_handling/legend_picking.html
        """
        # On the pick event, find the original line corresponding to the legend
        # proxy line, and toggle its visibility.
        legend_line = event.artist
        # print(f"legend line: {legend_line}")

        # Do nothing if the source of the event is not a legend line.
        if legend_line not in map_legend_to_ax:
            return

        ax_line, polygon = map_legend_to_ax[legend_line]
        # ax_line = map_legend_to_ax[legend_line]
        visible = not ax_line.get_visible()
        ax_line.set_visible(visible)
        polygon.set_visible(visible)
        # Change the alpha on the line in the legend, so we can see what lines
        # have been toggled.
        legend_line.set_alpha(1.0 if visible else 0.2)
        plt.gcf().canvas.draw()
    
    plt.xlabel("Number of scramble moves since solved state.")
    plt.ylabel("average step reward $\pm 1 \sigma$")
    plt.gcf().canvas.mpl_connect('pick_event', legend_on_pick)
    plt.show()