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

from reward_functions import binary_reward, euclidean_distance_reward

class Twisty_Puzzle_Env(Env):
    def __init__(self,
            solved_state: list[int],
            actions: dict[str, list[tuple[int, ...]]],
            base_actions: list[str] = None,
            max_moves=50,
            initial_scramble_length=1, # 1 seems to work best
            success_threshold=0.9,
            ):
        super(Twisty_Puzzle_Env, self).__init__()
        self.solved_state = solved_state
        self.actions = actions
        self.base_actions: list[str] = base_actions if base_actions else list(actions.keys())
        self.max_moves: int = max_moves
        self.scramble_length: int = initial_scramble_length
        self.success_threshold: float = success_threshold

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
            mean_success_rate = np.mean(self.episode_success_history)
            if mean_success_rate >= self.success_threshold:
                results = self.monitor.get_episode_rewards()
                # last_n_episodes = len(self.episode_success_history)  # Or any desired number of episodes
                mean_reward = np.mean(results[-self.last_n_episodes:]) if len(results) > 0 else 0
                self.scramble_length += 1
                if self.scramble_length < 25 or self.scramble_length % 25 == 0:
                    print(f"[st={self.success_threshold}] Increased scramble length to {self.scramble_length} after {self.episode_counter} episodes.")
                    print(f"[st={self.success_threshold}] Mean reward over last {self.last_n_episodes} episodes: {mean_reward:.2f}")
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
            state = self.apply_permutation(state, permutation)
        if print_scramble:
            print(f"Scramble: {' '.join(scramble)}")
        return state

    def step(self, action):
        action_name = self.action_index_to_name[action]
        permutation = self.actions[action_name]
        self.state = self.apply_permutation(self.state, permutation)
        
        self.current_step += 1
        
        # terminated = np.all(self.state == self.solved_state)
        truncated = self.current_step >= self.max_moves
        
        # reward = 1 if terminated else 0
        # reward, terminated = euclidean_distance_reward(self.state, action, self.solved_state)
        reward, terminated = binary_reward(self.state, action, self.solved_state)
        
        if truncated or terminated:
            self.episode_success_history[self.episode_counter % self.last_n_episodes] = terminated
        
        return self.state, reward, terminated, truncated, {}
    
    def apply_permutation(self, state, permutation):
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

class EvalCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(EvalCallback, self).__init__(verbose)

    def _on_step(self):
        self.training_env.ep_rew_mean = np.mean(self.locals.get("episode_rewards", []))
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
        from src.interaction_modules.load_from_xml import load_puzzle
    except ImportError:
        import sys
        import os
        # Get the absolute path to the project's root directory (A)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
        # Add the project root and the C directory to the Python path
        sys.path.insert(0, project_root)
        from src.interaction_modules.load_from_xml import load_puzzle
    try:
        point_dicts, moves_dict, state_space_size = load_puzzle(puzzle_name)
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
        id="",
    ):
    start_time = time.perf_counter()
    print(f"[{id}] Testing agent on {num_tests} scrambles of length {scramble_length}...")
    env.scramble_length = scramble_length
    success_count: int = 0
    for i in range(num_tests):
        obs, _ = env.reset(print_scramble=True)
        done = False
        action_sequence = []
        while not done:
            action, _ = model.predict(obs, deterministic=False)
            obs, _, terminated, truncated, _ = env.step(int(action))
            done = terminated or truncated
            action_sequence.append(env.action_index_to_name[int(action)])
        success_count += int(terminated)
        print(f"Test {i+1} solve: {' '.join(action_sequence)}")
        print(f"{'Solved' if terminated else 'Failed'} after {env.current_step} steps")
    print(f"[{id}] Success rate: {success_count}/{num_tests} = {success_count/num_tests:.1%}. \ttesting took {time.perf_counter()-start_time:.2f} s.")

def main(
        puzzle_name: str = "rubiks_2x2_ai",
        base_actions: list[str] = None,
        load_model: str = None,
        train_new: bool = False,
        n_episodes: int = 20_000,
        start_scramble_depth: int = 1,
        success_threshold: float = 0.9,
    ):
    # exp_name = f"{puzzle_name}_model"
    exp_name = f"{puzzle_name}_binary_st={success_threshold}"
    solved_state, actions_dict = load_puzzle(puzzle_name)
    env = Twisty_Puzzle_Env(
            solved_state,
            actions_dict,
            base_actions=base_actions,
            initial_scramble_length=start_scramble_depth,
            success_threshold=success_threshold,)
    # env.scramble_length = start_scramble_depth
    monitor_env = Monitor(env)
    env.monitor = monitor_env
    # env
    model_path = os.path.join("models", f"{exp_name}.zip")
    if load_model:
        model_path = os.path.join("models", load_model)
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
            tensorboard_log=f"tb_logs/{exp_name}",
        )
        # print(model.policy)
    exp_identifier = f"{exp_name}_{start_scramble_depth}_{n_episodes}"
    if n_episodes > 0:
        # callback = ProgressBarCallback(total_timesteps=n_episodes)
        # # Disable Stable Baselines3 Logging
        # logging.getLogger("stable_baselines3").setLevel(logging.WARNING)
        checkpoint_callback = CheckpointCallback(
            save_freq=100_000,
            save_path=os.path.join("models", exp_identifier),
            name_prefix=f"{exp_name}_{start_scramble_depth}",
        )
        model.learn(
            total_timesteps=n_episodes,
            reset_num_timesteps=False,
            tb_log_name=f"{exp_name}_{n_episodes}_{env.scramble_length}",
            callback=checkpoint_callback,
            # log_interval=5000,
        )
    os.makedirs("models", exist_ok=True)
    if n_episodes > 0:
        if load_model:
            n_prev_episodes = int(load_model.split("_")[-1].split(".")[0])
            n_episodes += n_prev_episodes
        model.save(os.path.join("models", f"{exp_identifier}.zip"))
    print(f"Testing agent {exp_name}...")
    test_agent(model, env, num_tests=5, scramble_length=10, id=f"st={success_threshold}")


if __name__ == "__main__":
    # main(
    #     # load_model="rubiks_2x2_ai_model_600000.zip",
    #     # train_new=True,
    # )
    import multiprocessing as mp
    success_thresholds = [.1, .3, .5, .7, .8, .9, .95, 1.]
    n_processes = 1
    kwargs_list  = [
            (
            "skewb_sym_half", # puzzle_name
            ["wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"],            # base_actions
            # None,            # load_model
            f"skewb_sym_half_binary_st={threshold}_1_10000000.zip",            # load_model
            # f"skewb_pyramid_binary_st={threshold}_1_5000000",            # load_model
            False,            # train_new
            0,         # n_episodes
            1,               # start_scramble_depth
            threshold,       # success_threshold
        ) for threshold in success_thresholds
        ]
    with mp.Pool(n_processes) as pool:
        pool.starmap(main, kwargs_list)
    # main(
    #     puzzle_name="rubiks_2x2",
    #     base_actions=["f", "f'", "r", "r'", "t", "t'", "b", "b'", "l", "l'", "d", "d'"],
    #     start_scramble_depth=1,
    #     load_model=None,
    #     train_new=True,
    #     n_episodes=20_000_000,
    # )
    # main(
    #     puzzle_name="skewb",
    #     base_actions=["wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"],
    #     load_model=None,
    #     start_scramble_depth=1,
    #     # load_model="skewb_sym_model_500000.zip",
    #     # load_model="skewb_sym_half_model_1500000.zip",
    #     train_new=True,
    #     n_episodes=1_500_000,
    # )
    # In terminal, run "tensorboard --logdir tb_logs/..." to view training progress
