import os
import random
import time

import numpy as np
from stable_baselines3.common.env_checker import check_env
from gymnasium import Env
from gymnasium.spaces import MultiDiscrete, Discrete
from stable_baselines3 import DQN, HerReplayBuffer
# from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
from stable_baselines3.common.callbacks import CheckpointCallback
from tqdm.auto import tqdm
from gymnasium.spaces import Dict

from nn_rl_training import Twisty_Puzzle_Env, test_agent, load_puzzle
from reward_functions import binary_reward

class Twisty_Puzzle_Env_HER(Twisty_Puzzle_Env):
    def __init__(self,
                 solved_state: list[int],
                 actions: dict[str, list[tuple[int, ...]]],
                 base_actions: list[str] = None,
                 max_moves=50,
                 initial_scramble_length=1,
                 success_threshold=0.9):
        super().__init__(solved_state, actions, base_actions, max_moves, initial_scramble_length, success_threshold)
        
        # Override observation space: Dict for the state and goal
        self.observation_space = Dict({
            'observation': MultiDiscrete([6] * len(solved_state)),
            'achieved_goal': MultiDiscrete([6] * len(solved_state)),
            'desired_goal': MultiDiscrete([6] * len(solved_state)),
        })
        # self.step_calls=0

    def reset(self, seed=None, options=None, print_scramble=False):
        super().reset(seed, options, print_scramble)
        return self._get_obs(), {}

    def step(self, action):
        # self.step_calls += 1
        next_state, reward, terminated, truncated, info = super().step(action)
        # print(f"Step {self.step_calls} terminated: {terminated}, type: {type(terminated)}")
        # print(f"Step {self.step_calls} reward: {reward}, type: {type(reward)}")
        return self._get_obs(), reward, terminated, truncated, info

    def compute_reward(self, achieved_goal: np.ndarray, desired_goal: np.ndarray, info: dict):
        """
        Compute the binary reward: 1 if achieved_goal == desired_goal, 0 otherwise
        """
        done = np.all(achieved_goal == desired_goal, axis=-1)
        reward = np.where(done, np.float16(1), np.float16(0))
        return reward
        # return binary_reward(achieved_goal, None, desired_goal)[0]

    def _get_obs(self):
        return {
            'observation': np.array(self.state),
            'achieved_goal': np.array(self.state),
            'desired_goal': np.array(self.solved_state),
        }


def main(
        puzzle_name: str = "rubiks_2x2_ai",
        base_actions: list[str] = None,
        load_model: str = None,
        model_folder: str = "models_her",
        train_new: bool = False,
        n_episodes: int = 20_000,
        start_scramble_depth: int = 1,
        success_threshold: float = 0.9,
        device="cpu",
    ):
    exp_name = f"{puzzle_name}_binary_st={success_threshold}"
    solved_state, actions_dict = load_puzzle(puzzle_name)
    env = Twisty_Puzzle_Env_HER(
            solved_state,
            actions_dict,
            base_actions=base_actions,
            initial_scramble_length=start_scramble_depth,
            success_threshold=success_threshold)
    # check_env(env)
    monitor_env = Monitor(env)
    env.monitor = monitor_env

    model_path = os.path.join(model_folder, f"{exp_name}.zip")
    if load_model:
        print("Loading existing model...")
        model_path = os.path.join(model_folder, load_model)
        # model = DQN.load(
        #     model_path,
        #     env,
        #     device=device,
        #     # learning_starts=10_000,
        # )
        # model.learning_starts = 10_000
        model = DQN(
            "MultiInputPolicy",
            monitor_env,
            replay_buffer_class=HerReplayBuffer,
            replay_buffer_kwargs=dict(
                n_sampled_goal=4,
                goal_selection_strategy='future',
            ),
            learning_starts=10_000,
            verbose=0,
            device=device,
            tensorboard_log=f"tb_logs_her/{exp_name}",
        )
        model.set_parameters(model_path, device=device)
    # elif not train_new and os.path.exists(model_path):
    #     print("Loading existing model...")
    #     model = DQN.load(
    #         model_path,
    #         device=device,
    #         learning_starts=10_000,
    #     )
    else:
        print("Training new model...")
        model = DQN(
            "MultiInputPolicy",
            monitor_env,
            replay_buffer_class=HerReplayBuffer,
            replay_buffer_kwargs=dict(
                n_sampled_goal=4,
                goal_selection_strategy='future',
            ),
            verbose=0,
            device=device,
            tensorboard_log=f"tb_logs_her/{exp_name}",
        )

    exp_identifier = f"{exp_name}_{start_scramble_depth}_{n_episodes}"
    if n_episodes > 0:
        checkpoint_callback = CheckpointCallback(
            save_freq=250_000,
            save_path=os.path.join(model_folder, exp_identifier),
            name_prefix=f"{exp_name}_{start_scramble_depth}",
        )
        model.learn(
            total_timesteps=n_episodes,
            reset_num_timesteps=False,
            tb_log_name=f"{exp_name}_{n_episodes}_{env.scramble_length}",
            callback=checkpoint_callback,
            # learning_starts=100,
            # progress_bar=True,
        )

    # os.makedirs(model_folder, exist_ok=True)
    if n_episodes > 0:
        if load_model:
            n_prev_episodes = int(load_model.split("_")[-1].split(".")[0])
            n_episodes += n_prev_episodes
        model.save(os.path.join(model_folder, f"{exp_identifier}.zip"))
        print(f"Saved final model to {os.path.join(model_folder, f'{exp_identifier}.zip')}")

    print(f"Testing agent {exp_name}...")
    test_agent(model, env, num_tests=5, scramble_length=20, id=f"st={success_threshold}", verbose=None)


if __name__ == "__main__":
    import multiprocessing as mp
    scramble_depths: list[int] = [1]#, 8, 16]
    success_thresholds: list[float] = [0.1, 0.9]
    # kwargs_list: list[tuple[any]] = [(
    #     "rubiks_2x2_ai",
    #     None, # ["f", "f'", "r", "r'", "t", "t'", "b", "b'", "l", "l'", "d", "d'"],
    #     None, # f"rubiks_2x2_ai_binary_st={success_threshold}_1_10000000.zip", # load_model
    #     "models_her",
    #     True, # train_new
    #     # 100_000, # n_episodes
    #     30_000_000,
    #     start_scramble_depth,
    #     success_threshold,
    # ) for start_scramble_depth in scramble_depths
    #     for success_threshold in success_thresholds
    # ]
    kwargs_list: list[tuple[any]] = [(
        "skewb_sym_half",
        ["wbr", "wbr'", "wgo", "wgo'", "ryg", "ryg'", "oyb", "oyb'"],            # base_actions
        None, # f"rubiks_2x2_ai_binary_st={success_threshold}_1_10000000.zip", # load_model
        "models_her",
        True, # train_new
        # 100_000, # n_episodes
        10_000_000,
        start_scramble_depth,
        success_threshold,
    ) for start_scramble_depth in scramble_depths
        for success_threshold in success_thresholds
    ]
    
    
    
    
    # main(*kwargs_list[1])
    with mp.Pool(2) as pool:
        pool.starmap(main, kwargs_list)
    # In terminal, run "tensorboard --logdir tb_logs_her" to view training progress