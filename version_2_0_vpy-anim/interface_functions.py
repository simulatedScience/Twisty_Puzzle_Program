"""
interface methods
"""
import time
import vpython as vpy
from interaction_modules.colored_text import colored_text
from interaction_modules.methods import *


def run_command(command_dict, user_input, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    execute a given command

    inputs:
    -------
        user_input - (str) - string representing a valid command

    returns:
    --------
        None
    """
    command = user_input.split(" ")[0]

    if command in ["import", "snap", "newmove", "move", "printmove", "savepuzzle", "loadpuzzle", "rename", "delmove"]:
        try:
            user_arguments = user_input[len(command)+1:]
            print(
                f"executing {colored(command, command_color)} {colored(user_arguments, arg_color)} ...")
        except IndexError:
            print(
                f"{colored('Error:', error_color)} {colored(command, command_color)} requires additional options.")
        command_dict[command](user_arguments,
                              history_dict,
                              command_color=command_color,
                              arg_color=arg_color,
                              error_color=error_color)
    else:
        command_dict[command](history_dict,
                              command_color=command_color,
                              arg_color=arg_color,
                              error_color=error_color)


def interface_help(history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    run_help(command_color, arg_color)


def interface_import(filepath, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    import puzzle from geogebra file and save information in 'history_dict'
    """
    try:
        point_dicts, vpy_objects, canvas = run_import(filepath)
        history_dict["point_dicts"] = point_dicts
        # list of vpython objects essential to the puzzle
        history_dict["vpy_objects"] = vpy_objects
        history_dict["canvas"] = canvas
        # deepcopy of correct point positions for snapping
        history_dict["POINT_POS"] = [vpy.vec(obj.pos) for obj in vpy_objects]
        history_dict["puzzle_com"] = vpy.vec(0, 0, 0)
        print(f"successfully imported {colored(filepath, arg_color)}")
    except ValueError:
        print(f"{colored('Error:', error_color)} The path must lead to a .ggb file including the file ending.")
    except FileNotFoundError:
        print(f"{colored('Error:', error_color)} Invalid file path, try again.")


def interface_snap(user_arguments, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        history_dict["snap_obj"].visible = False
    except KeyError:
        history_dict["snap_obj"] = None
    except AttributeError:
        pass
    try:
        snap_obj, puzzle_com = run_snap(
            user_arguments, history_dict["vpy_objects"], prev_shape=history_dict["snap_obj"])
        history_dict["snap_obj"] = snap_obj
        history_dict["puzzle_com"] = puzzle_com
        # deepcopy of correct point positions for snapping
        history_dict["POINT_POS"] = [
            vpy.vec(obj.pos) for obj in history_dict["vpy_objects"]]
    except KeyError:
        print(
            f"{colored('Error:', error_color)} use {colored('import', command_color)} before snapping")


def interface_newmove(movename, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if movename == "" or movename[0] == " ":
        print(
            f"{colored('Error:', error_color)} Movename cannot be empty or start with a space.")
        return
    # cleanup if previous move has not been ended properly
    if history_dict["movecreator"] == True:
        interface_endmove(history_dict, command_color=command_color,
                    arg_color=arg_color, error_color=error_color)

    history_dict["movecreator"] = True
    history_dict["active_move_name"] = movename  # saving the current movename
    history_dict["active_move_cycles"] = []
    history_dict["active_arrows"] = []
    history_dict["bound_method"] = run_newmove(history_dict["canvas"],
                                               history_dict["active_move_cycles"],
                                               history_dict["vpy_objects"],
                                               history_dict["active_arrows"])


def interface_endmove(history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if history_dict["movecreator"] == True:
        if not "moves" in history_dict.keys():
            history_dict["moves"] = dict()

        history_dict["movecreator"] = False
        movename = history_dict["active_move_name"]
        history_dict["moves"][movename] = run_endmove(history_dict["active_move_cycles"],
                                                      history_dict["active_arrows"],
                                                      history_dict["canvas"],
                                                      history_dict["bound_method"])
        # define inverse move name
        if "'" == movename[-1]:
            inv_movename = movename[:-1]
        else:
            inv_movename = movename + "'"
        add_inverse_move(history_dict["active_move_cycles"])
        history_dict["moves"][inv_movename] = history_dict["active_move_cycles"]


def add_inverse_move(cycle_list):
    """
    calculate the inverse of all cycles in 'cycle_list'
    """
    for cycle in cycle_list:
        cycle.reverse()


def interface_move(movename, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    if " " in movename:
        moves = movename.split(" ")
        for move in moves:
            interface_move(move, history_dict,
                           command_color=command_color, arg_color=arg_color, error_color=error_color)
            time.sleep(0.1)
    else:
        try:
            run_move(history_dict["vpy_objects"],
                    history_dict["moves"][movename],
                    history_dict["POINT_POS"],
                    history_dict["puzzle_com"])
        except KeyError:
            print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet.\
 Create a move using {colored('newmove', command_color)}.")


def interface_printmove(movename, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    try:
        run_printmove(
            movename, history_dict["moves"][movename], arg_color=arg_color)
    except KeyError:
        print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet. Create a move using {colored('newmove', command_color)}.")


def interface_savepuzzle(puzzlename, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    print("success 1")
    try:
        history_dict["puzzlename"] = puzzlename
        run_savepuzzle(puzzlename, history_dict)
    except KeyError:
        print(f"{colored('Error:', error_color)} move '{colored(movename, arg_color)}' does not exist yet. Create a move using {colored('newmove', command_color)}.")


def interface_loadpuzzle(puzzlename, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    load a puzzle 'puzzlename' from 'puzzles/[puzzlename]/puzzle_definition.xml' and
        save information in history_dict
    """
    try:
        point_dicts, moves_dict, vpy_objects, canvas = run_loadpuzzle(puzzlename)
        history_dict["point_dicts"] = point_dicts
        history_dict["moves"] = moves_dict
        history_dict["vpy_objects"] = vpy_objects
        history_dict["canvas"] = canvas
        history_dict["POINT_POS"] = [vpy.vec(obj.pos) for obj in vpy_objects]
        history_dict["puzzle_com"] = vpy.vec(0, 0, 0)
        history_dict["puzzlename"] = puzzlename
    except FileNotFoundError:
        print(f"{colored('Errod:', error_color)} Puzzle file does not exist yet. Create necessary files with {colored('savepuzzle', command_color)}")


def interface_listmoves(history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    for movename in history_dict["moves"].keys():
        interface_printmove(movename,
                            history_dict=history_dict,
                            command_color=command_color,
                            arg_color=arg_color,
                            error_color=error_color)


def interface_rename(user_input, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    renames the move given in user_input

    inputs:
    -------
        user_input - (str) - two movenames, old and new seperated by a space
    """
    old_name, new_name = user_input.split(" ")
    history_dict["moves"][new_name] = history_dict["moves"][old_name]
    del(history_dict["moves"][old_name])


def interface_delmove(movename, history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    deletes the given move from the 'history_dict'
    """
    try:
        del(history_dict["moves"][movename])
        print(f"successfully delted the move {colored(movename, arg_color)}.")
    except:
        print(f"{colored('Error:', error_color)} Move does not exist.")


def interface_closepuzzle(history_dict, command_color="#ff8800", arg_color="#5588ff", error_color="#ff0000"):
    """
    close the current puzzle and reset history_dict
    """
    save_answer = ""
    while not save_answer in ["y", "n"]:
        save_answer = input("save current puzzle before closing? (y/n) ")
        if save_answer.lower() == "y":
            try:
                interface_savepuzzle(history_dict["puzzlename"],
                                     history_dict,
                                     command_color=command_color,
                                     arg_color=arg_color,
                                     error_color=error_color)
            except KeyError:
                puzzlename = " "
                while " " in puzzlename:
                    puzzlename = input("Enter a name without spaces to save the puzzle: ")
                interface_savepuzzle(puzzlename,
                                     history_dict,
                                     command_color=command_color,
                                     arg_color=arg_color,
                                     error_color=error_color)
        try:
            history_dict["canvas"].delete()
        except KeyError:
            pass
        history_dict.clear()
        history_dict["movecreator"] = False
            
