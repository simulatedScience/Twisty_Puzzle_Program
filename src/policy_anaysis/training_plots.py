"""
This module helps to plot data collected with TensorBoard using matplotlib. It focuses on comparing two agents (dense and binary) on two metrics: episode length and episode reward. The data is extracted from the TensorBoard logs and plotted on two subplots.

Author: Sebastian Jost & GPT-4o (27.11.2024)
"""

import os
import matplotlib.pyplot as plt
# from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
from tensorflow.python.summary.summary_iterator import summary_iterator # ? (suggested by stackoverflow)
import numpy as np
# set mpl dpi
plt.rcParams['figure.dpi'] = 200

# Function to extract data from TensorBoard logs
def extract_tensorboard_data(filepaths, tag):
    """Extracts data from tensorboard files given a list of filepaths and a tag."""
    data = []
    for filepath in filepaths:
        steps, values = [], []
        for event in summary_iterator(filepath):
            for value in event.summary.value:
                if tag in value.tag:
                    steps.append(event.step)
                    values.append(value.simple_value)
        if steps and values:
            data.append((steps, values))
    return data

# Function to plot data on a given axis
def plot_data(ax, data, color_base, linestyles: str | list[str], alpha_step: float = 0.4, labels: list[str] = None, **kwargs):
    num_lines = len(data)
    alpha_values = [1 - alpha_step*i for i in range(num_lines)]
    if not labels:
        labels = [None] * num_lines
    if isinstance(linestyles, str):
        linestyles = [linestyles] * num_lines
    for (steps, values), alpha, linestyle, label in zip(data, alpha_values, linestyles, labels):
        ax.plot(steps, values, linestyle=linestyle, color=color_base, alpha=alpha, label=label, **kwargs)

# Main function to load data and plot
def main(
        dense_paths: list[str],
        binary_paths: list[str],
        dense_color: str = "#58f",
        binary_color: str = "#f80",
        labels: list[str] = [],
        alpha_step: float = 0.4,
    ):
    # Load data for both agent types
    dense_len_data = extract_tensorboard_data(dense_paths, 'ep_len_mean')
    dense_reward_data = extract_tensorboard_data(dense_paths, 'ep_rew_mean')
    binary_len_data = extract_tensorboard_data(binary_paths, 'ep_len_mean')
    binary_reward_data = extract_tensorboard_data(binary_paths, 'ep_rew_mean')

    # Create the figure and axes
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex=True, figsize=(10, 8))

    if len(labels) <= 4:
        linestyles: list[str] = ["-", ":", "--", "-."][:len(labels)]
    else:
        linestyles: list[str] = ["-"] * len(labels)

    # Plot dense agents (blue, dashed lines)
    plot_data(ax1, dense_len_data, dense_color, linestyles=linestyles, labels=["dense, " + label for label in labels], alpha_step=alpha_step)
    plot_data(ax2, dense_reward_data, dense_color, linestyles=linestyles, alpha_step=alpha_step)

    # Plot binary agents' data (red, solid)
    plot_data(ax1, binary_len_data, binary_color, linestyles=linestyles, labels=["binary, " + label for label in labels], alpha_step=alpha_step)
    # Create secondary y-axis for binary agents' rewards
    ax2_right = ax2.twinx()
    plot_data(ax2_right, binary_reward_data, binary_color, linestyles=linestyles, alpha_step=alpha_step)

    # Configure axes and legends
    ax1.set_ylabel('average episode length')
    ax2.set_ylabel('average episode reward (dense)', color=dense_color)
    ax2.set_xlabel('training timesteps')
    ax2_right.set_ylabel('average episode reward (binary)', color=binary_color)

    ax1.legend(loc='upper right')

    # Configure reward plot y-axis limits
    ax1.set_ylim(0, None)  # Allow full length range for all
    ax2.set_ylim(-50, None)  # Allow full length range for all
    ax2_right.set_ylim(-0.05, None)  # Allow full length range for all
    
    # set ax2 axis colors
    ax2.tick_params(axis='y', colors=dense_color)
    ax2.spines['left'].set_color(dense_color)
    ax2.spines['left'].set_linewidth(2)
    ax2_right.tick_params(axis='y', colors=binary_color)
    ax2_right.spines['right'].set_color(binary_color)
    ax2_right.spines['right'].set_linewidth(2)
    ax2_right.spines['left'].set_visible(False)
    
    ax1.grid(color="#ddd")
    ax2.grid(color="#ddd")

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Example usage (replace with actual paths)
    dense_paths: list[str] = [
        # r"src\final_models\cube_2x2x2_sym_algs\2024-11-21_18-16-15_dense\tb_logs\dense_0.25\events.out.tfevents.1732209376.DatacentreAtHome.110568.0",
        r"src\final_models\cuboid_3x3x2_sym_algs\2024-11-21_15-59-38_dense\tb_logs\dense_0.25\events.out.tfevents.1732201178.DatacentreAtHome.64648.0",
        r"src\final_models\rubiks_ai_sym_algs\2024-11-21_18-16-39_dense\tb_logs\dense_0.25\events.out.tfevents.1732209400.DatacentreAtHome.107924.0",
        # r"src\final_models\rubiks_image_cube_sym_algs\2024-11-21_18-17-21_dense\tb_logs\dense_0.25\events.out.tfevents.1732209442.DatacentreAtHome.109404.0",
    ]
    binary_paths: list[str] = [
        # r"src\final_models\cube_2x2x2_sym_algs\2024-11-23_16-43-35_binary_random\tb_logs\binary_random_0.7\events.out.tfevents.1732376616.DatacentreAtHome.457176.0",
        r"src\final_models\cuboid_3x3x2_sym_algs\2024-11-23_14-42-19_binary_random\tb_logs\binary_random_0.7\events.out.tfevents.1732369340.DatacentreAtHome.456920.0",
        r"src\final_models\rubiks_ai_sym_algs\2024-11-22_20-47-35_binary_random\tb_logs\binary_random_0.7\events.out.tfevents.1732304857.DatacentreAtHome.266184.0",
        # r"src\final_models\rubiks_image_cube_sym_algs\2024-11-22_20-47-04_binary_random\tb_logs\binary_random_0.7\events.out.tfevents.1732304825.DatacentreAtHome.264328.0",
    ]
    main(
        dense_paths,
        binary_paths,
        labels=[
            # "2x2x2 Cube",
            # "3x3x2 Cuboid",
            "3x3x3 Cube",
            # "picture Cube",
            ],
        alpha_step=0.5,
        )
