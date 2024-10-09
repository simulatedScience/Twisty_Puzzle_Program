"""
This module uses `rotational_symmetry_detection.py` to add symmetry moves to a given puzzle.
"""
import vpython as vpy
import numpy as np
import os
from sympy.combinatorics import Permutation
from scipy.spatial.transform import Rotation

from rotational_symmetry_detection import find_rotational_symmetries
from algorithm_generation_CLI import add_moves_to_puzzle, load_twisty_puzzle
from algorithm_analysis import get_sympy_moves

def rotations_to_moves(X: np.ndarray, rotations: list[tuple[float, np.ndarray, np.ndarray]]) -> dict[str, list[int]]:
    """
    Convert rotational symmetries into moves of the puzzle's pieces.
    Apply the rotation to X, then find the closest point in X to each rotated point.

    Args:
        X (np.ndarray): set of points
        rotations (list[tuple[float, np.ndarray, np.ndarray]]): rotational symmetries

    Returns:
        dict[str, list[int]]: moves of the puzzle's pieces
            The i'th point gets mapped to X[permutation[i]]. This is a bijection.
    """
    rotation_moves: dict[str, list[int]] = {}
    for i, rotation in enumerate(rotations):
        move_name: str = f"rot_{i}"
        permutation: list[int] = rotation_to_permutation(X, rotation)
        rotation_moves[move_name] = permutation
    return rotation_moves

def rotation_to_permutation(X: np.ndarray, rotation: tuple[float, np.ndarray, np.ndarray]) -> list[int]:
    """
    Convert a rotational symmetry into a permutation of the puzzle's pieces.
    Apply the rotation to X, then find the closest point in X to each rotated point.

    Args:
        X (np.ndarray): set of points
        rotation (tuple[float, np.ndarray, np.ndarray]): rotation angle, axis, axis support

    Returns:
        list[int]: permutation of the puzzle's pieces as a list of indices
            The i'th point gets mapped to X[permutation[i]]. This is a bijection.

    Raises:
        ValueError: if the detected permutation is not a bijection
    """
    rotation_angle, axis, axis_support = rotation
    # translate X by line_support
    X_translated: np.ndarray = X - axis_support
    # rotate X
    r = Rotation.from_rotvec(rotation_angle * axis)
    X_rotated = r.apply(X_translated)
    # translate X back
    X_permuted = X_rotated + axis_support
    # for every point in X_permuted, find the closest point's index in X
    permutation = [find_closest(X, point) for point in X_permuted]
    
    # def array_to_set(array: np.ndarray) -> set[tuple[float, float, float]]:
    #     return {tuple(point) for point in array}
    # print(f"rotation around axis {axis} with support {axis_support} by {360*rotation_angle/(2*np.pi):.2f}°.")
    # print(f"X has {len(array_to_set(X))} points.")
    # print(f"X_permuted has {len(array_to_set(X_permuted))} points.")
    
    # print("X:\n", X)
    # print("X_permuted:\n", X_permuted.round(3))
    # print(f"permutation has {len(set(permutation))} points.")
    # if len(set(permutation)) != len(X):
    #     error_message: str = f"Did not find a bijection between the points of X and the rotated points.\n" + \
    #         f"rotation around axis {axis} with support {axis_support} by {360*rotation_angle/(2*np.pi):.2f}° ({rotation_angle:.3} rad).\n" + \
    #         f"{len(X) - len(set(permutation))} points remained unmapped."
    #     raise ValueError(error_message)
    return permutation

def find_closest(X: np.ndarray, point: np.ndarray) -> int:
    """
    Find the closest point in X to a given point.

    Args:
        X (np.ndarray): set of points. shape: (n, 3)
        point (np.ndarray): point to find the closest point to. shape: (3,)

    Returns:
        int: index of the closest point in X
    """
    return np.argmin(np.linalg.norm(X - point, axis=1))

def filter_rotations(
        base_moves: dict[str, Permutation],
        rotations: dict[str, Permutation],
    ) -> list[str]:
    """
    Filter out rotations that result in otherwise invalid moves.

    Args:
        base_moves (dict[str, Permutation]): base moves of the puzzle
        rotations (dict[str, Permutation]): rotations to filter

    Returns:
        list[str]: names of valid rotations
    """
    valid_rotation_names: list[str] = []
    for rot_name, rotation in rotations.items():
        rot_inverse: Permutation = rotation**-1
        rotated_moves: list[Permutation] = [rotation * move * rot_inverse for move in base_moves.values()]
        for move_name, move in base_moves.items():
            if not(move in rotated_moves or move**-1 in rotated_moves):
                print(f"Rotating {move_name} by {rot_name} results in an invalid move.")
                break
        else:
            valid_rotation_names.append(rot_name)
        # for move_name, move in base_moves.items():
        #     rotated_move: Permutation = rotation * move * rotation**-1
        #     if rotated_move.cyclic_form != move.cyclic_form and (rotated_move**-1).cyclic_form != move.cyclic_form:
        #     # if rotated_move != move and rotated_move**-1 != move:
        #         print(f"Rotating {move_name} by {rot_name} results in an invalid move.")
        #         break
        # else:
        #     valid_rotation_names.append(rot_name)
    return valid_rotation_names

def add_rotation_moves_to_puzzle(
        puzzle: "Twisty_Puzzle",
        new_puzzle_name: str = "",
        suffix: str = "_sym",
        verbosity: int = 1,
    ) -> None:
    """
    Calculate rotational symmetries of a puzzle and add them as moves to the puzzle.
    The new puzzle (with rotation moves) is saved as `new_puzzle_name` or `puzzle.name + suffix`.
    
    Args:
        puzzle (Twisty_Puzzle): puzzle to add rotational symmetries to
        new_puzzle_name (str): name of the new puzzle
        suffix (str): suffix to add to the puzzle's name (ignored if `new_puzzle_name` is given)
        verbosity (int): verbosity level
    """
    point_coordinates: np.ndarray = load_puzzle_points(puzzle)
    # calculate rotational symmetries
    rotations: list[tuple[float, np.ndarray, np.ndarray]] = find_rotational_symmetries(
        X=point_coordinates,
        num_candidate_rotations = 20000, # number of candidate rotations to consider
        plane_similarity_threshold = 0.1, # threshold for distance between planes to consider them equal
        min_angle = np.pi / 12.5, # minimum rotation angle in radians (= 1/)
        num_best_rotations = 1000, # number of best rotations to keep
        epsilon_Q = 0.05, # parameter for quarternion similarity
        epsilon_s = 0.05, # parameter for axis similarity
        min_score_ratio=0.9, # minimum score ratio between best and other rotations
    )
    if verbosity >= 1:
        print(f"Found {len(rotations)} rotational symmetries.")
    # convert rotations to moves for the puzzle
    named_rotations: dict[str, list[int]] = rotations_to_moves(point_coordinates, rotations)
    # # TODO: filter symmetries that result in otherwise invalid moves
    n_points = len(point_coordinates)
    sympy_base_moves: dict[str, Permutation] = get_sympy_moves(puzzle)
    rotation_permutations: dict[str, Permutation] = {name: Permutation(move, size=n_points) for name, move in named_rotations.items()}
    valid_rotations: list[str] = filter_rotations(sympy_base_moves, rotation_permutations)
    # sort valid rotations by their order (= rotation angle)
    valid_rotations.sort(key=lambda name: rotation_permutations[name].order())
    named_rotations: dict[str, list[int]] = {f"rot_{i+1}": rotation_permutations[name].cyclic_form for i, name in enumerate(valid_rotations)}

    # add moves to puzzle and save
    if verbosity >= 1:
        print(f"Adding {len(named_rotations)} rotational symmetries to the puzzle.")
    add_moves_to_puzzle(
        puzzle=puzzle,
        new_moves=named_rotations,
        new_puzzle_name=new_puzzle_name,
        suffix=suffix,
    )
    os._exit(0)
    

def load_puzzle_points(puzzle: "Twisty_Puzzle") -> tuple[np.ndarray, np.ndarray]:
    """
    Load the points and colors of a puzzle.

    Args:
        puzzle_name (str): name of the puzzle

    Returns:
        tuple[np.ndarray, np.ndarray]: points and colors of the puzzle
    """
    point_dicts = puzzle.POINT_INFO_DICTS
    points: list[vpy.vector] = [point["coords"] for point in point_dicts]
    point_coordinates: np.ndarray = np.array([[p.x, p.y, p.z] for p in points])
    return point_coordinates

def main():
    # load puzzle
    puzzle, puzzle_name = load_twisty_puzzle()
    
    add_rotation_moves_to_puzzle(
        puzzle=puzzle,
    )

if __name__ == "__main__":
    main()