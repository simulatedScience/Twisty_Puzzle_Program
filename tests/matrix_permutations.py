import scipy.sparse

def convert_move_dict(move_dict, n_points):
    """
    generate a dictionary to represent the moves (permutations)
        as matrices. This uses scipy.sparse.csr_matrix.
    
    inputs:
    -------
        move_dict - (dict) - keys are movenames,
            values are permutations in cyclic notation
        n_points - (int) - number of points in the puzzle
    """
    data = [1]*n_points
    matrix_moves = scipy.sparse.csr_matrix()