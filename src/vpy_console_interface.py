"""
This module provides an interface to control the vpython animation via the terminal

it should be able to...
    - import a .ggb file                # done (running import twice is still broken)
    - show the points defined there     # done (except cone option)
    - allow visual input of cycles      # done
    - allow visual input of moves       # done
    - provide output option for moves   # done
    - perform animated moves            # done
"""
from os import _exit as exit
from .interaction_modules.colored_text import colored_text as colored
from .interface_functions import *
from .console_help import interface_help
from .puzzle_class import Twisty_Puzzle


def main_interaction(load_puzzle: str = None):
    """
    user interaction via the terminal
    allowing different commands and executing them accordingly

    Args:
        load_puzzle (str): name of the puzzle to load at the start

    inputs: (via terminal)
    -------
        - 'import' [filepath]          - load file from 'filepath' and show points in vpython
        - 'snap' [mode]                - snap points to shape, 'mode' = 'cube'='c' or 'sphere'='s'
        - 'newmove' [movename]         - create new move with name 'movename'
        - 'endmove'                    - exit move creator mode and save current move to some file
        - 'move' [movename]            - perform the mive with the given 'movename'
        - 'listmoves'                  - list all saved moves
        - 'printmove' [movename]       - print all cycles of the given move
        - 'help'                       - print this overview
        - 'exit'                       - close program
        - 'savepuzzle' [puzzlename]    - save the current puzzle into a file 'puzzledefinition.xml'
        - 'loadpuzzle' [puzzlename]    - load puzzle from a given file
        - 'listpuzzles'                - list all available puzzles
        - 'rename' [oldname] [newname] - rename a move
        - 'delmove' [movename]         - delete the given move
        - 'closepuzzle'                - close the current puzzle animation
        - 'animtime' [time]           - change the sleep time to change animation speed (default: 5e-3)
        - 'scramble' [max_moves]       - scramble the puzzle randomly
        - 'editpoints'                 - enter point color editing mode
        - 'endeditpoints'              - exit point color editing mode
        - 'solve_greedy' [max_time]    - solve the puzzle using a greedy algorithm
        - 'train_q'                    - train Q-table for current puzzle
        - 'plot' [average length]      - plot the success of the Q-table over time
        - 'move_q'                     - make a move based on current Q-table
        - 'solve_q' [max_time]         - solve puzzle based on current Q-table
        - 'load_nn'                    - load a trained neural network (RL-agent) from file
        - 'move_nn'                    - make a move based on current Neural Network
        - 'solve_nn'                   - solve puzzle based on current Neural Network
        - 'clipshape'                  - define a shape for the puzzle
        - 'drawpieces'                 - draw 3D pieces within the clip shape
    """
    command_color = "#ff8800"
    argument_color = "#5588ff"
    error_color: str = "#ff2222"
    user_input = ""

    puzzle = Twisty_Puzzle()
    if load_puzzle:
        interface_loadpuzzle(load_puzzle, puzzle)
        load_puzzle = None
    n = 0

    while user_input.lower() != "exit":
        print()
        print(
            f"Waiting for command: ('{colored('help', command_color)}' to list valid commands)")
        user_input = input(">>> ")
        if user_input.lower() == "exit":
            exit(0)
        command_dict = {"help": interface_help,
                        "import": interface_import,
                        "snap": interface_snap,
                        "animtime": interface_animtime,
                        "maxanimtime": interface_maxanimtime,
                        "alganimstyle": interface_alganimstyle,
                        "newmove": interface_newmove,
                        "endmove": interface_endmove,
                        "move": interface_move,
                        "printmove": interface_printmove,
                        "listmoves": interface_listmoves,
                        "savepuzzle": interface_savepuzzle,
                        "loadpuzzle": interface_loadpuzzle,
                        "listpuzzles": interface_listpuzzles,
                        "rename": interface_rename,
                        "delmove": interface_delmove,
                        "closepuzzle": interface_closepuzzle,
                        "scramble": interface_scramble,
                        "reset": interface_reset,
                        "editpoints": interface_start_point_edit,
                        "endeditpoints": interface_end_point_edit,
                        "move_greedy": interface_move_greedy,
                        "solve_greedy": interface_solve_greedy,
                        "train_q": interface_train_Q,
                        "move_q": interface_move_Q,
                        "solve_q": interface_solve_Q,
                        "plot": interface_plot_success,
                        "train_v": interface_train_v,
                        "move_v": interface_move_v,
                        "solve_v": interface_solve_v,
                        "load_nn": interface_load_nn,
                        "move_nn": interface_move_nn,
                        "solve_nn": interface_solve_nn,
                        "clipshape": interface_clip_shape,
                        "drawpieces": interface_draw_pieces,
                        "validate": interface_validate}
        
        # try:
        if validate_command(command_dict, user_input):
            run_command(
                command_dict=command_dict,
                user_input=user_input,
                puzzle=puzzle,
                command_color=command_color,
                arg_color=argument_color,
                error_color=error_color,
            )
        # except Exception as e:
        #     print(colored(f"Error: {e}", error_color))
        #     print(colored("please try again", error_color))


def validate_command(command_dict, user_input):
    """
    check whether the given input is a valid command

    inputs:
    -------
        user_input - (str) - any string, only valid commands cause action

    returns:
    --------
        (bool) - whether or not the input is a valid command
    """
    input_list = user_input.split(" ")

    if input_list[0].lower() in command_dict.keys():
        return True
    return False


def run_command(command_dict, user_input, puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    execute a given command

    inputs:
    -------
        user_input - (str) - string representing a valid command

    returns:
    --------
        None
    """
    command = user_input.split(" ")[0].lower()
    commands_with_args = ["help",
                          "import",
                          "snap",
                          "animtime",
                          "maxanimtime",
                          "alganimstyle",
                          "newmove",
                          "rename",
                          "move",
                          "delmove",
                          "printmove",
                          "savepuzzle",
                          "loadpuzzle",
                          "scramble",
                          "move_greedy",
                          "solve_greedy",
                          "train_q",
                          "solve_q",
                          "plot",
                          "train_v",
                          "move_v",
                          "solve_v",
                          "move_nn",
                          "solve_nn",
                          "clipshape",
                          "drawpieces"]
    if command in commands_with_args:
        user_arguments = user_input[len(command)+1:].strip()
        print(
            f"executing {colored(command, command_color)} {colored(user_arguments, arg_color)} ...")
        try:
            command_dict[command](
                user_arguments,
                puzzle,
                command_color=command_color,
                arg_color=arg_color,
                error_color=error_color)
        except Exception as exception:
            print(exception.with_traceback())
            print(colored(f"Error: {exception}", error_color))
            print(colored("please try again", error_color))
    elif command in command_dict:
        print(f"executing {colored(command, command_color)} ...")
        command_dict[command](puzzle,
                              command_color=command_color,
                              arg_color=arg_color,
                              error_color=error_color)
    else:
        print(colored("Error: Unknown command:", error_color) +
              colored(f" {command}", command_color) +
              f"\nType {colored('help', command_color)} for a list of valid commands.")

def interface_loadpuzzle(puzzlename, puzzle: Twisty_Puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    load a puzzle 'puzzlename' from 'puzzles/[puzzlename]/puzzle_definition.xml' and
        save information in history_dict
    """
    if hasattr(puzzle, "PUZZLE_NAME") and puzzle.PUZZLE_NAME is not None:
        # close current puzzle before loading a new one
        interface_closepuzzle(puzzle, load_puzzle=puzzlename)
    try:
        puzzle.load_puzzle(puzzlename)
    except FileNotFoundError:
        print(f"{colored('Errod:', error_color)} Puzzle file does not exist yet. Create necessary files with {colored('savepuzzle', command_color)}.")


def interface_closepuzzle(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000", load_puzzle: str = None):
    """
    close the current puzzle and reset history_dict
    """
    save_answer = ""
    while not save_answer in ["y", "n"]:
        save_answer = input("save current puzzle before closing? (y/N) ")
        if save_answer.lower() == "y":
            if puzzle.PUZZLE_NAME == None:
                puzzlename = ' '
                while ' ' in puzzlename:
                    puzzlename = input("Enter a name without spaces to save the puzzle: ")
            else:
                puzzlename = puzzle.PUZZLE_NAME
            puzzle.save_puzzle(puzzlename)
            print(f"saved puzzle as {colored(puzzlename, arg_color)}")
        try:
            puzzle.canvas.delete()
        except:
            pass
        main_interaction(load_puzzle=load_puzzle)

if __name__ == "__main__":
    main_interaction()
