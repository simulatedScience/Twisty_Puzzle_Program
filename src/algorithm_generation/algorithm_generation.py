

# add src to path
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parent2dir = os.path.dirname(parentdir)
sys.path.insert(0,parent2dir)

import random
import time

from sympy.combinatorics import Permutation

from src.smart_scramble import smart_scramble
from src.algorithm_generation.algorithm_analysis import Twisty_Puzzle_Algorithm, get_move_sequence_info

def generate_algorithms(
        puzzle: "Twisty_Puzzle",
        sympy_base_moves: dict[str, Permutation],
        sympy_rotations: dict[str, Permutation],
        max_time: float = 10, # seconds
        max_base_sequence_length=16,
        max_move_sequence_order: int = 200,
        max_algorithm_moves: int = 150,
        max_algorithm_order: int = 6,
        max_pieces_affected: int | None = None, # automatic
        max_number_of_algorithms: int = 30,
        max_iterations_without_new_algorithm: int = 1000,
    ):
    """
    Generate algorithms for the given puzzle within the given constraints.
    
    1. generate an efficient, random move sequence
    2. find repetitions of the move sequence that result in useful algorithms
    3. check overlap with previously found algorithms
    4. save or reject the found algorithms
    5. repeat 1-4 until end condition is met:
        - time runs out or
        - maximum number of algorithms is reached
        - algorithms with rotations generate entire puzzle group
    """
    if max_pieces_affected is None:
        raise NotImplementedError("Automatic calculation of max_pieces_affected is not implemented yet.\n" + 
                                  "This setting will eventually calculate the max number of pieces as the minimum/ median/ average/ maximum number of pieces affected by base moves.")

    end_time: float = time.time() + max_time
    found_algorithms: list[Twisty_Puzzle_Algorithm] = [] # TODO: initialize with existing algorithms
    # found_algorithms: list[Twisty_Puzzle_Algorithm] = puzzle.algorithms
    iterations_since_new_algorithm: int = 0
    while len(found_algorithms) < max_number_of_algorithms \
            and time.time() < end_time \
            and iterations_since_new_algorithm < max_iterations_without_new_algorithm:
            # TODO: add orbit based end condition
        added_algorithms_this_iteration: bool = False
        # generate efficient base sequence for algorithms
        sequence_length: int = random.randint(2, max_base_sequence_length)
        base_sequence: list[str] = smart_scramble(
            puzzle.SOLVED_STATE,
            puzzle.moves,
            sequence_length)
        # get cycles of base sequence
        repetitions_candidates, base_sequence_info = get_repetition_candidates(
            sympy_moves=sympy_base_moves,
            base_sequence=base_sequence,
            pieces=puzzle.pieces,
            max_algorithm_moves=max_algorithm_moves,
            max_algorithm_order=max_algorithm_order)
        # check repetitions for useful algorithms
        if base_sequence_info["order"] > max_move_sequence_order:
            continue
        # check repetitions for useful algorithms
        for n_reps in repetitions_candidates:
            # define algorithm candidate
            # move_sequence: list[str] = base_sequence
            algorithm = Twisty_Puzzle_Algorithm(
                base_action_sequence=base_sequence,
                n_repetitions=n_reps,
                puzzle=puzzle,
                alg_name=f"alg_{len(found_algorithms)+1}",
                sympy_moves=sympy_base_moves,
            )
            # add algorithm if it meets the requirements
            added_algorithms_step = filter_and_add_algorithm(
                new_algorithm=algorithm,
                found_algorithms=found_algorithms,
                rotations=sympy_rotations,
                max_pieces_affected=max_pieces_affected,
                )
            # keep track of whether a new algorithm was added
            if added_algorithms_step:
                iterations_since_new_algorithm = 0
                added_algorithms_this_iteration = True
        if not added_algorithms_this_iteration:
            iterations_since_new_algorithm += 1
    return found_algorithms

def get_repetition_candidates(
        sympy_moves: dict[str, Permutation],
        base_sequence: list[str],
        pieces: list[set[int]],
        max_algorithm_moves: int = float("inf"),
        max_algorithm_order: int = float("inf"),
        ) -> tuple[set[int], dict[str, any]]:
    """
    Get all number repetitions of a given base sequence that could yield a useful algorithm.
    These are all multiples of cycle lengths of the base sequence that are less than half the order of the base sequence.

    Args:
        sympy_moves (dict[str, Permutation]): dictionary of sympy permutations
        base_sequence (list[str]): a list of move names
        max_algorithm_moves (int): maximum number of moves an algorithm can have
        max_algorithm_order (int): maximum order of an algorithm

    Returns:
        (set[int]): set of repetition candidates
        (dict[str, any]): dictionary with information about the base sequence
    """
    base_sequence_info: dict[str, any] = get_move_sequence_info(
            move_sequence=base_sequence,
            sympy_moves=sympy_moves,
            pieces=pieces,
    )
    repetitions_candidates: set[int] = set()
    for cycle in base_sequence_info["cycles"]:
        cycle_length: int = len(cycle)
        factor: int = 1
        while (n_reps := cycle_length * factor) <= base_sequence_info["order"]//2:
            factor += 1
            if base_sequence_info["order"] / n_reps > max_algorithm_order:
                # algorithm order is too high
                continue
            if n_reps * len(base_sequence) > max_algorithm_moves:
                # algorithm is too long
                break
            repetitions_candidates.add(n_reps)
    return repetitions_candidates, base_sequence_info

def filter_and_add_algorithm(
        new_algorithm: Twisty_Puzzle_Algorithm,
        found_algorithms: list[Twisty_Puzzle_Algorithm],
        rotations: list[Permutation],
        max_pieces_affected: int = float("inf"),
        ) -> bool:
    """
    Add a newly found algorithm to the list of found algorithms if it is sufficiently different from existing ones or if it achieves the same permutation in fewer moves.
    
    Args:
        new_algorithm (Twisty_Puzzle_Algorithm): the new algorithm to be added
        found_algorithms (list[Twisty_Puzzle_Algorithm]): list of existing algorithms
        rotations (list[Permutation]): list of permutations that rotate the puzzle in 3D space
        max_pieces_affected (int): maximum number of pieces affected by the algorithm

    Returns:
        (bool): True if the algorithm was added, False otherwise
    """
    if len(new_algorithm.affected_pieces) > max_pieces_affected:
        # algorithm affects too many pieces
        return found_algorithms
    accepted_new_algorithm: bool = False
    potential_matches: list[Twisty_Puzzle_Algorithm] = []
    # compare algorithm signatures
    for alg in found_algorithms:
        if new_algorithm.is_similar(alg):
            potential_matches.append(alg)
    # check if any rotation of the new algorithm exists in the found algorithms
    for rotation_perm in rotations:
        rotated_alg_perm = new_algorithm.sympy_permutation * rotation_perm
        for alg in potential_matches:
            if rotated_alg_perm == alg.sympy_permutation \
                or new_algorithm.is_similar(alg):
                # check if new algorithm is shorter
                if len(new_algorithm.full_action_sequence) < len(alg.full_action_sequence):
                    print(f"Replacing old algorithm with new one:\n  {new_algorithm}")
                    # rename new algorithm to old name
                    new_algorithm.name = alg.name
                    # replace old algorithm with new one
                    found_algorithms.remove(alg)
                    found_algorithms.append(new_algorithm)
                    accepted_new_algorithm = True
                break
        else:
            # break out of both loops if a match is found
            continue
        break
    if not potential_matches:
        # add new algorithm if no potential matches were found
        print(f"Adding new algorithm:\n  {new_algorithm}")
        found_algorithms.append(new_algorithm)
        accepted_new_algorithm = True
    # else: # similar algorithms exist, but no exact match
    #     print(f"Adding new new_algorithm with similar signature to existing ones:\n  {new_algorithm}")
    #     found_algorithms.append(new_algorithm)
    #     accepted_new_algorithm = True
    return accepted_new_algorithm



def main(puzzle_name: str = "rubiks_3x3", rotations_prefix: str = "rot_") -> list[Twisty_Puzzle_Algorithm]:
    """
    Generate algorithms for the given puzzle.
    """
    from src.puzzle_class import Twisty_Puzzle
    from algorithm_analysis import get_sympy_moves

    print(f"Generating algorithms for {puzzle_name}...")

    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)

    sympy_moves: dict[str, Permutation] = get_sympy_moves(puzzle)
    sympy_rotations: dict[str, Permutation] = {name: perm for name, perm in sympy_moves.items() if name.startswith(rotations_prefix)}
    # remove permutations that are rotations
    sympy_base_moves = {name: perm for name, perm in sympy_moves.items() if not name in sympy_rotations}
    # generate algorithms
    found_algorithms = generate_algorithms(
        puzzle=puzzle,
        sympy_base_moves=sympy_base_moves,
        sympy_rotations=sympy_rotations,
        max_time=10,
        max_base_sequence_length=16,
        max_move_sequence_order=200,
        max_algorithm_moves=150,
        max_algorithm_order=4,
        max_pieces_affected=4,
        max_number_of_algorithms=30,
        max_iterations_without_new_algorithm=1000,
    )
    # output found algorithms
    print(f"\n\nFound {len(found_algorithms)} algorithms:")
    for alg in found_algorithms:
        print("="*75)
        print(alg)
        alg.print_signature()

    return found_algorithms

if __name__ == "__main__":
    main(
        puzzle_name="rubiks_3x3",
        rotations_prefix="rot_",
    )