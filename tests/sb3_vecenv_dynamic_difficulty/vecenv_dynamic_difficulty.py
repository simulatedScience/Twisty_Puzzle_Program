import gymnasium as gym
import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env

class SimpleEnv(gym.Env):
    def __init__(self,
            initial_scramble_length=1,
            success_threshold=0.9,
            last_n_episodes=100,
            max_moves=10,
            ):
        super(SimpleEnv, self).__init__()
        self.observation_space = gym.spaces.Discrete(max_moves+2)  # Example: two possible states
        self.action_space = gym.spaces.Discrete(2)  # Example: two possible actions
        self.scramble_length = initial_scramble_length
        self.success_threshold = success_threshold
        self.last_n_episodes = last_n_episodes
        # self.success_history = np.zeros(last_n_episodes, dtype=bool)
        # self.episode_counter = 0
        self.current_state: int = 0
        self.move_counter: int = 0
        self.max_moves: int = max_moves

    def reset(self, seed=None, options=None):
        self.current_state = 0
        self.move_counter = 0
        return self.current_state, {}

    def step(self, action_index):
        self.move_counter += 1
        self.current_state += 1
        # taking action 1 always succeeds
        terminated: bool = action_index == 1 and self.move_counter == self.scramble_length
        reward: float = 1. if terminated else 0.
        truncated: bool = self.move_counter >= self.max_moves
        # self.success_history[self.episode_counter % self.last_n_episodes] = done
        # self.episode_counter += 1
        # print(f"state: {self.current_state}, reward: {reward}, terminated: {terminated}, truncated: {truncated}")
        # done = truncated or terminated
        return self.current_state, reward, terminated, truncated, {}

    def set_scramble_length(self, scramble_length):
        self.scramble_length = scramble_length
        print(f"Updated scramble length to: {scramble_length}")
    
    def get_scramble_length(self):
        return self.scramble_length

class UpdateScrambleLengthCallback(BaseCallback):
    def __init__(self, success_threshold=0.9, last_n_episodes=100, verbose=0):
        super().__init__(verbose)
        self.success_threshold = success_threshold
        self.last_n_episodes = last_n_episodes

    def _on_step(self):
        return True

    def _on_rollout_end(self):
        env = self.training_env.envs[0]  # Access the first environment
        success_rate = self.locals["dones"].mean()
        old_scramble_length = self.training_env.env_method("get_scramble_length")[0]
        print(f"Success rate: {success_rate:.2f}.")
        if success_rate >= self.success_threshold:
            new_scramble_length = old_scramble_length + 1
            self.training_env.env_method("set_scramble_length", new_scramble_length)
            print("="*75)
            print(f"Success rate: {success_rate:.2f}. Increased scramble length to {new_scramble_length}.")
            print("="*75)
        return True

if __name__ == "__main__":
    # Create the environment and wrap it in a VecEnv
    vec_env = make_vec_env(lambda: SimpleEnv(), n_envs=2)

    # Create the agent
    model = PPO(
        'MlpPolicy',
        env=vec_env,
        n_steps=5,
        batch_size=10,
        device='cpu',
        verbose=1)

    # Create and use the callback
    callback = UpdateScrambleLengthCallback()

    # Train the model with the callback
    model.learn(
        total_timesteps=10_000,
        reset_num_timesteps=False,
        callback=[callback],
    )
