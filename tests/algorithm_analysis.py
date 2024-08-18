"""
a module for automatic evaluation and analysis of twisty puzzle algorithms

features:
    - calculate order d of the algorithm
    - repeat algorithm n times where n is a factor of d
    - decide whether or not an algorithm is likely to be useful based on
        these repetitions
"""
from typing import List, Tuple
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


def analyse_alg(
        moves,
        sympy_moves,
        pieces,
        max_pieces=6,
        max_order=5,
        max_move_sequence_order=300,
        ) -> dict[tuple[str, int], str]:
    """
    analyse a given algorithm (a move sequence)
    """
    move_list = moves.split(" ")
    alg_perm = sympy_moves[move_list[0]]
    for perm in move_list[1:]:
        alg_perm *= sympy_moves[perm]
    n = alg_perm.order()
    if n > max_move_sequence_order:
        print(f"The move sequence has order {n} > {max_move_sequence_order}.")
        print(f"Move sequence is too long. => not likely to be useful.")
        return {}
    else:
        print(f"The move sequence has order {n}")
    divs = get_divisors(n)
    divs.sort()
    alg_number: int = 1
    found_algorithms: dict[tuple[str, int], str] = dict()
    
    for k in divs[:-1]:
        k_rep = alg_perm**k
        pot_alg_order = k_rep.order()
        affected_pieces = get_affected_pieces(k_rep, pieces)
        n_pieces = len(affected_pieces)
        if n_pieces <= max_pieces and pot_alg_order <= max_order:
            print(f"Algorithm {alg_number}: {k}*({moves})")
            print(f"After {k} repetitions, we get an algorithm with order {pot_alg_order}:")
            print(f"This algorithm affects {n_pieces} pieces.")
            print(k_rep)
            print(affected_pieces)
            print()
            alg_moves: str = get_algorithm_move_sequence(moves, n_rep=k)
            found_algorithms[(moves, k)] = alg_moves
            alg_number += 1
    return found_algorithms

def get_algorithm_move_sequence(moves, n_rep):
    """
    get the move sequence of an algorithm that is repeated n_rep times

    inputs:
    -------
        moves - (str) - a move sequence
        n_rep - (int) - number of repetitions

    returns:
    --------
        (str) - move sequence of the algorithm
    """
    alg_moves = (moves + " ")*n_rep
    return alg_moves[:-1]

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
    divs = list()
    i = 1
    while i <= math.sqrt(n):
        if (n % i == 0):
            # If divisors are equal, print only one
            k = n//i
            divs.append(i)
            divs.append(k)
        i += 1
    if k == i-1: # n is a square number -> counted last divisor twice
        return divs[:-1]
    return divs


def main(
        puzzle_name="geared_mixup",
        max_pieces=6,
        max_order=5,
        max_move_sequence_order=300,
        clipshape="sphere",
        drawpieces=False):
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from src.puzzle_class import Twisty_Puzzle

    print(f"Enter 'exit' to quit the program.")

    puzzle: Twisty_Puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)
    n = puzzle.state_space_size
    sympy_dict = get_sympy_dict(puzzle)

    current_algorithms: dict[int, str] = dict()
    puzzle.animation_time = 0.1

    puzzle.listmoves(print_perms=False)
    
    if not drawpieces and clipshape != "":
        puzzle.snap(clipshape)
    elif drawpieces:
        puzzle.draw_3d_pieces()

    user_input = str()
    while user_input.lower() != "exit":
        print()
        user_input = input("Enter a move sequence for analysis:\n ")
        if user_input.lower() == "reset":
            puzzle.reset_to_solved()
            continue
        try:
            user_input = int(user_input)
        except ValueError:
            pass
        if user_input in current_algorithms:
            if len(current_algorithms[user_input]) > 100:
                puzzle.animation_time = 0
            else:
                puzzle.animation_time = 0.1
            print(f"Showing algorithm {user_input}.")
            puzzle.perform_move(current_algorithms[user_input])
            user_input = str(user_input)
            continue

        try:
            new_algorithms = analyse_alg(
                user_input,
                sympy_dict,
                puzzle.pieces,
                max_pieces=max_pieces,
                max_order=max_order,
                max_move_sequence_order=max_move_sequence_order)
            current_algorithms: dict[int, str] = dict()
            for i, alg_value in enumerate(new_algorithms.values()):
                current_algorithms[i+1] = alg_value
            puzzle.reset_to_solved()
            print(f"Enter one of the following algorithm numbers to show it: {list(current_algorithms.keys())}")
        except KeyError as e:
            print(f"Unknown move: {e}")


if __name__ == "__main__":
    
    # puzzle_name = input("Enter a puzzle name: ")
    # puzzle_name = "geared_mixup"
    puzzle_name = "rubiks_2x2"
    main(
        puzzle_name=puzzle_name,
        max_pieces=8,
        max_order=5,
        max_move_sequence_order=300,
        clipshape="cube",
        drawpieces=True)
    
    
    
    ### sympy tests ###
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
