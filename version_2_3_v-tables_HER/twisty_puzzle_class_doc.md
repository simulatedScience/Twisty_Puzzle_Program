# Introduction
Every twisty puzzle will require some basic information to be stored.
There are also quite a few functions that would make sense as puzzle-specific methods.

Therefor we will create a class that represents a given puzzle.

# Requirements
the different tasks require different sets of information.
i.e. in the animation it makes sense to store the state of the puzzle directly as a list of vpython objects. However for the AI this is completely unnecessary and would only slow down the training process.

So we need to make a choice how to implement this.
- There will probably be two seperate classes.
- Can one inherit and build on top of the other? Or are they completely seperate?

Let's list exactly what information is needed for each task:

## for animation
We want to show the puzzle using vpython and allow all kinds of interaction.
### Minimum information
#### Variables
  - dictionary of all possible moves
  - center of mass of the 3d points - _used to calculate rotation axis_
  - correct position of the 3d points - _used to prevent numerical errors during animation_
  - (temporary storage for functions assigned to clickevents)
  - (list of displayed vpython objects)
  - (currently displayed canvas)
#### Methods
  - `perform_move`
  - `scramble_puzzle` - _randomly scramble the puzzle so the user doesn't have to do it manually_
### Potential expansion
  - name of the puzzle - _mainly for determining file names_

## for AI
This should be a simplified, faster representation of the puzzle used for training the AI to solve the puzzle.
### Why this should be a class
There is a bit of puzzle-specific data that the AI needs to know to perform any action on the puzzle. This data is specified below under _Variables_.

Using a class could also be used to cut down on the massive number of arguments needed to pass beteween all the learning functions.

All those arguments make it quite confusing and add unnecessary length to doc-strings.
### Minimum information
#### Variables
  - dictionary of all possible moves
  - a fixed _"solved"_ state - _essential for training the ai_
    - may also be necessary to know when so stop solving the puzzle
    - this could also be changed to make a pattern on a puzzle
  - current AI data (Q-table / Network weights)
  - (current puzzle state) - _could be useful so the state doesn't need to be converted for every move. Instead every time a move is performed this variable would update_
    - keeping this in sync with the state of the animated puzzle may be difficult if the user can interfere.
  - reward dictionary
#### Methods
  - `train_ai` - train the AI to solve the puzzle
    - this may be split into two functions, one for pure Q-Learning and one for additional Neural Networks
    - `perform_move` - _to learn about the following state under a chosen action_
    - `scramble_puzzle` - _to create an inital state for training_
    - `solve_puzzle` = `play_episode` - _maybe without learning during solving_
  - `get_move` - get the best move from a given state
    - the relation of the two classes dictated the requirements for the state representation
  - `save_ai` - save the current Q-table or Neural Network of the AI
  - `load_ai` - load AI from a file

### Potential expansion
  - automatically load AI info (Q-Table / Neural Network) from a file (if availiable) when this class is initialized
    - simply try executing `load_ai`
  - name of the puzzle - _mainly for determining file names_

## summary