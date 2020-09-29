"""
module implementing a class to check whether or not twisty puzzle states are valid or not
"""

from copy import deepcopy

class State_Validator():
    def __init__(self, solved_state, pieces, n_colors):
        """
        This class checks whether or not a state of a puzzle is solveable (valid).

        inputs:
        -------
            solved_state - (list) of ints - list of color indices. Each integer corresponds to a unique color
            pieces - (list) of frozensets of ints- list of sets of point indices corresponding to all points making up each piece.
            n_colors - (int) - number of different colors in the puzzle
        """
        self.size = len(solved_state)
        self.n_colors = n_colors
        self.solved_state = solved_state
        if isinstance(pieces[0], frozenset):
            self.pieces = [list(piece) for piece in pieces]
        else:
            self.pieces = pieces
        self.color_numbers = [solved_state.count(i) for i in range(n_colors)]
        self.solved_piece_dicts = self._gen_piece_dicts(solved_state)

        self._has_duplicate_pieces = False
        self._has_piece_order = False


    def _gen_piece_dicts(self, state):
        """
        for every piece, count how often each color appears.

        inputs:
        -------
            state - (list) of ints - list of color indices representing a state

        returns:
        --------
            (list) of dicts - each dictionary represents the piece with the same index.
                keys of the dicts are the color indices,
                values are how often each color appears on that piece
        """
        piece_dicts = []
        for piece in self.pieces:
            piece_dict = dict()
            for point_index in piece:
                if hasattr(piece_dict, point_index):
                    piece_dict[point_index] += 1
                else:
                    piece_dict[point_index] = 1
            piece_dicts.append(piece_dict)
        return piece_dicts


    def validate_state(self, state):
        """
        check whether or not a given state is valid through several methods

        inputs:
        -------
            state

        returns:
        --------
            (int) or (float) - if the validity can be confirmed with 100% accuracy, returns an integer 0 or 1
                otherwise returns a float in [0,1] with the probability of state validity.
        """
        # check that every color is present in the correct number
        # runtime O(k*n) where k is the number of colors and n the number of points
        for i in range(n_colors):
            if state.count(i) != self.color_numbers[i]:
                return False

        # check that the pieces in the current state and the solved state are identical
        # runtime O(n*n)
        solved_piece_dicts = deepcopy(self.solved_piece_dicts)
        piece_dicts = self._gen_piece_dicts(state)
        while piece_dicts != dict() and solved_piece_dicts != dict():
            piece_dict = piece_dicts[0]
            for i, solved_piece_dict in enumerate(solved_piece_dicts):
                if piece_dict == solved_piece_dict:
                    del(piece_dicts[0])
                    del(solved_piece_dicts[i])
                    break
            else:
                # piece was not found in solution
                return False


    def _detect_duplicate_pieces(self):
        """
        check whether or not there are two identical pieces in the puzzle
        """

    def _detect_piece_order(self):
        """
        check whether or not there are pieces in the puzzle that can only be distinguished by the order of the colors on those pieces
        """
        for piece_dict in self.solved_piece_dicts:
            count = self.solved_piece_dicts.count(piece_dict)
            if count > 1:
                return True
        return False


if __name__ == "__main__":
    # ivy_cube states
    solved_state = (0, 1, 2, 0, 3, 4, 5, 3, 2, 1, 4, 5, 0, 2, 3, 4, 1, 5)
    S1 = (0, 1, 2, 3, 4, 0, 3, 2, 5, 1, 4, 5, 2, 5, 4, 0, 1, 3)
    S2 = (1, 2, 0, 3, 4, 0, 3, 2, 5, 5, 1, 4, 0, 2, 4, 1, 3, 5)
    S3 = (1, 2, 0, 4, 0, 3, 3, 2, 5, 4, 5, 1, 2, 1, 4, 3, 5, 0)
    S4 = (2, 0, 1, 4, 0, 3, 5, 3, 2, 1, 4, 5, 0, 4, 3, 5, 1, 2)
    S5 = (0, 1, 2, 0, 3, 4, 5, 3, 2, 5, 1, 4, 0, 1, 3, 2, 4, 5)
    S6 = (0, 1, 2, 4, 0, 3, 5, 3, 2, 4, 5, 1, 5, 1, 4, 2, 3, 0)
    S7 = (1, 2, 0, 3, 4, 0, 5, 3, 2, 5, 1, 4, 0, 5, 3, 1, 4, 2)