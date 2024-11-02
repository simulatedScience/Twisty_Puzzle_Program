"""
interface methods
"""
# import time
# import vpython as vpy
import os
from .interaction_modules.colored_text import colored_text as colored
# from interaction_modules.methods import *
from .puzzle_class import Twisty_Puzzle
from .ai_modules.nn_solver_interface import AI_FILES_FOLDER_NAME
from .ai_modules.test_from_file_CLI import pick_model

def interface_import(filepath, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
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


def interface_validate(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    check whether or not the puzzle is currently in a valid state.
    """
    validity = puzzle.validate_state()
    if validity == 0:
        print(f"The current state is invalid.")
    elif validity == 1:
        print(f"The current state is solveable.")
    else:
        print(f"There is a {100*validity:4.1}% probability that the current state is valid.")


def interface_snap(shape, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if not shape in ['r', 'c', 's', 'reset', 'cube', 'sphere']:
        print(f"{colored('Error:', error_color)} Invalid shape specified. Try {colored('cube', command_color)}, {colored('sphere', command_color)} or {colored('reset', command_color)}")
    if not puzzle.vpy_objects == []:
        puzzle.snap(shape)
    else:
        print(f"{colored('Error:', error_color)} use {colored('import', command_color)} before snapping")


def interface_clip_shape(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    user_args = user_args.split(' ')
    default_args = ["cuboid", None, True]
    data_types = [str, float, bool]
    n_args = 3
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    final_args = []
    for arg, default, dtype in zip(user_args, default_args, data_types):
        if isinstance(default, bool):
            if arg.lower == "false":
                final_args.append(False)
            else:
                final_args.append(default)
        else:
            try:
                final_args.append(dtype(arg))
            except ValueError:
                final_args.append(default)
    shape, size, show_edges = final_args

    if not puzzle.vpy_objects == []:
        try:
            puzzle.set_clip_poly(shape_str=shape, size=size, show_edges=show_edges)
        except ValueError:
            print(f"{colored('Error:', error_color)} Invalid shape specified. Try {colored('cube', command_color)} or {colored('octahedron', command_color)}")
    else:
        print(f"{colored('Error:', error_color)} use {colored('import', command_color)} before snapping")


def interface_draw_pieces(debug, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if debug.lower() in ["t", "true"]:
        puzzle.draw_3d_pieces(debug=True)
    else:
        puzzle.draw_3d_pieces(debug=False)


def interface_newmove(movename, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if len(movename) == 0 or ' ' in movename:
        print(
            f"{colored('Error:', error_color)} Movename cannot be empty or include a space.")
        return
    puzzle.newmove(movename, arg_color=arg_color)


def interface_endmove(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    puzzle.end_movecreation(arg_color=arg_color)


def interface_move(movename, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        puzzle.perform_move(movename)
    except KeyError as exception:
        print(f"{colored('Error:', error_color)} {exception}")
        print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet.\
 Create a move using {colored('newmove', command_color)}.")


def interface_printmove(movename, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        puzzle.print_move(movename, arg_color=arg_color)
    except KeyError:
        print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet. Create a move using {colored('newmove', command_color)}.")


def interface_savepuzzle(puzzlename, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        if puzzlename == '' and puzzle.PUZZLE_NAME != None:
            puzzle.save_puzzle(puzzle.PUZZLE_NAME)
            print(f"saved puzzle as {colored(puzzle.PUZZLE_NAME, arg_color)}")
        elif not ' ' in puzzlename:
            puzzle.save_puzzle(puzzlename)
            print(f"saved puzzle as {colored(puzzlename, arg_color)}")
        else:
            print(f"{colored('Error:', error_color)} invalid puzzle name. Name must not include spaces or other invalid characters for filenames.")
    except Exception as exception:
        print(f"{colored('Error:', error_color)} {exception}")
        print(f"{colored('Error:', error_color)} Saving failed due to the above exception. Please try again.")


def interface_listpuzzles(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    puzzle_folder_path = os.path.join(os.path.dirname(__file__), "puzzles")
    all_puzzles = os.listdir(puzzle_folder_path)
    print("loadable puzzles:")
    for puzzle_name in all_puzzles:
        print(f"\t{colored(puzzle_name, arg_color)}")


def interface_listmoves(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    list all moves saved for a puzzle
    """
    puzzle.listmoves(arg_color=arg_color)


def interface_rename(user_input, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    renames the move given in user_input

    inputs:
    -------
        user_input - (str) - two movenames, old and new seperated by a space
    """
    if not " " in user_input:
        print(f"{colored('Error:', error_color)} {colored('rename', command_color)} requires additional options.")
    old_name, new_name = user_input.split(" ")
    try:
        puzzle.rename_move(old_name, new_name)
    except KeyError:
        print(f"{colored('Error:', error_color)} Move {colored(old_name, arg_color)} does not exist.")


def interface_delmove(move_name, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    deletes the given move from the given puzzle object
    """
    if move_name == "":
        print(f"{colored('Error:', error_color)} {colored('delmove', command_color)} requires additional options.")
    try:
        puzzle.del_move(move_name)
        print(f"delted the move {colored(move_name, arg_color)}.")
    except KeyError:
        print(f"{colored('Error:', error_color)} Move {colored(move_name, arg_color)} does not exist.")



def interface_scramble(max_moves, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    scrambles the given puzzle
    """
    try:
        puzzle.scramble(max_moves=int(max_moves), arg_color=arg_color)
    except ValueError:
        puzzle.scramble(arg_color=arg_color)
    except IndexError: # random.choice raises an IndexError if it has to choose from an empty list
        print(f"{colored('Error:', error_color)} Load a puzzle or define moves scrambling.")


def interface_start_point_edit(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    starts point color editing mode
    """
    try:
        puzzle.edit_points()
    except AttributeError:
        print(f"{colored('Error:', error_color)} Load a puzzle before trying to edit one.")


def interface_end_point_edit(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    ends point color editing mode
    """
    try:
        puzzle.end_edit_points()
    except AttributeError:
        print(f"{colored('Error:', error_color)} Editing mode was not enabled.")


def interface_reset(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    reset puzzle to a solved state
    """
    puzzle.reset_to_solved()


def interface_animtime(animation_time, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    updates the animation time for each move in the active puzzle
    
    Abort if animation time is not between 0 and 60 seconds.
    """
    try:
        old_time: float = puzzle.animation_time
        new_time: float = float(animation_time.strip())
        if new_time > 60 or new_time < 0:
            print(f"{colored('Error:', error_color)} Invalid animation time. Must be between 0 and 60 seconds.")
            return
        puzzle.animation_time = new_time
        print(f"Animation time change from {old_time} to {new_time}")
    except ValueError:
        print(f"{colored('Error:', error_color)} Given time cannot be interpreted as a number.")

def interface_maxanimtime(max_anim_time, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    updates the max animation time per command. If the program expects to exceed that time, it will cut the animation short.
    """
    try:
        old_time: float = puzzle.max_animation_time
        new_time: float = float(max_anim_time.strip())
        if new_time < 0:
            print(f"Interpreted negative time as infinity (no limit).")
            new_time = float('inf')
        puzzle.max_animation_time = new_time
        print(f"Max animation time change from {old_time} to {new_time}")
    except ValueError:
        print(f"{colored('Error:', error_color)} Given time cannot be interpreted as a number.")

def interface_alganimstyle(alg_style, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    updates the algorithm style for the active puzzle.
    
    Args:
        alg_style (str): the new algorithm style for the puzzle bust be one of "m", "moves", "s", "shortened"
    """
    if alg_style.strip().lower() in ["m", "moves"]:
        puzzle.alg_anim_style = "moves"
    elif alg_style.strip().lower() in ["s", "shortened"]:
        puzzle.alg_anim_style = "shortened"
    else:
        print(f"{colored('Error:', error_color)} Invalid algorithm style. Must be one of {colored('m', arg_color)}, {colored('moves', arg_color)}, {colored('s', arg_color)}, {colored('shortened', arg_color)}")

##### AUTOMATIC SOLVERS #####

def interface_move_greedy(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    make a given number of moves based on the greedy algorithm (default: 1 move)
    """
    user_args = user_args.split(' ')
    n_args = 1
    default_args = [1]
    data_types = [int]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))
    final_args = [] # final arguments in correct datatype
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    num_moves = final_args[0]
    try:
        puzzle.move_greedy(num_moves=num_moves, arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Load a puzzle before trying to solve it.")

def interface_solve_greedy(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    solve the puzzle using a greedy algorithm
    """
    user_args = user_args.split(' ')
    n_args = 2
    default_args = [60, 0.1]
    data_types = [float, float]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    final_args = []
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    max_time, WEIGHT = final_args
    
    puzzle.solve_greedy(max_time=max_time, WEIGHT=WEIGHT, arg_color=arg_color)

#####     START Q-Learning     #####

def interface_train_Q(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    train the Q-table for the current puzzle
    """
    user_args = user_args.split(' ')
    defaults = [0, 200, 0.1, 0.99, 0.7]
    n_args = 6
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    try:
        int_args = [int(arg) if not arg=='' else default for arg,default in zip(user_args[:2], defaults[:2])]
        float_args = [float(arg) if not arg=='' else default for arg,default in zip(user_args[2:5], defaults[2:5])]
    except ValueError:
        print(f"{colored('Error:', error_color)} Invalid argument types.")
        return
    if user_args[5].lower() == "false":
        keep_Q = False
    else:
        keep_Q = True

    num_episodes, max_moves = int_args
    if num_episodes == None:
        num_episodes = 0
    learning_rate, discount_factor, exploration_rate = float_args

    puzzle.train_q_learning(num_episodes=num_episodes,
                            max_moves=max_moves,
                            learning_rate=learning_rate,
                            discount_factor=discount_factor,
                            base_exploration_rate=exploration_rate,
                            keep_q_table=keep_Q)

def interface_move_Q(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    make one move based on the current Q-table of the AI
    """
    try:
        puzzle.move_Q(arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the Q-table before requesting a move.")

def interface_solve_Q(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    solve the puzzle based on the current Q-table of the AI
    """
    user_args = user_args.split(' ')
    n_args = 2
    default_args = [60, 0.1]
    data_types = [float, float]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    final_args = []
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    max_time, WEIGHT = final_args
    try:
        puzzle.solve_Q(max_time=max_time, WEIGHT=WEIGHT, arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the Q-table before requesting a move.")

def interface_plot_success(batch_size, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
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

#####     END Q-Learning     #####
#####     START V-Learning     #####

def interface_train_v(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    train the V-table for the current puzzle
    """
    user_args = user_args.split(' ')
    defaults = [0, 50, 0.01, 0.99, 0.8, True]
    n_args = 6
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    try:
        int_args = [int(arg) if not arg=='' else default for arg,default in zip(user_args[:2], defaults[:2])]
        float_args = [float(arg) if not arg=='' else default for arg,default in zip(user_args[2:5], defaults[2:5])]
    except ValueError:
        print(f"{colored('Error:', error_color)} Invalid argument types.")
        return
    if user_args[5].lower() == "false":
        keep_v = False
    else:
        keep_v = True

    num_episodes, max_moves = int_args
    if num_episodes == None:
        num_episodes = 0
    learning_rate, discount_factor, exploration_rate = float_args

    puzzle.train_v_learning(num_episodes=num_episodes,
                            max_moves=max_moves,
                            learning_rate=learning_rate,
                            discount_factor=discount_factor,
                            base_exploration_rate=exploration_rate,
                            keep_v_table=keep_v)

def interface_move_v(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    make a given number of moves based on the current V-table of the AI (default: 1 move).
    """
    user_args = user_args.split(' ')
    n_args = 1
    default_args = [1]
    data_types = [int]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))
    final_args = [] # final arguments in correct datatype
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    num_moves = final_args[0]
    try:
        puzzle.move_v(num_moves=num_moves, arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the V-table before requesting a move.")

def interface_solve_v(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    solve the puzzle based on the current V-table of the AI
    """
    user_args = user_args.split(' ')
    n_args = 2
    default_args = [60, 0.1]
    data_types = [float, float]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    final_args = []
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    max_time, WEIGHT = final_args
    try:
        puzzle.solve_v(max_time=max_time, WEIGHT=WEIGHT, arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the V-table before requesting a move.")

#####     END V-Learning     #####
#####     START NN agent functions     #####

def interface_load_nn(puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    train neural network using HER
    """
    ai_files_folder_path: str = os.path.join("src", AI_FILES_FOLDER_NAME)
    model_path: str = pick_model(ai_files_folder_path)

    # try:
    puzzle.load_nn(
        model_path=model_path,
        arg_color=arg_color,
    )
    # except FileNotFoundError as exception:
    #     print(f"{colored(f'Error: {exception}', error_color)}\n Invalid model path. Try again.")

def interface_move_nn(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    make a given number of moves based on a loaded NN policy (default: 1 move)
    """
    user_args = user_args.split(' ')
    n_args = 1
    default_args = [1]
    data_types = [int]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))
    final_args = [] # final arguments in correct datatype
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    num_moves = final_args[0]
    try:
        puzzle.move_nn(num_moves=num_moves, arg_color=arg_color)
    except AttributeError as exception:
        print(f"{colored('Error: ', error_color)} {exception}")

def interface_solve_nn(user_args, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    solve the puzzle based on the current neural network trained for the puzzle
    """
    user_args = user_args.split(' ')
    n_args = 2
    default_args = [60, 0.1]
    data_types = [float, float]
    # make user_args the correct length (n_args)
    if len(user_args) > n_args:
        user_args = user_args[:n_args]
    elif len(user_args) < n_args:
        user_args += ['']*(n_args-len(user_args))

    final_args = []
    for arg, default, dtype in zip(user_args, default_args, data_types):
        try:
            final_args.append(dtype(arg))
        except ValueError:
            final_args.append(default)
    max_time, WEIGHT = final_args
    try:
        puzzle.solve_nn(max_time=max_time, WEIGHT=WEIGHT, arg_color=arg_color)
    except AttributeError:
        print(f"{colored('Error:', error_color)} Train the Neural Network before requesting a move.")

#####     END NN agent functions     #####
