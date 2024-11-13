"""
Identify common action sequences of given lengths in test data.

This may help to identify common patterns and evaluate whether the agent has learnt useful properties of puzzles like conjugates or commutators. This information can also help humans interpret and replicate an agent's strategies.

1. use a sliding window of length n to count all occuring action sequences of length n in the test data.
2. find the k most common sequences of length n.
3. Discard any other sequences whose frequency is below a certain threshold relative to the most common sequence.

IF RESULTS ARE INTERESTING: implement:

4. Plot results in a horizontal bar chart with the sequences on the y-axis and their frequencies on the x-axis. Leave room next to the bars to display the effect of the sequence on the puzzle (screenshot of applied sequence).
    automatically take and insert screenshots?
        a) calculate most common sequences
        b) let user orient the puzzle in viewport as desired
        c) let user select rectangle on screen to take screenshot of by clicking on two corners. (recommend powerToys Mouse Crosshairs)
        d) take screenshot of the selected area and save it to a file. filename: policy_analysis/move_sequences/effect_[move sequence].png
"""

from PIL import ImageGrab
import os
if __name__ == "__main__":
    import sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)

import matplotlib.pyplot as plt
import numpy as np

from src.algorithm_generation.algorithm_analysis import get_inverse_moves_dict
from src.interaction_modules.ai_file_management import load_test_file
from src.puzzle_class import Twisty_Puzzle
from src.interaction_modules.ai_file_management import get_policy_savepath

def get_action_sequence_frequencies(
        data: dict[str, any],
        sequence_length: int,
        num_tests: int = float("inf"),
    ) -> list[tuple[tuple[str], float]]:
    """
    Calculate the frequency of each action sequence of the given length in the successful runs of the test data.

    Args:
        data (dict[str, any]): test data to analyze
        sequence_length (int): length of the action sequences to analyze

    Returns:
        list[tuple[tuple[str], float]]: list of tuples containing the action sequence and its frequency in the test data. Sorted by frequency in descending order (most common first).
    """
    action_sequence_counts: dict[tuple[str], int] = {}

    n_sequences: int = 0
    run_num: int = 0
    for run in data["run_info"]:
        if run["success"] == False:
            continue
        agent_moves: list[str] = run["agent_moves:"].split(" ")
        for i in range(len(agent_moves) - sequence_length + 1):
            sequence: tuple[str] = tuple(agent_moves[i:i+sequence_length])
            action_sequence_counts[sequence] = action_sequence_counts.get(sequence, 0) + 1
            n_sequences += 1
        run_num += 1
        if run_num > num_tests:
            break
    # sort the sequences by count
    sorted_sequences: list[tuple[tuple[str], int]] = sorted(action_sequence_counts.items(), key=lambda x: x[1], reverse=True)
    # convert counts to frequencies and return
    return [(sequence, count/n_sequences) for sequence, count in sorted_sequences]

def plot_most_common_sequences(
        action_seq_frequencies: list[tuple[tuple[str], float]],
        n_best: int = 10,
        n_best_threshold: float = 0,
        threshold_reference: str = "last",
    ) -> list[tuple[tuple[str], float]]:
    """
    Plot the `n_best` most common action sequences.  Additionally, show other action sequences with frequency greater than `n_best_threshold` times the frequency of the `n_best`th most common sequence.

    Args:
        action_seq_frequencies (list[tuple[tuple[str], float]]): list of tuples containing the action sequence and its frequency in the test data. Sorted by frequency in descending order (most common first).
        n_best (int, optional): number of most common sequences to plot. Defaults to 10.
        n_best_threshold (float, optional): minimum frequency to plot additional sequences. Defaults to 0.
        threshold_reference (str, optional): reference for the threshold. "first" means the frequency of the first sequence, "last" means the frequency of sequence with `n_best`th frequency. Defaults to "last".

    Returns:
        list[tuple[tuple[str], float]]: list of action sequences and frequencies of the plotted sequences, sorted by frequency in descending order.

    Raises:
        ValueError: if `threshold_reference` is not "first" or "last".
    """
    if threshold_reference.lower() == "first":
        threshold_frequency: float = action_seq_frequencies[0][1] * n_best_threshold
    elif threshold_reference.lower() == "last":
        threshold_frequency: float = action_seq_frequencies[n_best-1][1] * n_best_threshold
    else:
        raise ValueError(f"Invalid threshold_reference: {threshold_reference}. Expected 'first' or 'last'.")
    plot_sequences: list[tuple[tuple[str], float]] = []
    for i, (sequence, frequency) in enumerate(action_seq_frequencies):
        if i < n_best or frequency > threshold_frequency:
            plot_sequences.append((sequence, frequency))
        else:
            break
    # plot the sequences
    fig: plt.Figure = plt.figure(figsize=(12, 6))
    ax: plt.Axes = fig.add_subplot(111)
    y_labels: list[str] = [' $|$ '.join(sequence) for sequence, _ in plot_sequences]
    x_values: list[float] = [frequency for _, frequency in plot_sequences]
    y_pos: np.ndarray = np.arange(len(y_labels))
    bars = ax.barh(
        y_pos,
        x_values,
        align='center',
        color="#fa5",
        zorder=2,
    )
    # bar labels
    for bar, label in zip(bars, y_labels):
        ax.text(
            bar.get_width(),
            bar.get_y() + bar.get_height()/2,
            s=label + "  ", 
            ha='right',
            va='center',
            fontsize=10,
            color='black',
            zorder=3,
        )
    ax.set_yticks([]) # hide yticks
    ax.invert_yaxis()  # Invert the y-axis to have the most common sequence on top
    ax.set_xlabel('Frequency')
    ax.set_title('Most common action sequences')
    ax.grid(color="#ccc", axis='x')
    fig.subplots_adjust(left=0.05, right=0.95)
    plt.show()


def screen_capture_sequence_effects(
        puzzle: Twisty_Puzzle,
        sequence: str,
        save_path: str,
    ) -> list[str]:
    """
    
    Returns:
        list[str]: paths to each screenshot taken
    """

def screenshot_area(
    x_min: int,
    y_min: int,
    x_max: int,
    y_max: int,
    save_path: str,
    ) -> str:
    """
    Take a screenshot of the area defined by the given coordinates and save it to the given path.
    """
    image = ImageGrab.grab(
        bbox=(
            x_min,       # x_min
            y_min,       # y_min
            x_max-x_min, # width
            y_max-y_min, # height
        )
    )
    image.save(save_path)
    return save_path

def main(
        test_file_path: str | None = None,
        sequence_lengths: tuple[int] = (2, 3, 4),
        num_tests=float("inf"),
        ):
    """
    Find the most common action sequences of the given lengths. For example some triplets of moves may be common to apply an algorithm to a certain part of a puzzle: rot_x alg_y rot_x'.

    Args:
        test_file_path (str | None): path to the test file to analyze. If None, a file dialog will open.
        sequence_lengths (tuple[int], optional): lengths of the action sequences to analyze. Defaults to (2, 3, 4).
    """
    test_data, test_file_path = load_test_file(test_file_path)
    
    for seq_length in sequence_lengths:
        action_seq_frequencies: list[tuple[tuple[str], float]] = get_action_sequence_frequencies(test_data, seq_length, num_tests=num_tests)
        # plot most common sequences
        plot_most_common_sequences(
            action_seq_frequencies,
            n_best=10,
            n_best_threshold=0.5,
            threshold_reference="first",
        )

if __name__ == "__main__":
    main(
        test_file_path="C:/Users/basti/Documents/programming/python/Twisty_Puzzle_Program/src/ai_files/rubiks_ai_sym_algs/2024-11-05_00-54-16/tests/test_2024-11-05_05-02-47.json",
        num_tests=400
    )
