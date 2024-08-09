# AI framework
This document describes the basic ideas of the different AIs implemented for solving twisty puzzles as well as the AI base class they share to interface with the program.

## Related Files
See `NN inputs for Twisty Puzzles.md` for possible inputs for the NNs. There, we consider different options and explain advantages and disadvantages of each.

See `smarter_ai.md` for detailed considerations on how to build the next AI that would likely be capable of solving complex puzzles with less compute than previously required while creating solutions that are easier  for humans to understand.


## AI base class
`puzzle_base_ai.py` implements the base class for all AIs. It provides the following methods:

* `__init__(self, actions_dict, solved_state)` - initializes the AI with the given puzzle
* `train(self, n_epochs, max_time, ...)` - trains the AI for the given number of epochs or until the given time limit is reached
* `play_episode(self, max_moves, max_time, ...)` - plays one episode of the puzzle, i.e. solves the puzzle from the current state  
  Each episode should be independent of other episodes such that multiple episodes can be run in parallel.
* `choose_action(self, state)` - returns the action to be performed on the given state, this is the place to implement different exploration and action policies
* `update_model(self, transitions)` - updates the AI's model based on a given list of transitions

