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
from interface_functions import *
from interaction_modules.colored_text import colored_text
import vpython as vpy
from os import _exit as exit


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
        - 'savepuzzle' [puzzlename]    - save the current puzzle into a file 'puzzledefinition.xml' or for now .txt
        - 'loadmoves' [filepath]       - load moves from a given file
        - 'rename' [oldname] [newname] - rename a move
        - 'delmove' [movename]         - delete the given move
        - 'closepuzzle'                - close the current puzzle animation
    """
    command_color = "#ff8800"
    argument_color = "#5588ff"
    user_input = ""

    history_dict = {"movecreator": False}
    n = 0

    while user_input.lower() != "exit":
        print()
        print(
            f"type in a command: ('{colored_text('help', command_color)}' to list all commands)")
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
                        "closepuzzle": interface_closepuzzle}

        if validate_command(command_dict, user_input):
            run_command(command_dict, user_input, history_dict,
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


if __name__ == "__main__":
    main_interaction()
