from .interaction_modules.colored_text import colored_text as colored

def interface_help(user_arg, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    print help as requested.
    """
    help_dict = get_help_dict(command_color, arg_color, error_color)
    if user_arg in help_dict:
        print_help(user_arg, help_dict[user_arg])
    else:
        for command, help_pair in help_dict.items():
            print_help(command, help_pair)


def print_help(command, help_pair, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    print a single entry of the help dictionary (see `get_help_dict`) using the given colors.
    """
    print(f"- {colored(command, command_color)}", end="")
    for command_arg in help_pair[0]:
        print(f" [{colored(command_arg, arg_color)}]", end="")
    print() # new line
    print("   ", help_pair[1])


def get_help_dict(command_color="#ff8800", arg_color="#0055cc", error_color="#ff0000"):
    """
    help_dict is a dictionary with command names as keys that contains information about these commands.
    values are pairs:
        first value in the pair is a list of positional arguments for that command
        the second value is a string describing what the command does
    """
    help_dict = {
        "exit": ([], "close zhe program"),
        "help": (["command"], "Print all available commands with their arguments and descriptions. " +
                 f"If `{colored('command', arg_color)}` is given, only print help for that command."),
        "import": (["filepath"], "Import a new puzzle from a .ggb file. The ending .ggb can be ommited. " + 
                   "All visible points get imported with their color and size."),
        "snap": (["mode"], f"Snap points to shape, {colored('mode', arg_color)} can be:\n" +
                 f"    `{colored('cube', arg_color)}`=`{colored('c', arg_color)}`\n" +
                 f"    or `{colored('sphere', arg_color)}`=`{colored('s', arg_color)}`\n" +
                 f"    `{colored('reset', arg_color)}`=`{colored('r', arg_color)}` -> resets points to inital positions\n" +
                 f"    run {colored('snap', command_color)} again to hide the snap shape"),
        "newmove": (["movename"], "Start the move editor mode to create a new move with the given name. " +
                    "If move editor is already open, save the current move and start creating a new one. " +
                    "If name already exists, the old move gets overwritten without warning."), # TODO: add warning when overwriting a move
        "endmove": ([], "Exit the move editor mode and save the new move"),
        "move": (["movename"], f"Perform the move with the given `{colored('movename', arg_color)}`"),
        "listmoves": ([], "List all saved moves for the current puzzle"),
        "printmove": (["movename"], f"Print all cycles of the given move `{colored('movename', arg_color)}`"),
        "savepuzzle": (["puzzlename"], f"Save the current puzzle under the given name. " +
                       f"`{colored('puzzlename', arg_color)}` should not contain spaces or characters that are invalid in filenames. " +
                       f"`{colored('puzzlename', arg_color)}` can be ommited if the puzzle was loaded from a file or was saved before."), 
                       # TODO: automatically detect and convert spaces in name, print warning or error if saving fails
                       # NEVER CAUSE A CRASH HERE !
        "loadpuzzle": (["puzzlename"], "Load a saved puzzle with the given name."),
        "listpuzzles": ([], "List all puzzles, that can be loaded."),
        "rename": (["oldname", "newname"], "Rename an existing move"),
        "delmove": (["movename"], "Delete an existing move"),
        "closepuzzle": ([], "Close the currently loaded puzzle. Unsaved changes can get lost."),
        "animtime": (["time"], "Change the length each move animation takes. (default: 0.25s)"),
        "scramble": (["num_moves"], "Scramble the puzzle by the given number of semi-random moves. " +
                     "The scrambling algorithm tries to prevent redundant moves."),
        "reset": ([], "Reset the puzzle to a solved state. Only works properly in the point-view."), # TODO: fix resetting for 3D pieces mode
        "editpoints": ([], "Enter point color editing mode for inputting puzzle states. Only works properly in the point-view."), # TODO: fix color editing for 3D pieces mode
        "endeditpoints": ([], "Exit point color editing mode"),
        "train_q": (["num_episodes", "max_moves", "learning_rate", "discount_factor", "exploration_rate", "reuse_Q-table"],
                    "Train the Q-table for the puzzle with the given parameters"),
        "move_q": ([], "Make a single move based on current Q-table"),
        "solve_q": (["max_time"], "Solve the puzzle based on the current Q-table and an A* algorithm. " +
                    f"If no solution is found within `{colored('max_time', arg_color)}`sec, stop searching. (default: 60s"),
        "plot": (["batch_size"], f"Plot the success of the last Q-training by averaging over `{colored('batch_size', arg_color)}` episodes."),
        "train_v": (["num_episodes", "max_moves", "learning_rate", "discount_factor", "exploration_rate", "reuse_V-table"],
                    "Train the V-table for the puzzle with the given parameters"),
        "move_v": ([], "Make a single move based on current V-table"),
        "solve_v": (["max_time", "weight"], "Solve the puzzle based on the current V-table using weighted A* search. " +
                    f"If no solution is found within `{colored('max_time', arg_color)}`sec, stop searching. (default: 60s, weight=0.1)"),
        "train_nn": (["num_episodes", "max_moves", "learning_rate", "discount_factor", "exploration_rate", "k_for_HER", "keep_nn"],
                     "Train a neural network to solve the puzzle. Use HER to enhance training  " +
                     "(Hindsight Experience Replay) and use the given parameters."),
        "move_nn": ([], "Make a single move based on the current neural network of the AI"),
        "solve_nn": (["max_time"], "Solve the puzzle based on the current neural network and an A* algorithm. " +
                    f"If no solution is found within `{colored('max_time', arg_color)}`sec, stop searching. (default: 60s"),
        "clipshape": (["shape", "size", "show_edges"], "define a shape for the puzzle. Currently availiable shapes: \n" +
                      f"`{colored('cuboid', arg_color)}`=`{colored('c', arg_color)}` (default), " +
                      f"`{colored('tetrahedron', arg_color)}`=`{colored('tet', arg_color)}`, " +
                      f"`{colored('cube', arg_color)}`, " +
                      f"`{colored('octahedron', arg_color)}`=`{colored('oct', arg_color)}`"),
        "drawpieces": ([], "create 3D pieces within the clip shape"),
        "validate": ([], "check whether or not the puzzle is currently in a valid state (untested).") # TODO: test or remove-
        }
    return help_dict