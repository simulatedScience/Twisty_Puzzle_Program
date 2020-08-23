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
from .puzzle_class import Twisty_Puzzle


def main_interaction():
    """
    user interaction via the terminal
    allowing different commands and executing them accordingly

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
        - 'rename' [oldname] [newname] - rename a move
        - 'delmove' [movename]         - delete the given move
        - 'closepuzzle'                - close the current puzzle animation
        - 'sleeptime' [time]           - change the sleep time to change animation speed (default: 5e-3)
        - 'scramble' [max_moves]       - scramble the puzzle randomly
    """
    command_color = "#ff8800"
    argument_color = "#5588ff"
    user_input = ""

    puzzle = Twisty_Puzzle()
    n = 0

    while user_input.lower() != "exit":
        print()
        print(
            f"type in a command: ('{colored('help', command_color)}' to list all commands)")
        user_input = input(">>> ")
        if user_input.lower() == "exit":
            exit(0)
        command_dict = {"help": interface_help,
                        "import": interface_import,
                        "snap": interface_snap,
                        "newmove": interface_newmove,
                        "endmove": interface_endmove,
                        "move": interface_move,
                        "printmove": interface_printmove,
                        "listmoves": interface_listmoves,
                        "savepuzzle": interface_savepuzzle,
                        "loadpuzzle": interface_loadpuzzle,
                        "rename": interface_rename,
                        "delmove": interface_delmove,
                        "closepuzzle": interface_closepuzzle,
                        "sleeptime": interface_sleeptime,
                        "scramble": interface_scramble,
                        "reset": interface_reset,
                        "train_q": interface_train_Q,
                        "move_q": interface_move_Q,
                        "solve_q": interface_solve_Q,
                        "plot": interface_plot_success}

        if validate_command(command_dict, user_input):
            run_command(command_dict, user_input, puzzle,
                        command_color, argument_color)


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

    if not input_list[0].lower() in command_dict.keys():
        return False
    return True


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
    commands_with_args = ["import",
                          "snap",
                          "newmove",
                          "rename",
                          "move",
                          "delmove",
                          "printmove",
                          "savepuzzle",
                          "loadpuzzle",
                          "sleeptime",
                          "scramble",
                          "train_q",
                          "plot"]
    if command in commands_with_args:
        try:
            user_arguments = user_input[len(command)+1:]
            print(
                f"executing {colored(command, command_color)} {colored(user_arguments, arg_color)} ...")
            command_dict[command](user_arguments,
                                puzzle,
                                command_color=command_color,
                                arg_color=arg_color,
                                error_color=error_color)
        except IndexError:
            print(
                f"{colored('Error:', error_color)} {colored(command, command_color)} requires additional options.")
    else:
        command_dict[command](puzzle,
                              command_color=command_color,
                              arg_color=arg_color,
                              error_color=error_color)


def interface_closepuzzle(puzzle, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    close the current puzzle and reset history_dict
    """
    save_answer = ""
    while not save_answer in ["y", "n"]:
        save_answer = input("save current puzzle before closing? (y/n) ")
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
        main_interaction()


def interface_help(puzzle, command_color="#ff8800", arg_color="#0055cc", error_color="#ff0000"):
    print(f"- {colored('import', command_color)} [{colored('filepath', arg_color)}]          \
- load file from 'filepath' and show points in vpython")

    print(f"- {colored('snap', command_color)} [{colored('mode', arg_color)}]                \
- snap points to shape, {colored('mode', arg_color)} = '{colored('cube', arg_color)}'='{colored('c', arg_color)}' \
or '{colored('sphere', arg_color)}'='{colored('s', arg_color)}'\n{' '*31}\
run {colored('snap', command_color)} again to hide the snap shape\n{' '*31}\
'{colored('reset', arg_color)}'='{colored('r', arg_color)}' - resets points to inital positions")

    print(f"- {colored('newmove', command_color)} [{colored('movename', arg_color)}]         \
- create new move with name 'movename'")

    print(f"- {colored('endmove', command_color)}                    \
- exit move creator mode and save current move to some file")

    print(f"- {colored('move', command_color)} [{colored('movename', arg_color)}]            \
- perform the move with the given 'movename'")

    print(f"- {colored('listmoves', command_color)}                  \
- list all saved moves")

    print(f"- {colored('printmove', command_color)} [{colored('movename', arg_color)}]       \
- print all cycles of the given move")

    print(f"- {colored('help', command_color)}                       \
- print this overview")

    print(f"- {colored('exit', command_color)}                       \
- close program")

    print(f"- {colored('savepuzzle', command_color)} [{colored('puzzlename', arg_color)}]    \
- save the current puzzle into a file 'puzzledefinition.xml'")

    print(f"- {colored('loadpuzzle', command_color)} [{colored('puzzlename', arg_color)}]    \
- load puzzle from .xml file")

    print(f"- {colored('rename', command_color)} [{colored('oldname', arg_color)}] [{colored('newname', arg_color)}] \
- rename a move")

    print(f"- {colored('delmove', command_color)} [{colored('movename', arg_color)}]         \
- delete the given move")

    print(f"- {colored('closepuzzle', command_color)}                \
- close the current animation window")

    print(f"- {colored('sleeptime', command_color)} [{colored('time', arg_color)}]           \
- change the sleep time to change animation speed (default: 5e-3)")

    print(f"- {colored('reset', command_color)}                      \
- reset the puzzle to a solved state")

    print(f"- {colored('train_Q', command_color)} [{colored('num_episodes', arg_color)}] [{colored('max_moves', arg_color)}] [{colored('learning_rate', arg_color)}] [{colored('discount_factor', arg_color)}] [{colored('exploration_rate', arg_color)}] [{colored('reuse Q-table', arg_color)}]\n{' '*29}\
- train the Q-table for the puzzle with the given parameters\n{' '*31}\
use '{colored('train_Q', command_color)} {colored('0', arg_color)}' to load an existing q_table for the puzzle")

    print(f"- {colored('move_Q', command_color)}                     \
- make one move based on the current Q_table of the AI")

    print(f"- {colored('solve_Q', command_color)}                    \
- solve the puzzle using the current Q_table of the AI")

    print(f"- {colored('plot', command_color)} [{colored('batch_size', arg_color)}]          \
- plot the success of the last q-training")

if __name__ == "__main__":
    main_interaction()
