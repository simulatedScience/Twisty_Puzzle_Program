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
The repository has a folder `Documentation` which should include links to markdown files with explanation of the implementation of many features. There is no user manual yet.

Currently the program is supposed to be used via a command-line interface. A proper user interface soon is planned but can still take a long time as I still need to find a better way to implement that.


## What can it do?
This version focusses on the 3d animation using `vpython`

It also implements a console interface to control the animation. Overall it can do the following things (commands for these features are in brackets):

### Setup of puzzles
 - import .ggb files into vpython 3d points (`import`)
 - save a puzzle imported like that in a new .xml file (`savepuzzle`)
 - visually define moves by clicking on the points (`newmove`, `endmove`)
 - automatically calculate the rotation axis for every move and animate it (`move`)
 - rename existing moves (`rename`)
 - delete exisiting moves (`delmove`)
 - load a previously saved puzzle with it's moves from a .xml file (`loadpuzzle`)
 - list all or just a single defined move (`listmoves`, `printmove`)

### playing with the puzzles
- change shape of the puzzle by snapping it to a sphere, cube or it's initial shape (`snap`)
- scramble the puzzle randomly (`scramble`)
- reset the puzzle to solved state (`reset`)
- train an AI using Q-Learning to learn to automatically solve any sufficiently easy puzzle. harder puzzles can be partially solved (`train_v`, `move_v`, `solve_v`)
- plot the success of the AI during training (basic plot, no legend, acis labels or any explanation) (`plot`)
- control animation speed (`animtime`). This defines the animation time of each move.

## planned Features
- A UI with a 3D viewport as well as buttons to control the shown puzzles and the AI solving them.
- Much better AI that can find and utilize useful algorithms for any puzzle and solve more complex puzzles.
- Enable user to save Algorithms for puzzles and use them to solve the puzzle more easily.
- Save written solving strategies for puzzles.
- Simplify puzzle definition.
- Enable user to save the current state of a puzzle and load it again later.
