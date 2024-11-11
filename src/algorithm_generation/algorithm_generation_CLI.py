

# add src to path
import cProfile
import json
import pstats
import os, sys, inspect
if __name__ == "__main__":
    currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
    parentdir = os.path.dirname(currentdir)
    parent2dir = os.path.dirname(parentdir)
    sys.path.insert(0,parent2dir)

from sympy.combinatorics import Permutation

from src.puzzle_class import Twisty_Puzzle
from src.interaction_modules.colored_text import colored_text
from src.algorithm_generation.algorithm_analysis import Twisty_Puzzle_Algorithm, get_sympy_moves
from src.algorithm_generation.algorithm_generation import generate_algorithms

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
        # print(colored_text(f"{alg_nbr+1:2}", COMMAND_COLORS['command']), end=": ")
        print(colored_text(f"{alg.name.split('_')[-1]:2}", COMMAND_COLORS['command']), end=": ")
        print(f"len={length:3}", end=", ")
        print(f"order={int(alg.order):3}", end=", ")
        print(f"pieces={alg.n_affected_pieces:3}", end=", ")
        print(colored_text(f'{alg.compact_moves():55}', COMMAND_COLORS['arguments']), end=" -> ")
        print(colored_text(alg.sympy_permutation.cyclic_form, COMMAND_COLORS['arguments']))
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
    puzzle._add_move_direct(alg_name, move_cycles, verbose=0)
    puzzle.perform_move(alg_name)
    puzzle.del_move(alg_name)

def print_command_help():
    """
    print all available commands:
    - help
    - list
    - show <number>
    - reset
    - exit
    """
    print("=" * 75)
    print(f"{colored_text('Commands:', COMMAND_COLORS['headline'])}")
    print(f"  {colored_text('help', COMMAND_COLORS['command'])}: show available commands.")
    print(f"  {colored_text('list', COMMAND_COLORS['command'])}: list available algorithms.")
    print(f"  {colored_text('show', COMMAND_COLORS['command'])} <{colored_text('number', COMMAND_COLORS['arguments'])}>: show algorithm with given number.")
    print(f"  <{colored_text('number', COMMAND_COLORS['arguments'])}>: show algorithm with given number. (shorthand for '{colored_text('show', COMMAND_COLORS['command'])} <{colored_text('number', COMMAND_COLORS['arguments'])}>')")
    # print(f"  {colored_text('save <number>', COMMAND_COLORS['command'])}: save algorithm with given number.")
    print(f"  {colored_text('reset', COMMAND_COLORS['command'])}: reset puzzle to solved state.")
    print(f"  {colored_text('exit', COMMAND_COLORS['command'])}: exit the program and save new puzzle version with the given algorithms.")
    print(f"  {colored_text('save', COMMAND_COLORS['command'])}: same as {colored_text('exit', COMMAND_COLORS['command'])}.")
    print("=" * 75)

def user_test_algorithms(
        puzzle: Twisty_Puzzle,
        algorithms: list[Twisty_Puzzle_Algorithm],
        saved_algs: dict[str, Twisty_Puzzle_Algorithm]
        ) -> tuple[str, dict[str, Twisty_Puzzle_Algorithm]]:
    """
    Allow user to visualize the given algorithms on the puzzle.
    """
    list_algorithms(algorithms)
    names_to_algorithms: dict[str, Twisty_Puzzle_Algorithm] = {alg.name: alg for alg in algorithms}
    print_command_help()
    while True:
        command = input(
            f"{colored_text('Enter a command:', COMMAND_COLORS['headline'])} "
        ).strip().lower()

        if command == "help":
            print_command_help()
            continue

        if command == "list":
            list_algorithms(algorithms)
            continue

        if command == "exit" or command == "save":
            return "exit", saved_algs

        if command == "reset":
            # reset puzzle
            puzzle.reset_to_solved()
            print(f"{colored_text('Algorithms reset.', COMMAND_COLORS['headline'])}")
            continue

        # show algorithm with given number
        if command.startswith("show"):
            try:
                alg_number = int(command.split()[1])
                alg = algorithms[alg_number-1]
                print_algorithm(alg, alg_number)
                show_algorithm_on_puzzle(puzzle, alg)
            except (IndexError, ValueError):
                print(f"{colored_text('Invalid algorithm number.', COMMAND_COLORS['headline'])}")
            continue
        # show algorithm by name or number
        try:
            alg_name = "alg_" + command
            # find algorithm by name
            alg: Twisty_Puzzle_Algorithm = names_to_algorithms[alg_name]
            print_algorithm(alg, alg_name)
            show_algorithm_on_puzzle(puzzle, alg)
            continue
        except ValueError:
            print(f"{colored_text('Invalid command.', COMMAND_COLORS['headline'])}")
            continue
        except KeyError:
            print(f"{colored_text('Algorithm not found.', COMMAND_COLORS['headline'])}")

def add_moves_to_puzzle(
        puzzle: Twisty_Puzzle,
        algorithms: dict[str, Twisty_Puzzle_Algorithm],
        new_moves: dict[str, list[int]],
        new_puzzle_name: str = "",
        suffix: str = "_algs"
        ) -> str:
    """
    Add moves to a puzzle and save it under a new name. If name already exists, a console interaction will ask if the existing puzzle should be overwritten and offer to enter a new name.

    Args:
        puzzle (Twisty_Puzzle): Puzzle to add moves to.
        algorithms (dict[str, Twisty_Puzzle_Algorithm]): Dictionary of current algorithms.
        new_moves (dict[str, Twisty_Puzzle_Algorithm]): Dictionary of moves to add to the puzzle.
        new_puzzle_name (str, optional): Name of the new puzzle. Defaults to "".
        suffix (str, optional): Suffix to add to the puzzle name if no name is given. Ignored if `new_puzzle_name` is given. Defaults to "_algs"

    Returns:
        str: Name of the new puzzle (may be different from the given name if the name already exists and the user chose a different name).
    """
    if not new_puzzle_name:
        new_puzzle_name: str = puzzle.PUZZLE_NAME + suffix
    # check if puzzle already exists
    while new_puzzle_name in ALL_PUZZLES:
        print(f"{colored_text(f'Puzzle {new_puzzle_name} already exists.', COMMAND_COLORS['headline'])}")
        overwrite_answer: str = input("Do you want to overwrite the existing puzzle? (y/N): ").strip().lower()
        if not overwrite_answer == "y":
            new_name_answer: str = " "
            while " " in new_name_answer:
                new_name_answer: str = input("If you want to save it under a different name, enter the new name. Press enter without a name to abort saving.").strip()
                if new_name_answer:
                    if " " in new_name_answer:
                        print(f"{colored_text('Name cannot contain spaces.', COMMAND_COLORS['headline'])}")
                        continue
                    new_puzzle_name = new_name_answer
                    break
                else:
                    return ""
        else:
            break
    # create new puzzle with 
    for move_name, move_perm in new_moves.items():
        puzzle.moves[move_name] = move_perm
    puzzle.save_puzzle(new_puzzle_name)
    print(f"{colored_text(f'Puzzle {new_puzzle_name} saved.', COMMAND_COLORS['headline'])}")
    
    # save algorithms' compact form to basic text file insie src/puzzles/new_puzzle_name/autogen_algorithms.txt
    if algorithms:
        filepath = os.path.join("src", "puzzles", new_puzzle_name, "algorithm_moves.json")
        algorithms_for_json: dict[str, str] = {name: alg.compact_moves() for name, alg in algorithms.items()}
        with open(filepath, "w") as file:
            json.dump(algorithms_for_json, file, indent=4)
        print(f"Algorithms saved to {colored_text(filepath, COMMAND_COLORS['arguments'])}")
    return new_puzzle_name

def generate_save_algorithms(
        puzzle: Twisty_Puzzle,
        anim_time: float = 0.1,
        rotations_prefix: str = "rot_",
        max_time: int = 300,
        max_base_sequence_length: int = 16,
        max_move_sequence_order: int = 200,
        max_algorithm_moves: int = 100,
        max_algorithm_order: int = 4,
        max_pieces_affected: int = 4,
        max_number_of_algorithms: int = 48,
        max_iterations_without_new_algorithm: int = 5000,
        verbosity: int = 2
    ):
    """
    Automatically find algorithms (move sequences with low order, affecting few pieces) for the given puzzle and save them to the puzzle.
    
    Args:
        puzzle (Twisty_Puzzle): Puzzle to find algorithms for.
        anim_time (float, optional): Animation time for the puzzle. Defaults to 0.1.
        rotations_prefix (str, optional): Prefix for rotation moves. Defaults to "rot_".
    """
    alg_generation_params: dict[str, int] = {
        "max_time": max_time,
        "max_base_sequence_length": max_base_sequence_length,
        "max_move_sequence_order": max_move_sequence_order,
        "max_algorithm_moves": max_algorithm_moves,
        "max_algorithm_order": max_algorithm_order,
        "max_pieces_affected": max_pieces_affected,
        "max_number_of_algorithms": max_number_of_algorithms,
        "max_iterations_without_new_algorithm": max_iterations_without_new_algorithm,
        # "verbosity": verbosity,
    }
    if verbosity > 1:
        print(f"Algorithm generation parameters:")
        for key, value in alg_generation_params.items():
            print(f"  {colored_text(key, COMMAND_COLORS['command'])}: {colored_text(value, COMMAND_COLORS['arguments'])}")

    sympy_moves: dict[str, Permutation] = get_sympy_moves(puzzle)
    sympy_rotations: dict[str, Permutation] = {name: perm for name, perm in sympy_moves.items() if name.startswith(rotations_prefix)}
    # remove permutations that are rotations
    sympy_base_moves = {name: perm for name, perm in sympy_moves.items() if not name in sympy_rotations}

    current_algorithms: dict[str, Twisty_Puzzle_Algorithm] = {}
    old_anim_time = puzzle.animation_time
    puzzle.animation_time = anim_time

    while True:
        profile = cProfile.Profile()
        new_algorithms = profile.runcall(
            generate_algorithms,
            puzzle=puzzle,
            sympy_base_moves=sympy_base_moves,
            sympy_rotations=sympy_rotations,
            max_time=max_time,
            max_base_sequence_length=max_base_sequence_length,
            max_move_sequence_order=max_move_sequence_order,
            max_algorithm_moves=max_algorithm_moves,
            max_algorithm_order=max_algorithm_order,
            max_pieces_affected=max_pieces_affected,
            max_number_of_algorithms=max_number_of_algorithms,
            max_iterations_without_new_algorithm=max_iterations_without_new_algorithm,
            verbosity=verbosity,
        )
        if verbosity > 2:
            ps = pstats.Stats(profile)
            ps.sort_stats(("tottime"))
            ps.print_stats(20)

        state, saved_algs = user_test_algorithms(puzzle, new_algorithms, current_algorithms)
        current_algorithms = {alg.name: alg for alg in new_algorithms}
        if state == "exit":
            break

    # save puzzle with new algorithms
    new_puzzle_name = puzzle.PUZZLE_NAME
    if input("Do you want to save the puzzle with the new algorithms? (y/N): ").strip().lower() == "y":
        # TODO: save algorithm generation parameters.
        algorithm_moves: dict[str, list[int]] = {name: alg.sympy_permutation.cyclic_form for name, alg in current_algorithms.items()}
        new_puzzle_name = add_moves_to_puzzle(
            puzzle=puzzle,
            algorithms=current_algorithms,
            new_moves=algorithm_moves,
            suffix="_algs",
        )
        alg_generation_params_file: str = os.path.join("src", "puzzles", new_puzzle_name, "algorithm_generation_parameters.json")
        with open(alg_generation_params_file, "w") as file:
            json.dump(alg_generation_params, file, indent=4)
        print(f"Saved algorithm generation parameters to {colored_text(alg_generation_params_file, COMMAND_COLORS['arguments'])}")
    # reset animation time
    puzzle.animation_time = old_anim_time
    return new_puzzle_name

def main(move_text_color="#5588ff", rotations_prefix="rot_"):
    puzzle, puzzle_name = load_twisty_puzzle()
    new_puzzle_name = generate_save_algorithms(
        puzzle,
        verbosity=3,
    )
    os._exit(0)

def load_twisty_puzzle(puzzle_name: str = None):
    print(f"Available puzzles: {colored_text(', '.join(ALL_PUZZLES), COMMAND_COLORS['arguments'])}")
    print(f"Enter {colored_text('exit', COMMAND_COLORS['command'])} to exit the program.")

    puzzle = Twisty_Puzzle()
    if not puzzle_name:
        puzzle_name = input("Enter a puzzle name: ").strip()
    try:
        puzzle.load_puzzle(puzzle_name)
    except FileNotFoundError:
        print(f"{colored_text('Puzzle not found.', COMMAND_COLORS['headline'])}")
        os._exit(0)
    return puzzle, puzzle_name

if __name__ == "__main__":
    main()
