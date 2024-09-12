"""
This module implements the training routine for neural network-based twisty puzzle agents using reinforcement learning.
"""
import datetime
import json
import os

import torch
from stable_baselines3.common.monitor import Monitor 
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3 import PPO 

from nn_rl_environment import Twisty_Puzzle_Env, EarlyStopCallback
from src.ai_modules.nn_rl_reward_factories import binary_reward_factory, correct_points_reward_factory, most_correct_points_reward_factory, sparse_most_correct_points_reward_factory

def train_agent(
        puzzle_name: str,
        base_actions: list[str] = None,
        load_model: str = None,
        n_steps: int = 20_000,
        start_scramble_depth: int = 1,
        success_threshold: float = 0.9,
        reward: str = "binary",
        device: str = "cuda",
    ) -> tuple[str, torch.nn.Module]:
    # experiment folder named as yyyy-mm-dd_hh-mm-ss
    exp_folder: str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    exp_folder_path: str = os.path.join("ai_files", puzzle_name, exp_folder)
    model_snapshots_folder: str = os.path.join(exp_folder_path, "model_snapshots")
    tb_log_folder: str = os.path.join(exp_folder_path, "tb_logs")
    os.makedirs(exp_folder_path, exist_ok=True)

    solved_state, actions_dict, reward_func = setup_training(puzzle_name, base_actions, reward)

    exp_identifier = f"{puzzle_name}_rew={reward}_sd={start_scramble_depth}_st={success_threshold}_eps={n_steps}"
    env = Twisty_Puzzle_Env(
            solved_state,
            actions_dict,
            base_actions=base_actions,
            initial_scramble_length=start_scramble_depth,
            success_threshold=success_threshold,
            reward_func=reward_func,
            exp_identifier=exp_identifier,
    )
    # env.scramble_length = start_scramble_depth
    monitor_env = Monitor(env)
    env.monitor = monitor_env
    # env
    if load_model:
        # load model with highest step count to continue training
        for root, _, files in os.walk(model_snapshots_folder):
            filename_stepcounts: dict[str, int] = {file: int(file.split("_")[0]) for file in files if file.endswith(".zip")}
            if filename_stepcounts:
                model_path = max(filename_stepcounts, key=filename_stepcounts.get)
                break
        print(f"Loading model from {model_path}...")
        model = PPO.load(
            model_path,
            env=monitor_env,
            device=device)
    else:
        print("Training new model...")
        model = PPO(
            "MlpPolicy",
            monitor_env,
            verbose=1,
            device=device,
            tensorboard_log=tb_log_folder,
        )
        # print(model.policy)
    # exp_identifier = f"{exp_name}_eps={n_episodes}"
    if n_steps > 0:
        # callback = ProgressBarCallback(total_timesteps=n_episodes)
        # # Disable Stable Baselines3 Logging
        # logging.getLogger("stable_baselines3").setLevel(logging.WARNING)
        checkpoint_callback = CheckpointCallback(
            save_freq=250_000,
            save_path=model_snapshots_folder,
            name_prefix=""
        )
        early_stopping_callback = EarlyStopCallback(
            monitor_env,
            max_difficulty=100, # Early Stopping at scramble depth 100
        )
        # save training info
        save_training_info(
            exp_folder_path,
            puzzle_name=puzzle_name,
            base_actions=base_actions,
            reward=reward,
            n_steps=n_steps,
            start_scramble_depth=start_scramble_depth,
            success_threshold=success_threshold,
            device=device,
        )
        # train model
        model.learn(
            total_timesteps=n_steps,
            reset_num_timesteps=False,
            tb_log_name=f"{exp_identifier}_{n_steps}_{env.scramble_length}",
            callback=[checkpoint_callback, early_stopping_callback],
            # progress_bar=True,
            # log_interval=5000,
        )
        if load_model:
            n_prev_episodes = int(load_model.split("_")[-1].split(".")[0])
            n_steps += n_prev_episodes
        save_path: str = os.path.join(model_snapshots_folder, f"{n_steps}_steps.zip")
        model.save(save_path)
        print(f"="*75 + f"\nSaved final model to {save_path}")

    return exp_folder_path, model, env

# def get_exp_name(
#         puzzle_name: str,
#         reward: str = "binary",
#         n_steps: int = 20_000,
#         start_scramble_depth: int = 1,
#         success_threshold: float = 0.9,
#     ) -> str:
#     exp_identifier = f"{puzzle_name}_rew={reward}_sd={start_scramble_depth}_st={success_threshold}_eps={n_steps}"
#     return exp_identifier

def save_training_info(
        exp_folder_path: str,
        **kwargs,
    ):
    """
    Save all information relevant to the training run to a file in the given experiment folder.

    Args:
        exp_folder_path (str): path to the experiment folder
    """
    with open(os.path.join(exp_folder_path, "training_info.json"), "w") as file:
        json.dump(kwargs, file, indent=4)

def load_puzzle(puzzle_name: str):
    """
    Load solved state and actions from puzzle definition file
    
    Args:
        puzzle_name (str): name of the puzzle
        
    Returns:
        list[int]: solved state of the puzzle
        dict[str, list[tuple[int, ...]]]: dictionary of actions (name -> permutation in cycle notation)
    """
    try:
        from src.interaction_modules.load_from_xml import load_puzzle as load_xml_puzzle
    except ImportError:
        import sys
        import os
        # Get the absolute path to the project's root directory (A)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
        # Add the project root and the C directory to the Python path
        sys.path.insert(0, project_root)
        from src.interaction_modules.load_from_xml import load_puzzle as load_xml_puzzle
    try:
        point_dicts, moves_dict, state_space_size = load_xml_puzzle(puzzle_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the puzzle '{puzzle_name}'.")
    # convert point colors to solved state for the environment
    # point_dicts: list[dict[str, tuple[vpy.vector, vpy.vector, float]]]
    #     list includes position, color and size (for visualization) of each point
    #     convert to color index for each point
    point_colors = [point["vpy_color"] for point in point_dicts]
    point_colors = [(color.x, color.y, color.z) for color in point_colors]
    colors = list(set(point_colors))
    solved_state: list[int] = [colors.index(color) for color in point_colors]
    return solved_state, moves_dict

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

def setup_training(
        puzzle_name: str,
        base_actions: list[str] = None,
        reward: str = "binary",
    ):
    solved_state, actions_dict = load_puzzle(puzzle_name)
    # check for whole puzzle rotation moves
    _, rotations, algorithms = filter_actions(actions_dict, base_actions, rotations_prefix="rot_")
    # calculate rotations of the solved state
    solved_states: torch.Tensor = [solved_state] + [Twisty_Puzzle_Env.apply_permutation(solved_state.copy(), actions_dict[rotation]) for rotation in rotations]
    # define reward function
    if reward == "binary":
        reward_func = binary_reward_factory(solved_state)
    elif reward == "correct_points":
        reward_func = correct_points_reward_factory(solved_state)
    elif reward == "most_correct_points":
        reward_func = most_correct_points_reward_factory(solved_states)
    elif reward == "sparse_most_correct_points":
        reward_func = sparse_most_correct_points_reward_factory(solved_states)
    else:
        raise ValueError(f"Unknown reward function: {reward}. Expected one of ('binary', 'correct_points', 'most_correct_points').")
    return solved_state, actions_dict, reward_func

def get_action_index_to_name(
        actions_dict: dict[str, list[list[int]]],
    ) -> dict[int, str]:
    """
    Create a mapping from action indices to action names.

    Args:
        actions_dict (dict[str, list[list[int]]]): Puzzle actions defined by name and permutation in cyclic form.

    Returns:
        dict[int, str]: A dictionary mapping action indices to their names. Indices are assigned by sorting the action names.
    """
    # IMPORTANT: this conversion must be the consistent with the one in nn_rl_environment.puzzle_info_to_torch!
    action_index_to_name = {
        i: name for i, name in enumerate(sorted(actions_dict.keys()))
    }
    return action_index_to_name
