"""
Let the user choose a test file, then analyse all successful episodes in it to create a histogram of actions used by the agents. Actions are grouped by category (algorithms, rotations, base moves) and displayed as a bar plot. An additional pie chart shows the relative frequency of each category.
"""

from collections import Counter

import matplotlib.pyplot as plt

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
        return int(action.split('_')[-1].strip("'"))
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
    # add_pie_chart(
    #     data=pie_data, colors)
    
    # Calculate relative frequencies (as percentages)
    counts_percentage = [(count / total_actions) * 100 for count in counts]
    
    # Assign colors from the color_list
    colors = [color_list[0]] * len(sorted_alg) + [color_list[1]] * len(sorted_rot) + [color_list[2]] * len(sorted_base)
    
    # Create the bar plot
    plt.figure(figsize=(12, 6))
    label_actions = [f"{action}" for action in actions]
    bars = plt.bar(label_actions, counts_percentage, color=colors)
    # Add text labels on top of each bar
    for bar in bars:
        yval = bar.get_height()  # Get the height of the bar (which is the value)
        plt.text(bar.get_x() + bar.get_width()/2, yval, f'{yval:.1f}%', 
                ha='center', va='bottom', fontsize=10, color='black')

    # Adding gridlines with color #ddd
    plt.grid(True, axis='y', color='#ddd')
    
    # Labeling and title
    plt.xlabel("Actions")
    plt.ylabel("Relative Frequency (%)")
    plt.title("Histogram of Actions by Category (Relative Frequency)")
    plt.xticks(rotation=90)  # Rotate action labels for better visibility
    
    # Adding legend
    plt.legend([bars[0], bars[len(sorted_alg)], bars[len(sorted_alg) + len(sorted_rot)]], 
               ['Algorithms (alg_)', 'Rotations (rot_)', 'Base Moves'], loc='upper right')

    plt.tight_layout()
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
