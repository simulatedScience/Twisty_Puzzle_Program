# Program structure

## Console Interface
### Tasks
- handles all user interaction
  - input of commands
  - interpretation and validation of those commands
    - print error messages and command feedback to the user
- acts according to these commands:
  - loads geogebra files by making use of the scripts implemented in *ggb_import*
  - initializes a class for an imported puzzle (see *puzzle_class*)
  - stops display of animation of a puzzle by terminating the class via `close_animation`

## Puzzle Class
### Tasks
- stores all information about a puzzle:
  - current 3d objects (using vpython)
  - current state of those objects
- can print out all currently defined moves via `listmoves`
- changes the stored information and controls the animation accordingly
- save all stored information about the puzzle in files
- load puzzle information from a file
  - !!! This may cause a conflict:

    when geogebra files are loaded, a puzzle class will be created from the outside.
- initialize AI class to train an AI to solve the puzzle
  - start Q-Learning via `train_Q_learning`
  - start Neural Network training via `train_NN`

## AI Class
Are these seperate classes for Neural Networks and Q-Learning? If so, how exactly do they relate?

### Tasks
- stores information about the Q-table
- stores solved state and moves of the puzzle
- trains the Q-table via self-play
- calculates an AI-action based on a given state and algorithm (either Q-Learning or NN; only if previously trained)
- saves information (Q-table, NN weights and structure) for the AI in files
- loads AI information (Q-table, NN weights and structure) from a file