# Documentation Overview for Twisty Puzzle Simulator and AI Solver
This project aims to help humans in solving general twisty puzzles by recreating them digitally and offering help in solving puzzles in various ways. These include: being able to try out moves digitally with easy reset and undo, find algorithms to solve sub-problems of puzzles or find solutions from any given state.
Instead of using established human-made methods developed for each puzzle, this projects uses Reinforcement learning along with some general properties of twisty puzzles to solve them without human knowledge. This has the key benefit of being able to solve puzzles that have not been solved by humans before (either because they are too complex, too new or too rare).

This project can be partitioned into a few key components:
1. **puzzle simulator** (representation of puzzles with 3D points, tools for interactions, puzzle creation and visualizations)
2. **puzzle solver** (RL-based algorithms with some more traditional supporting algorithms for automatically solving twisty puzzles)
3. **command-line interface** (CLI) for interacting with the simulator and solver

Each component consist of many sub-components and modules. The following sections will provide a high-level overview of the project structure and the key components.

## Definitions


## Puzzle Simulator
The puzzle simulator aims to digitally recreate many twisty puzzles and provide tools for interacting with them. Puzzles are represented using colored points in 3D space and permutations on these points to define moves. This process discards most of the puzzle's physical properties like shape, overhanging pieces to achieve a more abstract, general representation. Some of these can be recreated later by calculating 3D pieces from the points and moves.

The simulator provides tools for:
- creating puzzles from scratch (import 3D points, define moves, rename puzzles)
- interact with puzzles (make moves, reset to solved, randomly scramble)
- visualize puzzles (show 3D points, show moves, map points to different shapes, calculate 3D pieces for various puzzle shapes)
- analyze puzzle properties (count number of points, moves, calculate symmetries, calculate (bounds for) number of states)

## Puzzle Solver
The puzzle solver aims to find solutions to twisty puzzles from any given state. Ideally, these should be helpful for humans in the following ways:
- generalizable to many different puzzle states
- realistic in length and complexity for humans to execute on physical puzzles
- reasonably fast to compute

Humans typically achieve generalizability of solutions by developing move sequences (a.k.a. "algorithms") that solve certain sub-problems of puzzles like swapping or rotating a few pieces at a time. These are then combined to solve the whole puzzle.
Therefore, this project attempts to replicate the human solving-process by first developing useful algorithms, then applying these to solve the puzzle.

The solver provides tools for:
- finding algorithms for sub-problems of puzzles
- given a puzzle and moves (and/or algorithms), find a solution using Reinforcement Learning

## Command-Line Interface
The CLI provides a way to interact with the simulator and solver from the command line. This enables a workflow for creating, solving and playing with puzzles:

1. load colored 3D points from a Geogebra file (`.ggb`)  
   _Geogebra has many useful tools for creating 3D points_
2. define moves for the puzzle  
   _Moves are defined by clicking on 3D points and where they move. Users specify a move name. inverses are automatically added if possible._
3. save and name the puzzle
4. if desired, calculate 3D pieces for the puzzle in any desired shape  
   <!-- _This is useful for visualizing the puzzle in 3D_ -->
5. train an AI to solve the puzzle  
   _The AI will learn to solve the puzzle from any given state_
6. play with the puzzle by randomly scambling it, manually making moves or letting the AI solve it
7. when needing help with a physical puzzle, input the current state, then let the AI find a solution or find algorithms that could help with solving the puzzle
