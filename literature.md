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
- **Korf's Algorithm**
  - [paper](https://cdn.aaai.org/AAAI/1997/AAAI97-109.pdf): _Finding Optimal Solutions to Rubik's Cube Using Pattern Databases_ AAAI-1997
  - This paper by Richard korf describes an often implemented optimal solver.
  - Abstract states that the algorithm's time and space requirements are linear in state space size, which makes this highly unsuitable for large puzzles.
  - Uses puzzle specific domain knowledge like prcomputed shortest solutions for the corners (aka the 2x2x2 cube) as well as some move optimizations

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

---

### RL based solvers

- **DeepCube** - Solving the Rubik's Cube Without Human Knowledge/  
  Solving the Rubik's Cube with Approximate Policy Iteration
  - [paper](https://openreview.net/pdf?id=Hyfn2jCcKm) ([preprint](https://arxiv.org/pdf/1805.07470.pdf))
  - Learn to solve the Rubik's cube using Approximate Policy Iteration (API) with a deep neural network as a function approximator.
  - claimed first ever RL solution to the Rubik's Cube
```BibTex
@article{
EfficientCube,
title={Self-Supervision is All You Need for Solving Rubik{\textquoteright}s Cube},
author={Kyo Takano},
journal={Transactions on Machine Learning Research},
issn={2835-8856},
year={2023},
url={https://openreview.net/forum?id=bnBeNFB27b},
note={}
}
```

- **DeepCubeA** - Solving the Rubik's Cube with Deep Reinforcement Learning and Search
  - [code (latest)](https://github.com/forestagostinelli/DeepCubeA)
  - [code (original)](https://codeocean.com/capsule/5723040/tree)
  - [demonstration](https://deepcube.igb.uci.edu/)
  - [paper](https://deepcube.igb.uci.edu/static/files/SolvingTheRubiksCubeWithDeepReinforcementLearningAndSearch_Final.pdf)
  - Solve the Rubik's cube, sliding tile puzzles, and other combinatorial puzzles using a combination of deep reinforcement learning and Batch-weighted A* search.
```BibTex
@article{deepCubeA,
title = {Solving the Cubik's cube with Deep Reinforcement Learning and Search},
journal = {Nature Machine Intelligence},
year = {2019},
volume = {1},
pages = {356–363},
doi = {https://doi.org/10.1038/s42256-019-0070-z},
url = {https://deepcube.igb.uci.edu/},
author = {Agostinelli, Forest, McAleer, Stephen, Shmakov, Alexander, Baldi, Pierre}
}
```

- **QUBE** - Solving Rubik’s Cube via Quantum Mechanics and Deep Reinforcement Learning
  - Trained successful RL solver in about 10^5 episodes, but used 4 human-designed stages of training:
    1. orient edges
    2. orient corners
    3. position corners
    4. position edges
  - Each phase trains a separate NN, with different available moves (see table 1)
  - uses DDQN agents with experience replay (memory size $10^4$). Episodes end after #scramble steps + 5 moves

- **Efficientcube** - Self-Supervision is All You Need for Solving Rubik's Cube
  - [code](https://github.com/kyo-takano/efficientcube)
  - [paper](https://openreview.net/pdf?id=bnBeNFB27b)
  - Solve the Rubik's cube, sliding tile puzzles, and other combinatorial puzzles using a combination of deep reinforcement learning from reverse scrambles and Beam search.
  - This includes scaling laws for compute as well as a clear figure of the compute budget for training the model: $5.14 \times 10^19$ FLOPs with a $1.19 \times 10^8$ parameter model (119 Million).
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
  - Tried adding options (different sets of 10+ algorithms) to action set in A* search, but found no improvements.
  - Similar motivation to our work: solve in a more intuitive way than DeepCubeA, more restricted directly to lawer-wise solving, which is not practical for all puzzles.
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
  - [paper](https://proceedings.mlr.press/v130/pan21a/pan21a.pdf), [website](https://proceedings.mlr.press/v130/pan21a.html)
  - Exploiting the symmetry group structure of permutation puzzles using Fourier basis functions in reinforcement learning. (maths heavy)  
  - claims significantly better results than RL with Deep Value Networks (as in DeepCubeA), using 2-3 orders of magnitude less parameters and less training data (as low as 1/10th) and time.
  - solved pyraminx, 2x2 rubiks and S8 puzzle
  - states how many states of each puzzle were seen during training with different methods!
    - ~50% of 2x2x2 with Deep Value Networks (DVN), only 4.5-20% with Fourier Bases
    - 100% of Pyraminx states with all methods

  ```Bibtex
  @InProceedings{pmlr-v130-pan21a,
    title = 	 { Fourier Bases for Solving Permutation Puzzles },
    author =       {Pan, Horace and Kondor, Risi},
    booktitle = 	 {Proceedings of The 24th International Conference on Artificial Intelligence and Statistics},
    pages = 	 {172--180},
    year = 	 {2021},
    editor = 	 {Banerjee, Arindam and Fukumizu, Kenji},
    volume = 	 {130},
    series = 	 {Proceedings of Machine Learning Research},
    month = 	 {13--15 Apr},
    publisher =    {PMLR},
    pdf = 	 {http://proceedings.mlr.press/v130/pan21a/pan21a.pdf},
    url = 	 {https://proceedings.mlr.press/v130/pan21a.html},
    abstract = 	 { Traditionally, permutation puzzles such as the Rubik’s Cube were often solved by heuristic search like $A^*\!$-search and value based reinforcement learning methods. Both heuristic search and Q-learning approaches to solving these puzzles can be reduced to learning a heuristic/value function to decide what puzzle move to make at each step. We propose learning a value function using the irreducible representations basis (which we will also call the Fourier basis) of the puzzle’s underlying group. Classical Fourier analysis on real valued functions tells us we can approximate smooth functions with low frequency basis functions. Similarly, smooth functions on finite groups can be represented by the analogous low frequency Fourier basis functions. We demonstrate the effectiveness of learning a value function in the Fourier basis for solving various permutation puzzles and show that it outperforms standard deep learning methods. }
  }
  ```

- **Minkwitz Algorithm** - Solving Twisty Puzzles as a Factorization problem
  - [link](https://mathstrek.blog/2018/06/21/solving-permutation-based-puzzles/)

- **An Algorithm for Solving the Factorization Problem in Permutation Groups**
  - [paper](https://doi.org/10.1006/JSCO.1998.0202) by Torsten Minkwith (1998), Karlsruhe, [pdf](https://www.sciencedirect.com/science/article/pii/S0747717198902024?via%3Dihub)
```BibTex
@article{MINKWITZ199889,
  title = {An Algorithm for Solving the Factorization Problem in Permutation Groups},
  journal = {Journal of Symbolic Computation},
  volume = {26},
  number = {1},
  pages = {89-95},
  year = {1998},
  issn = {0747-7171},
  doi = {https://doi.org/10.1006/jsco.1998.0202},
  url = {https://www.sciencedirect.com/science/article/pii/S0747717198902024},
  author = {T. Minkwitz},
  abstract = {The factorization problem in permutation groups is to represent an elementgof some permutation groupGas a word over a given setSof generators ofG. For practical purposes, the word should be as short as possible, but must not be minimal. Like many other problems in computational group theory, the problem can be solved from a strong generating set (SGS) and a base ofG. Different algorithms to compute an SGS and a base have been published. The classical algorithm is the Schreier–Sims method. However, for factorization an SGS is needed that has all its elements represented as words overS. The existing methods are not suitable, because they lead to an exponential growth of word lengths. This article presents a simple algorithm to solve the factorization problem. It is based on computing an SGS with elements represented by relatively short words over the generators.}
}
```

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


## Misc.
- [Number of states of even nxnxn cubes](https://www.quora.com/How-many-scrambled-possibilities-for-a-1000-x-1000-Rubik-s-cube-are-there/answer/David-Smith-2412?ch=10&share=2e1e997e&srid=hl1xV)  
  Number of reachable positions of a cube of sidelength $2n$:
  $$N_{2n} = \frac{1}{24} \cdot (8! \cdot 3^7) \cdot 24!^{n-1} \cdot \left(\frac{24!}{4!^6}\right)^{(n-1)^2}$$
- [Parallel A* Graph Search](https://people.csail.mit.edu/rholladay/docs/parallel_search_report.pdf)
- [Reflection symmetry detection]()
```BibTex
@article{ref_sym_detection,
author = {Hruda, Lukas and Kolingerova, Ivana and Váša, Libor},
year = {2022},
month = {02},
pages = {},
title = {Robust, fast and flexible symmetry plane detection based on differentiable symmetry measure},
volume = {38},
journal = {The Visual Computer},
doi = {10.1007/s00371-020-02034-w},
abstract = {Reflectional symmetry is a potentially very useful feature which many real-world objects exhibit. It is instrumental in a variety of applications such as object alignment, compression, symmetrical editing or reconstruction of incomplete objects. In this paper, we propose a novel differentiable symmetry measure, which allows using gradient-based optimization to find symmetry in geometric objects. We further propose a new method for symmetry plane detection in 3D objects based on this idea. The method performs well on perfectly as well as approximately symmetrical objects, it is robust to noise and to missing parts. Furthermore, it works on discrete point sets and therefore puts virtually no constraints on the input data. Due to flexibility of the symmetry measure, the method is also easily extensible, e.g., by adding more information about the input object and using it to further improve its performance. The proposed method was tested with very good results on many objects, including incomplete objects and noisy objects, and was compared to other state-of-the-art methods which it outperformed in most aspects.}
}
```
- [Rotational symmetry detection]()
```BibTex
@article{rot_sym_detection,
title = {Rotational symmetry detection in 3D using reflectional symmetry candidates and quaternion-based rotation parameterization},
journal = {Computer Aided Geometric Design},
volume = {98},
pages = {102138},
year = {2022},
issn = {0167-8396},
doi = {https://doi.org/10.1016/j.cagd.2022.102138},
url = {https://www.sciencedirect.com/science/article/pii/S0167839622000747},
author = {Lukáš Hruda and Ivana Kolingerová and Miroslav Lávička and Martin Maňák},
keywords = {Symmetry detection, Rotation, Rotational symmetry, Rotation parameterization, Quaternion},
abstract = {The property of symmetry in 3D objects is helpful in various applications such as object alignment, compression, symmetrical editing or reconstruction of incomplete objects. However, its robust and efficient detection is a challenging task. The two most commonly occurring types of symmetry are probably reflectional and rotational symmetry. While reflectional symmetry detection methods are quite plentiful, this does not seem to be the case with rotational symmetry detection. In this paper a use of approximate reflectional symmetries to derive plausible approximate rotational symmetries is proposed that can be integrated with multiple different approaches for reflectional symmetry detection. One such specific approach, based on maximizing a given symmetry measure, is chosen and combined with this idea. A modification of the maximization step for rotations is further proposed using a simple, yet efficient, quaternion-based parameterization of the rotation transformation which seems novel in the field of symmetry detection. The results confirm that this combination provides a robust and efficient solution for finding rotational symmetry in a 3D point set and can handle approximate symmetry, noisy input or even partial data.}
}
```