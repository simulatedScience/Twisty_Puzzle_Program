"""
This module implements a class to store twisty puzzle algorithms along with some properties for comparing them.
"""

import itertools
from collections import namedtuple, Counter

from sympy.combinatorics import Permutation


# cycle signature: (cycle_length, affected_pieces, piece_type)
CYCLE_SIGNATURE = namedtuple(
    "CYCLE_SIGNATURE",
    ["cycle_length", "n_affected_pieces", "piece_type"])
# cycles signature: (cycle_signature, number of cycles with this signature)
CYCLES_SIGNATURE = namedtuple(
    "CYCLES_SIGNATURE",
    ["cycle_signature", "num"])
# piece signature: (piece_type, number of pieces of this type)
PIECES_SIGNATURE = namedtuple(
    "PIECES_SIGNATURE",
    ["piece_type", "num"])

class Twisty_Puzzle_Algorithm:
    def __init__(
            self,
            base_action_sequence: list[str],
            n_repetitions: int,
            puzzle: "Twisty_Puzzle",
            alg_name: str,
        ):
        """
        Initialize a new twisty puzzle algorithm based on a given move sequence that is repeated n times.
        """
        # self.puzzle_name: str = puzzle_name
        self.name: str = alg_name
        self.puzzle: "Twisty_Puzzle" = puzzle
        self.sympy_moves: dict[str, Permutation] = get_sympy_moves(puzzle)
        
        self.base_action_sequence: list[str] = base_action_sequence
        self.n_repetitions: int = n_repetitions
        self.full_action_sequence: list[str] = self.base_action_sequence*self.n_repetitions

        self.sympy_permutation: Permutation = self._get_sympy_permutation(
            move_sequence=self.full_action_sequence,
            sympy_moves=self.sympy_moves,
        )
        self._calculate_properties(self.puzzle.pieces)

    def __str__(self) -> str:
        """
        Return the algorithm name
        """
        return f"{self.name} = {self.compact_moves()}"

    def compact_moves(self) -> str:
        """
        Returns:
            str: the base move sequence of the algorithm
        """
        return f"{self.n_repetitions}*({' '.join(self.base_action_sequence)})"
    
    def as_base_moves(self) -> str:
        """
        Returns:
            str: the full move sequence of the algorithm
        """
        return ' '.join(self.full_action_sequence)

    def print_signature(self):
        """
        Print the algorithm signature.
        """
        print(f"Signature of algorithm `{self.name}`:")
        print(f"Algorithm has order {self.order}.")
        print("Piece signature:")
        for piece_signature in self.algorithm_signature[0]:
            print(f"    {piece_signature.num} pieces of type {piece_signature.piece_type}.")
        print("Cycle signature:")
        for cycle_signature in self.algorithm_signature[1]:
            print(f"    {cycle_signature.num} cycles of length {cycle_signature.cycle_signature.cycle_length} affecting {cycle_signature.cycle_signature.n_affected_pieces} pieces of type {cycle_signature.cycle_signature.piece_type}.")


    def _get_sympy_permutation(self,
            move_sequence: list[str],
            sympy_moves: dict[str, Permutation],
        ) -> Permutation:
        """
        Get the algorithm as a sympy permutation
        """
        if hasattr(self, "_sympy_permutation"):
            return self.sympy_permutation
        # generate self.sympy_permutation from action_sequence and puzzle moves
        sympy_permutation = sympy_moves[move_sequence[0]]
        for move in move_sequence[1:]:
            sympy_permutation *= sympy_moves[move]
        return sympy_permutation

    def _calculate_properties(self,
            pieces: list[set[int]],
            ):
        """
        Calculate the properties of the algorithm:
            - order of the algorithm
            - number of affected pieces
            - number of affected points
        """
        self.order: int = self.sympy_permutation.order()
        # calculate affected pieces
        self.affected_pieces: list[set[int]] = get_affected_pieces(
                perm=self.sympy_permutation,
                pieces=pieces,
                )
        self.n_affected_pieces: int = len(self.affected_pieces)
        
        self.affected_points: set[int] = get_affected_points(self.sympy_permutation)
        
        self.algorithm_signature: tuple[tuple[PIECES_SIGNATURE], tuple[CYCLES_SIGNATURE]] = get_algorithm_signature(self.sympy_permutation, pieces)

def get_affected_pieces(perm: Permutation, pieces: list[set[int]]) -> list[set[int]]:
    """
    get a list of all pieces moved by the given permutation

    Args:
        perm (sympy.combinatorics.Permutation): a sympy permutation for analysis
        pieces (list[set[int]]): list of all pieces in the puzzle
            each piece is represented as a set of point indices

    Returns:
        list[set[int]]: list of pieces affected by the permutation.
            each piece is represented as a set of point indices
    """
    # flatten the cyclic form of the permutation into the set of all affected points
    affected_points: set[int] = get_affected_points(perm)
    affected_pieces: list[set[int]] = list()
    for piece in pieces:
        if affected_points & piece != set(): # if piece is affected by algorithm: append piece
            affected_pieces.append(piece)
    return affected_pieces

def get_affected_points(perm: Permutation) -> set[int]:
    """
    From a given sympy permutation, get the set of all affected points
    
    Args:
        perm (sympy.combinatorics.Permutation): a sympy permutation for analysis

    Returns:
        set[int]: set of all affected points given by their indices
    """
    return set(itertools.chain(*perm.cyclic_form))

def get_cycle_signatures(perm: Permutation, pieces: list[set[int]]) -> list[CYCLE_SIGNATURE]:
    """
    Get the cycle signature of a permutation:
        a list of information about each cycle in the permutation:
            - cycle length
            - number of pieces affected by the cycle
            - type of pieces affected by the cycle

    Args:
        perm (sympy.combinatorics.Permutation): a sympy permutation for analysis
        pieces (list[set[int]]): list of all pieces in the puzzle
            each piece is represented as a set of point indices

    Returns:
        list[CYCLE_SIGNATURE]: list of named tuples containing the cycle signature
    """
    cycle_signatures = list()
    for cycle in perm.cyclic_form:
        cycle_length = len(cycle)
        affected_points: set[int] = set(cycle)
        empty_set: set = set()
        # get the number of points in each affected piece
        affected_piece_types = [
            len(piece)
                for piece in pieces
                if affected_points & piece != empty_set]
        if len(set(affected_piece_types)) > 1:
            raise ValueError("Cycle affects multiple piece types. This is not unexpected!")
        
        cycle_signatures.append(
            CYCLE_SIGNATURE(
                cycle_length,
                len(affected_piece_types),
                affected_piece_types[0],
            )
        )
    return cycle_signatures

def get_algorithm_signature(perm: Permutation, pieces: list[set[int]]) -> tuple[tuple[PIECES_SIGNATURE], tuple[CYCLES_SIGNATURE]]:
    """
    Given a permutation describing a move sequence, calculate the signature of the algorithm:
        - a tuple of named tuples, each describing a piece type and how many pieces of this type are affected by the algorithm.
        - a tuple of cycle signatures and how many cycles with this signature appear in the algorithm

    Args:
        perm (sympy.combinatorics.Permutation): a sympy permutation for analysis
        pieces (list[set[int]]): list of all pieces in the puzzle
            each piece is represented as a set of point indices
    
    Returns:
        tuple[tuple[PIECES_SIGNATURE], tuple[CYCLES_SIGNATURE]]: the algorithm signature
    """
    cycle_signatures = get_cycle_signatures(perm, pieces)
    # 1. count how often each cycle signature appears in the cycle signatures
    # Count how often each cycle signature appears
    cycle_signature_counter = Counter(cycle_signatures)
    # Generate the CYCLES_SIGNATURE tuple
    cycles_signature = tuple(
        CYCLES_SIGNATURE(cycle_signature, count)
        for cycle_signature, count in cycle_signature_counter.items()
    )
    # 2. count how many pieces of each type are affected by the algorithm
    affected_pieces: list[set[int]] = get_affected_pieces(perm, pieces)
    piece_type_counter = Counter(len(piece) for piece in affected_pieces)
    # Generate the PIECES_SIGNATURE tuple
    pieces_signature = tuple(
        PIECES_SIGNATURE(piece_type, count)
        for piece_type, count in piece_type_counter.items()
    )
    # assemble the algorithm signature
    return (pieces_signature, cycles_signature)

def get_sympy_moves(puzzle):
    """
    generate the moves of the given puzzle as sympy permutations

    Args:
        puzzle (Twisty_Puzzle): a puzzle object where a puzzle is loaded

    Returns:
        (dict[str, Permutation]): dictionary with sympy permutations
            keys are the same as in `puzzle move_dict`
            values are the same permutations as sympy permutations
    """
    sympy_moves = dict()
    for name, move_perm in puzzle.moves.items():
        sympy_moves[name] = Permutation(move_perm)
    return sympy_moves

def get_divisors(n: int) -> list[int]:
    """
    Calculate all integer divisors of n.
    The returned list of divisors is not sorted but can be sorted very efficiently.
    The sublist [::2] contains increasing elements and.
    The sublist [1::2] contains decreasing elements.
    To get a sorted list:
    ```
        L = get_divisors(n)
        L = L[::2] + L[1::2].reversed()
    ```

    Args:
        n (int): any integer
    
    Returns:
        list[int]: unsorted list of all divisors of n (see above)
            includes divisors 1 and n as the first two elements.
    """
    divs = list()
    i = 1
    while i <= n**.5:
        if (n % i == 0):
            # If divisors are equal, print only one
            k = n//i
            divs.append(i)
            divs.append(k)
        i += 1
    if k == i-1: # n is a square number -> counted last divisor twice
        return divs[:-1]
    return divs




def main(puzzle_name="rubiks_3x3"):
    """
    Allow the user to manually input algorithms as move sequences, then print the analysis of the algorithm.
    """
    import os,sys,inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parentdir)
    sys.path.insert(0,parent2dir)
    from src.puzzle_class import Twisty_Puzzle

    print(f"Enter 'exit' to quit the program.")

    puzzle: Twisty_Puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)

    print("Available moves:")
    puzzle.listmoves(print_perms=False)
    
    user_input: str = ""
    while user_input.lower() != "exit":
        print()
        user_input = input("Enter a move sequence for analysis:\n ")
        move_sequence = user_input.split(' ')
        # validate input
        for move in move_sequence:
            if move not in puzzle.moves:
                print(f"Error: move `{move}` is not available.")
                break
        else:
            user_input = input("How often should the move sequence be repeated?\n ")
            try:
                n_repetitions = int(user_input)
            except ValueError:
                print("Error: input is not a number. Assuming 1 repetition.")
            # input is valid
            algorithm = Twisty_Puzzle_Algorithm(
                base_action_sequence=move_sequence,
                n_repetitions=n_repetitions,
                puzzle=puzzle,
                alg_name="user_input",
            )
            algorithm.print_signature()

if __name__ == "__main__":
    main(puzzle_name="rubiks_3x3")