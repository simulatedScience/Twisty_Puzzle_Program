from math import ceil
import pickle
import random
import time

# def save_bin_dict(max_n=1e6):
#     D = {bin(i):1/i for i in range(1,max_n)}
#     with open("bin_dict","wb") as bin_dict:
#         pickle.dump(D, bin_dict, protocol=4)


# def save_int_dict(max_n=1e6):
#     D = {i:1/i for i in range(1,max_n)}
#     with open("int_dict","wb") as bin_dict:
#         pickle.dump(D, bin_dict, protocol=4)


def save_compressed_dict(state_dict, n_colors=6):
    start = time.process_time()
    comp_dict = {tuple(compress_state(state, n_colors)):value for state, value in state_dict.items()}
    with open("compressed_dict","wb") as file:
        pickle.dump(comp_dict, file, protocol=4)
    end = time.process_time()
    print(f"saved the dictionary in {end-start:.3} s")

def save_regular_dict(state_dict):
    start = time.process_time()
    with open("regular_dict","wb") as file:
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
    bin_digits = n_colors.bit_length()
    compact_state = [1]
    bit_number = 1
    for s in state:
        if bit_number >= 31:
            bit_number = 1
            compact_state.append(1)
        compact_state[-1] <<= bin_digits
        compact_state[-1] |= s
        bit_number += bin_digits
    return compact_state


def decompress_state(compact_state, n_colors, state_len):
    bin_digits = n_colors.bit_length()
    state = list()
    k = 2**bin_digits - 1
    state_index = 0
    for sub_int in compact_state:
        sub_state = list()
        bit_number = 0
        while bit_number < 30+bin_digits and state_index != state_len:
            sub_state.append(sub_int & k)
            sub_int >>= bin_digits
            bit_number += bin_digits
            state_index += 1
        sub_state.reverse()
        state.extend(sub_state)
    # state.reverse()
    return state


if __name__ == "__main__":
    save_dummy_dict(max_n=10**6, n_colors=6, n_stickers=54)


    # max_n = int(1e7)
    # save_bin_dict(max_n)
    # save_int_dict(max_n)
    # state = [0,3,1,2,2,3,1,0,0,0,2,3,1,1,2,3]
    # state = [0,3,1,2,2,3,1,0,0,0,2,3,1,1,2,3,0,3,1,0,2,2,1,3]
    # import random
    # random.seed(2)
    # symbols = list(range(n_colors))
    # state = [random.choice(symbols) for _ in range(24)]
    # n_colors = len(set(state))
    # compressed_state = compress_state(state, n_colors)
    # print(compressed_state, [len(bin(i))-2 for i in compressed_state])
    # new_state = decompress_state(compressed_state, n_colors, len(state))
    # print(state)
    # print(new_state)
    # print(state==new_state)
