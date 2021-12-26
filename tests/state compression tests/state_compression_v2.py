import pickle
import random
import time

def perform_action(state, action):
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    inputs:
    -------
        state - (list) of ints - list representing the state
        action - (list) of lists of ints - list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
    """
    for cycle in action: # loop over all cycles in the move
        j = cycle[0]
        for i in cycle[1:]:  # apply cycle
            state[i], state[j] = state[j], state[i]
    return state

def save_compressed_dict(state_dict, n_colors=6):
    start = time.process_time()
    comp_dict = {compress_state(state, n_colors):value for state, value in state_dict.items()}
    with open("compressed_dict_v2","wb") as file:
        pickle.dump(comp_dict, file, protocol=4)
    end = time.process_time()
    print(f"saved the dictionary in {end-start:.3} s")


def save_regular_dict(state_dict):
    start = time.process_time()
    with open("regular_dict_v2","wb") as file:
        pickle.dump(state_dict, file, protocol=4)
    end = time.process_time()
    print(f"saved the dictionary in {end-start:.3} s")


def save_dummy_dict(max_n=1e5, n_colors=6, n_stickers=24):
    symbols = list(range(n_colors))
    dummy_dict = dict()
    for _ in range(max_n):
        state = tuple([random.choice(symbols) for _ in range(n_stickers)])
        dummy_dict[state] = random.random()
    save_regular_dict(dummy_dict)
    save_compressed_dict(dummy_dict, n_colors)


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


def perform_compressed_action(state_int, action, shift_list, state_map):
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


def test_compress_action(state, action, n_colors):
    state_len = len(state)
    bin_digits = n_colors.bit_length()
    shift_list = [bin_digits*i for i in range(state_len-1, -1, -1)]
    state_map = 2**bin_digits -1
    x = compress_state(state, bin_digits)
    # print(decompress_state(x, n_colors, state_len))
    start = time.process_time_ns()
    x = perform_compressed_action(x, action, shift_list, state_map)
    end = time.process_time_ns()
    return decompress_state(x, bin_digits, state_len), end-start


if __name__ == "__main__":
    from copy import deepcopy
    n_colors = 6
    symbols = list(range(n_colors))
    action = [[0,1,2], [3,7,5], [4,6,12,15,10], [9,8,13,14], [19,18,17,20,23,22]]
    # action = [[0,1]]
    # succ = 0
    N = 10000
    tot_a_time = 0
    tot_b_time = 0
    for _ in range(N):
        state = [random.choice(symbols) for _ in range(24)]
        state2 = deepcopy(state)
        # print(state2)
        start = time.process_time_ns()
        a = perform_action(state, action)
        end = time.process_time_ns()
        a_time = end-start
        b, b_time = test_compress_action(state2, action, n_colors)
        tot_a_time += a_time
        tot_b_time += b_time
    # print(f"{succ/N*100: .4} % were correct")
    print(f"Regular action took on average {tot_a_time/N: .6} ns.")
    print(f"Compressed action took on average {tot_b_time/N: .6} ns.")
    print(f"{N} Regular action took a total time of {tot_a_time/10**9} s.")
    print(f"{N} Compressed action took a total time of {tot_b_time/10**9} s.")
    if tot_a_time > 0:
        print(f"Compression actions are {tot_b_time/tot_a_time: .3} times slower.")
    # save_dummy_dict(max_n=10**6, n_colors=6, n_stickers=54)
    # n_colors = 6
    # symbols = list(range(n_colors))
    # succ = 0
    # N = 10000
    # for _ in range(N):
    #     state = [random.choice(symbols) for _ in range(24)]
    #     compressed_state = compress_state(state, n_colors)
    #     new_state = decompress_state(compressed_state, n_colors, len(state))
    #     if state==new_state:
    #         succ += 1
    # print(f"{succ/N*100: .4} % were correct")