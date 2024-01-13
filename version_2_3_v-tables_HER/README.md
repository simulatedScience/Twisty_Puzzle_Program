# Twisty Puzzle Analysis version 2.3
by Sebastian Jost

work began 28.07.2021

-----

## Dependecies
Python 3.9
non-standard library modules:
- vpython (3d-visualisation)
  - autobahn==22.3.2
  - txaio==22.2.1
- colored==1.4.4 (colored terminal outputs)
- lxml (read/write xml files)
- sympy ()
- scipy (combinatorics)
- keras

-----

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

-----

### Additions in version 2.3
- implemented smarter scramble-algorithm that scrambles much more efficiently
- (may need improvements) use V-tables instead of Q-tables (evaluate states instead of actions). This reduces the number of possible states by 1/A where A is the number of possible actions. Should increase learning speed a lot too.
- improved animation speed control
<!-- - (planned) use hindsight-experience-replay: treat each episode as a success by redefining the goal. This will require some major conceptual changes to the neural network architechture. -->

-----

## fixed issues:

-----

## possible improvements

Train the AIs not on permutations of the color points but on permutations of the pieces instead. This doesn't decrease the state space size but it could decrease the computational cost for each applied move and decrease the size of the neural network.

Both of which would accelerate the training and massively decrease the time it takes to solve puzzles with the implemented A* algorithm.