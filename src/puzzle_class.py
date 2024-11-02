"""
a class for storing information about twisty puzzles and performing various tasks with them
"""
# import standard library modules
import cProfile
from copy import deepcopy
import json
import os
import pstats
import time

# import third party modules
import numpy as np
import matplotlib.pyplot as plt
# from sympy.combinatorics.perm_groups import PermutationGroup
import vpython as vpy
from sympy import factorint
from sympy.combinatorics import Permutation

# import custom modules
from .smart_scramble import smart_scramble

from .ggb_import.ggb_to_vpy import draw_points, get_point_dicts

from .interaction_modules.colored_text import colored_text as colored
from .interaction_modules.save_to_xml import save_to_xml
from .interaction_modules.load_from_xml import load_puzzle

from .puzzle_analysis_modules.size_analysis import get_state_space_size, approx_int
from .puzzle_analysis_modules.piece_detection_v2 import detect_pieces
from .puzzle_analysis_modules.state_validation import State_Validator, gen_puzzle_group

from .vpython_modules.vpy_functions import create_canvas, next_color, bind_next_color
from .vpython_modules.vpy_rotation import get_com, animate_move
from .vpython_modules.cycle_input import bind_click
from .vpython_modules.polyhedra import Polyhedron
from .vpython_modules.piece_modeling import draw_3d_pieces
from .vpython_modules.clip_shapes import shapes

from .shape_snapping import snap_to_cube, snap_to_sphere
from .puzzle_solver import solve_puzzle

# from .ai_modules.twisty_puzzle_model import scramble, perform_action
from .ai_modules.ai_data_preparation import state_for_ai
from .ai_modules.greedy_solver import Greedy_Puzzle_Solver
from .ai_modules.q_puzzle_class import Puzzle_Q_AI
from .ai_modules.v_puzzle_class import Puzzle_V_AI
from .ai_modules.nn_solver_interface import NN_Solver
# from .ai_modules.nn_puzzle_class import Puzzle_Network
# from .ai_modules.nn_v_her_puzzle_class import Puzzle_NN_V_HER_AI



class Twisty_Puzzle():
    def __init__(self):
        self.PUZZLE_NAME = None

        self.POINT_POSITIONS = [] # list of vpython vectors - correct position of 3d points
        self.SOLVED_STATE = [] # list of vpython vectors - correct colors of 3d points
        self.POINT_INFO_DICTS = []
        self.COM = None # vpython vector - center of mass of 3d points
        self.vpy_objects = [] # list of vpython objects - current state of the puzzle in animation
        self.animation_time: float = 0.25 # animation time per move
        self.max_animation_time: float = 120 # maximum time for a sequence of moves (move_v, move_nn etc.)
        self.alg_anim_style: str = "moves" # animation style for algorithm moves. will be either "moves" or "shortened"
        self.canvas = None
        self.moves = dict() # dcitionary containing all moves for the puzzle
        self.movecreator_mode = False
        self.moves_changed = False


    def validate_state(self):
        """
        using sympy permutation groups, check whether or not the current puzzle state is valid.
        Since some information about the puzzle state can get lost in the representation if multiple stickers (points)
            have the same color, the output is not always an integer but sometimes a float in range [0,1].
            This float is the probability that the state is valid.

        returns:
        --------
            (int) of (float) - if the validity can be confirmed with 100% accuracy, returns an integer 0 or 1
                otherwise returns a float in [0,1] with the probability of state validity.
        """
        if not hasattr(self, "state_validator"):
            self._update_perm_group()
        return self.state_validator.validate_state(self._get_ai_state())


    def _update_perm_group(self):
        """
        update the permutation group for the puzzle based on the currently defined moves

        also updates the state validator with the new group
        """
        if not hasattr(self, "color_list"):
            self.color_list = []
            for color in self.SOLVED_STATE:
                if not color in self.color_list:
                    self.color_list.append(color)
        size = len(self.SOLVED_STATE)
        puzzle_group = gen_puzzle_group(self.moves.values(), size)
        print("Calculated new puzzle group.")
        # try:
        #     self.state_validator.puzzle_group = puzzle_group
        # except AttributeError:
        #     self.state_validator = State_Validator(
        #             self._get_ai_state(),
        #             self.pieces,
        #             puzzle_group)
        self.state_space_size = puzzle_group.order()


    def snap(self, shape):
        """
        snap points to a given shape

        inputs:
        -------
            shape - (str) - the shape
                should be:
                    'cube' or 'c' for a cube
                    'sphere' or 's' for a sphere
                    'reset' or 'r' to reset to default positions
        """
        try:
            self.snap_obj.visible = False
        except AttributeError:
            self.snap_obj = None
        except NameError: # define self.snap_obj
            self.snap_obj = None
        if shape == "r" or shape == "reset":
            self._reset_point_positions()
        elif shape == "c" or shape =="cube":
            if not isinstance(self.snap_obj, vpy.box):
                self.snap_obj = snap_to_cube(self.vpy_objects, show_cube=True)
        elif shape == "s" or shape =="sphere":
            if not isinstance(self.snap_obj, vpy.sphere):
                self.snap_obj = snap_to_sphere(self.vpy_objects, show_sphere=True)
        self.POINT_POSITIONS = [vpy.vec(obj.pos) for obj in self.vpy_objects]


    def set_clip_poly(self, shape_str="cuboid", size=None, show_edges=True):
        """
        define a polyhedron to set the shape of the puzzle.
        saves the polyhedron as self.clip_poly
            and displays it with low opacity

        inputs:
        -------
            shape_str - (str) - the shape of the polyhedron
                current options:
                    - 'cuboid' = 'c' (default)
                    - 'cube'
                    - 'octahedron' = 'oct'
                    - 'tetrahedron' = 'tet'
            size - (float) or (vpy.vector) - if shape is a cuboid,
                this has to be a vpython vector, otherwise it needs to be a float

        raises:
        -------
            - ValueError if the shape is not valid
            - TypeError if the shape is not given as a string
        """
        if not isinstance(shape_str, str):
            raise TypeError(f"'shape_str' should be of type 'str' \
but was of type '{type(shape_str)}'")
        if hasattr(self, "clip_poly"):
            self.clip_poly.obj.visible = False
            # if isinstance(self.clip_poly, Polyhedron):
            #     self.clip_poly.toggle_visible(False)
            # else:
        if shape_str in ("cuboid", "c"):
            if size == None:
                xsize = max([obj.pos.x for obj in self.vpy_objects]) \
                      + abs(min([obj.pos.x for obj in self.vpy_objects]))
                ysize = max([obj.pos.y for obj in self.vpy_objects]) \
                      + abs(min([obj.pos.y for obj in self.vpy_objects]))
                zsize = max([obj.pos.z for obj in self.vpy_objects]) \
                      + abs(min([obj.pos.z for obj in self.vpy_objects]))
                size = vpy.vec(xsize, ysize, zsize)
            elif isinstance(size, (float, int)):
                size = vpy.vec(size,size,size)
            corners, faces = shapes["cuboid"](size=size)

        elif shape_str in ("tetrahedron", "tet"):
            if size == None:
                size = 2*max([obj.pos.mag for obj in self.vpy_objects])
            corners, faces = shapes["tetrahedron"](radius=size)

        elif shape_str in ("cube"):
            if size == None:
                size = 2*max(
                    [max([abs(obj.pos.x), abs(obj.pos.y), abs(obj.pos.z)]) \
                    for obj in self.vpy_objects])
            corners, faces = shapes["cube"](sidelength=size)

        elif shape_str in ("octahedron", "oct"):
            if size == None:
                size = 2*max([obj.pos.mag for obj in self.vpy_objects])
            corners, faces = shapes["octahedron"](radius=size)
        elif shape_str in ("cylinder", "cyl"):
            if size == None:
                size = max([vpy.sqrt(obj.pos.x**2 + obj.pos.y**2) for obj in self.vpy_objects])
            height = max([obj.pos.z for obj in self.vpy_objects]) \
                   + abs(min([obj.pos.z for obj in self.vpy_objects]))
            corners, faces = shapes["cylinder"](radius=size, height=height)
        else:
            raise ValueError(f"Invalid shape. Got {shape_str} but expected one of ['c', 'cuboid', 'tetrahedron', 'cube', 'oct', 'octahedron'].")
        self.clip_poly = Polyhedron(corners, faces,
                opacity=.2,
                color=vpy.vec(0.4,0,0.6),
                show_edges=show_edges,
                show_corners=show_edges)


    def draw_3d_pieces(self, debug=False):
        """
        draw 3d pieces within the already set clip polyhedron. If no clip_poly is set, clip to a cube.
        """
        if not hasattr(self, "clip_poly"):
            self.set_clip_poly(shape_str="cuboid")
        self.vpy_objects, self.unclipped_polys = \
                draw_3d_pieces(self.vpy_objects, self.clip_poly, show_edges=True, debug=debug)
        self.clip_poly.obj.visible = False
        # if isinstance(self.clip_poly, Polyhedron):
        #     self.clip_poly.toggle_visible(False)
        # else:
    

    def _reset_point_positions(self):
        """
        resets the point positions to their initial position
        """
        for point_dict, obj in zip(self.POINT_INFO_DICTS, self.vpy_objects):
            obj.pos = point_dict["coords"]
        try:
            self.snap_obj.visible = False
            self.snap_obj = None
        except:
            self.snap_obj = None


    def scramble(self, max_moves=30, arg_color="#0066ff"):
        """
        scramble the puzzle by applying [max_moves] random moves

        inputs:
        -------
            max_moves - (int) - the number of random moves
        """
        # scramble_hist = ""
        scramble_list = smart_scramble(self.SOLVED_STATE, self.base_moves, max_moves)
        scramble_hist = " ".join(scramble_list)
        # print scramble moves
        print(f"scrambled with the following moves:\n{colored(scramble_hist, arg_color)}")
        # perform scramble moves
        self.perform_move(scramble_hist)

    def reset_to_solved(self):
        """
        resets the puzzle colors to a solved state
        """
        for color, obj in zip(self.SOLVED_STATE, self.vpy_objects):
            obj.color = color


    def perform_move(self, moves: str, start_time: float = None, anim_time_override: float = None) -> None:
        """
        perform the given move on the puzzle self
        if multiple moves are given (seperated by spaces), they are all executed.
        

        Args:
            moves (str): a single move or several seperated by spaces
                Algorithms (starting with 'alg_') may be replaced with their base move sequence if `self.alg_anim_style` is set to "moves".
                May also include parentheses to repeat a sequence of moves, e.g. "3*(U R F)".
        """
        if start_time is None:
            start_time: float = time.time()
        def perform_single_move(move: str) -> None:
            """
            Perform a single move. If it is an algorithm, possibly replace it with the corresponding move sequence, calling self.perform_move() recursively.
            """
            if self.alg_anim_style == "moves" and move.startswith("alg_"):
                new_moves = self.alg_to_moves.get(move, moves)
                if new_moves != move:
                    print(f"Showing Alg. {move} as move sequence: {new_moves}")
                    self.perform_move(
                        new_moves,
                        start_time=start_time,
                        anim_time_override=self.animation_time/2)
                    return
                else:
                    print(f"Algorithm {move} not found. Showing as direct permutation.")
            if time.time() - start_time > self.max_animation_time:
                move_anim_time: float = 0.
            else:
                move_anim_time: float = self.animation_time if not anim_time_override else anim_time_override
            # make_move also permutes the vpy_objects
            animate_move(self.vpy_objects,
                      self.moves[move],
                      self.POINT_POSITIONS,
                      self.COM,
                      animation_time=move_anim_time,
                      target_fps=60) # TODO: get monitor refresh rate
        
        current_move: str = ""
        wait_for_parentheses: int = 0
        for char in moves:
            if char == "(":
                wait_for_parentheses += 1
                current_move += char
                continue
            if not wait_for_parentheses:
                if char == " ":
                    perform_single_move(current_move)
                    current_move = ""
                else:
                    current_move += char
            else: # wait for closing parentheses
                if char != ")":
                    current_move += char
                else:
                    wait_for_parentheses -= 1
                if wait_for_parentheses == 0:
                    num_repetitions, base_sequence = current_move.split("(")
                    try:
                        num_repetitions = int(num_repetitions.strip("*"))
                    except ValueError:
                        raise ValueError(f"Invalid number of repetitions: {num_repetitions}")
                    for _ in range(num_repetitions):
                        self.perform_move(
                            base_sequence,
                            start_time=start_time,
                            anim_time_override=self.animation_time/2)
                    current_move = ""
        if current_move:
            perform_single_move(current_move)
        # if "*" in moves:
        #     moves_list: list[str] = moves.split("*")
            
            
        # if "(" in moves:
        #         num, base_sequence = moves.split("(").strip(")")
        #         for _ in range(int(num)):
        #             self.perform_move(base_sequence)
        # elif ' ' in moves:
        #     moves_list: list[str] = moves.split(' ')
        #     num_moves: int = len(moves_list)
        #     # disable animations that take more than `self.max_animation_time` seconds
        #     old_anim_time: float = self.animation_time
        #     if num_moves*old_anim_time > self.max_animation_time:
        #         print(f"Not showing animation for {num_moves} moves.")
        #         self.animation_time = 0
        #     for move in moves_list:
        #         self.perform_move(move)
        #     # reset animation time
        #     self.animation_time = old_anim_time
        # else:
        #     if self.alg_anim_style == "moves" and moves.startswith("alg_"):
        #         new_moves = self.alg_to_moves.get(moves, default=moves)
        #         print(f"Showing {moves} as {new_moves}")
        #         self.perform_move(new_moves)
        #         return
            
        #     # make_move also permutes the vpy_objects
        #     animate_move(self.vpy_objects,
        #               self.moves[moves],
        #               self.POINT_POSITIONS,
        #               self.COM,
        #               animation_time=self.animation_time,
        #               target_fps=60) # TODO: get monitor refresh rate


    def newmove(self, movename, arg_color="#0066ff"):
        """
        start defining a new move with the given name, enable movecreator mode

        inputs:
        -------
            movename - (str) - the name of the new move
                must not include spaces
        """
        self.moves_changed = True
        if self.movecreator_mode:
            self.end_movecreation(arg_color=arg_color, update_group=False)
        self.movecreator_mode = True
        self.active_move_name = movename
        self.active_move_cycles = []
        self.active_arrows = []
        self.on_click_function = bind_click(self.canvas,
                                            self.active_move_cycles,
                                            self.vpy_objects,
                                            self.active_arrows)


    def end_movecreation(self, arg_color="#0066ff", add_inverse=True, update_group=True):
        """
        exit movecreator mode and save the last move
        """
        self.moves_changed = True
        self.movecreator_mode = False
        try:
            self.canvas.unbind("mousedown", self.on_click_function)
            del(self.on_click_function)
        except AttributeError:
            pass
        try:
            for arrow in self.active_arrows: #hide all arrows showing the move
                arrow.visible = False
            del(self.active_arrows)
        except AttributeError:
            pass
        if not self.active_move_cycles:
            print("no move defined.")
            return
        # reduce permutation to proper cycle notation (merge cycles with overlapping elements)
        reduced_cycles = Permutation(self.active_move_cycles).cyclic_form
        # save move
        self.moves[self.active_move_name] = [cycle[:] for cycle in reduced_cycles]
        print(f"saved move {colored(self.active_move_name, arg_color)}.")
        # add inverse move
        cycle_lengths = [len(cycle) for cycle in reduced_cycles]
        if update_group and (max(cycle_lengths) == 2 or not add_inverse):
            self._update_perm_group()
            print(f"updated state validator")
        if add_inverse and max(cycle_lengths) > 2:
            # prepare for adding inverse move:
            self._inverse_cycles(self.active_move_cycles)
            self.active_move_name = self.active_move_name[:-1] \
                if "'" == self.active_move_name[-1] else self.active_move_name + "'"
            self.end_movecreation(arg_color=arg_color, add_inverse=False) # add inverse move
        else:
            # cleanup temporary variables
            del(self.active_move_cycles)
            del(self.active_move_name)

    def _add_move_direct(self,
            move_name: str,
            move_cycles: list[tuple[int]],
            verbose: int = 1,
            arg_color="#0066ff") -> None:
        """
        add a move directly to the puzzle without using the movecreator mode
        """
        if move_name in self.moves:
            raise ValueError(f"Move {move_name} already exists.")
        self.moves[move_name] = [cycle[:] for cycle in move_cycles] # save copy of cycles as move
        # self.moves[move_name] = deepcopy(move_cycles)
        if verbose:
            print(f"saved move {colored(move_name, arg_color)}.")

    def _inverse_cycles(self, cycle_list):
        """
        inverts all cycles in [cycle_list]
        """
        for cycle in cycle_list:
            cycle.reverse()


    def rename_move(self, old_name, new_name):
        """
        rename the move [old_name] to [new_name]
        if the move [new_name] already exists, a warning could be useful

        inputs:
        -------
            old_name - (str) - name of the move to be renamed
            new_name - (str) - new name for that move
        """
        # check if any element appears in multiple cycles
        move_elements: set[int] = set()
        for cycle in self.moves[old_name]:
            for element in cycle:
                if element in move_elements:
                    break
                move_elements.add(element)
            else:
                continue
            # at least one element appears in multiple cycles
            print(f"Updating cyclic form of move {old_name}:")
            print(f"old cycles: {self.moves[old_name]}")
            self.moves[old_name] = Permutation(self.moves[old_name]).cyclic_form
            print(f"new cycles: {self.moves[old_name]}")
            break
        self.moves_changed = True
        self.moves[new_name] = self.moves[old_name]
        if old_name != new_name:
            del(self.moves[old_name])
        return
        


    def del_move(self, move_name):
        """
        delete the move [move_name]

        inputs:
        -------
            move_name - (str) - name of the move to be deleted
        """
        self.moves_changed = True
        del(self.moves[move_name])


    def edit_points(self):
        """
        allow editing of point colors
        """
        if not hasattr(self, "color_list"):
            self.color_list = []
            for color in self.SOLVED_STATE:
                if not color in self.color_list:
                    self.color_list.append(color)
        self.point_edit_method = bind_next_color(self.canvas, self.color_list)


    def end_edit_points(self):
        """
        unbind and delete the point editing function to end editing mode
        """
        self.canvas.unbind("mousedown", self.point_edit_method)
        del(self.point_edit_method)


    def save_puzzle(self, puzzle_name):
        """
        save the puzzle under the given name.
        if puzzle_name is None, try to save it as self.puzzle_name

        inputs:
        -------
            puzzle_name - (str) - name of the puzzle
                must not include spaces or other invalid characters for filenames
        """
        if puzzle_name != '':
            self.PUZZLE_NAME = puzzle_name
        save_to_xml(self)


    def load_puzzle(self, puzzle_name):
        """
        load the given puzzle from a .xml file
        set all important class variables accordingly

        inputs:
        -------
            puzzle_name - (str) - name of the puzzle
                must not include spaces or other invalid characters for filenames
        """
        self.POINT_INFO_DICTS, self.moves, state_space_size = load_puzzle(puzzle_name)
        self.base_moves = {name: cycles for name, cycles in self.moves.items() if not name[:4] in ("rot_", "alg_")}
        self.canvas = create_canvas()
        self.vpy_objects = draw_points(self.POINT_INFO_DICTS)

        self.POINT_POSITIONS = [point["coords"] for point in self.POINT_INFO_DICTS]
        self.SOLVED_STATE = [point["vpy_color"] for point in self.POINT_INFO_DICTS]
        self.COM = get_com(self.vpy_objects)
        self.PUZZLE_NAME = puzzle_name
        # load or calculate the state space size
        if state_space_size == None:
            self.state_space_size = get_state_space_size(
                    self.moves.values(), len(self.SOLVED_STATE))
        else:
            self.state_space_size = state_space_size

        # try to load algorithm moves if applicable
        for move in self.moves:
            if move.startswith("alg_"):
                # load algorithm moves from `algorithm_moves.json`
                try:
                    alg_moves_filepath = os.path.join("src", "puzzles", self.PUZZLE_NAME, "algorithm_moves.json")
                    with open(alg_moves_filepath, "r") as file:
                        self.alg_to_moves: dict[str, str] = json.load(file)
                    print(f"Loaded algorithm moves from {alg_moves_filepath}")
                    break
                except FileNotFoundError as exception:
                    print(exception)
                    print("No algorithm moves file found.")
                    self.alg_to_moves: dict[str, str] = dict()
                    self.alg_anim_style: str = "shortened"
        else:
            self.alg_to_moves: dict[str, str] = dict()
            self.alg_anim_style: str = "shortened"

        print(f"The loaded puzzle has {approx_int(self.state_space_size)} possible states and {len(self.moves)} availiable moves.")
        print(f"Exact number of states: {self.state_space_size}")
        print(f"prime factors: {factorint(self.state_space_size)}")
        # calculate the number of pieces in the puzzle
        if len(self.moves) > 0:
            self.pieces = detect_pieces(self.moves, len(self.SOLVED_STATE))
            print(f"The loaded puzzle has {len(self.pieces)} pieces:\n", *self.pieces)
        self.moves_changed = False


    def import_puzzle(self, filepath):
        """
        imports a puzzle from a given .ggb (Geogebra) file
        The puzzle will automatically be centered around the origin.

        inputs:
        -------
            filepath - (str) - path to a .ggb file represeting a puzzle
        """
        try:
            self.POINT_INFO_DICTS = get_point_dicts(filepath)
        except FileNotFoundError:
            self.POINT_INFO_DICTS = get_point_dicts(filepath+".ggb")
        if not hasattr(self, "canvas") or self.canvas == None:
            self.canvas = create_canvas()
        # draw_points also converts coords in dictionaries to vpython vectors
        self.vpy_objects = draw_points(self.POINT_INFO_DICTS)
        self.COM = get_com(self.vpy_objects)

        if not self.COM.mag < 1e-10:
            for point_dict, obj in zip(self.POINT_INFO_DICTS, self.vpy_objects):
                obj.pos -= self.COM
                point_dict["coords"] -= self.COM

        self.POINT_POSITIONS = [point["coords"] for point in self.POINT_INFO_DICTS]
        self.SOLVED_STATE = [point["vpy_color"] for point in self.POINT_INFO_DICTS]
        self.moves_changed = False


    def listmoves(self, arg_color="#0066ff", print_perms=True):
        """
        print all availiable moves for this puzzle
        if every move has an inverse: don't print the inverse moves
        """
        print(f"the puzzle {colored(self.PUZZLE_NAME, arg_color)} is defined with the following moves:")
        if print_perms:
            for movename in self.moves.keys():
                self.print_move(
                    movename,
                    arg_color=arg_color)
        if len(self.moves) > 0:
            print("\nThe following moves are availiable: ")
            for movename in list(self.moves.keys())[:-1]:
                print(colored(movename, arg_color), end=", ")
            print(colored(list(self.moves.keys())[-1], arg_color))
        else:
            print("No moves are defined yet.")


    def print_move(self, move_name, arg_color="#0066ff"):
        """
        print the given move
        """
        move_str = [tuple(cycle) for cycle in self.moves[move_name]]
        print(f"{colored(move_name, arg_color)} =", move_str)


    def move_greedy(self, num_moves: int = 1, arg_color: str = "#0066ff"):
        """
        Make `num_moves` moves using a greedy policy with rewards counting the number of solved points

        Args:
            num_moves (int, optional): number of moves to make. Defaults to 1.
            arg_color (str, optional): color for printing the moves. Defaults to "#0066ff".
        """
        # disable animations that take more than `self.max_animation_time` seconds
        old_anim_time: float = self.animation_time
        if num_moves * self.animation_time > self.max_animation_time:
            print(f"Not showing animation for {num_moves} moves.")
            self.animation_time = 0
        # execute `num_moves` moves using the V-table
        max_move_name_len = max([len(move) for move in self.moves.keys()])
        # init greedy solver
        ai_solved_state, self.color_list = state_for_ai(self.SOLVED_STATE)
        greedy_solver: Greedy_Puzzle_Solver = Greedy_Puzzle_Solver(
            self.moves,
            ai_solved_state,
            puzzle_name=self.PUZZLE_NAME,
        )
        for i in range(num_moves):
            # get move from the greedy solver
            ai_state = self._get_ai_state()
            value = greedy_solver.get_state_value(ai_state)
            ai_move = greedy_solver.choose_action(ai_state)
            self.perform_move(ai_move)
            # print move info
            ai_move_str = f"{ai_move:{max_move_name_len}}"
            print(f"made move: {colored(ai_move_str, arg_color)}. Previous state had value: {value}.")
            # check if puzzle is solved
            if self._get_ai_state() == ai_solved_state:
                print(f"Puzzle was solved after {colored(str(i+1), arg_color)} moves.")
                break
        # reset animation time
        if self.animation_time != old_anim_time:
            self.animation_time = old_anim_time


    def solve_greedy(self, max_time: float = 60, WEIGHT: float = 0.1, arg_color="#0066ff"):
        """
        solve the puzzle using a greedy algorithm
        """
        ai_solved_state, self.color_list = state_for_ai(self.SOLVED_STATE)
        greedy_solver: Greedy_Puzzle_Solver = Greedy_Puzzle_Solver(
            self.moves,
            ai_solved_state,
            puzzle_name=self.PUZZLE_NAME,
        )
        solve_moves = solve_puzzle(
            self._get_ai_state(),
            self.moves,
            ai_solved_state,
            ai_class=greedy_solver,
            max_time=max_time,
            WEIGHT=WEIGHT,
        )
        if not solve_moves == "":
            print(f"solved the puzzle after {colored(str(len(solve_moves.split(' '))), arg_color)} moves:")
            print(f"{colored(solve_moves, arg_color)}")
            self.perform_move(solve_moves)

    def _get_ai_state(self):
        """
        return the current puzzle state for the ai based on self.color_list
        """
        ai_state = []

        for color in [obj.color for obj in self.vpy_objects]:
            for i, index_color in enumerate(self.color_list):
                if index_color == color:
                    ai_state.append(i)

        return ai_state

#####     START Q-learning     #####

    def train_q_learning(self, num_episodes=None, max_moves=None, learning_rate=None, discount_factor=None, base_exploration_rate=None, keep_q_table=True):
        """
        train the Q-table for the current puzzle
        """
        ai_state, self.color_list = state_for_ai(self.SOLVED_STATE)
        reward_dict = {"solved":1,
                       "timeout":0,
                       "move":0}
        if not hasattr(self, "ai_q_class"):
            self.ai_q_class = Puzzle_Q_AI(deepcopy(self.moves), ai_state, reward_dict=reward_dict, name=self.PUZZLE_NAME, keep_q_table=keep_q_table)
        profile = cProfile.Profile()
        training_history = \
            profile.runcall(
                self.ai_q_class.train_q_learning,
                reward_dict=reward_dict,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                base_exploration_rate=base_exploration_rate,
                max_moves=max_moves,
                num_episodes=num_episodes,
                keep_q_table=keep_q_table
                )
        ps = pstats.Stats(profile)
        ps.sort_stats(("tottime"))
        ps.print_stats(10)


    def move_Q(self, arg_color="#0066ff"):
        """
        make one move based on the current Q-table of the AI
        """
        ai_state = tuple(self._get_ai_state())
        ai_move = self.ai_q_class.choose_q_action(ai_state)
        self.perform_move(ai_move)
        print(f"made move: {colored(ai_move, arg_color)}")
        try:
            value = self.ai_q_class.q_table[(ai_state,ai_move)]
        except KeyError:
            value = 0
        print(f"move had value {value}")


    def solve_Q(self, max_time=60, WEIGHT=0.1, arg_color="#0066ff"):
        """
        solve the puzzle based on the current Q-table of the AI
        """
        solve_moves = solve_puzzle(self._get_ai_state(),
                                   self.moves,
                                   self.ai_q_class.SOLVED_STATE,
                                   self.ai_q_class,
                                   max_time=max_time,
                                   WEIGHT=WEIGHT)
        if not solve_moves == "":
            print(f"solved the puzzle after {colored(str(len(solve_moves.split(' '))), arg_color)} moves:")
            print(f"{colored(solve_moves, arg_color)}")
            self.perform_move(solve_moves)
        # solve_moves = ""
        # last_moves = []
        # for n in range(max_moves):
        #     ai_state = self.get_ai_state()
        #     if self.ai_q_class.puzzle_solved(ai_state, n, max_moves=max_moves) == "solved":
        #         print(f"solved the puzzle after {colored(str(n), arg_color)} moves:")
        #         print(f"{colored(solve_moves[:-1], arg_color)}")
        #         break
        #     if len(set(last_moves[-10:])) == 1 and len(last_moves) > 5:
        #         ai_move = self.ai_q_class.choose_Q_action(tuple(ai_state), exploration_rate=0.5)
        #         print("detected loop")
        #     else:
        #         ai_move = self.ai_q_class.choose_Q_action(tuple(ai_state), exploration_rate=0)
        #     last_moves.append(ai_move)
        #     self.perform_move(ai_move)
        #     solve_moves += ai_move + ' '


    def plot_q_success(self, batch_size=30):
        x_data = []
        y_data = []
        for i in range(batch_size, len(self.solved_hist)):
            solved_percent = self.solved_hist[i-batch_size:i].count(True)/batch_size
            y_data.append(solved_percent)
            x_data.append(i)

        plt.vlines(self.diff_increase, 0, 1, colors=["#dddddd"], linestyles="--")


        plt.plot([i for i in range(len(self.solved_hist))], self.explo_rates, ".", color="#ff8800")

        plt.plot(x_data, y_data, ".")
        plt.show()

#####     END Q-learning     #####
#####     START V-learning     #####

    def train_v_learning(self,
            num_episodes=None,
            max_moves=None,
            learning_rate=None,
            discount_factor=None,
            base_exploration_rate=None,
            keep_v_table=True):
        """
        train the V-table for the current puzzle
        """
        ai_state, self.color_list = state_for_ai(self.SOLVED_STATE)
        reward_dict = {"solved":1,
                       "timeout":0,
                       "move":0}
        if not hasattr(self, "ai_v_class"):
            self.ai_v_class = Puzzle_V_AI(
                    deepcopy(self.moves),
                    ai_state,
                    # reward_dict=reward_dict,
                    name=self.PUZZLE_NAME,
                    keep_v_table=keep_v_table)
        profile = cProfile.Profile()
        training_history = \
            profile.runcall(self.ai_v_class.train_v_learning, 
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                base_exploration_rate=base_exploration_rate,
                max_moves=max_moves,
                num_episodes=num_episodes,
                keep_v_table=keep_v_table)
        ps = pstats.Stats(profile)
        ps.sort_stats(("tottime"))
        ps.print_stats(10)
        # self.v_param_history = \
        #     self.ai_v_class.train_v_learning(
        #             # reward_dict=reward_dict,
        #             learning_rate=learning_rate,
        #             discount_factor=discount_factor,
        #             base_exploration_rate=base_exploration_rate,
        #             max_moves=max_moves,
        #             num_episodes=num_episodes,
        #             keep_v_table=keep_v_table)


    def move_v(self, num_moves: int = 1, arg_color: str = "#0066ff"):
        """
        make one move based on the current V-table of the AI
        """
        # disable animations that take more than `self.max_animation_time` seconds
        old_anim_time = self.animation_time
        if num_moves * self.animation_time > self.max_animation_time:
            print(f"Not showing animation for {num_moves} moves.")
            self.animation_time = 0
        ai_solved_state, self.color_list = state_for_ai(self.SOLVED_STATE)
        # execute `num_moves` moves using the V-table
        max_move_name_len = max([len(move) for move in self.moves.keys()])
        for _ in range(num_moves):
            ai_state = self._get_ai_state()
            ai_move = self.ai_v_class.choose_v_action(ai_state)
            self.perform_move(ai_move)
            try:
                value = self.ai_v_class.v_table[tuple(ai_state)]
            except KeyError:
                value = 0
            ai_move_str = f"{ai_move:{max_move_name_len}}"
            print(f"made move: {colored(ai_move_str, arg_color)}. Previous state had value: {value}.")
            # check if puzzle is solved
            if self._get_ai_state() == ai_solved_state:
                print(f"Puzzle was solved after {colored(str(i+1), arg_color)} moves.")
                break
        # reset animation time
        if self.animation_time != old_anim_time:
            self.animation_time = old_anim_time

    def solve_v(self, max_time=60, WEIGHT=0.1, arg_color="#0066ff"):
        """
        solve the puzzle based on the current V-table of the AI
        """
        solve_moves = solve_puzzle(self._get_ai_state(),
                                   self.moves,
                                   self.ai_v_class.SOLVED_STATE,
                                   self.ai_v_class,
                                   max_time=max_time,
                                   WEIGHT=WEIGHT)
        if not solve_moves == "":
            solution_length = len(solve_moves.split(' '))
            print(f"solved the puzzle after {colored(str(solution_length), arg_color)} moves:")
            print(f"{colored(solve_moves, arg_color)}")
            self.perform_move(solve_moves)

#####     END V-learning     #####
#####     START NN-V-learning     #####

    def _get_ai_nn_state(self):
        """
        return the current puzzle state for the ai based on self.color_list_nn
        """
        # ai_state = []
        # for color in [obj.color for obj in self.vpy_objects]:
        #     for i, index_color in enumerate(self.color_list_nn):
        #         if index_color == color:
        #             ai_state.append(i)
        ai_state: list[int] = [
            self.color_list_nn.index(vpy_vec_to_tuple(obj.color)) for obj in self.vpy_objects
        ]

        return ai_state

    def load_nn(self,
            model_path: str,
            arg_color: str = "#0066ff"
        ):
        """
        Load a trained RL agent's neural network from a given file.
        
        
        """
        # if no specific model is chosen, automatically choose the latest one.
        if not model_path:
            model_path = self.PUZZLE_NAME
        
        self.color_list_nn: list[vpy.vector] = [vpy_vec_to_tuple(color) for color in self.SOLVED_STATE]
        self.color_list_nn = list(set(self.color_list_nn))
        ai_solved_state = [self.color_list_nn.index(vpy_vec_to_tuple(color)) for color in self.SOLVED_STATE]
        # ai_solved_state, self.color_list_nn = state_for_ai(self.SOLVED_STATE)
        # self.color_list_nn.reverse()
        # set up the neural network solver
        self.nn_solver: NN_Solver = NN_Solver(
            ACTIONS_DICT=self.moves,
            SOLVED_STATE=ai_solved_state,
            model_path=model_path,
        )
        print(f"Loaded RL agent from {colored(model_path, arg_color)}.")


    def move_nn(self, num_moves, arg_color="#0066ff"):
        """
        make one move based on the current Q-table of the AI
        
        Args:
            num_moves (int): (maximum) number of moves to make. May take fewer moves if the puzzle is solved.
            arg_color (str): color for printing the moves
        
        Raises:
            AttributeError: 
        """
        # disable animations that take more than `self.max_animation_time` seconds
        old_anim_time: float = self.animation_time
        if num_moves * self.animation_time > self.max_animation_time:
            print(f"Not showing animation for {num_moves} moves.")
            self.animation_time = 0
        # execute `num_moves` moves using the V-table
        max_move_name_len = max([len(move) for move in self.moves.keys()])
        for i in range(num_moves):
            # get move from the greedy solver
            ai_state: list[int] = self._get_ai_nn_state()
            ai_move = self.nn_solver.choose_action(ai_state)
            self.perform_move(ai_move)
            reward, done = self.nn_solver.reward_func(np.array(self._get_ai_nn_state()), truncated=False)
            # print move info
            ai_move_str = f"{ai_move:{max_move_name_len}}"
            print(f"made move: {colored(ai_move_str, arg_color)}  Reward for new state: {reward}")
            # check if puzzle is solved
            if done or self._get_ai_nn_state() == self.nn_solver.solved_state:
                print(f"Puzzle was solved after {colored(str(i+1), arg_color)} moves.")
                break
        # reset animation time
        if self.animation_time != old_anim_time:
            self.animation_time = old_anim_time
        if not hasattr(self, "nn_solver"):
            raise AttributeError(f"Load a NN-based solver before trying to use it. Use {colored('load_nn', arg_color)}.")


    def solve_nn(self, max_time=60, WEIGHT=0.1, arg_color="#0066ff"):
        """
        solve the puzzle based on the current Q-table of the AI
        """
        solve_moves = solve_puzzle(self._get_ai_state(),
                                   self.moves,
                                   self.nn_solver.SOLVED_STATE,
                                   self.nn_solver,
                                   max_time=max_time,
                                   WEIGHT=WEIGHT)
        if not solve_moves == "":
            print(f"solved the puzzle after {colored(str(len(solve_moves.split(' '))), arg_color)} moves:")
            print(f"{colored(solve_moves, arg_color)}")
            self.perform_move(solve_moves)
        # solve_moves = ""
        # last_moves = []
        # for n in range(max_moves):
        #     ai_state = self.get_ai_state()
        #     if self.ai_q_class.puzzle_solved(ai_state, n, max_moves=max_moves) == "solved":
        #         print(f"solved the puzzle after {colored(str(n), arg_color)} moves:")
        #         print(f"{colored(solve_moves[:-1], arg_color)}")
        #         break
        #     if len(set(last_moves[-10:])) == 1 and len(last_moves) > 5:
        #         ai_move = self.ai_nn_class.choose_nn_move(ai_state, self.moves, exploration_rate=0.5)
        #         print("detected loop")
        #     else:
        #         ai_move = self.ai_nn_class.choose_nn_move(ai_state, self.moves, exploration_rate=0)
        #     last_moves.append(ai_move)
        #     self.perform_move(ai_move)
        #     solve_moves += ai_move + ' '

#####     END NN-learning     #####

def vpy_vec_to_tuple(vec: vpy.vector) -> tuple[float, float, float]:
    """
    Convert a vpython vector to a tuple of floats

    Args:
        vec (vpy.vector): vpython vector

    Returns:
        tuple[float, float, float]: tuple of three floats
    """
    return (vec.x, vec.y, vec.z)
