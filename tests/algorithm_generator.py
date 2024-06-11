import random

# add src to path
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir) 
from src.smart_scramble import smart_scramble
from src.puzzle_class import Twisty_Puzzle
from src.interaction_modules.colored_text import colored_text
import algorithm_analysis as alg_ana
from sympy.combinatorics import Permutation


def generate_algorithms(
        puzzle,
        sympy_moves,
        max_base_sequence_length=16,
        find_n_algorithms=10,
        max_pieces_affected=6,
        max_order=6,
        max_move_sequence_order=100,
        max_algorithm_length=150,
        ) -> dict[tuple[str, int], str]:
    """
    Generate a list of algorithms that can be used to scramble the puzzle.
    
    Args:
        puzzle (Twisty_Puzzle): puzzle to generate algorithms for
        sympy_moves (dict): dictionary of sympy moves for the puzzle
        max_base_sequence_length (int): maximum length of the base sequence
        find_n_algorithms (int): number of algorithms to find
        max_pieces_affected (int): maximum number of pieces affected by the algorithm
        max_order (int): maximum order of the algorithm
        max_move_sequence_order (int): maximum order of the move sequence
        max_algorithm_length (int): maximum length of the algorithm
    """
    found_algorithms: dict[tuple[str, int], str] = dict()
    while len(found_algorithms) < find_n_algorithms:
        # choose random sequence length
        sequence_length: int = random.randint(2, max_base_sequence_length)
        algorithm_base: list[str] = smart_scramble(
                puzzle.SOLVED_STATE,
                puzzle.moves,
                sequence_length)
        # algorithm_base = ["t", "t", "d'", "d'", "f", "b'"]
        algorithm_base_str = " ".join(algorithm_base)
        new_algorithms = alg_ana.analyse_alg(
            algorithm_base_str ,
            sympy_moves,
            puzzle.pieces,
            max_pieces=max_pieces_affected,
            max_order=max_order,
            max_move_sequence_order=max_move_sequence_order,
        )
        for alg_key, alg_moves in new_algorithms.items():
            if len(alg_moves.split(" ")) > max_algorithm_length:
                continue
            found_algorithms[alg_key] = alg_moves
    return found_algorithms

def user_test_algorithms(
        puzzle: Twisty_Puzzle,
        sympy_moves: dict,
        puzzle_algorithms: dict,
        draw_pieces: bool = True,
        move_text_color: str = "#5588ff"):
    """
    Given a dict of generated algorithms and a puzzle, allow the user to test and view the algorithms.

    Args:
        puzzle (Twisty_Puzzle): puzzle for which the algorithms were generated
        sympy_moves (dict): dictionary of sympy moves for the puzzle
        puzzle_algorithms (dict): dictionary of generated algorithms
    """
    if draw_pieces:
        puzzle.draw_3d_pieces()
    user_input_algorithms = dict()
    for alg_nbr, (key, alg_moves) in enumerate(puzzle_algorithms.items()):
        alg_nbr += 1
        user_input_algorithms[alg_nbr] = {
            "alg_moves": alg_moves,
            "base_sequence": key[0],
            "n_reps": key[1]
        }
    # sort by algorithm length   l := n_rep * len(base_sequence.split(" "))
    user_input_algorithms = dict(sorted(
        user_input_algorithms.items(),
        key=lambda x: x[1]["n_reps"] * len(x[1]["base_sequence"].split(" ")),
        reverse=True))
    def list_algs():
        print("Available algorithms:")
        for alg_nbr, alg in user_input_algorithms.items():
            # get order and affected pieces
            alg_order, alg_permutation = get_alg_order(alg, sympy_moves)
            affected_pieces = alg_ana.get_affected_pieces(alg_permutation, puzzle.pieces)
            length = alg["n_reps"] * len(alg["base_sequence"].split(" "))
            print(f"{alg_nbr:2}", end=": ")
            print(f"len={int(length):3}", end=", ")
            print(f"order={int(alg_order):3}", end=", ")
            print(f"pieces={len(affected_pieces):3}", end=", ")
            print(f"{alg['n_reps']}*({alg['base_sequence']})")
            # print(f"{alg_nbr:2}: len={length:3}, order={alg_order:3}, pieces={len(affected_pieces):3}" + 
            #         f"{alg['n_reps']}*({alg['base_sequence']})")
    list_algs()

    saved_algs: dict[str, dict[str, str|str|int]] = dict()
    user_input: str = ""
    while user_input.lower() != "exit":
        user_input = input("Enter an algorithm number to show or\n 'list' to list available ones or\n 'exit' to quit the program:\n ")
        if user_input.lower() == "exit":
            print("Exiting program.")
            break
        if user_input.lower() == "reset":
            puzzle.reset_to_solved()
            print("Puzzle reset.")
            continue
        if user_input.lower() == "list":
            list_algs()
            continue
        if user_input.lower() == "new":
            return "new_algs", saved_algs
        if user_input.lower()[:5] == "keep ":
            # save the specified algorithm
            keep_input_parts = user_input.split(" ")
            if len(keep_input_parts) > 3:
                print("invalid syntax for 'keep'. Expected 'keep <alg_nbr> <alg_name>'. `alg_name` cannot contain spaces.")
            try:
                alg_nbr = int(keep_input_parts[1])
            except ValueError:
                print(f"Invalid algorithm number: {user_input[5:]}. Expected integer 1 to {len(user_input_algorithms)}.")
                print("To save an alg, enter 'keep <alg_nbr> <alg_name>'.")
                continue
            if alg_nbr not in user_input_algorithms:
                print(f"Unknown algorithm number: {alg_nbr}. Expected integer 1 to {len(user_input_algorithms)}.")
                print("To save an alg, enter 'keep <alg_nbr> <alg_name>'.")
                continue
            try:
                saved_algs[keep_input_parts[2]] = user_input_algorithms[alg_nbr]
                print(f"Saved algorithm {alg_nbr} as '{keep_input_parts[2]}'.")
            except IndexError:
                print("Invalid syntax for 'keep'. Expected 'keep <alg_nbr> <alg_name>'.")

        else: # show algorithm
            try:
                if user_input[-1] == "'":
                    alg_nbr = int(user_input[:-1])
                    inverse = True
                else:
                    alg_nbr: int = int(user_input)
                    inverse = False
                show_algorithm(
                    puzzle,
                    sympy_moves,
                    user_input_algorithms[alg_nbr],
                    alg_nbr,
                    inverse=inverse,
                    move_text_color=move_text_color,
                )
            except ValueError as exception:
                print(f"Invalid input. Enter an\n" +
                        "  - algorithm number, to show it,\n" +
                        "  - 'list' to list available algorithms,\n" +
                        f"  - 'keep <{colored_text('alg_nbr', move_text_color)}> <{colored_text('alg_name', move_text_color)}>' to save an algorithm,\n" +
                        "  - 'new' to generate new algorithms, or\n"
                        "  - 'exit' to quit the program.\n")
            except KeyError as exception:
                print(f"Unknown algorithm. Expected integer 1 to {len(user_input_algorithms)}.")
    return "exit", saved_algs


def show_algorithm(
        puzzle: Twisty_Puzzle,
        sympy_moves: dict,
        alg: dict[str, str|str|int],
        alg_nbr: int,
        inverse: bool=False,
        move_text_color: str = "#5588ff"):
    # show basic algorithm info
    if inverse:
        inverse_base_sequence = " ".join([f"{move}'" for move in alg['base_sequence'].split(" ")][::-1])
        print(f"Algorithm {alg_nbr}': {alg['n_reps']}*({colored_text(inverse_base_sequence, move_text_color)})")
    else:
        print(f"Algorithm {alg_nbr}: {alg['n_reps']}*({colored_text(alg['base_sequence'], move_text_color)})")
    print(f"Algorithm length: {alg['n_reps'] * len(alg['base_sequence'].split(' '))} moves")
    alg_order, alg_permutation = get_alg_order(alg, sympy_moves)
    print(f"Alg. order: {alg_order}")
    affected_pieces = alg_ana.get_affected_pieces(alg_permutation, puzzle.pieces)
    print(f"Alg. affects {len(affected_pieces)} pieces:\n {affected_pieces}")
    # invert permutation
    if inverse:
        alg_permutation = ~alg_permutation # invert permutation
    # show algorithm on puzzle
    # puzzle.reset_to_solved()
    show_algorithm_on_puzzle(puzzle, alg_permutation, alg, alg_nbr)
    # puzzle.perform_move(alg["alg_moves"])
    print(f"Algorithm {alg_nbr} applied.")

def print_algorithm(
        puzzle: Twisty_Puzzle,
        sympy_moves: dict,
        alg: dict,
        alg_name: str,
        move_text_color: str = "#5588ff"):
    print(f"Algorithm {alg_name}: {alg['n_reps']}*({colored_text(alg['base_sequence'], move_text_color)})")
    print(f"Algorithm length: {alg['n_reps'] * len(alg['base_sequence'].split(' '))} moves")
    alg_order, alg_permutation = get_alg_order(alg, sympy_moves)
    print(f"Alg. order: {alg_order}")
    affected_pieces = alg_ana.get_affected_pieces(alg_permutation, puzzle.pieces)
    print(f"Alg. affects {len(affected_pieces)} pieces:\n {affected_pieces}")

def show_algorithm_on_puzzle(puzzle: Twisty_Puzzle, alg_permutation, alg: dict, alg_nbr: int):
    """
    Show a given algorithm on the puzzle.

    Args:
        puzzle (Twisty_Puzzle): puzzle to show the algorithm on
        alg (dict): algorithm to show
        alg_nbr (int): number of the algorithm
    """
    puzzle.animation_time = 1
    # define algorithm as new move in puzzle
    alg_name = f"alg{alg_nbr}"
    # calculate move cycles
    move_cycles: list[tuple[int]] = alg_permutation.cyclic_form
    puzzle._add_move_direct(alg_name, move_cycles)
    puzzle.perform_move(alg_name)
    puzzle.del_move(alg_name)
    

def get_alg_order(move_sequence, sympy_moves) -> tuple[int, Permutation]:
    """
    Get the order of a given move sequence.

    Args:
        move_sequence (str): move sequence
        sympy_moves (dict): dictionary of sympy moves

    Returns:
        int: order of the move sequence
        Permutation: permutation of the move sequence
    """
    move_list = move_sequence["alg_moves"].split(" ")
    alg_perm = sympy_moves[move_list[0]]
    for perm in move_list[1:]:
        alg_perm *= sympy_moves[perm]
    return alg_perm.order(), alg_perm

def main(move_text_color: str = "#5588ff"):
    import os, sys, inspect
    from src.puzzle_class import Twisty_Puzzle
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    sys.path.insert(0,parentdir) 

    print(f"Enter 'exit' to quit the program.")

    puzzle: Twisty_Puzzle = Twisty_Puzzle()
    puzzle_name = input("Enter a puzzle name: ")
    # puzzle_name = "rubiks_2x2"
    # puzzle_name = "geared_mixup"
    puzzle.load_puzzle(puzzle_name)
    n = puzzle.state_space_size
    sympy_moves = alg_ana.get_sympy_dict(puzzle)

    current_algorithms: dict[str, dict[str, str|str|int]] = dict()
        # key: algorithm name
        # value: dict with keys:
        #   - alg_moves: move sequence of the algorithm as str
        #   - base_sequence: base sequence of the algorithm as str
        #   - n_reps: number of repetitions of the base sequence
    puzzle.animation_time = 0.1

    state = "new_algs"
    while state == "new_algs":
        # generate algorithms
        puzzle_algorithms = generate_algorithms(
            puzzle,
            sympy_moves,
            max_base_sequence_length=16
            find_n_algorithms=9,
            max_pieces_affected=5,
            max_order=6,
            max_algorithm_length=60,
            )
        # puzzle_algorithms = generate_algorithms(
        #     puzzle,
        #     sympy_moves,
        #     find_n_algorithms=16,
        #     max_pieces_affected=16,
        #     max_order=6,
        #     max_algorithm_length=30,
        #     )
        state, saved_algs = user_test_algorithms(puzzle, sympy_moves, puzzle_algorithms, draw_pieces=False)
        current_algorithms = current_algorithms | saved_algs # merge dictionaries
    # print current algorithms
    print("="*30 + "\nCurrent algorithms:")
    for alg_name, alg in current_algorithms.items():
        print_algorithm(puzzle, sympy_moves, alg, alg_name, move_text_color)
    # close program
    os._exit(0)

if __name__ == "__main__":
    main()