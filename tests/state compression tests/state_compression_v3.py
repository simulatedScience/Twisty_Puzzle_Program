from os import stat
import pickle
import random
import time


def save_compressed_dict(state_dict, n_colors=6):
    start = time.process_time()
    comp_dict = {compress_state(state, n_colors):value for state, value in state_dict.items()}
    with open("compressed_dict_v3_2","wb") as file:
        pickle.dump(comp_dict, file, protocol=4)
    end = time.process_time()
    print(f"saved the dictionary in {end-start:.3} s")


def save_regular_dict(state_dict):
    start = time.process_time()
    with open("regular_dict_v3_2","wb") as file:
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


def compress_state(state, n_colors):
    state_int = 0
    for i,s in enumerate(state):
        state_int += s*n_colors**i
    return state_int


def decompress_state(state_int, n_colors, state_len):
    state = list()
    for i in range(state_len):
        # k = n_colors**i
        s = state_int % n_colors
        state.append(s)
        # print(state_int, s)
        state_int //= n_colors
    return state


def perform_compressed_action(state_int, action, power_list):
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    inputs:
    -------
        state - (list) of ints - list representing the state
        action - (list) of lists of ints - list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
        power_list - (list) or (tuple) - list of powers of the number n of colors in the puzzle.
            i.e.: `powerlist = [n**i for i in range(k)]` where k is the number of points in the puzzle.
    """
    for cycle in action: # loop over all cycles in the move
        j = cycle[0]
        state_i = state_int//power_list[j] % power_list[0]
        for i in cycle[1:]:  # apply cycle
            state_j, state_i = state_i, state_int//power_list[i] % power_list[0]
            # state_int += state_i * power_list[j]
            state_int += (state_j-state_i) * power_list[i]
    return state_int

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


############################################################################################
######################                   NEW                        ########################
############################################################################################


def compress_state(state, n_colors):
    state_int = 0
    for i,s in enumerate(state):
        state_int += s*n_colors**i
    return state_int


def decompress_state(state_int, n_colors, state_len):
    state = list()
    for i in range(state_len):
        # k = n_colors**i
        s = state_int % n_colors
        state.append(s)
        # print(state_int, s)
        state_int //= n_colors
    return state


def perform_compressed_action(state_int, action, power_list, n_colors):
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    inputs:
    -------
        state - (list) of ints - list representing the state
        action - (list) of lists of ints - list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
        power_list - (list) or (tuple) - list of powers of the number n of colors in the puzzle.
            i.e.: `powerlist = [n**i for i in range(k)]` where k is the number of points in the puzzle.
    """
    for cycle in action: # loop over all cycles in the move
        j = cycle[-1]
        state_i = (state_int//power_list[j]) % n_colors
        # state_int -= state_i*power_list[j]
        for i in cycle: # apply cycle
            state_j, state_i = state_i, (state_int//power_list[i]) % n_colors
            state_int += (state_j-state_i) * power_list[i]
        # state_int += state_i*power_list[j]
    return state_int


def test_compress_action(state, action, n_colors):
    state_len = len(state)
    power_list = [n_colors**i for i in range(state_len)]
    x = compress_state(state, n_colors)
    # print(decompress_state(x, n_colors, state_len))
    start = time.process_time_ns()
    x = perform_compressed_action(x, action, power_list, n_colors)
    end = time.process_time_ns()
    return decompress_state(x, n_colors, state_len), end-start


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


# if __name__ == "__main__":
    # save_dummy_dict(max_n=10**6, n_colors=6, n_stickers=54)
    # random.seed(2)
    # n_colors = 6
    # symbols = list(range(n_colors))
    # succ = 0
    # N = 1
    # for _ in range(N):
    #     # state = [random.choice(symbols) for _ in range(24)]
    #     state = [5, 1, 5, 1, 3, 4, 4, 0, 1, 3, 0, 5, 5, 4, 4, 1, 5, 3, 1, 5, 3, 5, 1, 5]
    #     print(state)
    #     compressed_state = compress_state(state, n_colors)
    #     # print(compressed_state)
    #     new_state = decompress_state(compressed_state, n_colors, len(state))
    #     # if state != new_state:
    #     print(new_state)
    #     if state==new_state:
    #         succ += 1
    # print(f"{succ/N*100: .4} % were correct")