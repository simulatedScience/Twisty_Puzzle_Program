"""
a class for storing information about twisty puzzles
"""
import time
import random
from copy import deepcopy
import matplotlib.pyplot as plt
import vpython as vpy

from .ggb_import.ggb_to_vpy import draw_points, get_point_dicts

from .interaction_modules.colored_text import colored_text as colored
from .interaction_modules.save_to_xml import save_to_xml
from .interaction_modules.load_from_xml import load_puzzle

from .vpython_modules.create_canvas import create_canvas
from .vpython_modules.vpy_rotation import get_com, make_move
from .vpython_modules.cycle_input import bind_click

from .shape_snapping import snap_to_cube, snap_to_sphere

from .ai_modules.twisty_puzzle_model import scramble, perform_action
from .ai_modules.ai_data_preparation import state_for_ai
from .ai_modules.ai_puzzle_class import puzzle_ai


class Twisty_Puzzle():
    def __init__(self):
        self.PUZZLE_NAME = None

        self.POINT_POSITIONS = [] # list of vpython vectors - correct position of 3d points
        self.SOLVED_STATE = [] # list of vpython vectors - correct colors of 3d points
        self.POINT_INFO_DICTS = []
        self.COM = None # vpython vector - center of mass of 3d points
        self.vpy_objects = [] # list of vpython objects - current state of the puzzle in animation
        self.sleep_time = 5e-3
        self.canvas = None
        self.moves = dict() # dcitionary containing all moves for the puzzle
        self.movecreator_mode = False


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
            self.reset_point_positions()
        elif shape == "c" or shape =="cube":
            if not isinstance(self.snap_obj, vpy.box):
                self.snap_obj = snap_to_cube(self.vpy_objects, show_cube=True)
        elif shape == "s" or shape =="sphere":
            if not isinstance(self.snap_obj, vpy.sphere):
                self.snap_obj = snap_to_sphere(self.vpy_objects, show_sphere=True)
        self.POINT_POSITIONS = [vpy.vec(obj.pos) for obj in self.vpy_objects]


    def reset_point_positions(self):
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
        scramble_hist = ""
        for _ in range(max_moves):
            move = random.choice(list(self.moves.keys()))
            scramble_hist += move + ' '
            self.perform_move(move)
            time.sleep(50*self.sleep_time)
        print(f"scrambled with the following moves:\n{colored(scramble_hist, arg_color)}")


    def reset_to_solved(self):
        """
        resets the puzzle colors to a solved state
        """
        for color, obj in zip(self.SOLVED_STATE, self.vpy_objects):
            obj.color = color


    def perform_move(self, moves):
        """
        perform the given move on the puzzle self
        if multiple moves are given, they are all executed

        inputs:
        -------
            moves - (str) - a single move or several seperated by spaces
        """
        if ' ' in moves:
            for move in moves.split(' '):
                self.perform_move(move)
                time.sleep(50*self.sleep_time)
        else:
            # make_move also permutes the vpy_objects
            make_move(self.vpy_objects,
                      self.moves[moves],
                      self.POINT_POSITIONS,
                      self.COM,
                      sleep_time=self.sleep_time,
                      anim_steps=45)


    def newmove(self, movename, arg_color="#0066ff"):
        """
        start defining a new move with the given name, enable movecreator mode

        inputs:
        -------
            movename - (str) - the name of the new move
                must not include spaces
        """
        if self.movecreator_mode:
            self.end_movecreation(arg_color=arg_color)
        self.movecreator_mode = True
        self.active_move_name = movename
        self.active_move_cycles = []
        self.active_arrows = []
        self.on_click_function = bind_click(self.canvas,
                                            self.active_move_cycles,
                                            self.vpy_objects,
                                            self.active_arrows)


    def end_movecreation(self, arg_color="#0066ff", add_inverse=True):
        """
        exit movecreator mode and save the last move
        """
        self.movecreator_mode = False
        try:
            for arrow in self.active_arrows: #hide all arrows showing the move
                arrow.visible = False
            del(self.active_arrows)
        except AttributeError:
            pass
        self.moves[self.active_move_name] = deepcopy(self.active_move_cycles)

        print(f"saved move {colored(self.active_move_name, arg_color)}.")
        if add_inverse:
            # prepare for adding inverse move:
            self.inverse_cycles(self.active_move_cycles)
            self.active_move_name = self.active_move_name[:-1] \
                if "'" == self.active_move_name[-1] else self.active_move_name + "'"
            self.end_movecreation(arg_color=arg_color, add_inverse=False) # add inverse move


    def inverse_cycles(self, cycle_list):
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
        self.moves[new_name] = self.moves[old_name]
        del(self.moves[old_name])


    def del_move(self, move_name):
        """
        delete the move [move_name]

        inputs:
        -------
            move_name - (str) - name of the move to be deleted
        """
        del(self.moves[move_name])


    def save_puzzle(self, puzzle_name):
        """
        save the puzzle under the given name.
        if puzzle_name is None, try to save it as self.puzzle_name

        inputs:
        -------
            puzzle_name - (str) - name of the puzzle
                must not include spaces or other invalid characters for filenames
        """
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
        self.POINT_INFO_DICTS, self.moves = load_puzzle(puzzle_name)
        self.canvas = create_canvas()
        self.vpy_objects = draw_points(self.POINT_INFO_DICTS)

        self.POINT_POSITIONS = [point["coords"] for point in self.POINT_INFO_DICTS]
        self.SOLVED_STATE = [point["vpy_color"] for point in self.POINT_INFO_DICTS]
        self.COM = get_com(self.vpy_objects)
        self.PUZZLE_NAME = puzzle_name

    
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
        self.canvas = create_canvas()
        # draw_points also converts coords in dictionaries to vpython vectors
        self.vpy_objects = draw_points(self.POINT_INFO_DICTS)
        self.COM = get_com(self.vpy_objects)

        if not self.COM.mag < 1e-10:
            for point_dict, obj in zip(self.POINT_INFO_DICTS, self.vpy_objects):
                obj.pos -= self.COM
                point_dict["coords"] -= self.COM

        self.POINT_POSITIONS = [point["coords"] for point in self.POINT_INFO_DICTS]
        self.SOLVED_STATE = [point["color"] for point in self.POINT_INFO_DICTS]


    def listmoves(self, arg_color="#0066ff"):
        """
        print all availiable moves for this puzzle
        if every move has an inverse: don't print the inverse moves
        """
        print(f"the puzzle {colored(self.PUZZLE_NAME, arg_color)} is defined with the following moves:")
        for movename in self.moves.keys():
            self.print_move(movename,
                           arg_color=arg_color)


    def print_move(self, move_name, arg_color="#0066ff"):
        """
        print the given move
        """
        print(f"{colored(move_name, arg_color)} is defined by the cycles", self.moves[move_name])


    def train_q_learning(self, num_episodes=None, max_moves=None, learning_rate=None, discount_factor=None, base_exploration_rate=None, keep_Q_table=True):
        """
        train the Q-table for the current puzzle
        """
        ai_state, self.ai_color_list = state_for_ai(self.SOLVED_STATE)
        reward_dict = {"solved":1000,
                       "timeout":0,
                       "move":-1}
        if not hasattr(self, "AI_class"):
            self.ai_q_class = puzzle_ai(deepcopy(self.moves), ai_state, reward_dict=reward_dict, name=self.PUZZLE_NAME, keep_Q_table=keep_Q_table)
        games, self.solved_hist, self.diff_increase, self.explo_rates = \
            self.ai_q_class.train_q_learning(reward_dict=reward_dict,
                                           learning_rate=learning_rate,
                                           discount_factor=discount_factor,
                                           base_exploration_rate=base_exploration_rate,
                                           max_moves=max_moves,
                                           num_episodes=num_episodes,
                                           keep_Q_table=keep_Q_table)


    def move_Q(self, arg_color="#0066ff"):
        """
        make one move based on the current Q-table of the AI
        """
        ai_state = self.get_ai_state()
        ai_move = self.ai_q_class.choose_Q_action(ai_state)
        self.perform_move(ai_move)
        print(f"made move: {colored(ai_move, arg_color)}")


    def solve_Q(self, max_moves=100, arg_color="#0066ff"):
        """
        solve the puzzle based on the current Q-table of the AI
        """
        solve_moves = ""
        last_moves = []
        for n in range(max_moves):
            ai_state = self.get_ai_state()
            if self.ai_q_class.puzzle_solved(ai_state, n, max_moves=max_moves) == "solved":
                print(f"solved the puzzle after {colored(str(n), arg_color)} moves:")
                print(f"{colored(solve_moves[:-1], arg_color)}")
                break
            if len(set(last_moves[-10:])) == 1:
                ai_move = self.ai_q_class.choose_Q_action(tuple(ai_state), exploration_rate=0.5)
                print("detected loop")
            else:
                ai_move = self.ai_q_class.choose_Q_action(tuple(ai_state), exploration_rate=0)
            last_moves.append(ai_move)
            self.perform_move(ai_move)
            solve_moves += ai_move + ' '



    def get_ai_state(self):
        """
        return the current puzzle state for the ai based on self.ai_color_list
        """
        ai_state = []

        for color in [obj.color for obj in self.vpy_objects]:
            for i, index_color in enumerate(self.ai_color_list):
                if index_color == color:
                    ai_state.append(i)

        return ai_state


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