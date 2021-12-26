"""
module implementing a class to check whether or not twisty puzzle states are valid or not
"""

import random
from copy import deepcopy

from sympy.combinatorics import Permutation
from sympy.combinatorics.perm_groups import PermutationGroup
import vpython as vpy

from ..vpython_modules.vpy_rotation import get_com


class State_Validator():
    def __init__(self, solved_state, pieces, puzzle_group, vpy_objects):
        """
        This class checks whether or not a state of a puzzle is solveable (valid).

        inputs:
        -------
            solved_state - (list) of ints - list of color indices. Each integer corresponds to a unique color
            pieces - (list) of frozensets of ints- list of sets of point indices corresponding to all points making up each piece.
            puzzle_group - (PermutationGroup) - a permutation group object
                from sympy.combinatorics.perm_groups
        """
        self.size = len(solved_state)
        self.n_colors = len(set(solved_state))
        self.solved_state = solved_state
        self.puzzle_group = puzzle_group
        if isinstance(pieces[0], (set, frozenset)):
            self.pieces = [list(piece) for piece in pieces]
        else:
            self.pieces = pieces
        self.vpy_objects = vpy_objects
        self.sort_all_points()
        self.color_numbers = [solved_state.count(i) for i in range(self.n_colors)]
        self.solved_piece_dicts, self.solved_piece_lists = \
                self._gen_pieces_info(solved_state)

        self._has_duplicate_pieces = self._detect_duplicate_pieces()


    def sort_all_points(self):
        """
        sort the 3d points of each piece to make state validation much more efficient.
        We sort such that the resulting state meets the following criteria:
            1. points belonging to pieces with few points are listed before those
                that belong to pieces with more points.
            2. all points belonging to the same piece are right next to each other.
            3. the points within a piece are sorted counterclockwise
                when viewed from the outside towards the CoM of the puzzle.

        Instead of sorting the actual state list, we just calculate the permutation that
            leads from the unchanged state to the sorted state.
        That way we don't have to change all moves, saved states of the AI or the Neural Networks.

        returns:
        --------
            None

        outputs:
        --------
            write the sorting permutation to self._sort_permutation
        """
        self._sort_permutation = list()
        for piece in sorted(self.pieces, key=len): # loop over sorted self.pieces for rule 1
            # append sorted points of the whole piece at once for rule 2 & 3
            self._sort_permutation += sort_piece(piece)
            # redefine pieces
            stop = len(self._sort_permutation)
            start = stop - len(piece)
            piece[:] = [i for i in range(start, stop)]
        del(self.vpy_objects)


    def sort_piece(self, piece):
        """
        sort the 3d points within the given piece
        """
        point_coordinates = [self.vpy_objects[i].pos for i in piece]
        piece_com = get_com(point_coordinates)
        start_vec = point_coordinates[0] - piece_com
        def sort_face(point_index):
            """
            return three values for sorting (in that order):
                1. angle between the starting vector and `point_coordinates[point_index] - piece_com`
                2. angle between `piece_com` and `point_coordinates[point_index] - piece_com`
                3. magnitude of `point_coordinates[point_index] - piece_com`

            inputs:
            -------
                index of an element in piece
            """
            current_vec = point_coordinates[point_index] - piece_com
            angle = vpy.diff_angle(start_vec, current_vec) * \
                sign(vpy.dot(vpy.cross(start_vec, current_vec), piece_com))
            return (angle, vpy.diff_angle(piece_com, current_vec), current_vec.mag)
        return sorted(piece, key=sort_face)


    def sort_state(self, state):
        """
        apply `self._sort_permutation` to the given state to sort the 3d points within the pieces

        inputs:
        -------
            state - (list) of (int)s - state as list of color indices

        returns:
        --------
            (list) of (int)s - sorted state as list of color indices
        """
        return [state[i] for i in self._sort_permutation]


    def get_valid_permutation(self, state):
        """
        return the given state as a solveable permutation
        """
        sorted_state = self.sort_state(state)
        piece_indices = list()
        for piece_dict in self.pieces_dict:
            piece_indices.append(self.pieces_dicts, get_index(piece))


    def validate_state(self, state):
        """
        check whether or not a given state is valid through several methods
        1. check that each color appears the correct number of times
        2. check that every piece still exists (defined as a specific unordered list of colors)
        3. calculate the permutation that leads from the solved state to the current one.
            check that this perm is in the permutation group specific to the puzzle.

        inputs:
        -------
            state - (list) - list of color indices representing the current puzzle state

        returns:
        --------
            (int) or (float) - if the validity can be confirmed with 100% accuracy,
                returns an integer 0 or 1. Otherwise returns a float in ]0,1[
                representing the probability of state validity.
        """
        # check that every color is present in the correct number
        # runtime O(k*n) where k is the number of colors and n the number of points
        for i in range(self.n_colors):
            if state.count(i) != self.color_numbers[i]:
                return 0 # given state is invalid
        # check that the pieces in the current state and the solved state are identical
        piece_dicts, piece_lists = self._gen_pieces_info(state)
        pieces_perms = self._find_pieces_permutation(state, piece_dicts)
        if pieces_perms == 0:
            return 0 # given state is invalid
        # convert permutation of the pieces into actual puzzle permutation
        perms = list()
        for pieces_perm in pieces_perms:
            perms += self._find_all_point_permutations(state, pieces_perm, piece_lists)
        return validity


    def _find_pieces_permutation(self, state, piece_dicts):
        """
        1. check that every piece still exists in the given state
        2. if so, determine all possible permutations of pieces that could
            result in the given state

        inputs:
        -------
            state - (list) of (int)s - list of color indices representing the current state
            piece_dicts - (list) of (dict)s - list with one dictionary for each piece
                keys in the dict are all color indices in the piece,
                values are how often that color appears in the piece.

        returns:
        --------
            (list) of (list)s of (int)s - list of all possible piece permutations
                given as the bottom row of the long permutation notation:
                Example:
                    the permutation (1 2 3 4 5 6)
                                    (2 4 5 1 3 6)
                    will be returned as [2,4,5,1,3,6]
        """
        perms = [[]]
        for piece_dict in self.solved_piece_dicts:
            indices = get_index(piece_dicts, piece_dict)
            if len(indices) == 0:
                # piece was not found in solution
                return 0 # current state invalid
            elif len(indices) == 1: # append new index to all existing permutations
                i = indices[0]
                for perm in perms:
                    perm.append(i)
                del(i, perm)
            else: # append every new indeces to all existing permutations
                indices = random.choices(indices, k=2)
                n_perms = len(perms)
                perms *= len(indices)
                for k, new_i in enumerate(indices):
                    for perm in perms[k*n_perms:(k+1)*n_perms]:
                        perm.append(new_i)
        return perms


    def _find_all_point_permutations(self, state, pieces_perm, piece_lists):
        """
        Given the permutation of the pieces, find all possible permutations of the points,
            that could result in the given state.

        inputs:
        -------
            state - (list) of (int)s - list of color indices representing the current state
            pieces_perm - (list)s of (int)s - one piece permutation
                given as the bottom row of the long permutation notation:
                Example:
                    the permutation (1 2 3 4 5 6)
                                    (2 4 5 1 3 6)
                    must be given as [2,4,5,1,3,6]
            piece_list - (list) of (list)s of (int)s - list of all detected pieces 
                as lists of point indices belonging to each piece

        returns:
        --------
            (list) of (list)s of (int)s - list of all possible point permutations
                given as the bottom row of the long permutation notation:
                Example:
                    the permutation (1 2 3 4 5 6)
                                    (2 4 5 1 3 6)
                    will be returned as [2,4,5,1,3,6]
        """
        perms = [dict()]
        # generate all possible permutations as dictionaries
        for piece_index, piece in enumerate(self.pieces):
            new_piece_index = pieces_perm[piece_index]
            new_piece = self.pieces[new_piece_index]
            new_piece_list = piece_lists[new_piece_index]
            for old_index, color in zip(piece, self.solved_piece_lists[piece_index]):
                new_color_indices = get_index(new_piece_list, color)
                if len(new_color_indices) == 0:
                    print("Error. color not found. piece permutation was incorrect")
                if len(new_color_indices) == 1:
                    for perm_dict in perms:
                        perm_dict[old_index] = new_piece[new_color_indices[0]]
                else:
                    n_perms = len(perms)
                    perms *= len(new_color_indices)
                    for k, new_i in enumerate(new_color_indices):
                        for perm_dict in perms[k*n_perms:(k+1)*n_perms]:
                            perm_dict[old_index] = new_i
        # convert permutation dictionaries to lists
        perm_lists = [[perm_dict[i] for i in range(len(self.solved_state))] \
                for perm_dict in perms]
        return perm_lists



    def _gen_pieces_info(self, state):
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
        piece_dicts = list()
        piece_lists = list()
        for piece in self.pieces:
            piece_dict = dict()
            piece_list = list()
            for point_index in piece:
                color = state[point_index]
                if hasattr(piece_dict, "color"):
                    piece_dict[color] += 1
                else:
                    piece_dict[color] = 1
                piece_list.append(color)
            piece_dicts.append(piece_dict)
            piece_lists.append(piece_list)
        return piece_dicts, piece_lists


    def _check_perm(self, perm):
        """
        check whether or not the given permutation is in the puzzle group

        inputs:
        -------
            perm - (list) of (int) - one potential permutation
                given as lists representing the bottom row of the
                long standard notation for permutations (NOT cyclic notation)
                Example:
                    the permutation (1 2 3 4 5 6)
                                    (2 4 5 1 3 6)
                    should be given as [2,4,5,1,3,6]

        returns:
        --------
            (bool) - True if the permutation represents a solveable state, otherwise False
        """
        perm = get_cycles(perm)
        perm = Permutation(perm, size=len(self.solved_state))
        return perm in self.puzzle_group


    def _detect_duplicate_pieces(self):
        """
        check whether or not there are two identical pieces in the puzzle
        pieces count as identical if:
            1. all appearing colors are the same
            2. the number how often each color appears are identical
        """
        for i, piece_dict in enumerate(self.solved_piece_dicts):
            if piece_dict in self.solved_piece_dicts[i+1:]:
                return True
        return False


def get_index(iterable, elem):
    """
    get all indices where elem appears in the given iterable

    inputs:
    -------
        iterable - any iterable, i.e. (list) - any iterable object.
            items must support equality checks
        elem - (any) - any element that could be in the iterable and supports equality checks

    returns:
    --------
        (list) - list of all indices where elem appeared.
            empty list if elem wasn't found.
    """
    indices = list()
    for i, item in enumerate(iterable):
        if item == elem:
            indices.append(i)
    return indices


def get_piece_permutations(solved_piece, piece):
    """
    determine all possible permutations of the points within one sorted piece

    inputs:
    -------
        solved_piece - (list) of (int)s - list of color indices
        piece - (list) of (int)s - list of color indices

    returns:
    --------
        (list) of (list)s of (int)s - possible permutations
            empty list if the given pieces are not the same.

    Examples:
    ---------
        >>> get_piece_permutations([1,1,2,2], [2,1,1,2])
        [[1,2,3,0]]
        >>> get_piece_permutations([1,2,1,2], [2,1,2,1])
        [[1,2,3,0], [3,0,1,2]]
        >>> get_piece_permutations([1,1,1,1], [1,1,1,1])
        [[0,1,2,3], [1,2,3,0], [2,3,0,1], [3,0,1,2]]
        >>> get_piece_permutations([1,2,3,4], [1,1,2,2])
        [] # pieces aren't the same
    """
    n = len(piece)
    if len(solved_piece) != n:
        return list()
    comp_list = solved_piece*2
    perms = list()
    for i in range(n):
        if comp_list[i:i+n] == piece:
            perms.append([k%n for k in range(i,i+n)])
    return perms


def get_cycles(perm):
    """
    calculate the cyclic notation for a given permutation

    inputs:
    -------
        perm - (list) of (int)s - permutation given as a list of integers.
            this list represents the bottom row of a permutation:
            Example:
                the permutation (1 2 3 4 5 6)
                                (2 4 5 1 3 6)
                must be given as [2,4,5,1,3,6]

    returns:
    --------
        (list) of (list)s of (int)s - a list of cycles describing the same permutation
            The example above would result in [[1,2,4],[3,5]]
    """
    cycles = list()
    cycles_set = set()
    for i in range(len(perm)):
        if not i in cycles_set:
            ni = perm[i]
            cycle = [i]
            while ni != i:
                cycle.append(ni)
                cycles_set.add(ni)
                ni = perm[ni]
            if len(cycle)>1:
                cycles.append(tuple(cycle))
    return cycles


def gen_puzzle_group(moves, n_points):
    """
    generate the group representing the puzzle.
    The group will be a subgroup of the symmetric group with order [n_points]
        and it will have the given moves as generators.

    inputs:
    -------
        moves - (list) of (list)s of (list)s of (int)s - list of moves represented
            as lists of cycles defining the permutation.
        n_points - (int) - number of points in the puzzle
            n_points = len(puzzle.SOLVED_STATE)

    returns:
    --------
        (sympy.combinatorics.perm_groups.PermutationGroup) -
            a sympy permutation group generated by the moves.
    """
    perms = list()
    for move in moves:
        perms.append(Permutation(move, size=n_points))
    return PermutationGroup(perms)


def sign(n):
    """
    return sign of the given number n. -1 for negative numbers, +1 for all edge cases (0, nan, ...)
    """
    if n < 0:
        return -1
    return 1


if __name__ == "__main__":
    from piece_detection import detect_pieces
    # ivy cube moves:
    wrg = [(3, 4, 5), (12, 14, 15)]
    wrg2 = [(5, 4, 3), (15, 14, 12)]
    wob = [(0, 1, 2), (12, 16, 13)]
    wob2 = [(2, 1, 0), (13, 16, 12)]
    rby = [(7, 8, 6), (14, 13, 17)]
    rby2 = [(6, 8, 7), (17, 13, 14)]
    ogy = [(9, 10, 11), (16, 15, 17)]
    ogy2 = [(11, 10, 9), (17, 15, 16)]
    moves = [wrg, wrg2, wob, wob2, rby, rby2, ogy, ogy2]
    # ivy_cube states:
    solved_state = (0, 1, 2, 0, 3, 4, 5, 3, 2, 1, 4, 5, 0, 2, 3, 4, 1, 5)
    # valid states
    S1 = (0, 1, 2, 3, 4, 0, 3, 2, 5, 1, 4, 5, 2, 5, 4, 0, 1, 3)
    S2 = (1, 2, 0, 3, 4, 0, 3, 2, 5, 5, 1, 4, 0, 2, 4, 1, 3, 5)
    S3 = (1, 2, 0, 4, 0, 3, 3, 2, 5, 4, 5, 1, 2, 1, 4, 3, 5, 0)
    S4 = (2, 0, 1, 4, 0, 3, 5, 3, 2, 1, 4, 5, 0, 4, 3, 5, 1, 2)
    S5 = (0, 1, 2, 0, 3, 4, 5, 3, 2, 5, 1, 4, 0, 1, 3, 2, 4, 5)
    S6 = (0, 1, 2, 4, 0, 3, 5, 3, 2, 4, 5, 1, 5, 1, 4, 2, 3, 0)
    S7 = (1, 2, 0, 3, 4, 0, 5, 3, 2, 5, 1, 4, 0, 5, 3, 1, 4, 2)
    # invalid states
    I1 = (1, 1, 2, 3, 4, 0, 3, 2, 5, 1, 4, 5, 2, 5, 4, 0, 0, 3)
    I2 = (1, 2, 0, 3, 3, 0, 3, 2, 5, 5, 1, 4, 0, 2, 4, 1, 3, 5)
    I3 = (1, 2, 0, 4, 0, 3, 3, 3, 5, 4, 5, 1, 2, 1, 4, 3, 5, 0)
    I4 = (2, 1, 0, 4, 0, 3, 5, 3, 2, 1, 4, 5, 0, 4, 3, 5, 1, 2)
    I5 = (0, 1, 2, 3, 0, 4, 5, 3, 2, 5, 1, 4, 0, 1, 3, 2, 4, 5)
    I6 = (1, 0, 2, 4, 0, 3, 5, 3, 2, 4, 5, 1, 5, 1, 4, 2, 3, 0)
    I7 = (1, 2, 0, 3, 4, 0, 5, 3, 2, 5, 1, 4, 0, 5, 3, 1, 2, 4)
    states = [S1, S2, S3, S4, S5, S6, S7, I1, I2, I3, I4, I5, I6, I7]

    ivy_cube_group = gen_puzzle_group(moves, len(solved_state))
    ivy_cube_pieces = detect_pieces(moves, len(solved_state))
    validator = State_Validator(solved_state, ivy_cube_pieces, ivy_cube_group)
    print(f"Calculated a group of order {ivy_cube_group.order()}.")
    print(f"Detected {len(ivy_cube_pieces)} pieces:\n", ivy_cube_pieces)
    print("",validator.solved_piece_lists)
    for i, state in enumerate(states):
        symbol = "S" if i < 7 else "I"
        print(f"Evaluation of state {symbol}{i%7+1}:",
              validator.validate_state(state))
