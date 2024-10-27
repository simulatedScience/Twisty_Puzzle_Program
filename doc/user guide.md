# Twisty Puzzle Simulator User Guide
The main program can be started by running `run_program.py`. This will open a command line interface (CLI). Type `help` to see a list of commands or `help [commandname]` to see info about a specific command. The most important ones are explained below. Loading puzzles will open a browser window with a 3D viewport showing the puzzle.
To see which puzzles are available, type `listpuzzles`

## Setup of puzzles
### Option 1:
- non-shapeshifting cuboid-shaped puzzles can be generated using `src/puzzles/cuboid_generator.py` They are automatically named and include all usual moves with standard names. You can immediately start playing with them.

- A similar tool exists to generate the megaminx puzzle, but is not flexible yet. While it is partially made to be adjustable to higher or lower ordered minx puzzles, this is not fully implemented yet.

### Option 2:
To add other puzzles, the following workflow is supported:
1. Create colored 3D points with Geogebra. Save the file to `src/ggb_files`
2. import .ggb files into the program using the main CLI (`import [filename]`)  
   Any invisible or auxilliary objects will be ignored. Only point objects will be imported. The command line output will show how many points were imported.
3. save the imported puzzle from the main CLI (`savepuzzle [puzzlename]`)
4. visually define moves by clicking on the points and where they are mapped from the main CLI (`newmove [movename]`, `endmove`)  
   If you call `newmove` while move definition is running, `endmove` will automatically be called to save the current move.  
   Current puzzles follow the convention that regular moves are clockwise and inverses marked with a "`" at the end. Some parts of the code run faster when this convention is followed.

While defining moves, the following commands/ functionalities can help:
- list all or just a single defined move (`listmoves`, `printmove [movename]`)
- show a given move (`move [movename]` `movename` can be a sequence of move names, separated by spaces)  
  This tries to automatically calculate rotation axes to animate the move. This may not always look correct. AFter the animation, points/ pieces are snapped to their correct positions. 3D Pieces may be oriented incorrectly though.
- rename an existing move (`rename [oldname] [newname]`)  
  Note that renaming moves will likely break any AI currently trained for this puzzle. When training an RL-based AI, a backup of the puzzle version it was trained on is copied to its training folder.
- delete an exisiting move (`delmove [movename]`)
- load a previously saved puzzle with it's moves from an .xml file (`loadpuzzle`)

You don't need to define all moves in one sitting. save the puzzle any time with `savepuzzle` and load it again later with `loadpuzzle [puzzlename]`. Editing moves in the CLI is not supported, but the puzzle files are human-readable and can be edited with a text editor, some courage and backup copies. So fixing any small errors in the move definitions is possible.

## Playing with Puzzles
- change shape of the puzzle by snapping it to a sphere, cube or it's initial shape (`snap [shape]`).
  This still shows points for stickers, but adds the snap shape for some visual guidance.
- Calculate and show 3D pieces (`drawpieces`)  
  By default, this creates pieces to fit the puzzle into a cuboid shaped bounding box. Some other shapes can be set by calling `clipshape [shape] [size]` first.
- scramble the puzzle randomly (`scramble [n_moves]`)
- reset the puzzle to solved state (`reset`) (only works properly when 3D pieces are not displayed)
- plot the success of the AI during training (basic plot, no legend, acis labels or any explanation) (`plot`)
- control animation speed (`animtime`). This defines the animation time of each move.

## Training an AI
There are three different automated solvers implemented in the program:
1. A greedy solver that tries to maximize the number of correct points with every move. This is mostly deterministic (only random when multiple moves have the same score) and can solve very few puzzles. It uses the same reward function as the RL-based AI solvers.
2. A V-table based AI that learns the state value function ($V(s)$) using Q-learning.  
   This function is represented as a table (large dictionary). This AI is learning based, but scales very poorly with state space size. It can solve small puzzles like a 2x2x2 cube in a few minutes, using a few MB of storage, but can't solve much larger puzzles. (`train_v`, `move_v`, `solve_v`)
3. An RL-based solver that trains an artificial neural network using PPO. This is by far the most capable solver. It learns to solve the 3x3x3 Rubik's cube in a few hours. This is the only solver that benefits from a GPU.

To train an AI using the RL solver, we strongly recommend adding symmetry and algorithm moves to the puzzle first. For large puzzles, this can significantly reduce training times. (For small ones it may not matter much or increase training times slightly.)
1. Detect rotational symmetries using `src/algorithm_generation/move_com_symmetry_detection.py` and define moves for them.  
   Resulting moves are named `rot_[c1][c2]`, where c1 is the first letter of the color rotated to the white face and c2 is the first letter of the color rotated to the green or lime face (if they exist). Otherwise, rotations have numeric names.
2. Generate Algorithms using `src/algorithm_generation/algorithm_generation_CLI.py`.  
   This script generates algorithms for a given puzzle. It is highly recommended to use this on puzzles with symmetry moves already defined. (move names starting with `rot_`, turning the whole puzzle in space). This prevents finding many algorithms that are just rotations of each other.
3. Train the AI using `src/ai_modules/nn_rl_testing.py` or `src/ai_modules/nn_rl_training.py`

## Evaluating an AI
There are three main ways of evaluating the learned policy of an AI:
1. Use `move_v [n_moves]` and `move_nn [n_moves]` to let the AI make a given number of moves.  
   This will print and animate the AI's moves, trying to solve the puzzle from its current state. If the puzzle is solved before the given number of moves, the AI will be stopped early.
2. Use `solve_v` (in the future also `solve_nn`) to let the AI solve the puzzle using its policy and weighted A* search using the AI's policy as a heuristic.  
   This will print and animate the AI's moves (if successful), trying to solve the puzzle from its current state. If the puzzle is solved before the given number of moves, the AI will be stopped early.

Finally, for RL agents, there are more tools implemented:
1. test AI on random scrambles `src/ai_modules/nn_rl_testing.test_from_file()`  
   Results are solved in test files to be evaluated later. This already prints a success rate.
2. Visualize test data using three provided tools:
   1. Action histograms `src/policy_analysis/action_histogram.py`  
    Shows how often each action was chosen.
   2. Move utilization plots `src/policy_analysis/move_utilization.py`  
      Shows when during the solve each move was usually used. This can enable insights into the agents strategy.
    3. Solution strategy visualization `src/policy_analysis/strategy_visualization.py`  
      Shows the order in which the points of the puzzle were solved on average. This can expose patterns like solving a specific face or piece type first.