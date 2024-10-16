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

import numpy as np

from algorithm_analysis import get_inverse_moves_dict
from find_puzzle_symmetries_CLI import get_puzzle_points

def find_rotational_symmetries(puzzle: "Twisty_Puzzle"):
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
    move_coms = reduce_to_coms(X, reduced_moves)
    move_signatures: dict[str, tuple[tuple[int, int], ...]] = get_move_signatures(reduced_moves)
    # group move_coms bs move signature
    signatures_to_names: dict[tuple[tuple[int, int], ...], list[str]] = {}
    for move_name, move_signature in move_signatures.items():
        if move_signature not in signatures_to_names:
            signatures_to_names[move_signature] = []
        signatures_to_names[move_signature].append(move_name)
    # find the smallest set of move COMs
    smallest_com_set: list[np.ndarray] = min(signatures_to_names.values(), key=lambda move_names: len(move_names))
    # select two points from the smallest set
    p1: np.ndarray = move_coms[smallest_com_set[0]]
    if len(smallest_com_set) > 1:
        p2: np.ndarray = move_coms[smallest_com_set[1]]
        smallest_com_set2 = smallest_com_set[1:]
    else:
        # get second smallest set of COMs
        smallest_com_set2 = min([move_names for move_names in signatures_to_names.values() if not move_names == smallest_com_set], key=lambda move_names: len(move_names))
        p2: np.ndarray = move_coms[smallest_com_set2[0]]
    for t1 in (move_coms[move_name] for move_name in smallest_com_set):
        if np.all(t1 == p1):
            continue
        for t2 in (move_coms[move_name] for move_name in smallest_com_set2):
            if np.all(t2 == p2):
                continue
            # check if angle between p1 and p2 matches angle between t1 and t2
            if _angle_between(p1, p2) != _angle_between(t1, t2):
                continue
            # calculate rotation matrix R
            R = _calculate_rotation_matrix(p1, p2, t1, t2)
            # apply R to all other points and record the symmetry measure
            for move_name, move_com in move_coms.items():
                if move_name in smallest_com_set or move_name in smallest_com_set2:
                    continue
                rotated_points = np.dot(R, X.T).T
                # calculate symmetry measure

    return move_coms # TODO: for now

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

def _angle_between(p1: np.ndarray, p2: np.ndarray) -> float:
    """
    Calculate the angle between two points.
    """
    return np.arccos(np.dot(p1, p2) / (np.linalg.norm(p1) * np.linalg.norm(p2)))

def _calculate_rotation_matrix(p1: np.ndarray, p2: np.ndarray, t1: np.ndarray, t2: np.ndarray) -> np.ndarray:
    """
    Calculate the rotation matrix that rotates p1 to t1 and p2 to t2.
    """
    # calculate rotation axis
    rotation_axis: np.ndarray = np.cross(p1, t1)
    # calculate rotation angle
    rotation_angle: float = _angle_between(p1, t1)
    # rotate around p1 such that p2 moves to t2
    

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
    import matplotlib.pyplot as plt
    # create 3D axes
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    X = get_puzzle_points(puzzle)
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], c="#000", label="puzzle points")

    move_coms = np.array(list(move_coms.values()))
    ax.scatter(move_coms[:, 0], move_coms[:, 1], move_coms[:, 2], c="#f00", label="move COMs")
    ax.legend()
    plt.show()