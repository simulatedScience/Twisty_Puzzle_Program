

# add src to path
import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
parent2dir = os.path.dirname(parentdir)
sys.path.insert(0,parent2dir)

from sympy.combinatorics import Permutation

from src.puzzle_class import Twisty_Puzzle
from src.interaction_modules.colored_text import colored_text
from algorithm_analysis import Twisty_Puzzle_Algorithm, get_sympy_moves
from algorithm_generation import generate_algorithms

COMMAND_COLORS = {
    "command": "#ff8800",  # orange
    "arguments": "#5588ff",  # blue
    "headline": "#22dd22",  # green
}
ALL_PUZZLES = [f for f in os.listdir(os.path.join("src", "puzzles")) if os.path.isdir(os.path.join("src", "puzzles", f))]

def list_algorithms(user_input_algorithms: list[Twisty_Puzzle_Algorithm], alg_prefix="alg_"):
    print("=" * 75)
    print(f"{colored_text('Available algorithms:', COMMAND_COLORS['headline'])} (sorted by length)")
    for alg_nbr, alg in enumerate(user_input_algorithms):
        length = len(alg.full_action_sequence)
        print(colored_text(f"{alg_nbr+1:2}", COMMAND_COLORS['command']), end=": ")
        print(f"len={length:3}", end=", ")
        print(f"order={int(alg.order):3}", end=", ")
        print(f"pieces={alg.n_affected_pieces:3}", end=", ")
        print(colored_text(alg.compact_moves(), COMMAND_COLORS['arguments']))
    print("=" * 75)

def print_algorithm(alg: Twisty_Puzzle_Algorithm, alg_number: int):
    # print(f"Algorithm {alg_number}: {alg.compact_moves()}")
    # print(f"Algorithm length: {len(alg.full_action_sequence)} moves")
    # print(f"Alg. order: {alg.order}")
    # print(f"Alg. affects {alg.n_affected_pieces} pieces:\n {alg.affected_pieces}")
    print(alg)
    alg.print_signature()

def show_algorithm_on_puzzle(puzzle: Twisty_Puzzle, alg: Twisty_Puzzle_Algorithm):
    puzzle.animation_time = 1
    alg_name = alg.name
    move_cycles = alg.sympy_permutation.cyclic_form
    puzzle._add_move_direct(alg_name, move_cycles)
    puzzle.perform_move(alg_name)
    puzzle.del_move(alg_name)

def user_test_algorithms(puzzle, algorithms, saved_algs):
    while True:
        list_algorithms(algorithms)
        print(f"\n{colored_text('Commands:', COMMAND_COLORS['headline'])} show <alg_number>, save <alg_number>, reset, quit")
        command = input("Enter a command: ").strip().lower()

        if command == "quit":
            return "quit", saved_algs

        if command == "reset":
            # reset puzzle
            puzzle.reset_to_solved()
            print(f"{colored_text('Algorithms reset.', COMMAND_COLORS['headline'])}")
            continue

        if command.startswith("show"):
            try:
                alg_number = int(command.split()[1])
                alg = algorithms[alg_number-1]
                print_algorithm(alg, alg_number)
                show_algorithm_on_puzzle(puzzle, alg)
            except (IndexError, ValueError):
                print(f"{colored_text('Invalid algorithm number.', COMMAND_COLORS['headline'])}")
            continue

        if command.startswith("save"):
            try:
                alg_number = int(command.split()[1])
                alg = algorithms[alg_number]
                saved_algs[alg_number] = alg
                print(f"{colored_text('Algorithm saved.', COMMAND_COLORS['headline'])}")
            except (IndexError, ValueError):
                print(f"{colored_text('Invalid algorithm number.', COMMAND_COLORS['headline'])}")
            continue

        print(f"{colored_text('Invalid command.', COMMAND_COLORS['headline'])}")

def main(move_text_color="#5588ff", rotations_prefix="rot_"):
    print(f"Available puzzles: {colored_text(', '.join(ALL_PUZZLES), COMMAND_COLORS['arguments'])}")
    print(f"Enter {colored_text('exit', COMMAND_COLORS['command'])} to quit the program.")

    puzzle = Twisty_Puzzle()
    puzzle_name = input("Enter a puzzle name: ")
    # puzzle_name = "rubiks_3x3"
    try:
        puzzle.load_puzzle(puzzle_name)
    except FileNotFoundError:
        print(f"{colored_text('Puzzle not found.', COMMAND_COLORS['headline'])}")
        os._exit(0)
    
    sympy_moves: dict[str, Permutation] = get_sympy_moves(puzzle)
    sympy_rotations: dict[str, Permutation] = {name: perm for name, perm in sympy_moves.items() if name.startswith(rotations_prefix)}
    # remove permutations that are rotations
    sympy_base_moves = {name: perm for name, perm in sympy_moves.items() if not name in sympy_rotations}

    current_algorithms = {}
    puzzle.animation_time = 0.1

    while True:
        new_algorithms = generate_algorithms(
            puzzle=puzzle,
            sympy_base_moves=sympy_base_moves,
            sympy_rotations=sympy_rotations,
            max_time=120,
            max_base_sequence_length=16,
            max_move_sequence_order=200,
            max_algorithm_moves=150,
            max_algorithm_order=4,
            max_pieces_affected=4,
            max_number_of_algorithms=30,
            max_iterations_without_new_algorithm=1000,
        )

        state, saved_algs = user_test_algorithms(puzzle, new_algorithms, current_algorithms)
        if state == "quit":
            break
        current_algorithms.update(saved_algs)

    print("=" * 75 + "\nCurrent algorithms:")
    for alg_name, alg in current_algorithms.items():
        print_algorithm(alg, alg_name)

    os._exit(0)

if __name__ == "__main__":
    main()
