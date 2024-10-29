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
from stable_baselines3 import PPO

try:
    from nn_rl_environment import Twisty_Puzzle_Env
    from nn_rl_training import train_agent, get_action_index_to_name, setup_training
except ModuleNotFoundError:
    from .nn_rl_environment import Twisty_Puzzle_Env
    from .nn_rl_training import train_agent, get_action_index_to_name, setup_training

def test_agent(
        model: torch.nn.Module,
        env: Twisty_Puzzle_Env,
        action_index_to_name: dict[int, str],
        num_tests: int = 5,
        scramble_length: int = 5,
        deterministic: bool = True,
        exp_folder_path: str = "",
        verbosity: int = 1,
    ):
    """
    Test the given agent on the given environment with the given parameters.

    Args:
        model (torch.nn.Module): The agent to test.
        env (Twisty_Puzzle_Env): The environment to test the agent in.
        action_index_to_name (dict[int, str]): A dictionary mapping action indices to action names.
        num_tests (int): The number of tests to run.
        scramble_length (int): The length of the scrambles to test the agent on.
        deterministic (bool): Whether to use deterministic actions.
        exp_folder_path (str): The path to the experiment folder where test results will be saved.
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
            action, _ = model.predict(obs, deterministic=deterministic)
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
    # save all test results to file
    json_test_info: dict[str, str | int | list[tuple[str, str, bool, int]]] = {
        "summary": f"Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}",
        "num_tests": num_tests,
        "test_max_moves": env.max_moves,
        "deterministic": deterministic,
        "test_time": test_time_s,
        "run_info": test_run_info,
    }
    with open(log_file_path, "w") as file:
        json.dump(json_test_info, file, indent=4)
    # print results to stdout
    if verbosity:
        print(f"[{exp_identifier}] Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}. \ttesting took {test_time_s:.2f} s.")

def test_from_file(
        exp_folder_path: str,
        model_snapshot_steps: int = -1, # automatically choose highest step count model
        test_scramble_length: int = 50,
        test_max_moves: int = None, # use same as during training
        num_tests: int = 100,
        deterministic: bool = True,
    ):
    """
    load a model snapshot from the given experiment and test it with the given parameters.

    Args:
        exp_folder_path (str): The path to the experiment folder.
        model_snapshot_steps (int): The step count of the model snapshot to load. If -1, the model with the highest step count is loaded.
    """
    # load experiment configuration
    with open(os.path.join(exp_folder_path, "training_info.json"), "r") as file:
        exp_config: dict = json.load(file)
    # load puzzle from file
    puzzle_definition_path: str = os.path.join(exp_folder_path, "puzzle_definition.xml")

    if not test_max_moves:
        test_max_moves: int = exp_config["max_moves"]
        print(f"Using test_max_moves={test_max_moves} from training configuration.")
    # create environment
    solved_state, actions_dict, reward_func = setup_training(
            puzzle_name=puzzle_definition_path,
            base_actions=exp_config["base_actions"],
            reward=exp_config["reward"]
    )
    env = Twisty_Puzzle_Env(
        solved_state=solved_state,
        actions=actions_dict,
        base_actions=exp_config["base_actions"],
        max_moves=test_max_moves if test_max_moves else exp_config["max_moves"],
        initial_scramble_length=exp_config["start_scramble_depth"],
        success_threshold=exp_config["success_threshold"],
        reward_func=reward_func,
    )

    model_name: str = f"{model_snapshot_steps}_steps.zip"
    model_snapshots_folder: str = os.path.join(exp_folder_path, "model_snapshots")
    try:
        model_path = os.path.join(model_snapshots_folder, model_name)
        # load model from file
        model = PPO.load(
            model_path,
            env=env,
            device=exp_config["device"],
        )
    except FileNotFoundError:
        # load model with highest step count to continue training
        for root, _, files in os.walk(model_snapshots_folder):
            filename_stepcounts: dict[str, int] = {file: int(file.split("_")[-2]) for file in files if file.endswith(".zip")}
            if filename_stepcounts:
                model_path: str = max(filename_stepcounts, key=filename_stepcounts.get)
                model_path = os.path.join(model_snapshots_folder, model_path)
                break
        # load model from file
        model = PPO.load(
            model_path,
            env=env,
            device=exp_config["device"],
        )
    # set up actions dictionary for human-readable action logging
    action_index_to_name: dict[int, str] = get_action_index_to_name(actions_dict)
    # test the agent
    test_agent(
        model=model,
        env=env,
        action_index_to_name=action_index_to_name,
        num_tests=num_tests,
        scramble_length=test_scramble_length,
        deterministic=deterministic,
        exp_folder_path=exp_folder_path,
        verbosity=1,
    )

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
        test_max_moves: int = None,
    ) -> str:
    """
    Train a new model on a given puzzle using PPO, then test it with the given parameters.
    
    Args:
        puzzle_name (str): The name of the puzzle to train and test the agent on.
        base_actions (list[str]): The list of base actions to use for the puzzle.
        # TODO: describe training parameters

        num_tests (int): The number of random scrambles to test the agent on. Defaults to 100.
        test_scramble_length (int): The length of each test scramble. Defaults to 50.
        test_max_moves (int): The maximum number of moves the agent is allowed to take during testing. Defaults to value used in training: `max_moves`.

    Returns:
        str: The path to the experiment folder.
    """
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
    solved_state, actions_dict, reward_func = setup_training(
        puzzle_name=puzzle_name,
        base_actions=base_actions,
        reward=reward)
    action_index_to_name: dict[int, str] = get_action_index_to_name(actions_dict)
    
    
    if not test_max_moves:
        test_max_moves: int = max_moves
        print(f"Using test_max_moves={test_max_moves} from training configuration.")
    env = Twisty_Puzzle_Env(
            solved_state,
            actions_dict,
            base_actions=base_actions,
            max_moves=test_max_moves,
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
    return exp_folder_path

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
    #     max_moves=100,
    #     start_scramble_depth=24,
    #     success_threshold=0.3,
    #     last_n_episodes=1000,
    #     # reward="binary",
    #     reward="most_correct_points",
    #     # rl training parameters
    #     n_steps=20_000_000,
    #     learning_rate=0.005,
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

    # train_and_test_agent(
    #     # puzzle configuration
    #     # puzzle_name="gear_cube_extreme_sym_algs", # puzzle_name
    #     puzzle_name="gear_cube_extreme", # puzzle_name
    #     base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'"],
    #     # environment configuration
    #     load_model=None,
    #     max_moves=200,
    #     # start_scramble_depth=32,
    #     start_scramble_depth=1,
    #     success_threshold=0.25,
    #     last_n_episodes=1000,
    #     # reward="most_correct_points",
    #     reward="binary",
    #     # rl training parameters
    #     n_steps=50_000_000,
    #     learning_rate=0.001,
    #     batch_size=25000,
    #     # parallelization settings
    #     n_envs=1000,
    #     device="cuda",
    #     verbosity=1,
    #     # test configuration
    #     num_tests=250,
    #     test_scramble_length=200,
    # )
    # # tensorboard --logdir src/ai_files/gear_cube_extreme_sym_algs

    
    # train_and_test_agent(
    #     # puzzle configuration
    #     puzzle_name="cube_3x3x3_sym_algs",
    #     base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'", "M", "M'", "E", "E'", "S", "S'"],
    #     # environment configuration
    #     load_model="2024-09-28_23-37-59",
    #     max_moves=100,
    #     start_scramble_depth=16,
    #     success_threshold=0.25,
    #     last_n_episodes=1000,
    #     reward="most_correct_points",
    #     # reward="binary",
    #     # rl training parameters
    #     n_steps=200_000_000,
    #     learning_rate=0.001,
    #     batch_size=25000,
    #     # parallelization settings
    #     n_envs=1000,
    #     device="cuda",
    #     verbosity=1,
    #     # test configuration
    #     num_tests=500,
    #     test_scramble_length=100,
    # )
    # tensorboard --logdir src/ai_files/cube_3x3x3_sym_algs

    # test_from_file(
    #     # "src/ai_files/gear_cube_extreme_sym_algs/2024-09-28_13-12-56",
    #     "src/ai_files/dino_cube_plus/2024-09-20_20-24-20",
    #     model_snapshot_steps=-1,
    #     test_scramble_length=200,
    #     test_max_moves=100,
    #     num_tests=100,
    #     deterministic=False,
    # )

##############################################################################################
    train_and_test_agent(
        # puzzle configuration
        # puzzle_name="dino_cube_sym_algs",
        # base_actions=["wrg", "wrg'", "wgo", "wgo'", "yog", "yog'", "ygr", "ygr'", "wbr", "wbr'", "wob", "wob'", "yrb", "yrb'", "ybo", "ybo'"],
        # puzzle_name="skewb_sym_algs",
        # puzzle_name="skewb",
        # base_actions=["wbr", "wbr'", "wgo", "wgo'", "oyb", "oyb'", "ryg", "ryg'"],
        # puzzle_name="rubiks_ai_sym_algs",
        puzzle_name="geared_mixup_sym_algs",
        base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'"],
        # environment configuration
        # load_model=None,
        load_model="2024-10-28_05-40-25",
        max_moves=300,
        start_scramble_depth=32,
        # start_scramble_depth=2,
        success_threshold=0.25,
        last_n_episodes=1000,
        reward="most_correct_points",
        # reward="binary",
        # rl training parameters
        n_steps=700_000_000,
        learning_rate=0.001,
        batch_size=25000,
        # parallelization settings
        n_envs=1000,
        device="cuda",
        verbosity=1,
        # test configuration
        num_tests=1000,
        test_scramble_length=100,
    )
    # tensorboard --logdir src/ai_files/dino_cube_sym_algs
    # tensorboard --logdir src/ai_files/

    # test_from_file(
    #     # "src/ai_files/dino_cube_sym_algs/2024-10-21_19-56-31",
    #     # "src/ai_files/skewb_sym_algs/2024-10-21_22-23-45",
    #     # "src/ai_files/skewb/2024-10-21_22-23-39",
    #     "src/ai_files/rubiks_ai_sym_algs/2024-10-27_10-25-45",
    #     model_snapshot_steps=-1,
    #     # "src/ai_files/skewb_sym_algs/2024-10-21_21-35-49",
    #     # model_snapshot_steps=10_000_000,
    #     test_scramble_length=200,
    #     test_max_moves=200,
    #     num_tests=1000,
    #     deterministic=False,
    # )
    
    # # binary reward training
    # train_and_test_agent(
    #     # puzzle configuration
    #     # puzzle_name="gear_cube_extreme", # puzzle_name
    #     # base_actions=["F", "F'", "U", "U'", "R", "R'", "B", "B'", "L", "L'", "D", "D'"],
    #     puzzle_name="skewb_sym_algs",
    #     # puzzle_name="skewb",
    #     base_actions=["wbr", "wbr'", "wgo", "wgo'", "oyb", "oyb'", "ryg", "ryg'"],
    #     # environment configuration
    #     load_model=None,
    #     max_moves=200,
    #     start_scramble_depth=2,
    #     success_threshold=0.25,
    #     last_n_episodes=1000,
    #     reward="binary",
    #     # rl training parameters
    #     n_steps=30_000_000,
    #     learning_rate=0.003,
    #     batch_size=25000,
    #     # parallelization settings
    #     n_envs=1000,
    #     device="cuda",
    #     verbosity=1,
    #     # test configuration
    #     num_tests=250,
    #     test_scramble_length=200,
    # )
