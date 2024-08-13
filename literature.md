# Related literature

## Twisty Puzzle Simulators

- **pCubes** puzzle simulator
  - [code](https://github.com/BMouradov/pCubes/tree/main)
  - [download & info](https://twistypuzzles.com/forum/viewtopic.php?t=27054&sid=e826b4cc63d664a0a54fc80e2f47b623)
  - Written in Pascal (with Lazarus)
  - Published 2014, Open-Source since May 2023
  - Features:
      - Supports hundreds of puzzles
      - 3D viewport
      - dragging in viewport to make moves
      - No solver
- **Ruwix** online puzzle simulator
  - https://ruwix.com/online-puzzle-simulators/
  - No solver

- **Permuzzle/ Gelatinbrain** puzzle simulator
  - Written in Java
  - Features:
    - dual 3D viewport to see the puzzle from two sides
    - click on faces to turn them or
    - text input to perform moves
    - No solver

- **Twizzle Explorer** (?)
  - Written in TypeScript
  - compatible with ksolve, twsearch, GAP
  - [website](https://alpha.twizzle.net/explore/help.html)

## Twisty Puzzle Solvers

### classical solvers
Mostly for 3x3 rubiks cube, often without GUI, usually aim to solve the puzzle or a given state in the fewest moves possible.
- **ksolve+/ ksolve++**  
  cumbersome text-only interface for puzzle definitions and moves with custom interpreter
  - [website ksolve+](https://mzrg.com/rubik/ksolve+/)
  - [(deleted) reddit thread](https://www.reddit.com/r/Cubers/comments/873vzw/ksolve_a_new_fast_general_puzzle_solving_program/)
  - [website ksolve++](https://benwh1.github.io/web/software/ksolve++/index.html)
- **Cube Explorer**  
  only supports 3x3 rubiks cube
  - [website](https://kociemba.org/cube.htm)
- **Trangium Batch Solver**
  - [website](https://trangium.github.io/BatchSolver/)
- **nissy**  
  - [website](https://nissy.tronto.net/)

### RL based solvers
- **DeepCubeA** - Solving the Rubik's Cube with Deep Reinforcement Learning and Search
  - [code (latest)](https://github.com/forestagostinelli/DeepCubeA)
  - [code (original)](https://codeocean.com/capsule/5723040/tree)
  - [demonstration](https://deepcube.igb.uci.edu/)
  - [paper](https://deepcube.igb.uci.edu/static/files/SolvingTheRubiksCubeWithDeepReinforcementLearningAndSearch_Final.pdf)
  - Solve the Rubik's cube, sliding tile puzzles, and other combinatorial puzzles using a combination of deep reinforcement learning and Batch-weighted A* search.

- **DeepCube** - Solving the Rubik's Cube Without Human Knowledge/  
  Solving the Rubik's Cube with Approximate Policy Iteration
  - [paper](https://openreview.net/pdf?id=Hyfn2jCcKm) ([preprint](https://arxiv.org/pdf/1805.07470.pdf))
  - Learn to solve the Rubik's cube using Approximate Policy Iteration (API) with a deep neural network as a function approximator.

- **Efficientcube** - Self-Supervision is All You Need for Solving Rubik's Cube
  - [code](https://github.com/kyo-takano/efficientcube)
  - [paper](https://openreview.net/pdf?id=bnBeNFB27b)
  - Solve the Rubik's cube, sliding tile puzzles, and other combinatorial puzzles using a combination of deep reinforcement learning from reverse scrambles and Beam search.
  ```BibTex
  @article{
  takano2023selfsupervision,
  title={Self-Supervision is All You Need for Solving Rubik{\textquoteright}s Cube},
  author={Kyo Takano},
  journal={Transactions on Machine Learning Research},
  issn={2835-8856},
  year={2023},
  url={https://openreview.net/forum?id=bnBeNFB27b},
  note={}
  }
  ```

- **MultiH layer-wise solver** - Solving the Rubik's Cube with Deep Reinforcement Learning and Using Multi-Headed Models
  - [paper](https://cs229.stanford.edu/proj2021spr/report2/81889605.pdf)
  - Solve a Rubik's cube layer-wise using a multi-head DNN. Use dynamic scramble length to train the network (increases when 25% of recent episodes were successful).
  ```BibTex
  @article{

  title={Solving the Rubik's Cube with Deep Reinforcement Learning and Using Multi-Headed Models},
  author={WenXin Dong, Hanson Hao, George Nakayama},
  journal={
  issn={
  year={2021}
  url={https://cs229.stanford.edu/proj2021spr/report2/81889605.pdf},
  note={
  }
  ```

- **Fourier Basis RL** - Fourier Bases for Solving Permutation Puzzles  
 - [paper](https://proceedings.mlr.press/v130/pan21a/pan21a.pdf)
 - Exploiting the symmetry group structure of permutation puzzles using Fourier basis functions in reinforcement learning. (maths heavy)  
 - claims significantly better results than RL with Deep Value Networks (as in DeepCubeA), using 2-3 orders of magnitude less parameters and less training data (as low as 1/10th) and time.
 - solved pyraminx, 2x2 rubiks and S8 puzzle
  ```
  Proceedings of the 24th International Conference on Artificial Intelligence and Statistics (AISTATS) 2021, San Diego, California, USA. PMLR: Volume 130. Copyright 2021
  ```

- **?** - Solving Twisty Puzzles as a Factorization problem
- [link](https://mathstrek.blog/2018/06/21/solving-permutation-based-puzzles/)

- **An Algorithm for Solving the Factorization Problem in Permutation Groups**
  - [paper](https://doi.org/10.1006/JSCO.1998.0202) by Torsten Minkwith (1998), Karlsruhe, [pdf](https://www.sciencedirect.com/science/article/pii/S0747717198902024?via%3Dihub)
  - 

- **Modelling Perumtation puzzles** - Solving Puzzles related to Permutation Groups
  - [paper](https://dl.acm.org/doi/abs/10.1145/281508.281611), [pdf](https://dl.acm.org/doi/pdf/10.1145/281508.281611)
  - gives state space sizes for many popular twisty puzzles including Rubiks 2x2, 3x3, 4x4, Hungarian Rings (listed as "Pretzel"), Nintendo Barrel and Square One (listed as "MegaChallenger").
  - roughly describes techniques for modelling puzzles like the Nintendo Barrel using monooids and permutation groups.
  - briefly mentions the difficulty of finding legal moves in the Square-1 puzzle, solving this with a 3d model.
  ```BibTex
  @inproceedings{10.1145/281508.281611,
    author = {Egner, Sebastian and P\"{u}schel, Markus},
    title = {Solving puzzles related to permutation groups},
    year = {1998},
    isbn = {1581130023},
    publisher = {Association for Computing Machinery},
    address = {New York, NY, USA},
    url = {https://doi.org/10.1145/281508.281611},
    doi = {10.1145/281508.281611},
    booktitle = {Proceedings of the 1998 International Symposium on Symbolic and Algebraic Computation},
    pages = {186–193},
    numpages = {8},
    location = {Rostock, Germany},
    series = {ISSAC '98}
  }
  ```



## Useful Techniques for RL
- **Learning Options** - Learning Options in Reinforcement Learning
  - [paper](https://www.cs.cmu.edu/~mstoll/pubs/stolle2002learning.pdf)
  - Learn a set of options (sub-policies) that can be used to solve a task. Options are learned using Q-learning and a pseudo-reward function. In the context of twisty puzzles, every move and algortihm would be considered an option. The problem of finding options is equivalent to finding useful algorithms.
  ```Bibtex
  @inproceedings{inproceedings,
  author = {Stolle, Martin and Precup, Doina},
  year = {2002},
  month = {08},
  pages = {212-223},
  title = {Learning Options in Reinforcement Learning},
  volume = {2371},
  isbn = {978-3-540-43941-7},
  journal = {Lecture Notes in Computer Science},
  doi = {10.1007/3-540-45622-8_16}
  }
  ```

- **HER** - Hindsight Experience Replay
  - [paper](https://proceedings.neurips.cc/paper_files/paper/2017/file/453fadbd8a1a3af50a9df4df899537b5-Paper.pdf) ([preprint](https://arxiv.org/pdf/1707.01495.pdf))
  - Use hindsight to learn from failed episodes by adding a goal to the inputs. This allows the agent to learn more efficiently from failed episodes and is particularly useful for sparse reward multi-goal environments. Experiments have shown benefits in single-goal environments as well.
  ```BibTex
  @article{article,
  author = {Andrychowicz, Marcin and Wolski, Filip and Ray, Alex and Schneider, Jonas and Fong, Rachel and Welinder, Peter and McGrew, Bob and Tobin, Josh and Abbeel, Pieter and Zaremba, Wojciech},
  year = {2017},
  month = {07},
  pages = {},
  title = {Hindsight Experience Replay}
  }
  ```

- **Voyager with Skill Library** - Voyager: An Open-Ended Embodied Agent with Large Language Models
  - [code](https://github.com/MineDojo/Voyager)
  - [paper](https://voyager.minedojo.org/assets/documents/voyager.pdf)
  - [website](https://voyager.minedojo.org/)
  - Use automatic LLM prompting to generate a library of skills (sub-policies) that can be used to solve a task.
  ```BibTex
  @article{wang2023voyager,
    title   = {Voyager: An Open-Ended Embodied Agent with Large Language Models},
    author  = {Guanzhi Wang and Yuqi Xie and Yunfan Jiang and Ajay Mandlekar and Chaowei Xiao and Yuke Zhu and Linxi Fan and Anima Anandkumar},
    year    = {2023},
    journal = {arXiv preprint arXiv: Arxiv-2305.16291}
  }
  ```

