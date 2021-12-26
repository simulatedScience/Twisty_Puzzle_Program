"""
functions to analyse move sequences to find algorithms
"""

class Algorithm_Analyser():
    def __init__(self, moves_dict, n_pieces):
        """
        """

def analyse_alg(move_list, moves_dict):
    """
    calculate some information about the move sequence:
    - order
    - number of changed pieces
    - order of piece permutation (movement of pieces without checking piece rotation)
    - ? order of piece rotation ?
    - type of algorithm
        a) only moves pieces, keeping their rotation
        b) only rotates pieces, keeping their positions
        c) rotating and moving pieces
    """