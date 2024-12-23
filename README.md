# Twisty Puzzle Program - Simulator and AI solver
A Program to digitize many twisty puzzles and solve them with an AI using Reinforcement Learning and automatic algorithm generation.

This project includes a new twisty puzzle simulator for permutation puzzles as well as different solvers. The program can detect rotational symmetries of puzzles, find useful algorithms to solve them and then train an AI to solve the puzzle using Reinforcement Learning, making use of the generated algorithms and rotational symmetries.

<!-- An overview of all implemented and many planned features can be found in the following document:
[feature overview](https://docs.google.com/spreadsheets/d/1wllITKTaytmOBHMQu9dV0tIj7YtT3UqvB0RRak2qMqk/edit?usp=sharing)

An overview of known issues, planned features and what's currently being worked on can be found on meistertask: [meistertask-twisty-puzzle-analysis](https://www.meistertask.com/app/project/yy5iFYIE/twisty-puzzle-analysis) -->

# Requirements
Development started using python `3.8.5`, last tested in `3.11.3`

third party modules:  
see `requirements.txt` for a list of all required modules and versions.

All of them can be easily installed with `pip install ... ` or `pip install -r requirements.txt` to install all of them at once. You may need to install NVIDIA CUDA toolkit beforehand. Otherwise the program will run on the CPU which is slower.

# Documentation
The repository contains a folder `doc` which includes markdown files with explanation of the implementation of many features.

Currently the program is supposed to be used via a command-line interface. A proper user interface is planned but can still take a long time. There is no plan when I will find time to implement it.


## What can it do?
This version focusses on the 3d animation using `vpython`

It also implements a console interface to control the animation. A list of all CLI commands can be accessed by running `run_program.py` and typing `help` (then pressing enter).

See `doc/user guide.md` for more detailed usage instructions.

## planned Features
- DONE: Much better AI that can find and utilize useful algorithms for any puzzle and solve more complex puzzles.
- Simplify puzzle definition. -> Partially done. Cuboid generation is now automated with `src/puzzles/cuboid_generator.py`
- A UI with a 3D viewport as well as buttons to control the shown puzzles and the AI solving them.
- Enable user to save Algorithms for puzzles and use them to solve the puzzle more easily.
- Save written solving strategies for puzzles.
- Enable user to save the current state of a puzzle and load it again later.
