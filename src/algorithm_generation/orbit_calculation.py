"""
This module provides methods to calculate orbits of points and pieces under a given action set.
"""
from sympy.combinatorics import Permutation

def calculate_point_orbits(
        n_points: int,
        moves: list[Permutation],
    ) -> list[set[int]]:
    """
    Calculate orbits of points under a given action set.
    1. start with all points as single-element sets.
    2. for each move, join the sets of all points that are within the same cycle in the move.
    3. repeat step 2 until no more sets can be joined. (We expect to always reach a fixed point after the first iteration.)

    Args:
        n_points: The number of points to calculate orbits for.
        moves: A list of permutations that represent the action set.

    Returns:
        list[set[int]]: A list of sets, where each set contains the indices of points in the same orbit.
    """
    point_orbits: list[set[int]] = [set([point]) for point in range(n_points)]
    for move in moves:
        for cycle in move.cyclic_form:
            # find the orbits containing each point in the cycle
            orbits_to_join: list[set[int]] = [
                i for i, orbit in enumerate(point_orbits) if not orbit.isdisjoint(cycle)]
            # orbit indices are sorted in ascending order
            if len(orbits_to_join) > 1:
                # join the orbits
                for orbit_index in orbits_to_join[-1:0:-1]: # iterate in reverse order to avoid index shifting
                    point_orbits[orbits_to_join[0]] |= point_orbits.pop(orbit_index)
    return point_orbits

def calculate_piece_orbits(
        pieces: list[set[int]],
        point_orbits: list[set[int]]
    ) -> list[list[set[int]]]:

    # Initialize piece orbits: each piece starts in its own separate orbit
    piece_orbits = [[piece] for piece in pieces]

    # Function to find and merge piece orbits affected by the same point orbit
    def merge_piece_orbits(point_orbit: set[int]):
        affected_orbits = []

        for orbit in piece_orbits:
            for piece in orbit:
                if not point_orbit.isdisjoint(piece):  # Check if point_orbit intersects with the piece
                    affected_orbits.append(orbit)
                    break

        if len(affected_orbits) > 1:
            # Merge all affected orbits into the first one
            primary_orbit = affected_orbits[0]
            for orbit in affected_orbits[1:]:
                primary_orbit.extend(orbit)
                piece_orbits.remove(orbit)

    # Iterate over all point orbits and merge affected piece orbits
    for point_orbit in point_orbits:
        merge_piece_orbits(point_orbit)

    return piece_orbits


if __name__ == "__main__":
    # add src to path
    import os, sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)
    from src.puzzle_class import Twisty_Puzzle
    import algorithm_analysis as alg_ana

    # load puzzle
    # puzzle_name: str = "rubiks_3x3_sym"
    # puzzle_name: str = "rubiks_2x2_ai"
    # puzzle_name: str = "rubiks_2x2"
    # puzzle_name: str = "skewb"
    # puzzle_name: str = "cube_4x4x4"
    puzzle_name: str = "cube_5x5x5"
    # puzzle_name: str = "gear_cube"
    # puzzle_name: str = "geared_mixup"
    # puzzle_name: str = "skewb"
    puzzle: Twisty_Puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)

    sympy_moves: dict[str, Permutation] = alg_ana.get_sympy_moves(puzzle)

    point_orbits: list[set[int]] = calculate_point_orbits(
        n_points=len(puzzle.SOLVED_STATE),
        moves=list(sympy_moves.values())
    )
    piece_orbits: list[list[set[int]]] = calculate_piece_orbits(
        pieces=puzzle.pieces,
        point_orbits=point_orbits,
    )
    # print point orbits
    print(f"\nCalculated {len(point_orbits)} point orbits:")
    point_orbits = sorted(point_orbits, key=len)
    for i, orbit in enumerate(point_orbits):
        print(f"Orbit {i+1} with {len(orbit)} points:")
        print(f"  {orbit}")
    # print piece orbits
    print(f"\ncalculated {len(piece_orbits)} piece orbits.")
    piece_orbits = sorted(piece_orbits, key=lambda orbit: (len(orbit[0]), len(orbit)))
    for i, orbit in enumerate(piece_orbits):
        print(f"Orbit {i+1} with {len(orbit)} pieces of size {len(orbit[0])}:")
        print(f"  {orbit}")

    os._exit(0)
