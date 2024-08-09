"""
1. Scramble the puzzle randomly from a solved state using a given action set.
2. After each move, record the value of the reward function.
3. Repeat for many scrambles, averaging the results
4. Plot the average reward after each move in a grid.
"""

from src.smart_scramble import smart_scramble
from src.ai_modules.twisty_puzzle_model import perform_action
from tests.nn_rl_stable_baselines.reward_functions import binary_reward, correct_points_reward

def get_scramble_rewards(
        scramble_moves: list[str],
        reward_functions: dict[str, callable],
        solved_state: list[int],
        actions_dict: dict[str, list[list[int]]],
    ) -> dict[str, list[float]]:
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
            reward, done = reward_function(current_state, action, solved_state)
            rewards[name].append(reward)
            dones[name].append(done)
        if i != num_moves-1:
            current_state = perform_action(current_state, action)
    return rewards, dones

def plot_rewards(
    rewards: dict[str, list[float]],
    dones: dict[str, list[bool]],
    min_max_rewards: dict[str, list[tuple[float, float]]],
)