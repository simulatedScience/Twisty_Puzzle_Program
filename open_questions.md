## coding questionsn

- `sb3.PPO` has a parameter `n_steps`, the number of steps to take in an environment between updates. What happens if each episode has a potentially different length? Some may be terminated earlier.
When I increased `n_steps` from 50 to 100, learning behviour changed drastically (compare *`2024-09-26_17-14-26\tb_logs\gear_cube_extreme_sym_algs_rew=most_correct_points_sd=16_st=0.2_eps=100000000_lr=0.001_bs=25000_ne=1000_0`* and *`2024-09-26_23-17-52\tb_logs\gear_cube_extreme_sym_algs_rew=most_correct_points_sd=32_st=0.25_eps=200000000_lr=0.001_bs=25000_ne=1000_0`* by running *`tensorboard --logdir src/ai_files/gear_cube_extreme_sym_algs`* in a terminal)

- in the DynamicDifficultyCallback, I was unable to reproduce the `ep_rew_mean` metric displayed in the verbose outputs or the tensorboard log during training. I tried averaging all completed episodes during `_on_rollout_end`, averaging the done state of *all* environments, averaging the terminated state of *all* environments etc.  
  From what I know, episodes aren't necessarily completed when `_on_rollout_end` is called. `self.locals[infos]` stores booleans `'truncated'` in a dict for each environment. If the episode there is currenty completed, these dicts also contain `'reward'` and other keys, including anything returned in the on_step method of the environnment.
