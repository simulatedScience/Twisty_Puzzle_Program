from copy import deepcopy
import vpython as vpy

from .colored_text import colored_text as colored
from .save_to_xml import save_to_xml
from .load_from_xml import load_puzzle

from ..ggb_import import ggb_to_vpy as ggb_vpy

from ..shape_snapping import snap_to_cube, snap_to_sphere
from ..vpython_modules.create_canvas import create_canvas
from ..vpython_modules.vpy_rotation import get_com, make_move
from ..vpython_modules.cycle_input import bind_click, on_click


def run_import(filepath):
    """
    imports the given .ggb file and creates vpython objects
        for every point in the file

    inputs:
    -------
        filepath - (str) - a path to a .ggb file

    returns:
    --------
        (list) of dicts - representing every point of the .ggb file
        (list) of vpython objects - representing every point of the .ggb file
    """
    try:
        point_dicts = ggb_vpy.get_point_dicts(filepath)
    except FileNotFoundError:
        point_dicts = ggb_vpy.get_point_dicts(filepath+".ggb")
    return init_animation(point_dicts)


def run_loadpuzzle(puzzlename):
    """
    load a puzzle with the given name from a .xml file
    display it using vpython

    inputs:
    -------
        puzzlename - (str) - name of the puzzle folder

    returns:
    --------
        (list) of dicts - point_dicts
        (list) of vpython objects - vpy_objects
        (vpython canvas) - canvas used to display the puzzle
        (dict) - moves with keys [movename] and a list of lists as values
        coming soon: (list) - bandagings
    """
    point_dicts, moves_dict = load_puzzle(puzzlename)
    point_dicts, vpy_objects, canvas = init_animation(point_dicts)
    return point_dicts, moves_dict, vpy_objects, canvas


def init_animation(point_dicts):
    """
    create a canvas object and draw all points giben in 'point_dicts'

    inputs:
    -------
        point_dicts - (list) of dicts -

    returns:
    --------
        (list) - 'point_dicts' same as input value
        (list) - list of vpython objects that were drawn
        (vpython canvas) - the vpython canvas that was used
    """
    canvas = create_canvas()
    vpy_objects = ggb_vpy.draw_points(point_dicts)
    return point_dicts, vpy_objects, canvas

def run_snap(shape, vpy_objects, prev_shape=None):
    """
    snap points to the given shape
    """
    puzzle_com = get_com(vpy_objects)
    if not puzzle_com.mag < 1e-12:
        for obj in vpy_objects:
            obj.pos -= puzzle_com

    if shape == "cube" or shape == "c":
        if not isinstance(prev_shape, vpy.box):
            snap_obj = snap_to_cube(vpy_objects, show_cube=True)
        else:
            return None, puzzle_com
    elif shape == "sphere" or shape == "s":
        if not isinstance(prev_shape, vpy.sphere):
            snap_obj = snap_to_sphere(vpy_objects, show_sphere=True)
        else:
            return None, puzzle_com
    return snap_obj, puzzle_com


def run_newmove(canvas, cycle_list, object_list, arrow_list):
    """
    allow the visual input of cycles for a new move by binding
        the mousedown event on the canvas to an appropriate action

    inputs:
    -------
        canvas - (vpython canvas) - the vypthon canvas that was used to create the cycle
        cycle_list - (list) - list, will be changed in-place
        object_list - (list) - list of objects that are allowed in the cycles
        arrow_list - (list) - empty or list of vpython objects

    returns:
    --------
        None

    outputs:
    --------
        binds the mousedown event on the canvas to an appropriate action
    """
    return bind_click(canvas, cycle_list, object_list, arrow_list)


def run_endmove(cycle_list, arrow_list, canvas, bound_method):
    """
    unbind the mousedown button from any action
    return deepcopy of cycle_list
    delete all arrows showing the cycles of the move

    inputs:
    -------
        canvas - (vpython canvas) - the vypthon canvas that was used to create the cycle
        cycle_list - (list) of lists - list of cycles as lists
        arrow_list - (list) of vpython objects - list with the arrows
            displaying the cycles
        bound_method - (function) - the function that is bound to the
            'mousedown' event on the given canvas.

    returns:
    --------
        (list) - deepcopy of cycle_list

    outputs:
    --------
        unbinds the mousedown event
    """
    canvas.unbind("mousedown", bound_method)
    for arrow in arrow_list:
        arrow.visible = False
    arrow_list.clear()
    return deepcopy(cycle_list)


def run_printmove(movename, cycle_list, arg_color="#0066ff"):
    """
    prints the given move as it's cycles
    """
    print(f"{colored(movename, arg_color)} is defined by the cycles", cycle_list)


def run_savepuzzle(puzzlename, puzzle_info_dict, arg_color="#0066ff"):
    """
    prints the given move as it's cycles

    inputs:
    -------
        puzzle_name - (str) - name of the puzzle
        puzzle_info_dict - (dict) - dictionary containing information about the puzzle 
            using the following keys:
            "point_dicts" - list of dictionaries containing point information:
                "coords" - list of x,y,z coordinates
                "vpy_color" - vpython color vector (r,g,b) in range 0-1
            "moves" - dictionary containing moveames as keys and lists of cycles as values

    returns:
    --------
        None

    outputs:
    --------
        creates a file "puzzle_definition.xml" to save the important puzzle information
    """
    print(f"saved puzzle as {colored(puzzlename, arg_color)}.")
    save_to_xml(puzzlename, puzzle_info_dict)


def run_move(object_list, cycle_list, POINT_POS, PUZZLE_COM, sleep_time=5e-3, anim_steps=45):
    """
    perform the given move

    inputs:
    -------
        object_list - (list) of vpython objects - any vpython objects with .pos attribute
        cycle_list - (list) of lists - list of cycles as indices of object_list defining
            a permutation in cyclic notation
        POINT_POS - (list) of vpython vectors - list of correct positions for each object
            this list must not change when the objects move
        PUZZLE_COM - (vpython vector) - center of the puzzle (usually (0,0,0))
    
    returns:
    --------
        None

    outpus:
    -------
        changes the .pos attribute of the objects in object_list according to the move
        permutes the objects in object_list to represent the position changes
        animate move
    """
    make_move(object_list, cycle_list, POINT_POS, PUZZLE_COM, sleep_time=sleep_time, anim_steps=anim_steps)


def run_help(command_color="#ff8800", arg_color="#0055cc"):
    print(f"- {colored('import', command_color)} [{colored('filepath', arg_color)}]          \
- load file from 'filepath' and show points in vpython")
    print(f"- {colored('snap', command_color)} [{colored('mode', arg_color)}]                \
- snap points to shape, {colored('mode', arg_color)} = '{colored('cube', arg_color)}'='{colored('c', arg_color)}' \
or '{colored('sphere', arg_color)}'='{colored('s', arg_color)}'\n{' '*31}\
run {colored('snap', command_color)} again to hide the snap shape")
    print(f"- {colored('newmove', command_color)} [{colored('movename', arg_color)}]         \
- create new move with name 'movename'")
    print(f"- {colored('endmove', command_color)}                    \
- exit move creator mode and save current move to some file")
    print(f"- {colored('move', command_color)} [{colored('movename', arg_color)}]            \
- perform the mive with the given 'movename'")
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
