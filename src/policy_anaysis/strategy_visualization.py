"""
This module implements tools to analyse how an agent solves a twisty puzzle: which points are solved first and how many moves it takes (on average) to solve each point. A point is considered solved if it remains in the correct position for a certain percentage of the remaining solve time.
Combined with the analysis in `algorithm_utilization`, this can be used by humans to replicate the agent's solutions or derive human-readable instructions to solve the puzzle.

## Problem:
`get_inverse_moves_dict` may not always provide the inverse of an algorithm.
During algorithm generation, we don't add an inverse if the algorithm is self-inverse under rotation. So if a rotation r exists such that a^-1 = r a r^-1, then a' is self-inverse under rotation and we don't add a' to the inverse moves dict. In that case inversion requires multiple moves, which is currently not supported by `get_inverse_moves_dict` or this code.
"""
import time
import os, sys, inspect
if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)

import numpy as np
import matplotlib.pyplot as plt
import vpython as vpy

from src.ai_modules.twisty_puzzle_model import perform_action
from src.ai_modules.ai_data_preparation import state_for_ai
from src.algorithm_generation.algorithm_analysis import get_inverse_moves_dict
from src.interaction_modules.ai_file_management import load_test_file
from src.puzzle_class import Twisty_Puzzle

def analyze_strategy(
        test_data: dict[str, any],
        correctness_threshold: float,
        puzzle: Twisty_Puzzle
        ) -> list[float]:
    """
    For each point, calculate the average number of moves it took to solve it.
    "Solved" means that the point is in the correct position more than `correctness_threshold*100 %` of the remaining time in the solve. This is necessary because often moving the remaining pieces in the correct positions requires moving some already solved ones out of the way and back again.
    
    Rotation moves are also applied to the solved state.

    Args:
        test_data (dict[str, any]): test data to analyze
        correctness_threshold (float): threshold for correctness of a point
        puzzle (Twisty_Puzzle): puzzle to analyze

    Returns:
        list[float]: list of average number of moves it took to solve each point
    """
    solved_state, color_list = state_for_ai(puzzle.SOLVED_STATE)
    moves_dict: dict[str, list[list[int]]] = puzzle.moves
    inverse_dict: dict[str, str] = get_inverse_moves_dict(puzzle.moves)
    n_points: int = len(solved_state)
    
    deviations_per_point = [[] for _ in range(n_points)]  # List to track deviations for each point

    for run_num, run in enumerate(test_data["run_info"]):
        if run["success"] == False: # ignore failed runs
            continue
        agent_moves: list[str] = run["agent_moves:"].split()
        solution_length: int = len(agent_moves)
        # Reverse the solve sequence
        reverse_moves: list[str] = [inverse_dict[move] for move in reversed(agent_moves)]
        
        # Copy the solved state to track the current state
        current_state: list[int] = solved_state[:]
        current_solved_state: list[int] = solved_state[:]
        
        # Track correctness of each point over time
        correctness_history: np.ndarray = np.ones((solution_length, n_points), dtype=bool) # Keep track when during the solve each move was correct
        run_avg_point_correctness = [-1] * n_points  # Initialize the first deviation count

        # Apply moves in reverse
        for move_num, move in enumerate(reverse_moves):
            # Apply the move
            perform_action(current_state, moves_dict[move])
            # apply rotations to solved state as well
            if move.startswith("rot_"):
                perform_action(current_solved_state, moves_dict[move])
            
            # Track correctness
            for i, (current_val, solved_val) in enumerate(zip(current_state, current_solved_state)):
                correctness_history[move_num][i] = current_val == solved_val
        # calculate when each point stayed in its correct position
        # for point_idx in range(n_points):
        #     for move_num in range(solution_length):
        #         if np.average(correctness_history[move_num:][point_idx]) > correctness_threshold:
        #             deviation_move_counts[point_idx] = move_num
        #         break
        # average the correctness of each point over the whole solve
        for point_idx in range(n_points):
            run_avg_point_correctness[point_idx] = np.average(correctness_history[:,point_idx])
        # Add to overall deviations list
        for i in range(n_points):
            if run_avg_point_correctness[i] == -1:
                run_avg_point_correctness[i] = len(reverse_moves)
            deviations_per_point[i].append(run_avg_point_correctness[i])
        # print(f"run {run_num} deviation counts: {deviation_move_counts}")

    # Calculate averages for each point
    avg_solved_time_per_point = [sum(deviation_list) / len(deviation_list) for deviation_list in deviations_per_point]
    avg_solved_std_per_point = [np.std(deviation_list) for deviation_list in deviations_per_point]
    return avg_solved_time_per_point, avg_solved_std_per_point

def show_avg_deviations(
        avg_deviations: list[float],
        puzzle: Twisty_Puzzle,
        color: tuple[float] = (1., 0, 1.)) -> None:
    """
    On the given puzzle, color the points according to the average number of moves it took to solve them. Use a gradient from black (many moves) to `color` (few moves to solve).
    
    Args:
        avg_deviations (list[float]): list of average number of moves it took to solve each point
        puzzle (Twisty_Puzzle): puzzle to color
        color (tuple[float]): base color for the gradient
    """
    base_color = vpy.vector(*color)
    max_num_moves = max(avg_deviations)
    for i, avg_dev in enumerate(avg_deviations):
        point_color = base_color * (1 - avg_dev / max_num_moves)**.5
        puzzle.vpy_objects[i].color = point_color
    print("Brighter points are solved first.")
    print(f"Solving the first point took on average {min(avg_deviations):.1f} moves.")
    print(f"Solving the last point took on average {max(avg_deviations):.1f} moves.")

def main(
        test_file_path: str | None = None,
        show_on_puzzle: bool = True,
        color: tuple[float] = (0,1,0),
        ) -> list[float]:
    """
    Load a test file and analyze the strategy used to solve the puzzle.
    
    Args:
        test_file_path (str | None): path to the test file to analyze. If None, a file dialog will open.
        show_on_puzzle (bool): whether to show the results on the puzzle
        color (tuple[float]): base color for the gradient

    Returns:
        list[float]: list of average number of moves it took to solve each point
    """
    test_data, test_file_path = load_test_file(test_file_path)
    base_path = test_file_path.split("/")[:-2]
    # load corresponding puzzle
    puzzle_definition_path: str = os.path.join(*base_path, "puzzle_definition.xml")
    puzzle_definition_path = puzzle_definition_path[:2] + "/" + puzzle_definition_path[2:]
    print(puzzle_definition_path)
    # print(ref_path)
    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_definition_path)

    # correctness_threshold = 0.7  # Example threshold for deviation
    correctness_threshold = 0.8  # Example threshold for deviation

    avg_solved_time_per_point, avg_solved_std_per_point = analyze_strategy(
        test_data,
        correctness_threshold,
        puzzle)
    plt.errorbar(
        range(len(avg_solved_time_per_point)),
        avg_solved_time_per_point,
        yerr=avg_solved_std_per_point,
        fmt='o',
        ecolor='#000', # black error bars
        capsize=3,
    )
    plt.title(f"Avg. time each point was solved during {len(test_data['run_info'])} solves")
    plt.xlabel("Point index")
    plt.ylabel("average correct time")
    plt.ylim(0, 1)
    plt.show()
    print([round(dev, 2) for dev in avg_solved_time_per_point])
    if show_on_puzzle:
        show_avg_deviations(avg_solved_time_per_point, puzzle, color=color)
        # puzzle.set_clip_poly("cube", 0.7)
        # puzzle.draw_3d_pieces()

    return avg_solved_time_per_point

if __name__ == "__main__":
    main()