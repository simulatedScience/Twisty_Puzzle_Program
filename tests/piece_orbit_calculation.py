from sympy.combinatorics import Permutation

def calculate_point_orbits(n_points: int, moves: list[Permutation]) -> list[set[int]]:
    def apply_move(point: int, move: Permutation) -> int:
        try:
            return move(point)
        except (TypeError, IndexError):
            return point

    orbits = []
    visited = set()

    for point in range(n_points):
        if point not in visited:
            orbit = set()
            queue = [point]

            while queue:
                current = queue.pop(0)
                if current not in orbit:
                    orbit.add(current)
                    visited.add(current)
                    for move in moves:
                        new_point = apply_move(current, move)
                        if new_point not in orbit:
                            queue.append(new_point)
            
            orbits.append(orbit)
    
    return orbits

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

# Example usage:
if __name__ == "__main__":
    # add src to path
    import os, sys, inspect
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 
    from src.puzzle_class import Twisty_Puzzle
    import algorithm_analysis as alg_ana

    # load puzzle
    # puzzle_name: str = "rubiks_3x3"
    # puzzle_name: str = "rubiks_2x2_ai"
    puzzle_name: str = "rubiks_2x2"
    # puzzle_name: str = "skewb"
    # puzzle_name: str = "cube_4x4x4"
    # puzzle_name: str = "gear_cube"
    puzzle: Twisty_Puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)
    
    sympy_moves: dict[str, Permutation] = alg_ana.get_sympy_dict(puzzle)
    
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
        # print(f"  {orbit}")
    # print piece orbits
    print(f"\ncalculated {len(piece_orbits)} piece orbits.")
    piece_orbits = sorted(piece_orbits, key=lambda orbit: (len(orbit[0]), len(orbit)))
    for i, orbit in enumerate(piece_orbits):
        print(f"Orbit {i+1} with {len(orbit)} pieces of size {len(orbit[0])}:")
        # print(f"  {orbit}")

    # # calculate group order from orbits:
    # from math import lcm, prod, factorial
    # group_order_upper = prod([factorial(len(orbit)) for orbit in piece_orbits])
    # # group_order_upper = prod([len(orbit) for orbit in point_orbits])
    # group_order_lower = lcm(*[len(orbit) for orbit in piece_orbits])
    # group_order_middle = group_order_upper // group_order_lower
    # print(f"Estimated group order: {group_order_upper:6e} > |G| > {group_order_lower},\nmaybe {group_order_middle:6e}")
    # exit
    os._exit(0)