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
    return move_coms # TODO: for now

def reduce_to_coms(X: np.ndarray, moves: dict[str, list[list[int]]], com_tol: float = 1e-10) -> dict[str, np.ndarray]:
    """
    Reduce the point set of a given puzzle by calculating the center of mass of the points affected by each move.

    Args:
        X (np.ndarray): set of points
        puzzle (Twisty_Puzzle): puzzle to reduce the points for
        com_tol (float): if two new points are closer than this, return empty dict
            -> recommend fallback to symmetry detection with all points.

    Returns:
        dict[str, np.ndarray]: dictionary of move names and their center of mass. Empty if any two COMs are closer than `com_tol`.
    """
    seen_moves: set[str] = set()
    move_coms: dict[str, np.ndarray] = dict()
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
                continue
        move_coms[move_name] = move_com
    return move_coms

def get_move_signatures(moves: dict[str, list[list[int]]]) -> dict[str, tuple[int, tuple[int, int]]]:
    """

    """
    raise NotImplementedError
    
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