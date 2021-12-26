import random
import time

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


def perform_action(state_int, action, shift_list, state_map):
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    inputs:
    -------
        state - (list) of ints - list representing the state
        action - (list) of lists of ints - list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
        power_list - (list) or (tuple) - list of powers of the number n of colors in the puzzle.
            i.e.: `powerlist = [n*i for i in range(k)]` where k is the number of points in the puzzle.
    """
    for cycle in action: # loop over all cycles in the move
        state_i = (state_int>>shift_list[cycle[-1]]) & state_map
        for i in cycle: # apply cycle
            state_j, state_i = state_i, (state_int>>shift_list[i]) & state_map
            state_int ^= state_i << shift_list[i]
            state_int |= state_j << shift_list[i]
    return state_int


def compress_state(state, bin_digits):
    state_int = 1
    for s in state:
        state_int <<= bin_digits
        state_int |= s
    return state_int


def decompress_state(state_int, bin_digits, state_len):
    state = list()
    k = 2**bin_digits - 1
    state_index = 0
    for _ in range(state_len):
        state.append(state_int & k)
        state_int >>= bin_digits
        # bit_number += bin_digits
        # state_index += 1
    state.reverse()
    # state.reverse()
    return state


if __name__ == "__main__":
    from copy import deepcopy
    # for k in range(100):
    # random.seed(26)
    n_colors = 6
    symbols = list(range(n_colors))
    action = [[0,1,2], [3,7,5], [4,6,12,15,10], [9,8,13,14], [19,18,17,20,23,22]]
    # action = [[0,1]]
    # succ = 0
    N = 2000000
    tot_a_time = 0
    tot_b_time = 0
    for _ in range(N):
        state = [random.choice(symbols) for _ in range(24)]
        state2 = deepcopy(state)
        start = time.process_time_ns()
        a = perform_action(state, action)
        end = time.process_time_ns()
        a_time = end-start
        b, b_time = test_compress_action(state2, action, n_colors)
        tot_a_time += a_time
        tot_b_time += b_time
    #     if a == b:
    #         succ += 1
    # print(f"{succ/N*100: .4} % were correct")
    print(f"Regular action took on average {tot_a_time/N: .6} ns.")
    print(f"Compressed action took on average {tot_b_time/N: .6} ns.")
    print(f"{N} Regular action took a total time of {tot_a_time/10**9} s.")
    print(f"{N} Compressed action took a total time of {tot_b_time/10**9} s.")
    print(f"Compression actions are {tot_b_time/tot_a_time: .3} times slower.")