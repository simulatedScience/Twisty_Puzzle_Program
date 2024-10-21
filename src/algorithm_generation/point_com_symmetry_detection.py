"""
This module implements an alternative method for rotational symmetry detection that uses both the puzzle's geometry and defined moves.

1. For each move m, calculate the COM of all points affected by m.
2. calculate a move signature for each move (n_points_affected, (cycle_length_1, n_cycles_1), (cycle_length_2, n_cycles_2), ...)
3. Collect all move COMs in sets for each move signature
4. let M_s be the smallest set of move COMs (by number of points)
5. select two points p1, p2 from M_s (p1 != p2)
6. select two points t1, t2 in the smallest set of move COMs
7. For each t1 in the smallest set of move COMs
        For each t2 in the smallest set of move COMs (t1 != t2)
            If angle(p1, p2) != angle(t1, t2) or
                    dist(p1, p2) != dist(t1, t2):
                continue
            rotate p1 to t1 and p2 to t2.
            From this rota, calculate a rotation matrix R
            apply R to all other points and record the symmetry measure.
8. choose all rotations with close to maximum symmetry measure.
"""
from collections import Counter

import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation
from sympy.combinatorics import Permutation

from algorithm_analysis import get_inverse_moves_dict
from find_puzzle_symmetries_CLI import get_puzzle_points, rotations_to_moves
from symmetry_plane_detection import dist_similarity_function
from test_symmetry_plane_detection import set_equal_aspect_3d

DEBUG: bool = True

def find_rotational_symmetries(
        puzzle: "Twisty_Puzzle",
        min_sym_measure: float = 0.7,
        min_angle_rad: float = 0.1):
    """
    remove inverse moves
    """
    inverse_dict: dict[str, str] = get_inverse_moves_dict(puzzle.moves)
    reduced_moves: dict[str, list[list[int]]] = {}
    for move_name, move_cycles in puzzle.moves.items():
        if inverse_dict[move_name] in reduced_moves:
            continue
        reduced_moves[move_name] = move_cycles
    X: np.ndarray = get_puzzle_points(puzzle)
    com_x = np.mean(X, axis=0)
    move_coms = reduce_to_coms(X, reduced_moves)
    
    # calculate alpha = 20/average distance between points
    d_avg: float = np.mean(np.linalg.norm(X[:, np.newaxis] - X, axis=2))
    alpha: float = 20 / d_avg
    
    if DEBUG:
        fig = plt.figure()
        ax = fig.add_subplot(111, projection="3d")
        set_equal_aspect_3d(ax)
        ax.scatter(X[:, 0], X[:, 1], X[:, 2], c="#000", label="puzzle points", s=200, alpha=0.3)
        Y = np.array(list(move_coms.values()))
        ax.scatter(Y[:, 0], Y[:, 1], Y[:, 2], c="#f00", label="move COMs")
    
    move_signatures: dict[str, tuple[tuple[int, int], ...]] = get_move_signatures(reduced_moves)
    # remove signatures for discarded moves
    move_signatures = {move_name: move_signatures[move_name] for move_name in move_coms.keys()}
    # group move_coms bs move signature
    signatures_to_names: dict[tuple[tuple[int, int], ...], list[str]] = {}
    for move_name, move_signature in move_signatures.items():
        if move_signature not in signatures_to_names:
            signatures_to_names[move_signature] = []
        signatures_to_names[move_signature].append(move_name)
    # find the smallest set of move COMs
    smallest_com_set: list[np.ndarray] = min(signatures_to_names.values(), key=lambda move_names: len(move_names))
    # select two points from the smallest set
    p1: np.ndarray = move_coms[smallest_com_set[0]].copy()
    if len(smallest_com_set) > 1:
        p2_options = [move_coms[move_name] for move_name in smallest_com_set[1:]]
        # choose p2 in com_sets such that it is not parallel to p1
        for p2 in p2_options:
            if _angle_between(p1, p2) < 1e-4 or _angle_between(p1, p2) > np.pi - 1e-4:
                continue
            break
        smallest_com_set2: list[np.ndarray] = smallest_com_set
    else: # TODO: untested code block
        # get second smallest set of COMs
        smallest_com_set2 = min([move_names for move_names in signatures_to_names.values() if not move_names == smallest_com_set], key=lambda move_names: len(move_names))
        p2: np.ndarray = move_coms[smallest_com_set2[0]].copy()
        p2_options = [move_names for move_names in signatures_to_names.values() if not move_names == smallest_com_set2]
        # choose p2 in com_sets such that it is not parallel to p1
        for p2 in p2_options:
            if _angle_between(p1, p2) < 1e-4 or _angle_between(p1, p2) > np.pi - 1e-4:
                continue
            break

    symmetries: list[tuple[np.ndarray, float]] = [] # store rotation matrices and symmetry measures of good symmetries
    min_sym_measure: float = X.shape[0] * min_sym_measure

    i = 1
    for t1 in (move_coms[move_name] for move_name in smallest_com_set):
        for t2 in (move_coms[move_name] for move_name in smallest_com_set2):
            if np.all(t2 == p2) and np.all(t1 == p1):
                continue
            # check if angle between p1 and p2 matches angle between t1 and t2
            if np.abs(_angle_between(p1, p2) - _angle_between(t1, t2)) > 1e-4:
                continue
            # calculate rotation matrix R
            R: Rotation = _calculate_rotation_matrix(
                    p1.copy(),
                    p2.copy(),
                    t1.copy(),
                    t2.copy())
            # apply R to all other points and record the symmetry measure
            # for move_name, move_com in move_coms.items():
            # if move_name in smallest_com_set or move_name in smallest_com_set2:
            #     continue
            # rotated_points: np.ndarray = (R @ (X - p1).T).T + t1
            rotated_points: np.ndarray = (R @ X.T).T
            if DEBUG:
                print(f"p1 = {p1}")
                print(f"p2 = {p2}")
                print(f"t1 = {t1}")
                print(f"t2 = {t2}")
                print()
                # plot p1, p2, t1, t2 as vectors with base at COM(X)
                rot_artists = []
                for v, label, color in zip(
                        (p1, p2, t1*.6, t2*.6),
                        ("p1", "p2", "t1", "t2"),
                        ("#58f", "#0f0", "#259", "#090")):
                    rot_artists.append(ax.quiver(com_x[0], com_x[1], com_x[2], v[0], v[1], v[2], color=color, label=label))
                # plot rotated points
                scaled_points = rotated_points
                rot_artists.append(ax.scatter(scaled_points[:, 0], scaled_points[:, 1], scaled_points[:, 2], c="#2f2", label="rotated points*1.05", s=30, alpha=1))
                # plt.legend()
                plt.pause(1/2)
            
            # rotated_points: np.ndarray = R @ X
            # calculate symmetry measure
            sym_measure: float = _rotation_symmetry_measure(X, rotated_points, alpha)
            print(f"Symmetry measure for rot_{i}: {sym_measure}")
            i += 1
            if sym_measure > min_sym_measure:
                rotvec: np.ndarray = Rotation.from_matrix(R).as_rotvec()
                norm: float = np.linalg.norm(rotvec)
                if norm >= min_angle_rad:
                    symmetries.append((norm, rotvec/norm, com_x))
            # else:
            #     print(f"Symmetry measure {sym_measure} too low. Required {min_sym_measure}.")
            if DEBUG:
                # delete last symmetry drawing
                input("Press Enter to continue.")
                for artist in rot_artists:
                    artist.remove()

    rotation_moves: dict[str, list[int]] = rotations_to_moves(X, symmetries)
    # filter duplicates
    unique_move_perms: set[tuple[int]] = set()
    for move_name, move_perm in rotation_moves.items():
        tuple_perm = tuple(move_perm)
        if tuple_perm in unique_move_perms:
            continue
        unique_move_perms.add(tuple_perm)
    
    unique_rotation_moves: dict[str, list[int]] = {f"rot_{i}": move_perm for i, move_perm in enumerate(unique_move_perms)}

    print(f"Found {len(unique_rotation_moves)} rotational symmetries:")
    for (angle, axis, support) in symmetries:
        print(f"Rotation with angle {np.rad2deg(angle):.0f}° around axis {axis} with support {support}.")
    for move_name, move_perm in unique_rotation_moves.items():
        print(f"{move_name}: {move_perm}")
        # print(f"{move_name}: {Permutation(move_perm).cyclic_form}")
    return unique_rotation_moves

def reduce_to_coms(X: np.ndarray, moves: dict[str, list[list[int]]], com_tol: float = 1e-10) -> dict[str, np.ndarray]:
    """
    Reduce the point set of a given puzzle by calculating the center of mass of the points affected by each move.
    If multiple moves have the same center of mass (up to com_tol), remove all of them from the output.

    Args:
        X (np.ndarray): set of points
        puzzle (Twisty_Puzzle): puzzle to reduce the points for
        com_tol (float): if two move-COMs are closer than this, remove them both.
            -> we recommend fallback to symmetry detection with all points.

    Returns:
        dict[str, np.ndarray]: dictionary of move names and their center of mass.
    """
    seen_moves: set[str] = set()
    move_coms: dict[str, np.ndarray] = dict()
    ignore_moves: set[str] = set()
    for move_name, move_cycles in moves.items():
        seen_moves.add(move_name)
        # flatten cycles
        point_indices = _flatten_cycles(move_cycles)
        # calculate move's COM
        move_points: np.ndarray = X[point_indices]
        move_com: np.ndarray = np.mean(move_points, axis=0)
        # add move's COM to the list
        for com_name, com in move_coms.items():
            if np.linalg.norm(move_com - com) < com_tol:
                print(f"Warning: COMs of moves {move_name} and {com_name} are too close.")
                ignore_moves.add(move_name)
                ignore_moves.add(com_name)
                continue
        move_coms[move_name] = move_com
    for move_name in ignore_moves:
        del move_coms[move_name]
    return move_coms

def get_move_signatures(moves: dict[str, list[list[int]]]) -> dict[str, tuple[tuple[int, int], ...]]:
    """
    For each move, calculate its move signature: a tuple ([(cycle_length_1, n_cycles_1), (cycle_length_2, n_cycles_2), ...]). For each different cycle length, this counts how many cycles of that length are in the move.

    Args:
        moves (dict[str, list[list[int]]]): dictionary with move names and cycle lists
            every move is represented as a list of cycles
                describing the move 
    """
    move_signatures: dict[str, tuple[int, tuple[int, int]]] = dict()
    for move_name, move_cycles in moves.items():
        move_cycle_lengths: list[int] = [len(cycle) for cycle in move_cycles]
        # count how often each cycle length appears
        cycle_counts: Counter = Counter(move_cycle_lengths)
        # create a tuple of cycle lengths and their counts
        move_signature: tuple[tuple[int, int], ...] = tuple((length, count) for length, count in cycle_counts.items())
        move_signatures[move_name] = move_signature
    return move_signatures

def _rotation_symmetry_measure(
        X: np.ndarray,
        transformed_X: np.ndarray,
        alpha: float) -> float:
    """
    Calculate the symmetry measure of a rotation. Maximum (best) value is the number of points in X.

    Args:
        X (np.ndarray): set of points
        transformed_X (np.ndarray): set of points after (rotation) transformation
        alpha (float): parameter to control the similarity function

    Returns:
        float: symmetry measure. Higher = better symmetry.
    """
    pairwise_distances = np.linalg.norm(transformed_X[:, np.newaxis] - X, axis=2)
    # Apply the distance similarity function to all distances
    similarity_measures = dist_similarity_function(pairwise_distances, alpha)
    # Sum all the similarity measures
    similarity_measure = np.sum(similarity_measures)
    return similarity_measure

def _angle_between(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Calculate the angle between two points.
    """
    return np.abs(np.arccos(np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2))))

def _calculate_rotation_matrix(p1: np.ndarray, p2: np.ndarray, t1: np.ndarray, t2: np.ndarray) -> Rotation:
    """
    Calculate the rotation matrix that rotates p1 to t1 and p2 to t2.
    
    Args:
        p1 (np.ndarray): point 1
        p2 (np.ndarray): point 2
        t1 (np.ndarray): target point 1
        t2 (np.ndarray): target point 2
    
    Returns:
        Rotation: rotation object for the final rotation. Use e.g. `R.apply(X)` or `R.as_matrix() @ X` to apply the rotation.
    """
    # normalize vectors
    p1 /= np.linalg.norm(p1)
    p2 /= np.linalg.norm(p2)
    t1 /= np.linalg.norm(t1)
    # calculate rotation axis
    rotation_axis: np.ndarray = np.cross(p1, t1)
    # calculate rotation angle
    rotation_angle1: float = _angle_between(p1, t1)
    # rotation of p1 onto t1
    if np.linalg.norm(rotation_axis) < 1e-4:
        rot_p1: Rotation = Rotation.from_matrix(np.eye(3))
    else:
        rot_p1: Rotation = Rotation.from_rotvec(rotation_angle1 * rotation_axis/np.linalg.norm(rotation_axis))
    # rotate around t1 such that p2 moves to t2
    t1_rot_p2: np.ndarray = rot_p1.apply(p2)
    # project onto plane with normal a
    t1_rot_p2 -= np.dot(t1_rot_p2, t1) * t1
    t2 -= np.dot(t2, t1) * t1
    # normalize
    t1_rot_p2 /= np.linalg.norm(t1_rot_p2)
    t2 /= np.linalg.norm(t2)
    # get rotation angle
    rotation_angle2 = _angle_between(t1_rot_p2, t2)
    rot_p2: Rotation = Rotation.from_rotvec(rotation_angle2 * t1)
    # combine rotations into one matrix such that R(x) = rot2(rot1(x))
    R1 = rot_p1.as_matrix()
    R2 = rot_p2.as_matrix()
    R = R1 @ R2
    # R = Rotation.from_matrix(R)
    return R

def _flatten_cycles(move_cycles: list[list[int]]) -> np.ndarray:
    """
    Flatten a list of cycles into a list of point indices.

    Args:
        move_cycles (list[list[int]]): list of cycles as lists of integers

    Returns:
        np.ndarray: flattened list of point indices
    """
    return np.concatenate(move_cycles)

if __name__ == "__main__":
    from algorithm_generation_CLI import load_twisty_puzzle
    puzzle, puzzle_name = load_twisty_puzzle()
    move_coms = find_rotational_symmetries(puzzle)
    # plot move COMs
    # import matplotlib.pyplot as plt
    # # create 3D axes
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection="3d")
    # X = get_puzzle_points(puzzle)
    # ax.scatter(X[:, 0], X[:, 1], X[:, 2], c="#000", label="puzzle points")

    # move_coms = np.array(list(move_coms.values()))
    # ax.scatter(move_coms[:, 0], move_coms[:, 1], move_coms[:, 2], c="#f00", label="move COMs")
    # ax.legend()
    # plt.show()