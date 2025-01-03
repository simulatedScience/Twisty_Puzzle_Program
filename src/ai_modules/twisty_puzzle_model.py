import random

def scramble(
        state: list[int],
        actions: dict[str, list[list[int]]],
        max_moves: int = 30) -> list[str]:
    """
    scramble the puzzle starting at the given state by randomly applying [max_moves] actions
    `state` will be changed in-place!

    Argss:
        state (list[int]): list representing the initial state of the puzzle
        actions (dict[str, list[list[int]]]): a dictionary of all possible actions with unique names as keys
            - the values must be actions represented as lists of cycles
            - cycles are lists of state indices for permutations

    Returns:
        (list[str]) - scramble described as a list of actions
    """
    scramble = []
    for _ in range(max_moves):
        action_key = random.choice(list(actions.keys())) # choose a radom action
        perform_action(state, actions[action_key]) # perform this action
        scramble.append(action_key)                # save action to replicate the scramble
    return scramble


def perform_action(
        state: list[int],
        action: list[list[int]]) -> list[int]:
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    Args:
        state (list[int]): list representing the state
        action (list[list[int]]): list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
            
    Returns:
        (list[int]) - the new state (changed in-place and returned)
    """
    for cycle in action: # loop over all cycles in the move
        j = cycle[0]
        for i in cycle[-1:0:-1]:  # apply cycle
            state[i], state[j] = state[j], state[i]
    return state
