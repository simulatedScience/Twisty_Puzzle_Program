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
