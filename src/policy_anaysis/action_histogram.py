"""
Let the user choose a test file, then analyse all successful episodes in it to create a histogram of actions used by the agents. Actions are grouped by category (algorithms, rotations, base moves) and displayed as a bar plot. An additional pie chart shows the relative frequency of each category.
"""

from collections import Counter

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
from matplotlib.transforms import IdentityTransform

# from src.interaction_modules.ai_file_management import get_policy_savepath

def get_successful_runs(run_info):
    """Return all successful runs from run_info."""
    return [run for run in run_info if run.get("success")]

def get_failed_runs(run_info):
    """Return all failed runs from run_info."""
    return [run for run in run_info if not run.get("success")]

def average_moves(runs):
    """Calculate the average number of moves in a list of runs."""
    if not runs:
        return 0
    total_moves = sum(run.get("n_moves", 0) for run in runs)
    return total_moves / len(runs)

def success_rate(run_info):
    """Calculate the success rate from the run_info."""
    total_runs = len(run_info)
    successful_runs = get_successful_runs(run_info)
    return (len(successful_runs) / total_runs) * 100 if total_runs > 0 else 0

# Categorize actions into algorithms, rotations, and base moves
def categorize_actions(actions):
    algs, rots, base_moves = [], [], []
    
    for action in actions:
        if action.startswith('alg_'):
            algs.append(action)
        elif action.startswith('rot_'):
            rots.append(action)
        else:
            base_moves.append(action)
    
    return algs, rots, base_moves

def action_histogram(runs):
    """Return histograms of actions grouped by category across all runs."""
    total_actions = 0
    alg_counter, rot_counter, base_counter = Counter(), Counter(), Counter()
    
    for run in runs:
        actions = run.get("agent_moves:", "").split()  # Split the string into individual actions
        total_actions += len(actions)
        algs, rots, base_moves = categorize_actions(actions)
        
        alg_counter.update(algs)
        rot_counter.update(rots)
        base_counter.update(base_moves)
    
    return alg_counter, rot_counter, base_counter, total_actions

def draw_pie_chart(
        ax: plt.Axes,
        data: list[float],
        colors: list[str],
        labels: list[str],
        position: tuple[float, float],
        size: float = 1.0,
    ) -> list[plt.Artist]:
    """
    Draw a pie chart on the given axis with the given data, colors, and labels.
    Uses Wedge to draw the pie slices onto any axis.
    """
    # precalculate the seams of the wedges
    wedge_angles: np.ndarray = np.array(data) / sum(data) * 360
    last_angle: float = 90.
    artists: list[plt.Artist] = []
    # compute transform to stretch pie chart into proper circle based on aspect ratio of the axis
    ax.set_aspect('equal')
    # equal_aspect_transform = ax.transAxes#ax.transData # = default
    equal_aspect_transform = ax.transData#ax.transData # = default
    # add circle as background
    circle_bg: Circle = Circle(
        position,
        size/2*1.05,
        color='#000',
        transform=equal_aspect_transform,
        zorder=5,
    )
    ax.add_patch(circle_bg)
    artists.append(circle_bg)
    radius = size/2
    # start initial wedge at 0°
    for wedge_angle1, elem_color, elem_label in zip(wedge_angles, colors, labels):
        wedge_angle2 = last_angle + wedge_angle1
        wedge = Wedge(
            center=position,
            r=radius,
            theta1=last_angle,
            theta2=wedge_angle2,
            color=elem_color,
            label=elem_label,
            transform=equal_aspect_transform,
            zorder=6,
        )
        ax.add_patch(wedge)
        artists.append(wedge)
        last_angle: float = wedge_angle2
    circle_bg: Circle = Circle(
        position,
        size/10,
        color='#fff',
        transform=equal_aspect_transform,
        zorder=7,
    )
    ax.add_patch(circle_bg)
    artists.append(circle_bg)
    # add text above pie chart
    ax.text(
        position[0],
        position[1] - radius * 1.1,
        "Action Types\nDistribution",
        ha='center',
        va='top',
        fontsize=10,
        color='#000',
    )

    return artists

def plot_action_histogram(
        alg_counter,
        rot_counter,
        base_counter,
        total_actions,
        color_list=['#d22', '#58f', '#2d2']
    ):
    """
    Plot a histogram with color coding for algorithms, rotations, and base moves (in percentages).
    """
    def extract_number(action):
        """Extract the numeric part from an action name."""
        return str(action.split('_')[-1].strip("'"))
    # Sort the keys by the numeric part within each group
    sorted_alg = sorted(alg_counter.keys(), key=extract_number)
    sorted_rot = sorted(rot_counter.keys(), key=extract_number)
    sorted_base = sorted(base_counter.keys())  # For base moves, we can keep lexicographical sorting

    # Merge sorted actions and their respective counts
    actions = sorted_alg + sorted_rot + sorted_base
    counts = [alg_counter[action] for action in sorted_alg] + \
             [rot_counter[action] for action in sorted_rot] + \
             [base_counter[action] for action in sorted_base]
    
    # calculate total percentage for each category
    alg_total = sum(alg_counter.values()) / total_actions
    rot_total = sum(rot_counter.values()) / total_actions
    base_total = sum(base_counter.values()) / total_actions
    print(f"Total alg: {alg_total:.1%}, rot: {rot_total:.1%}, base: {base_total:.1%}")
    pie_data: list[float] = [alg_total, rot_total, base_total]

    # Calculate relative frequencies (as percentages)
    counts_percentage = [(count / total_actions) * 100 for count in counts]
    
    # Assign colors from the color_list
    colors = [color_list[0]] * len(sorted_alg) + [color_list[1]] * len(sorted_rot) + [color_list[2]] * len(sorted_base)
    
    # Create the bar plot
    fig: plt.Figure = plt.figure(figsize=(12, 6))
    ax = fig.add_subplot(111)
    label_actions = [f"{action}" for action in actions]
    bars = ax.bar(label_actions, counts_percentage, color=colors)
    # Add text labels on top of each bar
    for bar in bars:
        yval = bar.get_height()  # Get the height of the bar (which is the value)
        ax.text(
            bar.get_x() + bar.get_width()/2,
            yval,
            f'{yval:.1f}%', 
            ha='center',
            va='bottom',
            fontsize=10,
            color='black',
        )
    
    
    # Adding legend
    legend = ax.legend(
        handles=[bars[0], bars[len(sorted_alg)], bars[len(sorted_alg) + len(sorted_rot)]], 
        labels=['Algorithms (alg_)', 'Rotations (rot_)', 'Base Moves'],
        loc='upper center',
    )
    fig.canvas.draw()
    # get legend width in data coordinates
    legend_window_extent = ax.transData.inverted().transform(legend.get_window_extent())
    legend_width_data_coords: float = legend_window_extent[1][0] - legend_window_extent[0][0]
    
    # Draw the pie chart
    y_lim: float = max(counts_percentage)
    pie_radius: float = y_lim * 0.09
    legend_pie_gap: float = pie_radius / 2
    pie_x_coord: float = (len(actions) - legend_width_data_coords - legend_pie_gap) / 2
    pie_position: tuple[float, float] = (pie_x_coord, 0.9 * y_lim)
    draw_pie_chart(
        ax=ax,
        data=pie_data,
        colors=color_list,
        labels=["Algorithms", "Rotations", "Base Moves"],
        position=pie_position,
        size=2*pie_radius,
    )
    # move legend next to pie chart
    fig.canvas.draw()
    new_legend_loc = ax.transAxes.inverted().transform(
    ax.transData.transform((
            pie_position[0] + pie_radius + legend_pie_gap,
            pie_position[1] - pie_radius
        )))
    print(f"{new_legend_loc = }")
    legend.set_loc(new_legend_loc)
    # Adding gridlines with color #ddd
    ax.grid(True, axis='y', color='#ddd')
    
    # Labeling and title
    ax.set_xlabel("Actions")
    ax.set_ylabel("Relative Frequency (%)")
    ax.set_title("Histogram of Actions by Category (Relative Frequency)")
    ax.set_xticks(range(len(actions)),actions, rotation=90)  # Rotate action labels for better visibility

    fig.tight_layout()
    # save_path: str = get_policy_savepath()
    plt.show()


if __name__ == "__main__":
    import os, sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)
    from src.interaction_modules.ai_file_management import load_test_file
    
    data, test_file_path = load_test_file()
    # data, test_file_path = load_test_file(r"C:/Users/basti/Documents/programming/python/Twisty_Puzzle_Program/src/ai_files/cube_2x2x2_sym_algs/2024-11-11_12-30-52/tests/test_2024-11-11_12-39-01.json")
    # Example usage:
    successful_runs = get_successful_runs(data['run_info'])
    average_successful_moves = average_moves(successful_runs)
    print(f"Average moves in successful runs: {average_successful_moves:.2f}")

    # Example usage:
    rate = success_rate(data['run_info'])
    print(f"Success rate: {rate:.2f}%")

    # Example usage:
    alg_counter, rot_counter, base_counter, total_actions = action_histogram(successful_runs)
    plot_action_histogram(alg_counter, rot_counter, base_counter, total_actions)
