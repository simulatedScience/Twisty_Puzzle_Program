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
    # rotations = rubiks_2x2_rotations()
    rotations = rubiks_algs_rotations()
    # rotations = square_two_algs()
    moves = permutations_to_moves(rotations)
    for move in moves:
        print(f"{move}: {moves[move]}")

    # add_moves_to_puzzle(
    #     "skewb",
    #     moves,
    #     new_puzzle_name="skewb_sym")
    add_moves_to_puzzle(
        # "rubiks_2x2",
        "rubiks_algs",
        # "square_two",
        moves,
        # new_puzzle_name="square_two_algs")
        new_puzzle_name="rubiks_algs")

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

def rubiks_algs_rotations():
    return {
    "rot_1": [45, 46, 47, 49, 52, 50, 53, 28, 30, 27, 34, 35, 32, 33, 31, 29, 48, 51, 38, 37, 36, 41, 40, 39, 44, 43, 42, 9, 7, 15, 8, 14, 12, 13, 10, 11, 20, 19, 18, 23, 22, 21, 26, 25, 24, 0, 1, 2, 16, 3, 5, 17, 4, 6],
    "rot_2": [17, 16, 0, 3, 5, 1, 2, 27, 34, 28, 30, 29, 32, 31, 33, 35, 4, 6, 8, 15, 7, 13, 12, 14, 9, 11, 10, 44, 36, 37, 38, 39, 40, 41, 42, 43, 24, 25, 26, 21, 22, 23, 18, 19, 20, 47, 50, 53, 46, 49, 52, 45, 48, 51],
    "rot_3": [42, 43, 44, 40, 37, 41, 38, 30, 27, 34, 28, 31, 32, 35, 29, 33, 39, 36, 2, 5, 6, 1, 3, 4, 0, 16, 17, 47, 51, 52, 53, 48, 49, 50, 45, 46, 26, 23, 20, 25, 22, 19, 24, 21, 18, 9, 13, 8, 11, 12, 15, 10, 14, 7],
    "rot_4": [10, 11, 9, 12, 15, 13, 8, 34, 28, 30, 27, 33, 32, 29, 35, 31, 14, 7, 53, 52, 51, 50, 49, 48, 47, 46, 45, 0, 6, 5, 2, 4, 3, 1, 17, 16, 18, 21, 24, 19, 22, 25, 20, 23, 26, 44, 41, 38, 43, 40, 37, 42, 39, 36],
    "rot_5": [2, 5, 6, 3, 16, 4, 17, 20, 18, 24, 26, 25, 22, 21, 23, 19, 1, 0, 42, 43, 44, 39, 40, 41, 36, 37, 38, 7, 9, 11, 10, 13, 12, 14, 8, 15, 28, 29, 30, 31, 32, 33, 34, 35, 27, 51, 48, 45, 52, 49, 46, 53, 50, 47],
    "rot_6": [6, 4, 17, 3, 1, 16, 0, 44, 42, 36, 38, 37, 40, 39, 41, 43, 5, 2, 34, 35, 27, 31, 32, 33, 28, 29, 30, 20, 24, 25, 26, 21, 22, 23, 18, 19, 9, 11, 10, 13, 12, 14, 8, 15, 7, 53, 52, 51, 50, 49, 48, 47, 46, 45],
    "rot_7": [27, 33, 30, 32, 31, 29, 28, 17, 6, 2, 0, 1, 3, 5, 16, 4, 35, 34, 36, 39, 42, 37, 40, 43, 38, 41, 44, 10, 8, 13, 9, 15, 12, 11, 7, 14, 53, 50, 47, 52, 49, 46, 51, 48, 45, 26, 25, 24, 23, 22, 21, 20, 19, 18],
    "rot_8": [51, 48, 45, 49, 50, 46, 47, 9, 10, 7, 8, 15, 12, 14, 13, 11, 52, 53, 30, 29, 28, 33, 32, 31, 27, 35, 34, 24, 20, 19, 18, 23, 22, 21, 26, 25, 44, 43, 42, 41, 40, 39, 38, 37, 36, 2, 5, 6, 1, 3, 4, 0, 16, 17],
    "rot_9": [34, 35, 27, 32, 29, 33, 30, 10, 7, 8, 9, 13, 12, 15, 11, 14, 31, 28, 6, 4, 17, 5, 3, 16, 2, 1, 0, 45, 53, 50, 47, 52, 49, 46, 51, 48, 38, 41, 44, 37, 40, 43, 36, 39, 42, 24, 21, 18, 25, 22, 19, 26, 23, 20],
    "rot_10": [47, 50, 53, 49, 48, 52, 51, 36, 38, 44, 42, 43, 40, 41, 39, 37, 46, 45, 26, 25, 24, 23, 22, 21, 20, 19, 18, 28, 27, 35, 34, 33, 32, 31, 30, 29, 7, 15, 8, 14, 12, 13, 10, 11, 9, 17, 16, 0, 4, 3, 1, 6, 5, 2],
    "rot_11": [53, 52, 51, 49, 46, 48, 45, 24, 26, 20, 18, 19, 22, 23, 21, 25, 50, 47, 10, 11, 9, 14, 12, 13, 7, 15, 8, 36, 44, 43, 42, 41, 40, 39, 38, 37, 27, 35, 34, 33, 32, 31, 30, 29, 28, 6, 4, 17, 5, 3, 16, 2, 1, 0],
    "rot_12": [9, 13, 8, 12, 14, 15, 7, 51, 53, 47, 45, 46, 49, 50, 48, 52, 11, 10, 20, 23, 26, 19, 22, 25, 18, 21, 24, 34, 30, 33, 27, 29, 32, 35, 28, 31, 6, 5, 2, 4, 3, 1, 17, 16, 0, 42, 43, 44, 39, 40, 41, 36, 37, 38],
    "rot_13": [44, 41, 38, 40, 39, 37, 36, 6, 2, 0, 17, 16, 3, 1, 4, 5, 43, 42, 24, 21, 18, 25, 22, 19, 26, 23, 20, 30, 34, 31, 28, 35, 32, 29, 27, 33, 51, 52, 53, 48, 49, 50, 45, 46, 47, 10, 11, 9, 14, 12, 13, 7, 15, 8],
    "rot_14": [26, 25, 24, 22, 19, 21, 18, 8, 9, 10, 7, 14, 12, 11, 15, 13, 23, 20, 47, 50, 53, 46, 49, 52, 45, 48, 51, 2, 17, 4, 6, 16, 3, 5, 0, 1, 42, 39, 36, 43, 40, 37, 44, 41, 38, 27, 33, 30, 35, 32, 29, 34, 31, 28],
    "rot_15": [36, 39, 42, 40, 41, 43, 44, 47, 45, 51, 53, 52, 49, 48, 50, 46, 37, 38, 27, 33, 30, 35, 32, 29, 34, 31, 28, 18, 26, 23, 20, 25, 22, 19, 24, 21, 0, 16, 17, 1, 3, 4, 2, 5, 6, 8, 15, 7, 13, 12, 14, 9, 11, 10],
    "rot_16": [7, 14, 10, 12, 13, 11, 9, 0, 17, 6, 2, 5, 3, 4, 1, 16, 15, 8, 28, 31, 34, 29, 32, 35, 30, 33, 27, 26, 18, 21, 24, 19, 22, 25, 20, 23, 47, 46, 45, 50, 49, 48, 53, 52, 51, 38, 37, 36, 41, 40, 39, 44, 43, 42],
    "rot_17": [18, 19, 20, 22, 25, 23, 26, 38, 44, 42, 36, 39, 40, 43, 37, 41, 21, 24, 0, 1, 2, 16, 3, 5, 17, 4, 6, 53, 45, 48, 51, 46, 49, 52, 47, 50, 10, 14, 7, 11, 12, 15, 9, 13, 8, 28, 31, 34, 29, 32, 35, 30, 33, 27],
    "rot_18": [20, 23, 26, 22, 21, 25, 24, 2, 0, 17, 6, 4, 3, 16, 5, 1, 19, 18, 9, 13, 8, 11, 12, 15, 10, 14, 7, 38, 42, 39, 36, 43, 40, 37, 44, 41, 45, 48, 51, 46, 49, 52, 47, 50, 53, 30, 29, 28, 33, 32, 31, 27, 35, 34],
    "rot_19": [24, 21, 18, 22, 23, 19, 20, 53, 47, 45, 51, 48, 49, 46, 52, 50, 25, 26, 44, 41, 38, 43, 40, 37, 42, 39, 36, 8, 10, 14, 7, 11, 12, 15, 9, 13, 17, 4, 6, 16, 3, 5, 0, 1, 2, 34, 35, 27, 31, 32, 33, 28, 29, 30],
    "rot_20": [30, 29, 28, 32, 35, 31, 34, 42, 36, 38, 44, 41, 40, 37, 43, 39, 33, 27, 51, 48, 45, 52, 49, 46, 53, 50, 47, 17, 2, 1, 0, 5, 3, 16, 6, 4, 8, 13, 9, 15, 12, 11, 7, 14, 10, 20, 23, 26, 19, 22, 25, 18, 21, 24],
    "rot_21": [28, 31, 34, 32, 33, 35, 27, 45, 51, 53, 47, 50, 49, 52, 46, 48, 29, 30, 7, 14, 10, 15, 12, 11, 8, 13, 9, 42, 38, 41, 44, 37, 40, 43, 36, 39, 2, 1, 0, 5, 3, 16, 6, 4, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
    "rot_22": [38, 37, 36, 40, 43, 39, 42, 18, 24, 26, 20, 23, 22, 25, 19, 21, 41, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 6, 0, 16, 17, 1, 3, 4, 2, 5, 34, 31, 28, 35, 32, 29, 27, 33, 30, 7, 14, 10, 15, 12, 11, 8, 13, 9],
    "rot_23": [8, 15, 7, 12, 11, 14, 10, 26, 20, 18, 24, 21, 22, 19, 25, 23, 13, 9, 17, 16, 0, 4, 3, 1, 6, 5, 2, 51, 47, 46, 45, 50, 49, 48, 53, 52, 30, 33, 27, 29, 32, 35, 28, 31, 34, 36, 39, 42, 37, 40, 43, 38, 41, 44],
    }

def square_two_algs():
    return {
        "cycle_4": [4, 1, 2, 3, 7, 5, 6, 10, 8, 9, 0, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 27, 25, 26, 30, 28, 29, 33, 31, 32, 24, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
        "cycle_2_2": [0, 1, 2, 3, 10, 5, 6, 7, 8, 9, 4, 11, 12, 13, 20, 15, 16, 17, 18, 19, 14, 21, 22, 23, 24, 25, 26, 33, 28, 29, 30, 31, 32, 27, 34, 35, 36, 37, 38, 39, 46, 41, 42, 43, 44, 45, 40, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
        "cycle_5": [0, 1, 2, 3, 4, 5, 16, 7, 8, 6, 10, 11, 12, 9, 14, 15, 17, 13, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 42, 30, 31, 29, 33, 34, 35, 36, 37, 38, 32, 40, 41, 43, 39, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
        "cycle_2_2*": [0, 1, 15, 3, 4, 5, 6, 7, 21, 9, 10, 11, 12, 13, 14, 2, 16, 17, 18, 19, 20, 8, 22, 23, 24, 41, 26, 27, 28, 29, 30, 47, 32, 33, 34, 35, 36, 37, 38, 39, 40, 25, 42, 43, 44, 45, 46, 31, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
        "flip_middle": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 53, 52, 51, 50, 49, 48, 54, 55, 56, 57, 58, 59],
        "cycle_3": [0, 1, 2, 3, 4, 5, 6, 7, 21, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 9, 22, 23, 24, 25, 26, 27, 28, 29, 30, 47, 31, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 32, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59],
    }


if __name__ == "__main__":
    main()