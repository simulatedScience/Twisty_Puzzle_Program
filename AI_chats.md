
- GPT-4o 22.08.2024: [Lower bound for state space size](https://chatgpt.com/share/83eb993e-0ae3-4e24-903d-7d22eefa6992)  
  _After several messages, code was partially copied with some modifications to make it more efficient, calculating fewer factorials._

- GPT-4o 28.08.2024: [brainstorming to fix 180° rotation animations](https://chatgpt.com/share/40f1633a-fae4-4881-99e1-7b8641166ba0)  
  _Main ideas were my own, ChatGPT added suggestions for algorithms to use in an implementation and explained pro's and con's of the options._

- GPT-4o 29.08.2024: [implementing ideas for point- and piece orbit-calculations](https://chatgpt.com/share/42fdec47-8ce7-4808-b5b7-41c46560a406)  
  _After a few messages, code was almost directly copied to `tests/puzzle_piece_orbits.py`_

- Gemini (Gemini 1.5 Flash) ~17.08.2024 [Implementing early stopping with StableBaselines 3](https://g.co/gemini/share/031b42019a6e)  
  _This chat helped me learn about early stopping, which I simultaneously read up on in the StableBaselines documentation, then used a combination of what I learned from both sources in `tests/nn_rl_stable_baselines/nn_rl_training.py`. Code from this chat was not directly copied, but due to the simplicity of the problem is still similar._

- GPT-4o 16.09.2024 [parallel RL training with sb3 on GPU](https://chatgpt.com/share/66e93a8c-4228-8007-bb84-da1a41ac4412)
  _unused, read [sb3 documentation](https://stable-baselines3.readthedocs.io/en/master/guide/vec_envs.html) instead for more reliable information. Provided some inspiration for other RL methods to try if necessary._

- GPT-4o 19.09.2024 [fix incorrect inverses in definition of Geaer Cube Ultimate](https://chatgpt.com/share/66ec2d4e-31c0-8007-b686-8d2637191c0e)  
  _Saved some simple but tedious work to correct an error resulting from a minor bug. Doing this without an LLM would have taken a few minutes._

- GPT-4o 27.09.2024 [Write simple data analysis code for test files](https://chatgpt.com/share/66f727ba-c71c-8007-8f86-aa279a19b6db)  
  _Saved time for coding some plots and basic evaluations. I have coded very similar graphs many times before, so ChatGPT was used purely to save time. I uploaded my test data file for one puzzle and described what graphs I wanted. After several messages and some manual adjustments for style of code and plots, the code was mostly copied to `src/au_modules/poilcy_analysis.py`._

- GPT-4o 15.10.2024 [vectorize binary multi-goal reward](https://chatgpt.com/share/670e3661-e8a0-8007-addc-691e70718889)  
  _Very simple modification to existing code. The output was partially used in `src/ai_modules/nn_rl_reward_factories.py` (added `[:, None]` to `state` for vectorization)._

- GPT-4o 18.10.2024 [Implement agent strategy visualization](https://chatgpt.com/share/67137121-e160-8007-882a-f3d933753d44)  
  _Helped to implement a visualization I came up with. Output code was not working. I went through it, changing anything I wouldn't have done the same way and fixed the core logic of the implementation. The method used to store intermediate values was changed by me since the AI generated solution deviated from my original intent, eventhough both were correct approaches._

- GPT-4o 26.10.2024 [Simple GUI vor visualizing color mappings for rotation naming](https://chatgpt.com/share/671e2120-3dd0-8007-87a8-9fd209d7e94f)  
  _To verify that the implemented function to map colors (rgb tuples) to color names (strings) works, I wanted a GUI where I could visualize colors and where they are mapped. Once again, this was a simple code snippet that I have coded in a similar way many times before and it was faster to let an AI do it. I modified the output code to better reflect my vision. For example I removed borders, changed the background color, added logic to automatically split the output into multiple columns etc.._
