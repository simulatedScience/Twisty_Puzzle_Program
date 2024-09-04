

# add src to path
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parent2dir = os.path.dirname(parentdir)
sys.path.insert(0,parent2dir)

import random
import time

from sympy.combinatorics import Permutation
from sympy.combinatorics.perm_groups import PermutationGroup

from src.smart_scramble import smart_scramble
from src.algorithm_generation.algorithm_analysis import Twisty_Puzzle_Algorithm, get_move_sequence_info
from src.interaction_modules.colored_text import colored_text
from src.algorithm_generation.orbit_calculation import calculate_point_orbits

DEBUG: bool = False

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
        max_iterations_without_new_algorithm: int = 10000,
        verbosity: int = 2,
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
    num_base_sequences: int = 0
    base_moves: dict[str, list[list[str]]] = {name: puzzle.moves[name] for name in sympy_base_moves.keys()}
    
    n_points: int = len(puzzle.SOLVED_STATE)
    base_move_orbits: list[set[int]] = calculate_point_orbits(
        n_points=n_points,
        moves=list(sympy_base_moves.values()),
    )
    algs_generate_full_group: bool = False
    while len(found_algorithms) < max_number_of_algorithms \
            and time.time() < end_time \
            and iterations_since_new_algorithm < max_iterations_without_new_algorithm:
        # generate efficient base sequence for algorithms
        sequence_length: int = random.randint(2, max_base_sequence_length)
        base_sequence: list[str] = smart_scramble(
            puzzle.SOLVED_STATE,
            base_moves,
            sequence_length)
        num_base_sequences += 1
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
            iteration = num_base_sequences if verbosity else -1
            added_algorithms_step = filter_and_add_algorithm(
                new_algorithm=algorithm,
                found_algorithms=found_algorithms,
                rotations=sympy_rotations,
                max_pieces_affected=max_pieces_affected,
                iteration=iteration,
                )
            # keep track of whether a new algorithm was added
            if added_algorithms_step:
                # TODO: add inverse of new algorithm
                inverse_algorithm = algorithm.get_inverse()
                added_algorithms_step_inv = filter_and_add_algorithm(
                    new_algorithm=inverse_algorithm,
                    found_algorithms=found_algorithms,
                    rotations=sympy_rotations,
                    max_pieces_affected=max_pieces_affected,
                    iteration=iteration,
                )
                if full_group_reached(puzzle, found_algorithms, sympy_rotations):
                    algs_generate_full_group = True
                    break
                iterations_since_new_algorithm = 0
        else:
            iterations_since_new_algorithm += 1
            continue
        break
    # trim algorithms to minimal full set
    if algs_generate_full_group:
        found_algorithms = trim_algorithms_to_full_group(
            puzzle=puzzle,
            found_algorithms=found_algorithms,
            sympy_rotations=sympy_rotations,
        )
    # print end condition
    if verbosity:
        print()
        if len(found_algorithms) >= max_number_of_algorithms:
            print(f"Maximum number of algorithms ({max_number_of_algorithms}) reached.")
        if time.time() >= end_time:
            print(f"Maximum time ({max_time} seconds) reached.")
        if iterations_since_new_algorithm >= max_iterations_without_new_algorithm:
            print(f"Maximum iterations without new algorithm ({max_iterations_without_new_algorithm}) reached.")
        if algs_generate_full_group:
            print(f"Full group reached.")
    if verbosity >= 2:
        print(f"Searched {num_base_sequences} base sequences to find {len(found_algorithms)} algorithms in {time.time()-end_time+max_time:.2f} s.")
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
        iteration: int = -1,
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
        return None
    accepted_new_algorithm: bool = False
    potential_matches: list[Twisty_Puzzle_Algorithm] = []
    # compare algorithm signatures
    for alg in found_algorithms:
        if new_algorithm.is_similar(alg):
            potential_matches.append(alg)
    for alg in potential_matches:
        if new_algorithm.sympy_permutation.cyclic_form == alg.sympy_permutation.cyclic_form:
            if len(new_algorithm.full_action_sequence) < len(alg.full_action_sequence):
                print(f"Replacing old algorithm with new one:\n  old: {alg}\n  new: {new_algorithm}")
                # rename new algorithm to old name
                new_algorithm.name = alg.name
                # replace old algorithm with new one in-place
                found_algorithms[found_algorithms.index(alg)] = new_algorithm
                # found_algorithms.append(new_algorithm)
                accepted_new_algorithm = True
            return accepted_new_algorithm
    # check if any rotation of the new algorithm exists in the found algorithms
    for rotation_perm in rotations.values():
        rotated_alg_perm: Permutation = rotation_perm * new_algorithm.sympy_permutation * rotation_perm**-1
        for alg in potential_matches:
            # if rotated_alg_perm.cyclic_form == alg.sympy_permutation.cyclic_form:
            if rotated_alg_perm.cyclic_form == alg.sympy_permutation.cyclic_form \
                or new_algorithm.is_similar(alg):
                # check if new algorithm is shorter
                if len(new_algorithm.full_action_sequence) < len(alg.full_action_sequence):
                    print(f"Replacing old algorithm with new one:\n  old: {alg}\n  new: {new_algorithm}")
                    # rename new algorithm to old name
                    new_algorithm.name = alg.name
                    # replace old algorithm with new one in-place
                    found_algorithms[found_algorithms.index(alg)] = new_algorithm
                    # found_algorithms.append(new_algorithm)
                    accepted_new_algorithm = True
                return accepted_new_algorithm
        # # break out of both loops if a match is found
        # else:
        #     continue
        # break
    if not potential_matches:
        # add new algorithm if no potential matches were found
        if iteration >= 0:
            print(f"Adding new algorithm after {iteration} iterations:\n  {new_algorithm}")
        else:
            print(f"Adding new algorithm:\n  {new_algorithm}")
        found_algorithms.append(new_algorithm)
        accepted_new_algorithm = True
    # else: # similar algorithms exist, but no exact match
    #     print("="*75) if DEBUG else None
    #     suffix = " = " + colored_text(str(new_algorithm.sympy_permutation.cyclic_form), color="#5588ff") if DEBUG else ""
    #     print(f"Adding new new_algorithm with similar signature to existing ones:\n  {new_algorithm}"
    #           + suffix)
    #     if DEBUG:
    #         # print cyclic forms and index in found_algorithms for all potential matches
    #         print(f"Potential matches:")
    #         cyclic_forms_of_matches = [alg.sympy_permutation.cyclic_form for alg in potential_matches]
    #         for alg, cyclic_form in zip(potential_matches, cyclic_forms_of_matches):
    #             # index = found_algorithms.index(alg)
    #             print(f"  {alg.name:6} -> {colored_text(str(cyclic_form), color='#5588ff')}")
    #         # print rotations of new algorithm
    #         print(f"Rotations of new algorithm:")
    #         for rot_name, rotation_perm in rotations.items():
    #             rotated_alg_perm: Permutation = rotation_perm * new_algorithm.sympy_permutation * rotation_perm**-1
    #             color = "#22dd22" if rotated_alg_perm.cyclic_form in cyclic_forms_of_matches else "#ff2222"
    #             print(colored_text(f"  {rot_name:6} -> {rotated_alg_perm.cyclic_form}", color=color))
    #     found_algorithms.append(new_algorithm)
    #     accepted_new_algorithm = True
    return accepted_new_algorithm

def trim_algorithms_to_full_group(
        puzzle: "Twisty_Puzzle",
        found_algorithms: list[Twisty_Puzzle_Algorithm],
        sympy_rotations: list[Permutation],
    ) -> list[Twisty_Puzzle_Algorithm]:
    removed_algorithm: bool = True
    # sort algorithms by decreasing length.
    # sorting ensures that longer algorithms are discarded first.
    found_algorithms.sort(key=lambda alg: len(alg.full_action_sequence), reverse=True)
    necessary_algorithms: set[str] = set()
    unique_algorithm_signatures: set[str] = set([alg.algorithm_signature for alg in found_algorithms])
    while removed_algorithm:
        for i, alg in enumerate(found_algorithms):
            if alg.name in necessary_algorithms:
                # skip known necessary algorithms
                continue
            remaining_signatures = set([alg.algorithm_signature for alg in found_algorithms[:i] + found_algorithms[i+1:]])
            if len(remaining_signatures) <= len(unique_algorithm_signatures):
                # keep at least one algorithm of each unique signature
                necessary_algorithms.add(alg.name)
                continue
            # check if full group is still reached without the current algorithm
            if full_group_reached(
                puzzle,
                found_algorithms[:i] + found_algorithms[i+1:],
                sympy_rotations):
                break
            else:
                necessary_algorithms.add(alg.name)
        else:
            removed_algorithm = False
            continue
        found_algorithms.pop(i)
        removed_algorithm = True
        print(f"Removed redundant algorithm {alg} of length {len(alg.full_action_sequence)}.")
        if len(found_algorithms) <= (len(puzzle.moves) - len(sympy_rotations)) // 2:
            print(f"Stopping removing algorithms to keep at least {(len(puzzle.moves) - len(sympy_rotations)) // 2} algorithms.")
            break
    # rename algorithms
    for i, alg in enumerate(reversed(found_algorithms)):
        alg.name = f"alg_{i+1}"
    found_algorithms.reverse()
    return found_algorithms

def full_group_reached(
        puzzle: "Twisty_Puzzle",
        found_algorithms: list[Twisty_Puzzle_Algorithm],
        rotations: list[Permutation],
    ) -> bool:
    """
    Check if group generated by the found algorithms is the same as the one generated by the base moves. To calculate orbits of the found algorithms, we need to consider all possible rotations of the algorithms (i.e. all possible conjugates of the permutations).
    """
    rotated_algorithms: list[Permutation] = [alg.sympy_permutation for alg in found_algorithms]
    for rotation_perm in rotations.values():
        rotated_algorithms += [rotation_perm * alg.sympy_permutation * rotation_perm**-1 for alg in found_algorithms]
    # generate group from rotated algorithms
    algorithm_group = PermutationGroup(rotated_algorithms)
    if algorithm_group.order() == puzzle.state_space_size:
        return True
    return False
    # found_orbits: list[set[int]] = calculate_point_orbits(
    #     n_points=n_points,
    #     moves=rotated_algorithms,
    # )

    # if found_orbits == base_move_orbits:
    #     return True
    # for orbit in base_move_orbits:
    #     if not orbit in found_orbits:
    #         break
    # else:
    #     print(f"Equal orbits, but different orbit lists:\n  base: {base_move_orbits}\n  algs: {found_orbits}")
    #     return True
    # return False

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

"""
Replacing old algorithm with new one:
  old: alg_4 = 4*(slice_z' t l' slice_y' l slice_z')
  new: alg_6 = 4*(d slice_x')

12C3 = 220 = 2 * 5 * 11


For a 3x3x3 cube, there are probably *9* rotationally unique 3-cycles of edges + *9* inverses = 18.
Consider rotations of the pieces... *2?
probably *3* 3-cycles of corners + *3* inverses = 6
Consider rotations of the pieces... *3?

=> >50 unique 3-cycles of edges or corners affecting only 3 pieces. In reality, 4 algorithms are sufficient to solve the cube entirely.

for a megaminx, this gets way worse.
"""
