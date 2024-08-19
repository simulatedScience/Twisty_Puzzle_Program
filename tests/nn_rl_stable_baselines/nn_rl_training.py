"""
This module implements a basic training routine for training a NN to solve a twisty puzzle using Reinforcement Learning.
Here, we use stable baselines to simplify training.

observations (tuple[int]):
    state of the puzzle as a list of integers
        each int roughly represents one colored sticker of the puzzle (e.g. 0 = white, 1 = yellow, ..., 5=blue)
actions (dict[str, list[tuple[int, ...]]]):
    dictionary of actions
        key: name of the action
        value: permutation applied to the puzzle's state given in cycle notation.

        Example entry: {'U': [(0, 1, 2, 3), (4, 5, 6, 7)]} represents the action U that cyclically permutes the first 4 stickers and the next set of 4 stickers of the puzzle. All other stickers (indices >7) remain unchanged.
"""
import os
import random
import time

import numpy as np

from gymnasium import Env
from gymnasium.spaces import MultiDiscrete, Discrete
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from tqdm.auto import tqdm
# import logging

# if __name__ == "__main__":
#     from reward_functions import binary_reward, euclidean_distance_reward, correct_points_reward
# else:
#     from .reward_functions import binary_reward, euclidean_distance_reward, correct_points_reward
    
from reward_factories import binary_reward_factory, correct_points_reward_factory, most_correct_points_reward_factory

class Twisty_Puzzle_Env(Env):
    def __init__(self,
            solved_state: list[int],
            actions: dict[str, list[tuple[int, ...]]],
            base_actions: list[str] = None,
            max_moves=50,
            initial_scramble_length=1, # 1 seems to work best
            success_threshold=0.9,
            reward_func: callable = None,
            exp_identifier: str | None = None,
            ):
        super(Twisty_Puzzle_Env, self).__init__()
        self.solved_state = solved_state
        self.actions = actions
        self.base_actions: list[str] = base_actions if base_actions else list(actions.keys())
        self.max_moves: int = max_moves
        self.scramble_length: int = initial_scramble_length
        self.success_threshold: float = success_threshold
        # define reward. Default: binary reward with single solved state
        self.reward_func: callable = reward_func# if reward_func else lambda state: binary_reward(state, None, self.solved_state)
        self.early_stop: bool = False
        self.mean_success_rate: float = 0

        # calculate a unique identifier for the experiment
        if exp_identifier is None:
            self.exp_identifier = f"rew={self.reward_func.__name__}_sd={self.scramble_length}_st={self.success_threshold}"
        else:
            self.exp_identifier = exp_identifier

        self.current_step = 0
        self.episode_counter = 0
        self.last_n_episodes: int = 1000
        self.episode_success_history = np.zeros(self.last_n_episodes, dtype=bool)
        
        # Observation space: MultiDiscrete for the stickers, each can be one of the colors
        self.observation_space = MultiDiscrete([6] * len(solved_state))
        
        # Action space: Discrete, each action corresponds to a named move
        self.action_space = Discrete(len(actions))
        self.action_index_to_name = {i: name for i, name in enumerate(actions.keys())}
        self.name_to_action_index = {name: i for i, name in self.action_index_to_name.items()}
        
        # Initialize the state
        self.state = list(solved_state)

    def reset(self, seed=None, options=None, print_scramble=False):
        self.state = list(self.solved_state)
        self.current_step = 0
        self.episode_counter += 1
        # Access the monitor wrapper to get episode rewards
        if self.episode_counter%1000 == 0 and hasattr(self, 'monitor'):# and isinstance(self.env, Monitor):
            self.mean_success_rate = np.mean(self.episode_success_history)
            if self.mean_success_rate >= self.success_threshold:
                results = self.monitor.get_episode_rewards()
                # last_n_episodes = len(self.episode_success_history)  # Or any desired number of episodes
                mean_reward = np.mean(results[-self.last_n_episodes:]) if len(results) > 0 else 0
                self.scramble_length += 1
                if self.scramble_length < 25 or self.scramble_length % 25 == 0:
                    print(f"[{self.exp_identifier}] Increased scramble length to {self.scramble_length} after {self.episode_counter} episodes.")
                    print(f"[{self.exp_identifier}] Mean reward over last {self.last_n_episodes} episodes: {mean_reward:.2f}")
                    print(f"[{self.exp_identifier}] Current success rate: {self.mean_success_rate:.2%}")
        self.state = self.scramble_puzzle(self.scramble_length, print_scramble=print_scramble)
        return self.state, {}

    def scramble_puzzle(self, n, print_scramble=False):
        state = list(self.solved_state)
        if print_scramble:
            scramble = [0]*n
        for i in range(n):
            # only scramble using base actions
            action_name = random.choice(list(self.base_actions))
            if print_scramble:
                scramble[i] = action_name
            permutation = self.actions[action_name]
            state = Twisty_Puzzle_Env.apply_permutation(state, permutation)
        if print_scramble:
            print(f"Scramble: {' '.join(scramble)}")
        return state

    def step(self, action):
        action_name = self.action_index_to_name[action]
        permutation = self.actions[action_name]
        self.state = Twisty_Puzzle_Env.apply_permutation(self.state, permutation)
        
        self.current_step += 1
        
        # terminated = np.all(self.state == self.solved_state)
        truncated = self.current_step >= self.max_moves
        
        # reward = 1 if terminated else 0
        # reward, terminated = euclidean_distance_reward(self.state, action, self.solved_state)
        reward, terminated = self.reward_func(self.state)
        
        if truncated or terminated:
            self.episode_success_history[self.episode_counter % self.last_n_episodes] = terminated
        
        return self.state, reward, terminated, truncated, {}
    
    def apply_permutation(state, permutation):
        new_state = np.array(state)
        for cycle in permutation:
            if len(cycle) > 1:
                first_element = new_state[cycle[0]]
                new_state[cycle[:-1]] = new_state[cycle[1:]]
                new_state[cycle[-1]] = first_element
        return new_state

    def render(self, mode='human'):
        # Simple render function
        print(self.state)

class EarlyStopCallback(BaseCallback):
    def __init__(self, env: Twisty_Puzzle_Env, max_difficulty: int=100, verbose=0):
        super(EarlyStopCallback, self).__init__(verbose)
        self.env: Twisty_Puzzle_Env = env.unwrapped
        self.max_difficulty: int = max_difficulty

    def _on_step(self):
        if self.env.scramble_length > self.max_difficulty and self.env.last_success_rate >= 1.:
            print(f"Early stopping: Difficulty {self.env.scramble_length} > {self.max_difficulty} reached. Last success rate: {np.mean(self.env.episode_success_history):.2%}")
            return False
        return True

class ProgressBarCallback(BaseCallback):
    def __init__(self, total_timesteps):
        super().__init__()
        self.pbar = tqdm(total=total_timesteps, desc="Training Progress")
    def _on_step(self):
        self.pbar.update(self.locals["self"].num_timesteps - self.pbar.n)
        # self.pbar.set_postfix(
        #     time_elapsed=self.num_timesteps,  # or calculate a more accurate time remaining
        # )
        return True

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
    solved_state: np.ndarray[int] = np.array([colors.index(color) for color in point_colors])
    return solved_state, moves_dict


def test_agent(
        model,
        env: Twisty_Puzzle_Env,
        num_tests: int = 5,
        scramble_length: int = 5,
        id: str = "",
        verbose: bool | None =None,
    ):
    if verbose is None:
        verbose = num_tests <= 5
    start_time = time.perf_counter()
    print(f"[{id}] Testing agent on {num_tests} scrambles of length {scramble_length}...")
    env.scramble_length = scramble_length
    success_count: int = 0
    for i in range(num_tests):
        obs, _ = env.reset(print_scramble=verbose)
        done = False
        action_sequence = []
        while not done:
            action, _ = model.predict(obs, deterministic=False)
            obs, _, terminated, truncated, _ = env.step(int(action))
            done = terminated or truncated
            action_sequence.append(env.action_index_to_name[int(action)])
        success_count += int(terminated)
        if verbose:
            print(f"Test {i+1} solve: {' '.join(action_sequence)}")
            print(f"{'Solved' if terminated else 'Failed'} after {env.current_step} steps")
    print(f"[{id}] Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}. \ttesting took {time.perf_counter()-start_time:.2f} s.")

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

def main(
        puzzle_name: str = "rubiks_2x2_ai",
        base_actions: list[str] = None,
        load_model: str = None,
        train_new: bool = False,
        n_episodes: int = 20_000,
        model_folder: str = "models",
        tb_log_folder: str = "tb_logs",
        start_scramble_depth: int = 1,
        success_threshold: float = 0.9,
        reward: str = "binary",
    ):
    # exp_name = f"{puzzle_name}_model"
    exp_identifier = f"{puzzle_name}_rew={reward}_sd={start_scramble_depth}_st={success_threshold}_eps={n_episodes}"
    solved_state, actions_dict = load_puzzle(puzzle_name)
    # check for whole puzzle rotation moves
    _, rotations, algorithms = filter_actions(actions_dict, base_actions, rotations_prefix="rot_")
    # calculate rotations of the solved state
    solved_states = [solved_state] + [Twisty_Puzzle_Env.apply_permutation(solved_state.copy(), actions_dict[rotation]) for rotation in rotations]
    # define reward function
    if reward == "binary":
        reward_func = binary_reward_factory(solved_state)
    elif reward == "correct_points":
        reward_func = correct_points_reward_factory(solved_state)
    elif reward == "most_correct_points":
        reward_func = most_correct_points_reward_factory(solved_states)
    else:
        raise ValueError(f"Unknown reward function: {reward}. Expected one of ('binary', 'correct_points', 'most_correct_points').")
    
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
    model_path = os.path.join(model_folder, f"{exp_identifier}.zip")
    if load_model:
        model_path = os.path.join(model_folder, load_model)
        model = PPO.load(
            model_path,
            env,
            device="cpu",
        )
        # print(model.policy)
    elif not train_new and os.path.exists(model_path):
        print("Loading existing model...")
        model = PPO.load(
            model_path,
            device="cpu"
        )
    else:
        print("Training new model...")
        model = PPO(
            "MlpPolicy",
            monitor_env,
            verbose=0,
            device="cpu",
            tensorboard_log=f"{tb_log_folder}/{exp_identifier}",
        )
        # print(model.policy)
    # exp_identifier = f"{exp_name}_eps={n_episodes}"
    if n_episodes > 0:
        # callback = ProgressBarCallback(total_timesteps=n_episodes)
        # # Disable Stable Baselines3 Logging
        # logging.getLogger("stable_baselines3").setLevel(logging.WARNING)
        checkpoint_callback = CheckpointCallback(
            save_freq=250_000,
            save_path=os.path.join(model_folder, exp_identifier),
            name_prefix=f"{exp_identifier}",
        )
        early_stopping_callback = EarlyStopCallback(
            monitor_env,
            max_difficulty=100, # Early Stopping at scramble depth 100
        )
        model.learn(
            total_timesteps=n_episodes,
            reset_num_timesteps=False,
            tb_log_name=f"{exp_identifier}_{n_episodes}_{env.scramble_length}",
            callback=[checkpoint_callback, early_stopping_callback],
            # progress_bar=True,
            # log_interval=5000,
        )
    os.makedirs(model_folder, exist_ok=True)
    if n_episodes > 0:
        if load_model:
            n_prev_episodes = int(load_model.split("_")[-1].split(".")[0])
            n_episodes += n_prev_episodes
        save_path: str = os.path.join(model_folder, f"{exp_identifier}.zip")
        model.save(save_path)
        print(f"="*75 + f"\nSaved final model to {save_path}")
    print(f"Testing agent {exp_identifier}...")
    test_agent(model, env, num_tests=10, scramble_length=50, id=f"{exp_identifier}", verbose=None)


if __name__ == "__main__":
    # main(
    #     # load_model="rubiks_2x2_ai_model_600000.zip",
    #     # train_new=True,
    # )
    # ===============================
    # test various success thresholds with multiprocessing
    # ===============================
    import multiprocessing as mp
    # # success_thresholds = [.1, .3, .5, .7, .8, .9, .95, 1.]
    # success_thresholds = [.9]
    # scramble_depths = [1, 4, 8]
    # rewards = ["binary", "most_correct_points"]
    # n_processes = 6
    # kwargs_list  = [
    #         (
    #         "skewb_sym_half", # puzzle_name
    #         ["wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"],            # base_actions
    #         None,            # load_model
    #         # f"skewb_sym_half_binary_st={threshold}_1_10000000.zip",            # load_model
    #         # f"skewb_pyramid_binary_st={threshold}_1_5000000",            # load_model
    #         True,            # train_new
    #         1_000_000,      # n_episodes
    #         "piece_reward_models", # model_folder
    #         "piece_reward_tb_logs", # tb_log_folder
    #         scramble_depth,               # start_scramble_depth
    #         threshold,       # success_threshold
    #         reward, # rewards
    #     ) for threshold in success_thresholds
    #         for scramble_depth in scramble_depths
    #             for reward in rewards
    #     ]
    # # kwargs_list  = [
    # #         (
    # #         "skewb_sym_half", # puzzle_name
    # #         ["wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"],            # base_actions
    # #         None,            # load_model
    # #         # f"skewb_sym_half_binary_st={threshold}_1_10000000.zip",            # load_model
    # #         # f"skewb_pyramid_binary_st={threshold}_1_5000000",            # load_model
    # #         True,            # train_new
    # #         1_000_000,      # n_episodes
    # #         [1, 4, 8],               # start_scramble_depth
    # #         threshold,       # success_threshold
    # #         "most_correct_points", # reward
    # #     ) for threshold in success_thresholds
    # #     ]
    # with mp.Pool(n_processes) as pool:
    #     pool.starmap(main, kwargs_list)
    # ===============================
    # success_thresholds = [.9]
    # scramble_depths_rewards = [
    #     (1, "binary"),
    #     (1, "most_correct_points"),
    #     (4, "most_correct_points"),
    #     (8, "most_correct_points"),
    # ]
    # n_processes = 4
    # kwargs_list  = [
    #         (
    #         "rubiks_2x2_sym", # puzzle_name
    #         # "rubiks_algs", # puzzle_name
    #         ["f", "f'", "r", "r'", "t", "t'", "b", "b'", "l", "l'", "d", "d'"], # base_actions
    #         None,            # load_model
    #         True,            # train_new
    #         2_000_000,       # n_episodes
    #         "rubiks_2x2_models",  # model_folder
    #         "rubiks_2x2_tb_logs", # tb_log_folder
    #         # "rubiks_3x3_models",  # model_folder
    #         # "rubiks_3x3_tb_logs", # tb_log_folder
    #         scramble_depth,  # start_scramble_depth
    #         threshold,       # success_threshold
    #         reward,          # reward
    #     ) for threshold in success_thresholds
    #         for scramble_depth, reward in scramble_depths_rewards
    #     ]
    # with mp.Pool(n_processes) as pool:
    #     pool.starmap(main, kwargs_list)
    # ===============================
    # main(
    #     puzzle_name="rubiks_2x2",
    #     base_actions=["f", "f'", "r", "r'", "t", "t'", "b", "b'", "l", "l'", "d", "d'"],
    #     start_scramble_depth=1,
    #     load_model=None,
    #     train_new=True,
    #     n_episodes=20_000_000,
    # )
    # main(
    #     puzzle_name="skewb_sym_half",
    #     base_actions=["wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"],
    #     load_model=None,
    #     start_scramble_depth=8,
    #     # load_model="skewb_sym_model_500000.zip",
    #     # load_model="skewb_sym_half_model_1500000.zip",
    #     train_new=True,
    #     n_episodes=500_000,
    #     # n_episodes=1_500_000,
    #     model_folder="piece_reward_models",
    #     tb_log_folder="piece_reward_tb_logs",
    #     reward="most_correct_points",
    # )
    # import multiprocessing as mp
    # success_thresholds = [.1, .95]
    # puzzle_names = ["square_two", "square_two_algs"]
    # kwargs_list  = [
    #         (
    #         puzzle_name, # puzzle_name
    #         ["s", "t", "t'", "b", "b'"],            # base_actions
    #         f"{puzzle_name}_binary_st={threshold}_1_50000000/{puzzle_name}_binary_st={threshold}_1_59250000_steps.zip",            # load_model
    #         # None,            # load_model
    #         False,            # train_new
    #         0,         # n_episodes
    #         1,               # start_scramble_depth
    #         threshold,       # success_threshold
    #     ) for threshold in success_thresholds for puzzle_name in puzzle_names
    # ]
    # with mp.Pool(2) as pool:
    #     pool.starmap(main, kwargs_list)
    # main(
    #     puzzle_name="square_two_algs",
    #     base_actions=["s", "t", "t'", "b", "b'"],
    #     load_model=None,
    #     start_scramble_depth=1,
    #     # load_model="skewb_sym_model_500000.zip",
    #     # load_model="skewb_sym_half_model_1500000.zip",
    #     train_new=True,
    #     n_episodes=80_000_000,
    #     success_threshold=0.95
    # )
    # In terminal, run "tensorboard --logdir tb_logs/..." to view training progress

    # ===============================
    # success_thresholds = [.1]
    # scramble_depths_rewards = [
    #     (1, "binary"),
    #     (1, "most_correct_points"),
    #     (4, "most_correct_points"),
    #     (8, "most_correct_points"),
    # ]
    # n_processes = 4
    # kwargs_list  = [
    #         (
    #         "cuboid_3x2x2_algs", # puzzle_name
    #         ["L", "L'", "R", "R'", "F", "B", "D", "U"], # base_actions
    #         None,            # load_model
    #         True,            # train_new
    #         500_000,       # n_episodes
    #         "cuboid_3x2x2_models",  # model_folder
    #         "cuboid_3x2x2_tb_logs", # tb_log_folder
    #         scramble_depth,  # start_scramble_depth
    #         threshold,       # success_threshold
    #         reward,          # reward
    #     ) for threshold in success_thresholds
    #         for scramble_depth, reward in scramble_depths_rewards
    #     ]
    # with mp.Pool(n_processes) as pool:
    #     pool.starmap(main, kwargs_list)
    # In terminal, run "tensorboard --logdir cuboid_3x2x2_tb_logs" to view training progress
    # ===============================
    success_thresholds = [.3]
    # scramble_depths_rewards = [
    #     (1, "binary"),
    #     (1, "most_correct_points"),
    #     (4, "most_correct_points"),
    #     (8, "most_correct_points"),
    # ]
    scramble_depths_rewards = [
        (1, "binary"),
        (8, "most_correct_points"),
        (16, "most_correct_points"),
        (32, "most_correct_points"),
    ]
    n_processes = 4
    kwargs_list  = [
            (
            "cuboid_3x3x2_sym_algs", # puzzle_name
            ["L", "R", "F", "B", "D", "D'", "U", "U'", "M", "S"], # base_actions
            None,            # load_model
            True,            # train_new
            11_000_000,       # n_episodes
            "cuboid_3x3x2_models",  # model_folder
            "cuboid_3x3x2_tb_logs", # tb_log_folder
            scramble_depth,  # start_scramble_depth
            threshold,       # success_threshold
            reward,          # reward
        ) for threshold in success_thresholds
            for scramble_depth, reward in scramble_depths_rewards
        ]
    with mp.Pool(n_processes) as pool:
        pool.starmap(main, kwargs_list)
    # In terminal, run "tensorboard --logdir cuboid_3x3x2_tb_logs" to view training progress