"""
functions to prepare data about a puzzle given from the animation for the ai training.
"""
def state_for_ai(vpy_vectors):
    """
    convert the current state of the puzzle into it's representation for the ai
    the colors are taken from the vpython objects

    inputs:
    -------
        vpy_vectors - (list) of vpython vectors - a list of vpython vectors representing colors in the puzzle

    returns:
    --------
        (list) of ints - state of the puzzle as list of color indices
        (list) - list of colors occuring in the puzzle
            index in the list is the same as it's representation in the ai state
    """
    color_list = []
    ai_state = []
    for vec in vpy_vectors:
        if not vec in color_list:
            color_list.append(vec)
            color_index = len(color_list)-1
        else:
            color_index = 0
            while color_list[color_index] != vec:
                color_index += 1
        ai_state.append(color_index)
    return ai_state, color_list


def compress_state(state, n_colors):
    """
    Compresses a state given as a tuple of integers into a single integer.
    Each int of the state is saved with a fixed number of bits inside the
        final integer.

    inputs:
    -------
        state - (tuple) of (int) - the state of a twisty puzzle as a list
            or tuple of color-indices
        n_colors - (int) - number of unique colors in the puzzle

    returns:
    --------
        (int) - the state encoded in a single (potentially large) integer
    """
    bin_digits = n_colors.bit_length()
    state_int = 1
    for s in state:
        state_int <<= bin_digits
        state_int |= s
    return state_int


def decompress_state(state_int, n_colors, state_len):
    """
    Recovers the state tuple from a state integer.

    inputs:
    -------
    """
    bin_digits = n_colors.bit_length()
    state = list()
    k = 2**bin_digits - 1
    state_index = 0
    while state_index != state_len:
        state.append(state_int & k)
        state_int >>= bin_digits
        bit_number += bin_digits
        state_index += 1
        state.reverse()
    # state.reverse()
    return state