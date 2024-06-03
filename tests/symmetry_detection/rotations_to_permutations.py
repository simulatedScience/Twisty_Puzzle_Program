"""
This module aims to complete the automatic symmetry detection by converting the rotational symmetries detected for the points of a puzzle into permutations of the puzzle's pieces.
"""
import cProfile
import pstats

import numpy as np
from scipy.spatial.transform import Rotation

from rotational_symmetry_detection import find_rotational_symmetries
# def find_permutations(

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
    if len(set(permutation)) != len(X):
        raise ValueError("Did not find a bijection between the points of X and the rotated points.")
    return permutation

# def rotation_to_move(X: np.ndarray, rotation: tuple[float, np.ndarray, np.ndarray], colors: np.ndarray) -> list[str]:
#     """
#     Convert a rotational symmetry into a move sequence of the puzzle's pieces.
#     Apply the rotation to X, then find the closest point in X to each rotated point.

#     Args:
#         X (np.ndarray): set of points
#         rotation (tuple[float, np.ndarray, np.ndarray]): rotation angle, axis, axis support
#         colors (np.ndarray): colors of the points

#     Returns:
#         list[str]: move sequence of the puzzle's pieces
#             The i'th point gets mapped to X[permutation[i]]. This is a bijection.
#     """
#     permutation = rotation_to_permutation(X, rotation)

def find_closest(X, point):
    """
    Find the closest point in X to a given point.

    Args:
        X (np.ndarray): set of points
        point (np.ndarray): point to find the closest point to

    Returns:
        int: index of the closest point in X
    """
    return np.argmin(np.linalg.norm(X - point, axis=1))

def load_puzzle_points(puzzle_name: str) -> tuple[np.ndarray, np.ndarray]:
    """
    Load the points of a puzzle into a numpy array.

    Args:
        puzzle_name (str): name of the puzzle
    """
    try:
        from src.interaction_modules.load_from_xml import load_puzzle
    except ImportError:
        import sys
        import os
        # Get the absolute path to the project's root directory (A)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
        # Add the project root and the C directory to the Python path
        sys.path.insert(0, project_root)
        from src.interaction_modules.load_from_xml import load_puzzle
    try:
        point_dicts, moves_dict, state_space_size = load_puzzle(puzzle_name)
    except FileNotFoundError:
        raise FileNotFoundError(f"Could not find the puzzle '{puzzle_name}'.")
    points = [point["coords"] for point in point_dicts]
    point_coordinates = np.array([[p.x, p.y, p.z] for p in points])
    point_colors = [point["vpy_color"] for point in point_dicts]
    point_colors = [np.array([color.x, color.y, color.z]) for color in point_colors]
    return point_coordinates, point_colors


if __name__ == "__main__":
    # points, colors = load_puzzle_points("rubiks_2x2")
    # points, colors = load_puzzle_points("rubiks_cube")
    points, colors = load_puzzle_points("gear_cube")
    # rotations = find_rotational_symmetries(
    #     X=points,
    #     num_planes=300,
    #     min_angle=np.pi/4,)
    profile = cProfile.Profile()
    rotations = profile.runcall(
        find_rotational_symmetries,
        X=points,
        num_planes = 3000,
        num_candidate_rotations = 30,
        threshold = 0.1,
        min_angle = np.pi / 12.5,
        num_best_rotations = 40,
        alpha = 1.0,)
    print(f"Found {len(rotations)} rotational symmetries.")
    ps = pstats.Stats(profile)
    ps.sort_stats(("tottime"))
    ps.print_stats(10)
    for i, rotation in enumerate(rotations):
        print(f"rot_{i+1}/{len(rotations)}: {rotation_to_permutation(points, rotation)}")
    print("Done.")
