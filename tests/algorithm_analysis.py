"""
a module for automatic evaluation and analysis of twisty puzzle algorithms

features:
    - calculate order d of the algorithm
    - repeat algorithm n times where n is a factor of d
    - decide whether or not an algorithm is likely to be useful based on
        these repetitions
"""
import itertools
import math
from sympy.combinatorics import Permutation


def get_sympy_dict(puzzle):
    """
    generate the moves of the given puzzle as sympy permutations

    inputs:
    -------
        puzzle - (Twisty_Puzzle) - a puzzle object where a puzzle is loaded

    returns:
    --------
        (dict) - dictionary with sympy permutations
            keys are the same as in `puzzle move_dict`
            values are the same permutations as sympy permutations
    """
    sympy_moves = dict()
    for name, move_perm in puzzle.moves.items():
        sympy_moves[name] = Permutation(move_perm)
    return sympy_moves


def analyse_alg(moves, sympy_dict, pieces, max_pieces=6, max_order=4):
    """
    analyse a given algorithm (a move sequence)
    """
    move_list = moves.split(" ")
    alg_perm = sympy_dict[move_list[0]]
    for perm in move_list[1:]:
        alg_perm *= sympy_dict[perm]
    n = alg_perm.order()
    print(f"The algorithm has order {n}")
    divs = get_divisors(n)
    divs.sort()
    for k in divs[:-1]:
        k_rep = alg_perm**k
        l = k_rep.order()
        affected_pieces = get_affected_pieces(k_rep, pieces)
        n_pieces = len(affected_pieces)
        if n_pieces <= max_pieces and l <= max_order:
            print(f"After {k} repetitions, we get an algorithm with order {l}:")
            print(f"This algorithm affects {n_pieces} pieces.")
            print(k_rep)
            print(affected_pieces)
            print()


def get_affected_pieces(perm, pieces):
    """
    get a list of all pieces moved by the given permutation

    inputs:
    -------
        perm - (sympy.combinatorics.Permutation) - a sympy permutation for analysis
        pieces - (list) of (set) - list of all pieces in the puzzle
            each piece is represented as a set of point indices

    returns:
    --------
        (list) of (set) - list of pieces affected by the permutation.
            each piece is represented as a set of point indices
    """
    L = set(itertools.chain(*perm.cyclic_form))
    affected_pieces = list()
    for piece in pieces:
        if L & piece != set():
            affected_pieces.append(piece)
    return affected_pieces


def get_divisors(n):
    """
    calculates all divisors of n
    The returned list of divisors is not sorted but can be sorted very efficiently.
    The sublist [::2] contains increasing elements and
    The sublist [1::2] contains decreasing elements
    To get a sorted list:
        L = get_divisors(n)
        L = L[::2] + L[1::2].reversed()

    inputs:
    -------
        n - (int) - any integer
    
    returns:
    --------
        (list) of (int) - unsorted list of all divisors of n (see above)
            includes divisors 1 and n as the first two elements.
    """
    # Note that this loop runs till square root
    divs = list()
    i = 1
    while i <= math.sqrt(n):
        if (n % i == 0):
            # If divisors are equal, print only one
            k = n//i
            divs.append(i)
            divs.append(k)
        i += 1
    if k == i-1:
        return divs[:-1]
    return divs


def main():
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from version_2_2.gui.puzzle_class import Twisty_Puzzle

    puzzle = Twisty_Puzzle()
    # puzzle_name = input("Enter a puzzle name: ")
    puzzle_name = "geared_mixup"
    puzzle.load_puzzle(puzzle_name)
    n = puzzle.state_space_size
    sympy_dict = get_sympy_dict(puzzle)

    user_input = str()
    while user_input.lower() != "end":
        print()
        user_input = input("Enter a move sequence for analysis: \n ")
        analyse_alg(user_input, sympy_dict, puzzle.pieces)


if __name__ == "__main__":
    main()
    ### symps tests ###
    # P1 = Permutation([(1,2)], n=4)
    # P1.cyclic_form.flatten()
    # P2 = Permutation([(2,3)], n=4)
    # P3 = Permutation([(1,2,3)], n=4)

    # print(P1)
    # print(P2)
    # print(P3)

    # print(P1*P2)
    # print(P1*P3)
    # print(P2*P3)
    # print(P1*P2*P3)
