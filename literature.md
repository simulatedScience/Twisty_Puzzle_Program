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
  - no solver

- **Permuzzle/ Gelatinbrain** puzzle simulator
  - Written in Java
  - Features:
    - dual 3D viewport to see the puzzle from two sides
    - click on faces to turn them or
    - text input to perform moves
    - No solver

## Twisty Puzzle Solvers

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

- **MultiH layer-wise solver** - Solving the Rubik's Cube with Deep Reinforcement Learning and Using Multi-Headed Models
  - [paper](https://cs229.stanford.edu/proj2021spr/report2/81889605.pdf)
  - Solve a Rubik's cube layer-wise using a multi-head DNN. Use dynamic scramble length to train the network (increases when 25% of recent episodes were successful).

## Useful Techniques for RL
- **Learning Options** - Learning Options in Reinforcement Learning
  - [paper](https://www.cs.cmu.edu/~mstoll/pubs/stolle2002learning.pdf)
  - Learn a set of options (sub-policies) that can be used to solve a task. Options are learned using Q-learning and a pseudo-reward function. In the context of twisty puzzles, every move and algortihm would be considered an option. The problem of finding options is equivalent to finding useful algorithms.

- **HER** - Hindsight Experience Replay
  - [paper](https://proceedings.neurips.cc/paper_files/paper/2017/file/453fadbd8a1a3af50a9df4df899537b5-Paper.pdf) ([preprint](https://arxiv.org/pdf/1707.01495.pdf))
  - Use hindsight to learn from failed episodes by adding a goal to the inputs. This allows the agent to learn more efficiently from failed episodes and is particularly useful for sparse reward multi-goal environments. Experiments have shown benefits in single-goal environments as well.

- **Voyager with Skill Library** - Voyager: An Open-Ended Embodied Agent with Large Language Models
  - [code](https://github.com/MineDojo/Voyager)
  - [paper](https://voyager.minedojo.org/assets/documents/voyager.pdf)
  - [website](https://voyager.minedojo.org/)
  - Use automatic LLM prompting to generate a library of skills (sub-policies) that can be used to solve a task.


