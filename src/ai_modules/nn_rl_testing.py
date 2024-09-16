"""
This module implements the testing routine for neural network-based twisty puzzle agents using reinforcement learning.

This mainly consists of a program that lets an agent play many episodes of a twisty puzzle game and records the results (solved/ not solved, number of moves taken). We plan to extend this to include more statistics about moves used, common move combinations, use of commutators and conjugates, etc.

Author: Sebastian Jost
"""
import datetime
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
    log_file_name: str = f"test_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
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
    with open(log_file_path, "w") as file:
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
            file.write(f"Test {i+1} scramble: {env.scramble_actions}\n")
            file.write(f"Test {i+1} solve: {' '.join(action_sequence)}\n")
            file.write(f"{'Solved' if terminated else 'Failed'} after {env.move_counter} steps\n")
            # print results to stdout
            if verbosity > 1:
                print(f"Test {i+1} solve: {' '.join(action_sequence)}")
                print(f"{'Solved' if terminated else 'Failed'} after {env.move_counter} steps")
        file.write(f"Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}")
    if verbosity:
        print(f"[{exp_identifier}] Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}. \ttesting took {time.perf_counter()-start_time:.2f} s.")

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
        puzzle_name: str,
        base_actions: list[str] = None,
        load_model: str = None,
        n_steps: int = 50_000,
        start_scramble_depth: int = 1,
        success_threshold: float = 0.1,
        reward: str = "binary",
        device: str = "cuda",
        # test parameters
        num_tests: int = 100,
        test_scramble_length: int = 50,
    ):
    exp_folder_path, model, env = train_agent(
        puzzle_name=puzzle_name,
        base_actions=base_actions,
        load_model=load_model,
        n_steps=n_steps,
        start_scramble_depth=start_scramble_depth,
        success_threshold=success_threshold,
        reward=reward,
        device=device,
        
    )
    solved_state, actions_dict, reward_func = setup_training(puzzle_name, base_actions, reward)
    action_index_to_name: dict[int, str] = get_action_index_to_name(actions_dict)
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
    train_and_test_agent(
        puzzle_name="cube_2x2x2_sym_algs",
        base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'"],
        n_steps=5_000,
        start_scramble_depth=1,
        success_threshold=0.1,
        reward="binary",
        device="cuda",
        num_tests=100,
        test_scramble_length=50,
    )
