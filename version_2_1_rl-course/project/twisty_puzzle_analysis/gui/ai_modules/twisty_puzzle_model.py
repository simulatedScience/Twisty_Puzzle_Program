import random

def scramble(state, actions, max_moves=30):
    """
    scramble the puzzle starting at the given state by randomly applying [max_moves] actions
    the state list will be changed in-place
    inputs:
    -------
        state - (list) of ints - list representing the initial state of the puzzle
        actions - (dict) - a dictionary of all possible actions with unique names as keys
            - the values must be actions represented as lists of cycles
            - cycles are lists of state indices for permutations
    
    returns:
    --------
        (list) - scramble described as a list of actions
    """
    scramble = []
    for _ in range(max_moves):
        action_key = random.choice(list(actions.keys())) # choose a radom action
        perform_action(state, actions[action_key]) # perform this action
        scramble.append(action_key)                # save action to replicate the scramble
    return scramble


def perform_action(state, action):
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    inputs:
        state - (list) of ints - list representing the state
        action - (list) of lists of ints - list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
    """
    for cycle in action: # loop over all cycles in the move
        j = cycle[0]
        for i in cycle:  # apply cycle
            state[i], state[j] = state[j], state[i]
    return state