from os import _exit

def permutation_to_cycles(perm: list[int]) -> list[list[int]]:
    """
    Given a permutation as a list of indices, where each index is mapped to perm[index], return the permutation in cycle notation.

    Args:
        perm (list[int]): permutation as a list of indices such that i -> perm[i]

    Returns:
        list[list[int]]: permutation in cycle notation
    """
    cycles = []
    visited = [False]*len(perm)
    for i in range(len(perm)):
        if not visited[i]:
            cycle = []
            j = i
            while not visited[j]:
                visited[j] = True
                cycle.append(j)
                j = perm[j]
            if len(cycle) > 1:
                cycles.append(cycle)
    return cycles

def permutations_to_moves(perms: dict[str, list[int]]) -> dict[str, list[list[int]]]:
    """
    Given a dict of named permutations, return the permutations in cycle notation with the same names.

    Args:
        perms (dict[str, list[int]]): dict of named permutations where each permutation is a list of indices such that i -> perm[i]

    Returns:
        dict[str, list[list[int]]]: dict of named permutations in cycle notation
    """
    return {name: permutation_to_cycles(perm) for name, perm in perms.items()}

def add_moves_to_puzzle(
        puzzle_name: str,
        moves: dict[str, list[list[int]]],
        new_puzzle_name: str = ""):
    """
    Given a set of moves in cycle notation, add them to the puzzle and save it again.

    Args:
        
    """
    try:
        from src.puzzle_class import Twisty_Puzzle
    except ImportError:
        import sys
        import os
        # Get the absolute path to the project's root directory (A)
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')) 
        # Add the project root and the C directory to the Python path
        sys.path.insert(0, project_root)
        from src.puzzle_class import Twisty_Puzzle
    puzzle = Twisty_Puzzle()
    puzzle.load_puzzle(puzzle_name)
    # add moves
    for move_name, move in moves.items():
        puzzle.moves[move_name] = move
    if new_puzzle_name == "":
        new_puzzle_name = puzzle_name + "_sym"
    puzzle.save_puzzle(new_puzzle_name)
    print(f"Saved puzzle with {len(moves)} new moves as {new_puzzle_name}.")
    _exit(0)

def main():
    # rotations = skewb_rotations()
    rotations = rubiks_2x2_rotations()
    moves = permutations_to_moves(rotations)
    for move in moves:
        print(f"{move}: {moves[move]}")

    # add_moves_to_puzzle(
    #     "skewb",
    #     moves,
    #     new_puzzle_name="skewb_sym")
    add_moves_to_puzzle(
        "rubiks_2x2",
        moves,
        new_puzzle_name="rubiks_2x2_sym")

def skewb_rotations():
    return {
        "rot_1": [18, 12, 14, 13, 15, 16, 17, 20, 19, 23, 21, 22, 1, 3, 2, 4, 5, 6, 0, 8, 7, 10, 11, 9, 29, 25, 28, 27, 26, 24],
        "rot_2": [12, 18, 19, 20, 23, 21, 22, 13, 14, 15, 16, 17, 0, 7, 8, 9, 10, 11, 1, 2, 3, 5, 6, 4, 29, 27, 26, 25, 28, 24],
        "rot_3": [16, 10, 11, 9, 7, 0, 8, 15, 17, 13, 12, 14, 21, 23, 22, 20, 18, 19, 5, 6, 4, 1, 2, 3, 26, 25, 29, 27, 24, 28],
        "rot_4": [17, 6, 4, 5, 19, 20, 18, 16, 15, 8, 7, 0, 11, 10, 9, 14, 13, 12, 22, 23, 21, 3, 1, 2, 25, 29, 26, 24, 28, 27],
        "rot_5": [5, 21, 22, 23, 20, 18, 19, 4, 6, 3, 1, 2, 10, 9, 11, 7, 0, 8, 16, 17, 15, 12, 14, 13, 28, 25, 24, 27, 29, 26],
        "rot_6": [23, 15, 16, 17, 18, 19, 20, 22, 21, 12, 14, 13, 9, 11, 10, 1, 2, 3, 4, 5, 6, 8, 7, 0, 29, 28, 27, 26, 25, 24],
        "rot_7": [15, 23, 21, 22, 12, 14, 13, 17, 16, 18, 19, 20, 4, 6, 5, 0, 8, 7, 9, 10, 11, 2, 3, 1, 29, 26, 25, 28, 27, 24],
        "rot_8": [11, 22, 23, 21, 2, 3, 1, 10, 9, 14, 13, 12, 17, 16, 15, 8, 7, 0, 6, 4, 5, 20, 18, 19, 27, 24, 26, 29, 28, 25],
        "rot_9": [1, 0, 8, 7, 9, 10, 11, 3, 2, 4, 5, 6, 18, 20, 19, 23, 21, 22, 12, 14, 13, 16, 17, 15, 24, 27, 28, 25, 26, 29],
        "rot_10": [22, 11, 9, 10, 14, 13, 12, 21, 23, 2, 3, 1, 6, 5, 4, 19, 20, 18, 17, 15, 16, 7, 0, 8, 27, 29, 28, 24, 26, 25],
        "rot_11": [4, 9, 10, 11, 1, 2, 3, 6, 5, 0, 8, 7, 15, 17, 16, 18, 19, 20, 23, 21, 22, 14, 13, 12, 24, 28, 25, 26, 27, 29],
        "rot_12": [9, 4, 5, 6, 0, 8, 7, 11, 10, 1, 2, 3, 23, 22, 21, 12, 14, 13, 15, 16, 17, 19, 20, 18, 24, 26, 27, 28, 25, 29],
        "rot_13": [6, 17, 15, 16, 8, 7, 0, 5, 4, 19, 20, 18, 22, 21, 23, 2, 3, 1, 11, 9, 10, 13, 12, 14, 25, 24, 28, 29, 26, 27],
        "rot_14": [21, 5, 6, 4, 3, 1, 2, 23, 22, 20, 18, 19, 16, 15, 17, 13, 12, 14, 10, 11, 9, 0, 8, 7, 28, 27, 29, 25, 24, 26],
        "rot_15": [10, 16, 17, 15, 13, 12, 14, 9, 11, 7, 0, 8, 5, 4, 6, 3, 1, 2, 21, 22, 23, 18, 19, 20, 26, 27, 24, 25, 29, 28],
        "rot_16": [20, 3, 1, 2, 21, 22, 23, 19, 18, 5, 6, 4, 7, 8, 0, 16, 17, 15, 13, 12, 14, 11, 9, 10, 28, 29, 25, 24, 27, 26],
        "rot_17": [19, 8, 7, 0, 6, 4, 5, 18, 20, 17, 15, 16, 14, 12, 13, 22, 23, 21, 2, 3, 1, 9, 10, 11, 25, 28, 29, 26, 24, 27],
        "rot_18": [14, 2, 3, 1, 11, 9, 10, 12, 13, 22, 23, 21, 19, 18, 20, 17, 15, 16, 8, 7, 0, 4, 5, 6, 27, 26, 29, 28, 24, 25],
        "rot_19": [3, 20, 18, 19, 5, 6, 4, 2, 1, 21, 22, 23, 13, 14, 12, 10, 11, 9, 7, 0, 8, 17, 15, 16, 28, 24, 27, 29, 25, 26],
        "rot_20": [2, 14, 13, 12, 22, 23, 21, 1, 3, 11, 9, 10, 8, 0, 7, 6, 4, 5, 19, 20, 18, 15, 16, 17, 27, 28, 24, 26, 29, 25],
        "rot_21": [13, 7, 0, 8, 16, 17, 15, 14, 12, 10, 11, 9, 3, 2, 1, 21, 22, 23, 20, 18, 19, 6, 4, 5, 26, 29, 27, 24, 25, 28],
        "rot_22": [7, 13, 12, 14, 10, 11, 9, 8, 0, 16, 17, 15, 20, 19, 18, 5, 6, 4, 3, 1, 2, 22, 23, 21, 26, 24, 25, 29, 27, 28],
        "rot_23": [8, 19, 20, 18, 17, 15, 16, 0, 7, 6, 4, 5, 2, 1, 3, 11, 9, 10, 14, 13, 12, 23, 21, 22, 25, 26, 24, 28, 29, 27],
    }

def rubiks_2x2_rotations():
    return {
        "rot_1": [15, 23, 21, 22, 12, 14, 13, 17, 16, 18, 19, 20, 4, 6, 5, 0, 8, 7, 9, 10, 11, 2, 3, 1],
        "rot_2": [23, 15, 16, 17, 18, 19, 20, 22, 21, 12, 14, 13, 9, 11, 10, 1, 2, 3, 4, 5, 6, 8, 7, 0],
        "rot_3": [12, 18, 19, 20, 23, 21, 22, 13, 14, 15, 16, 17, 0, 7, 8, 9, 10, 11, 1, 2, 3, 5, 6, 4],
        "rot_4": [5, 21, 22, 23, 20, 18, 19, 4, 6, 3, 1, 2, 10, 9, 11, 7, 0, 8, 16, 17, 15, 12, 14, 13],
        "rot_5": [11, 22, 23, 21, 2, 3, 1, 10, 9, 14, 13, 12, 17, 16, 15, 8, 7, 0, 6, 4, 5, 20, 18, 19],
        "rot_6": [17, 6, 4, 5, 19, 20, 18, 16, 15, 8, 7, 0, 11, 10, 9, 14, 13, 12, 22, 23, 21, 3, 1, 2],
        "rot_7": [18, 12, 14, 13, 15, 16, 17, 20, 19, 23, 21, 22, 1, 3, 2, 4, 5, 6, 0, 8, 7, 10, 11, 9],
        "rot_8": [1, 0, 8, 7, 9, 10, 11, 3, 2, 4, 5, 6, 18, 20, 19, 23, 21, 22, 12, 14, 13, 16, 17, 15],
        "rot_9": [4, 9, 10, 11, 1, 2, 3, 6, 5, 0, 8, 7, 15, 17, 16, 18, 19, 20, 23, 21, 22, 14, 13, 12],
        "rot_10": [8, 19, 20, 18, 17, 15, 16, 0, 7, 6, 4, 5, 2, 1, 3, 11, 9, 10, 14, 13, 12, 23, 21, 22],
        "rot_11": [20, 3, 1, 2, 21, 22, 23, 19, 18, 5, 6, 4, 7, 8, 0, 16, 17, 15, 13, 12, 14, 11, 9, 10],
        "rot_12": [14, 2, 3, 1, 11, 9, 10, 12, 13, 22, 23, 21, 19, 18, 20, 17, 15, 16, 8, 7, 0, 4, 5, 6],
        "rot_13": [2, 14, 13, 12, 22, 23, 21, 1, 3, 11, 9, 10, 8, 0, 7, 6, 4, 5, 19, 20, 18, 15, 16, 17],
        "rot_14": [3, 20, 18, 19, 5, 6, 4, 2, 1, 21, 22, 23, 13, 14, 12, 10, 11, 9, 7, 0, 8, 17, 15, 16],
        "rot_15": [9, 4, 5, 6, 0, 8, 7, 11, 10, 1, 2, 3, 23, 22, 21, 12, 14, 13, 15, 16, 17, 19, 20, 18],
        "rot_16": [19, 8, 7, 0, 6, 4, 5, 18, 20, 17, 15, 16, 14, 12, 13, 22, 23, 21, 2, 3, 1, 9, 10, 11],
        "rot_17": [10, 16, 17, 15, 13, 12, 14, 9, 11, 7, 0, 8, 5, 4, 6, 3, 1, 2, 21, 22, 23, 18, 19, 20],
        "rot_18": [21, 5, 6, 4, 3, 1, 2, 23, 22, 20, 18, 19, 16, 15, 17, 13, 12, 14, 10, 11, 9, 0, 8, 7],
        "rot_19": [7, 13, 12, 14, 10, 11, 9, 8, 0, 16, 17, 15, 20, 19, 18, 5, 6, 4, 3, 1, 2, 22, 23, 21],
        "rot_20": [13, 7, 0, 8, 16, 17, 15, 14, 12, 10, 11, 9, 3, 2, 1, 21, 22, 23, 20, 18, 19, 6, 4, 5],
        "rot_21": [16, 10, 11, 9, 7, 0, 8, 15, 17, 13, 12, 14, 21, 23, 22, 20, 18, 19, 5, 6, 4, 1, 2, 3],
        "rot_22": [6, 17, 15, 16, 8, 7, 0, 5, 4, 19, 20, 18, 22, 21, 23, 2, 3, 1, 11, 9, 10, 13, 12, 14],
        "rot_23": [22, 11, 9, 10, 14, 13, 12, 21, 23, 2, 3, 1, 6, 5, 4, 19, 20, 18, 17, 15, 16, 7, 0, 8],
    }
if __name__ == "__main__":
    main()