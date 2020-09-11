# Twisty Puzzle Analysis version 2.2
by Sebastian Jost

work began 22.08.2020

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
- train an AI using Q-Learning to learn to automatically solve any sufficiently easy puzzle. harder puzzles can be partially solved (`train_q`, `move_q`, `solve_q`)
- plot the success of the AI during training (basic plot, no legend, acis labels or any explanation) (`plot`)
- control animation speed (`sleeptime`)

### Additions in version 2.1
- implemented Neural Networks for solving puzzles (`train_nn`)
- automatically load and save the Neural Networks before and after training (`train_nn`)
- solve puzzles with the neural networks (`move_nn`, `solve_nn`)
- implemented a variation of the A* algorithm to solve puzzles more reliably (`solve_q`, `solve_nn`)
- allow visual input of a current puzzle state where the scramble moves are unknown (`editpoints`, `endeditpoints`)

### other additions: Q-table analyser
- added a script `q_table_analyser` to show the average Q-values for a puzzle in dependency of the scramble difficulty
- "smart"-scramble the puzzle:

  scramble the puzzle a given number of mostly random moves:
    - ensure no state is reached twice
    - replace move sequences with their inverses if that reaches the same state more efficiently

  this way the result of $n$ scramble moves is more likely to actually require close to $n$ moves to solve, even with an optimal strategy.


### fixed issues:
- fixed critical bug where cycle input lists weren't reset properly. This made it impossible or unreliable to input more than one move without closing the puzzle in between

- made sure Q-tables and Networks can be saved even if the puzzle isn't saved yet. Although this is not tested thoroughly.

- made memory usage more efficient for Neural Networks. Once the network is trained, the keys in the Q-table are replaced with the keys as they are required for the Network.

  However this makes it impossible to 