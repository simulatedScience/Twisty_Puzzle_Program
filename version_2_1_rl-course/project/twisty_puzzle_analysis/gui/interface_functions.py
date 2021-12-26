"""
interface methods
"""
import time
import vpython as vpy
from .interaction_modules.colored_text import colored_text as colored
# from interaction_modules.methods import *


def interface_import(filepath, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    import puzzle from geogebra file and save information in 'history_dict'
    """
    try:
        puzzle.import_puzzle(filepath)
        print(f"successfully imported {colored(filepath, arg_color)}")
    except ValueError:
        print(f"{colored('Error:', error_color)} The path must lead to a .ggb file including the file ending.")
    except FileNotFoundError:
        print(f"{colored('Error:', error_color)} Invalid file path, try again.")


def interface_snap(shape, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if not shape in ['r', 'c', 's', 'reset', 'cube', 'sphere']:
        print(f"{colored('Error:', error_color)} Invalid shape specified. Try {colored('cube', command_color)}, {colored('sphere', command_color)} or {colored('reset', command_color)}")
    if not puzzle.vpy_objects == []:
        puzzle.snap(shape)
    else:
        print(f"{colored('Error:', error_color)} use {colored('import', command_color)} before snapping")


def interface_newmove(movename, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if len(movename) == 0 or ' ' in movename:
        print(
            f"{colored('Error:', error_color)} Movename cannot be empty or include a space.")
        return
    puzzle.newmove(movename, arg_color=arg_color)


def interface_endmove(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    puzzle.end_movecreation(arg_color=arg_color)


def interface_move(movename, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        puzzle.perform_move(movename)
    except KeyError:
        print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet.\
 Create a move using {colored('newmove', command_color)}.")


def interface_printmove(movename, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        puzzle.print_move(movename, arg_color=arg_color)
    except KeyError:
        print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet. Create a move using {colored('newmove', command_color)}.")


def interface_savepuzzle(puzzlename, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    # try:
        if not ' ' in puzzlename:
            puzzle.save_puzzle(puzzlename)
            print(f"saved puzzle as {colored(puzzlename, arg_color)}")
        else:
            raise ValueError("invalid puzzle name")
    # except:
        # print(f"{colored('Error:', error_color)} invalid puzzle name. Name must not include spaces or other invalid characters for filenames.")


def interface_loadpuzzle(puzzlename, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    load a puzzle 'puzzlename' from 'puzzles/[puzzlename]/puzzle_definition.xml' and
        save information in history_dict
    """
    try:
        puzzle.load_puzzle(puzzlename)
    except FileNotFoundError:
        print(f"{colored('Errod:', error_color)} Puzzle file does not exist yet. Create necessary files with {colored('savepuzzle', command_color)}.")


def interface_listmoves(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    puzzle.listmoves(arg_color=arg_color)


def interface_rename(user_input, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    renames the move given in user_input

    inputs:
    -------
        user_input - (str) - two movenames, old and new seperated by a space
    """
    old_name, new_name = user_input.split(" ")
    try:
        puzzle.rename_move(old_name, new_name)
    except KeyError:
        print(f"{colored('Error:', error_color)} Move {colored(old_name, arg_color)} does not exist.")


def interface_delmove(move_name, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    deletes the given move from the given puzzle object
    """
    try:
        puzzle.del_move(move_name)
        print(f"delted the move {colored(move_name, arg_color)}.")
    except KeyError:
        print(f"{colored('Error:', error_color)} Move {colored(move_name, arg_color)} does not exist.")


def interface_sleeptime(sleep_time, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    updates the sleep time in the active puzzle
    """
    try:
        print(puzzle.sleep_time)
        puzzle.sleep_time = float(sleep_time)
        print(puzzle.sleep_time)
    except:
        print(f"{colored('Error:', error_color)} Given time is not a float.")


def interface_scramble(max_moves, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    scrambles the given puzzle
    """
    try:
        puzzle.scramble(max_moves=int(max_moves), arg_color=arg_color)
    except:
        puzzle.scramble(arg_color=arg_color)


def interface_reset(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    reset puzzle to a solved state
    """
    puzzle.reset_to_solved()


def interface_train_Q(user_args, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    train the Q-table for the current puzzle
    """
    user_args = user_args.split(' ')
    n_args = 6
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    try:
        int_args = [int(arg) if not arg=='' else None for arg in user_args[:2]]
        float_args = [float(arg) if not arg=='' else None for arg in user_args[2:5]]
    except ValueError:
        print(f"{colored('Error:', error_color)} Invalid argument types.")
        return
    if user_args[5].lower() == "false":
        keep_Q = False
    else:
        keep_Q = True

    num_episodes, max_moves = int_args
    learning_rate, discount_factor, exploration_rate = float_args

    puzzle.train_q_learning(num_episodes=num_episodes,
                            max_moves=max_moves,
                            learning_rate=learning_rate,
                            discount_factor=discount_factor,
                            base_exploration_rate=exploration_rate,
                            keep_Q_table=keep_Q)


def interface_move_Q(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    make one move based on the current Q-table of the AI
    """
    try:
        puzzle.move_Q()
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the Q-table before requesting a move.")


def interface_solve_Q(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    solve the puzzle based on the current Q-table of the AI
    """
    try:
        puzzle.solve_Q(arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the Q-table before requesting a move.")


def interface_plot_success(batch_size, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    plot evalutation of the Q-training
    """
    try:
        batch_size = int(batch_size)
    except:
        batch_size = 30
    try:
        puzzle.plot_q_success(batch_size=batch_size)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the Q-table before evalutation.")
