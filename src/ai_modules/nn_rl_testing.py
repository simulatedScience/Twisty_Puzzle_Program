"""
This module implements the testing routine for neural network-based twisty puzzle agents using reinforcement learning.

This mainly consists of a program that lets an agent play many episodes of a twisty puzzle game and records the results (solved/ not solved, number of moves taken). We plan to extend this to include more statistics about moves used, common move combinations, use of commutators and conjugates, etc.

Author: Sebastian Jost
"""
import datetime
import json
import os
import time

import torch

from nn_rl_environment import Twisty_Puzzle_Env
from nn_rl_training import train_agent, get_action_index_to_name, setup_training

def test_agent(
        model: torch.nn.Module,
        env: Twisty_Puzzle_Env,
        action_index_to_name: dict[int, str],
        num_tests: int = 5,
        scramble_length: int = 5,
        exp_folder_path: str = "",
        verbosity: int = 1,
    ):
    """
    Test the given agent on the given environment with the given parameters.

    Args:
        model (torch.nn.Module): The agent to test.
        env (Twisty_Puzzle_Env): The environment to test the agent in.
        action_index_to_name (dict[int, str]): A dictionary mapping action indices to action names.
        log_file_path (str): The path to the log file to write the results to.
        num_tests (int): The number of tests to run.
        scramble_length (int): The length of the scrambles to test the agent on.
        id (str): An identifier for the test run.
        verbose (bool | None): Whether to print the results to stdout. If None, the results are printed if num_tests <= 5.
    """
    tests_folder: str = os.path.join(exp_folder_path, "tests")
    os.makedirs(tests_folder, exist_ok=True)
    log_file_name: str = f"test_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    log_file_path: str = os.path.join(tests_folder, log_file_name)
    exp_identifier: str = os.path.basename(exp_folder_path)

    if verbosity > 0:
        print(f"Testing agent {exp_folder_path}...")
    if verbosity is None:
        verbosity = num_tests <= 5
    start_time = time.perf_counter()
    if verbosity:
        print(f"[{exp_identifier}] Testing agent on {num_tests} scrambles of length {scramble_length}...")
    env.scramble_length = scramble_length
    success_count: int = 0
    test_run_info: list[tuple[str, str, bool, int]] = []
    # with open(log_file_path, "w") as file:
    for i in range(num_tests):
        obs, _ = env.reset()
        done = False
        action_sequence = []
        while not done:
            action, _ = model.predict(obs, deterministic=False)
            obs, _, terminated, truncated, _ = env.step(int(action))
            done = terminated or truncated
            action_sequence.append(action_index_to_name[int(action)])
        success_count += int(terminated)
        # log scramble, solve and result to file
        # use JSON format instead: store tuples (scramble, solve, success, move_count)
        test_run_info.append(
            {
                "scramble": ' '.join([action_index_to_name[action] for action in env.scramble_action_indices]), # scramble sequence
                "agent_moves:": ' '.join(action_sequence), # solve sequence
                "success": bool(terminated), # success
                "n_moves": int(env.move_counter), # move count
            }
        )
        # print results to stdout
        if verbosity > 1:
            print(f"Test {i+1} solve: {' '.join(action_sequence)}")
            print(f"{'Solved' if terminated else 'Failed'} after {env.move_counter} steps")
    test_time_s: int = time.perf_counter()-start_time
    json_test_info: dict[str, str | int | list[tuple[str, str, bool, int]]] = {
        "summary": f"Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}",
        "num_tests": num_tests,
        "run_info": test_run_info,
        "test_time": test_time_s,
    }
    
    with open(log_file_path, "w") as file:
        json.dump(json_test_info, file, indent=4)
    if verbosity:
        print(f"[{exp_identifier}] Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}. \ttesting took {test_time_s:.2f} s.")

# def test_from_file(
#         exp_folder_path: str,
#         model_snapshot_steps: int = -1, # automatically choose highest step count model
#     ):
#     """
#     load a model snapshot from the given experiment and test it with the given parameters.

#     Args:
#         exp_folder_path (str): The path to the experiment folder.
#         model_snapshot_steps (int): The step count of the model snapshot to load. If -1, the model with the highest step count is loaded.
#     """
#     model_name: str = f"{model_snapshot_steps}_steps.zip"
#     try:
#         model_path = os.path.join(exp_folder_path, "model_snapshots", model_name)
#         model = PPO.load(
#             model_path,
#             env=env,
#             device=device)
#     except FileNotFoundError:
#         # load model with highest step count to continue training
#         for root, _, files in os.walk(model_snapshots_folder):
#             filename_stepcounts: dict[str, int] = {file: int(file.split("_")[0]) for file in files if file.endswith(".zip")}
#             if filename_stepcounts:
#                 model_path = max(filename_stepcounts, key=filename_stepcounts.get)
#                 break
#     # test_agent(...) # TODO

def train_and_test_agent(
        # puzzle configuration
        puzzle_name: str,
        base_actions: list[str] = None,
        # environment configuration
        load_model: str = None,
        max_moves: int = 50,
        start_scramble_depth: int = 1,
        success_threshold: float = 0.1,
        last_n_episodes: int = 1000,
        reward: str = "binary",
        # rl training parameters
        n_steps: int = 50_000,
        batch_size: int = 1000,
        learning_rate: float = 0.0003,
        # parallelization settings
        n_envs: int = 3000,
        device: str = "cuda",
        verbosity: int = 1,
        # test parameters
        num_tests: int = 100,
        test_scramble_length: int = 50,
    ):
    exp_folder_path, model, vec_env = train_agent(
        # puzzle configuration
        puzzle_name=puzzle_name,
        base_actions=base_actions,
        # environment configuration
        load_model=load_model,
        max_moves=max_moves,
        start_scramble_depth=start_scramble_depth,
        success_threshold=success_threshold,
        last_n_episodes=last_n_episodes,
        reward=reward,
        # rl training parameters
        n_steps=n_steps,
        batch_size=batch_size,
        learning_rate=learning_rate,
        # parallelization settings
        n_envs=n_envs,
        device=device,
        verbosity=0,
    )
    solved_state, actions_dict, reward_func = setup_training(puzzle_name, base_actions, reward)
    action_index_to_name: dict[int, str] = get_action_index_to_name(actions_dict)
    
    
    env = Twisty_Puzzle_Env(
            solved_state,
            actions_dict,
            base_actions=base_actions,
            initial_scramble_length=start_scramble_depth,
            success_threshold=success_threshold,
            reward_func=reward_func,
    )
    
    test_agent(
        model=model,
        env=env,
        action_index_to_name=action_index_to_name,
        num_tests=num_tests,
        scramble_length=test_scramble_length,
        exp_folder_path=exp_folder_path,
        verbosity=1,
    )

if __name__ == "__main__":
#     train_and_test_agent(
#         # puzzle configuration
#         puzzle_name="cube_2x2x2_sym_algs",
#         base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'"],
#         # environment configuration
#         load_model=None,
#         max_moves=50,
#         start_scramble_depth=12,
#         success_threshold=0.1,
#         last_n_episodes=1000,
#         reward="sparse_most_correct_points",
#         # reward="binary",
#         # rl training parameters
#         n_steps=20_000_000,
#         learning_rate=0.001,
#         batch_size=50000,
#         # parallelization settings
#         n_envs=1000,
#         device="cuda",
#         verbosity=1,
#         # test configuration
#         num_tests=100,
#         test_scramble_length=50,
#     )
# # tensorboard --logdir src/ai_files/cube_2x2x2

    # train_and_test_agent(
    #     # puzzle configuration
    #     puzzle_name="cuboid_3x3x2_sym_algs2",
    #     base_actions=["L", "R", "F", "B", "D", "D'", "U", "U'", "M", "S"],
    #     # environment configuration
    #     load_model=None,
    #     max_moves=50,
    #     start_scramble_depth=6,
    #     success_threshold=0.2,
    #     last_n_episodes=1000,
    #     reward="most_correct_points",
    #     # reward="binary",
    #     # rl training parameters
    #     n_steps=20_000_000,
    #     learning_rate=0.002,
    #     batch_size=10000,
    #     # parallelization settings
    #     n_envs=1000,
    #     device="cuda",
    #     verbosity=1,
    #     # test configuration
    #     num_tests=100,
    #     test_scramble_length=50,
    # )
    # # tensorboard --logdir src/ai_files/cuboid_3x3x2


    # train_and_test_agent(
    #     # puzzle configuration
    #     # puzzle_name="dino_cube_plus", # puzzle_name
    #     puzzle_name="dino_cube_plus_sym_algs", # puzzle_name
    #     base_actions=["wob", "wob'", "wbr", "wbr'", "wrg", "wrg'", "wgo", "wgo'", "yrb", "yrb'", "ybo", "ybo'", "yog", "yog'", "ygr", "ygr'"], # base_actions
    #     # environment configuration
    #     load_model=None,
    #     max_moves=50,
    #     start_scramble_depth=16,
    #     success_threshold=0.2,
    #     last_n_episodes=1000,
    #     # reward="binary",
    #     reward="most_correct_points",
    #     # rl training parameters
    #     n_steps=20_000_000,
    #     learning_rate=0.001,
    #     batch_size=25000,
    #     # parallelization settings
    #     n_envs=1000,
    #     device="cuda",
    #     verbosity=1,
    #     # test configuration
    #     num_tests=100,
    #     test_scramble_length=50,
    # )
    # # tensorboard --logdir src/ai_files/dino_cube_plus_sym_algs

    train_and_test_agent(
        # puzzle configuration
        puzzle_name="gear_cube_extreme_sym_algs", # puzzle_name
        # puzzle_name="gear_cube_extreme", # puzzle_name
        base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'"],
        # environment configuration
        load_model=None,
        max_moves=50,
        start_scramble_depth=16,
        # start_scramble_depth=1,
        success_threshold=0.2,
        last_n_episodes=1000,
        reward="most_correct_points",
        # reward="binary",
        # rl training parameters
        n_steps=100_000_000,
        learning_rate=0.001,
        batch_size=25000,
        # parallelization settings
        n_envs=1000,
        device="cuda",
        verbosity=1,
        # test configuration
        num_tests=200,
        test_scramble_length=100,
    )
    # tensorboard --logdir src/ai_files/gear_cube_extreme_sym_algs
