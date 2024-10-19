"""
This module implements tools to analyse when algorithms are typically used by an agent during a solve.
This helps gain insights into the agent's strategy and can be used by humans to replicate the agent's solutions or derive human-readable instructions to solve the puzzle.

## Problem:
`get_inverse_moves_dict` may not always provide the inverse of an algorithm.
During algorithm generation, we don't add an inverse if the algorithm is self-inverse under rotation. So if a rotation r exists such that a^-1 = r a r^-1, then a' is self-inverse under rotation and we don't add a' to the inverse moves dict. In that case inversion requires multiple moves, which is currently not supported by `get_inverse_moves_dict` or this code.
"""
import os, sys, inspect
if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)

import vpython as vpy
import matplotlib.pyplot as plt
import numpy as np

from src.ai_modules.twisty_puzzle_model import perform_action
from src.ai_modules.ai_data_preparation import state_for_ai
from src.algorithm_generation.algorithm_analysis import get_inverse_moves_dict
from src.interaction_modules.ai_file_management import load_test_file
from src.puzzle_class import Twisty_Puzzle


def get_algorithm_utilization_data(test_data: dict[str, any], puzzle: Twisty_Puzzle) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """
    Analyze the usage of each algorithm and collect data on the number of moves to the solved state
    and the number of correct points when each algorithm is used.
    
    Args:
        test_data (dict[str, any]): test data to analyze
        puzzle (Twisty_Puzzle): puzzle to analyze

    Returns:
        tuple: Two dictionaries: 
            - moves_to_solved_algs: dict[str, list[int]]
            - correct_points_algs: dict[str, list[int]]
    """
    solved_state, _ = state_for_ai(puzzle.SOLVED_STATE)
    moves_dict: dict[str, list[list[int]]] = puzzle.moves
    
    # Initialize dictionaries to store data for algorithms
    moves_to_solved_algs: dict[str, list[int]] = {}
    correct_points_algs: dict[str, list[int]] = {}
    
    for run_num, run in enumerate(test_data["run_info"]):
        if run["success"] == False:
            continue

        agent_moves: list[str] = run["agent_moves:"].split()

        # Copy the solved state to track the current state
        current_state: list[int] = solved_state[:]
        for move in run["scramble"].split():
            perform_action(current_state, moves_dict[move])
        current_solved_state: list[int] = current_state[:]
        for move in agent_moves:
            perform_action(current_state, moves_dict[move])

        # Apply each move and collect data when an algorithm move (starting with "alg_") is found
        for move_num, move in enumerate(agent_moves):
            # Apply the move
            perform_action(current_state, moves_dict[move])
            
            # Track the number of correct points
            correct_points = sum([current_val == solved_val for current_val, solved_val in zip(current_state, solved_state)])

            if move.startswith("alg_"):
                moves_to_solved: int = len(agent_moves) - move_num
                # If this algorithm is not yet tracked, initialize an empty list
                if move not in moves_to_solved_algs:
                    moves_to_solved_algs[move] = []
                    correct_points_algs[move] = []
                
                # Record data for this algorithm occurrence
                moves_to_solved_algs[move].append(moves_to_solved)  # Moves to the solved state
                correct_points_algs[move].append(correct_points)  # Number of correct points
    
    return moves_to_solved_algs, correct_points_algs

def plot_boxplot_from_dict(data: dict[str, list[int]], title: str, xlabel: str, ylabel: str):
    """
    Create a horizontal boxplot from a dictionary.
    
    Args:
        data (dict[str, list[int]]): dictionary where keys are labels and values are lists of numbers
        title (str): title of the plot
        xlabel (str): label for the x-axis
        ylabel (str): label for the y-axis
    """
    fig, ax = plt.subplots(figsize=(10, len(data) * 0.5))
    
    # Sort algorithms by their names to have a consistent order in the plot
    sorted_data = {k: v for k, v in sorted(data.items())}
    
    # Prepare data for the boxplot
    labels = list(sorted_data.keys())
    values = list(sorted_data.values())
    
    # Create the horizontal boxplot
    ax.boxplot(values, vert=False, patch_artist=True)
    
    # Set y-ticks as algorithm names
    ax.set_yticklabels(labels)
    
    # Set plot labels and title
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    
    # Display the plot
    plt.tight_layout()
    plt.show()

# Example usage:
# Load or generate the test data (test_data) and the puzzle object (puzzle)

# Step 1: Analyze the algorithms and collect data
moves_to_solved_algs, correct_points_algs = get_algorithm_utilization_data(test_data, puzzle)

# Step 2: Create boxplots
plot_boxplot_from_dict(moves_to_solved_algs, "Moves to Solved State for Each Algorithm", "Moves to Solved State", "Algorithm")
plot_boxplot_from_dict(correct_points_algs, "Correct Points for Each Algorithm", "Correct Points", "Algorithm")
