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
    inverse_dict: dict[str, str] = get_inverse_moves_dict(puzzle.moves)
    
    # Initialize dictionaries to store data for algorithms
    moves_to_solved_algs: dict[str, list[int]] = {}
    unsolved_points_algs: dict[str, list[int]] = {}
    
    for run_num, run in enumerate(test_data["run_info"]):
        if run["success"] == False:
            continue
        agent_moves: list[str] = run["agent_moves:"].split()
        # Reverse the solve sequence
        reverse_moves: list[str] = [inverse_dict[move] for move in reversed(agent_moves)]

        # Copy the solved state to track the current state
        current_state: list[int] = solved_state[:]
        current_solved_state: list[int] = solved_state[:]
        moves_to_solved: int = 1

        # Apply each move and collect data when an algorithm move (starting with "alg_") is found
        for move_num, move in enumerate(reverse_moves):
            # Apply the move
            perform_action(current_state, moves_dict[move])
            # apply rotations to solved state as well
            if move.startswith("rot_"):
                perform_action(current_solved_state, moves_dict[move])
            else:
                moves_to_solved += 1
            
            # Track the number of correct points
            n_unseolved_points: int = sum([current_val != solved_val for current_val, solved_val in zip(current_state, current_solved_state)])

            # if move.startswith("alg_"):
            # If this algorithm is not yet tracked, initialize an empty list
            if move not in moves_to_solved_algs:
                moves_to_solved_algs[move] = []
                unsolved_points_algs[move] = []
            
            # Record data for this algorithm occurrence
            moves_to_solved_algs[move].append(moves_to_solved)  # Moves to the solved state
            unsolved_points_algs[move].append(n_unseolved_points)  # Number of correct points
    
    return moves_to_solved_algs, unsolved_points_algs

def plot_boxplot_from_dict(data: dict[str, list[int]], title: str, xlabel: str, ylabels: str):
    """
    Create a horizontal boxplot from a dictionary.
    
    Args:
        data (dict[str, list[int]]): dictionary where keys are labels and values are lists of numbers
        title (str): title of the plot
        xlabel (str): label for the x-axis
        ylabel (str): label for the y-axis
    """
    fig, axes = plt.subplots(
        # figsize=(10, len(data) * 0.5),
        nrows=1,
        ncols=3,)

    base_color: str = "#2d2"
    rot_color: str = "#58f"
    alg_color: str = "#d22"
    # split data by keys: (starts with "rot_", starts with "alg_", others)
    rot_data: dict[str, list[int]] = {k: v for k, v in data.items() if k.startswith("rot_")}
    alg_data: dict[str, list[int]] = {k: v for k, v in data.items() if k.startswith("alg_")}
    other_data: dict[str, list[int]] = {k: v for k, v in data.items() if not k in rot_data and not k in alg_data}

    labels: list[str] = []

    for data, color, ax, ylabel in zip((alg_data, rot_data, other_data), (alg_color, rot_color, base_color), axes, ylabels):
        # Sort algorithms by their names to have a consistent order in the plot
        # sort data by mean of values
        sorted_data = {k: v for k, v in sorted(data.items(), key=lambda item: np.mean(item[1]))}
        
        # Prepare data for the boxplot
        labels = list(sorted_data.keys())
        values = list(sorted_data.values())
        
        # Create the horizontal boxplot
        bplot: dict[str, list[plt.Line2D]] = ax.boxplot(values, vert=False, patch_artist=True)
        # fill with colors
        for patch in bplot['boxes']:
            patch.set_facecolor(color)
        
        # Set y-ticks as algorithm names
        ax.set_yticklabels(labels)
        # Set plot labels in bold font
        ax.set_xlabel(xlabel, fontweight="bold")
        ax.set_ylabel(ylabel, fontweight="bold")
    fig.tight_layout()
    fig.subplots_adjust(wspace=0.15)
    
    # Set plot labels and title
    fig.suptitle(title, fontweight="bold")
    
    # Display the plot
    plt.show()

# Example usage:
# Load or generate the test data (test_data) and the puzzle object (puzzle)

def main(
        test_file_path: str | None = None,
        ):
    """
    Load a test file and analyze when each algorithm is used during the solves.
    Visualize the data using stacked boxplots for each algorithm.

    Args:
        test_file_path (str | None): path to the test file to analyze. If None, a file dialog will open.
    """
    test_data, test_file_path = load_test_file(test_file_path)
    base_path = test_file_path.split("/")[:-2]
    if not base_path:
        base_path = test_file_path.split("\\")[:-2]
    # load corresponding puzzle
    puzzle_definition_path: str = os.path.join(*base_path, "puzzle_definition.xml")
    puzzle_definition_path = puzzle_definition_path[:2] + "/" + puzzle_definition_path[2:]
    print(puzzle_definition_path)
    # print(ref_path)
    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_definition_path)

    # Analyze the algorithms and collect data
    moves_to_solved_algs, unsolved_points_algs = get_algorithm_utilization_data(test_data, puzzle)

    # Create boxplots
    plot_boxplot_from_dict(
        moves_to_solved_algs,
        title="Moves to Solved State for Each Action",
        xlabel="Moves to Solved State",
        ylabels=("algorithm", "rotation", "move"))
    plot_boxplot_from_dict(
        unsolved_points_algs,
        title="Unsolved Points for Each Action",
        xlabel="Unsolved Points",
        ylabels=("algorithm", "rotation", "move"))

if __name__ == "__main__":
    # main(r"C:\Users\basti\Documents\programming\python\Twisty_Puzzle_Program\src\ai_files\cube_3x3x3_sym_algs\2024-09-28_23-37-59\tests\test_2024-09-29_05-31-09.json")
    main()