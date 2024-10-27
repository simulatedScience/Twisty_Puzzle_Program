# Twisty_Puzzle_Program
A Program to digitize many twisty puzzles and solve them with an AI using Reinforcement Learning.


An overview of all implemented and many planned features can be found in the following document:
[feature overview](https://docs.google.com/spreadsheets/d/1wllITKTaytmOBHMQu9dV0tIj7YtT3UqvB0RRak2qMqk/edit?usp=sharing)

An overview of known issues, planned features and what's currently being worked on can be found on meistertask: [meistertask-twisty-puzzle-analysis](https://www.meistertask.com/app/project/yy5iFYIE/twisty-puzzle-analysis)

# Requirements
Development started using python `3.8.5`, last tested in `3.9.13`

non-standard library modules:
- `vpython` (3d-visualisation)
  - `autobahn`==22.3.2
  - `txaio`==22.2.1
- `colored`==1.4.4 (colored terminal outputs)
- `lxml` (read/write xml files)
- `sympy` (to calculate number of states of a puzzle)
- `scipy` (combinatorics)
- `keras` (neural networks)
- `matplotlib` (plotting of training progress)

All of them can be easily installed with `pip install ... `.

# Documentation
The repository has a folder `doc` which includes markdown files with explanation of the implementation of many features.

Currently the program is supposed to be used via a command-line interface. A proper user interface is planned but can still take a long time. There is no plan when I will find time to implement it.


## What can it do?
This version focusses on the 3d animation using `vpython`

It also implements a console interface to control the animation. Overall it can do the following things (commands for these features are in brackets):

See `doc/user guide.md` for usage instructions.

## planned Features
- DONE: Much better AI that can find and utilize useful algorithms for any puzzle and solve more complex puzzles.
- Simplify puzzle definition. -> Partially done. Cuboid generation is now automated with `src/puzzles/cuboid_generator.py`
- A UI with a 3D viewport as well as buttons to control the shown puzzles and the AI solving them.
- Enable user to save Algorithms for puzzles and use them to solve the puzzle more easily.
- Save written solving strategies for puzzles.
- Enable user to save the current state of a puzzle and load it again later.
