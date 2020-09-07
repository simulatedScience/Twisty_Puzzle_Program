"""
this module implements a class for training a neural network for twisty puzzles
requires python 3.6 or newer
"""

import os
import random
import pickle
from copy import deepcopy
import itertools
import numpy as np
import tensorflow.keras as keras
from tensorflow.keras import layers
from .twisty_puzzle_model import perform_action

class Puzzle_Network():
    def __init__(self, ACTIONS_DICT, SOLVED_STATE, name=None, Q_table=None):
        """
        initialize class object for neural network training

        inputs:
        -------
            ACTIONS_DICT - (dict) - dictionary containing all possible moves as lists of cycles
                keys are the names of the moves
            SOLVED_STATE - (list) of ints - the solved state. Each integer represents one color
            name - (str) - name of the puzzle
        """
        if not name == None:
            self.name = name
        else:
            self.name = "twisty_puzzle #0"
        self.ACTIONS_DICT = ACTIONS_DICT
        self.SOLVED_STATE = SOLVED_STATE

        self.gen_action_vector_dict()
        self.gen_color_vector_dict()

        self.old_Q_table = True #whether or not the Q-table has been changed to store states for the NN inst
        if Q_table == None:
            try:
                self.Q_table = dict()
                self.import_q_table()
            except FileNotFoundError:
                print("cannot train without Q-table")
        else:
            self.Q_table = Q_table
        try:
            self.load_network()
            print("loaded existing network")
        except:
            pass


    def gen_action_vector_dict(self):
        """
        generate a dictionary that maps every action to it's one-hot list for the NN state
        """
        self.ACTION_VECTOR_DICT = dict()
        vec_len = len(self.ACTIONS_DICT)
        for i,action in enumerate(list(self.ACTIONS_DICT.keys())):
            self.ACTION_VECTOR_DICT[action] = [0]*i + [1] + [0]*(vec_len-i-1)


    def gen_color_vector_dict(self):
        """
        generarte a dictionary that maps every color to it's one-hot list for the NN state
        """
        self.COLOR_VECTOR_DICT = dict()
        vec_len = len(set(self.SOLVED_STATE))
        for i in range(vec_len):
            self.COLOR_VECTOR_DICT[i] = [0]*i + [1] + [0]*(vec_len-i-1)


    def prepare_data(self, additional_data=0.01):
        """
        prepare the data given in a Q-table for passing it to the neural network

        inputs:
        -------
            additional_data - (float) >=0 - percentage of additional data generated from inverse scrambles

        # returns: None
        # --------
        #     (np.ndarray) - input data (state-action vectors)
        #     (np.ndarray) - ouput data (target Q-values)
        """
        print(f"generating {100*additional_data:2.2}\% additional data points")
        if additional_data > 0:
            self.gen_inverse_scramble(additional_data=additional_data)
        dict_length = len(self.Q_table)
        print_i = dict_length//10
        for i, state_action in enumerate(self.Q_table.keys()):
            if i % print_i== 0:
                print(f"converted {i//dict_length*100}% of the data")
            if i == dict_length:
                break
            state, action = state_action
            self.Q_table[tuple(self.prepare_state(state) + self.ACTION_VECTOR_DICT[action])] = self.Q_table.pop(state_action)

        # return np.array(inputs), np.array(outputs)


    def prepare_state(self, state):
        """
        expand the state by replacing every color with a one-hot list representing the color

        inputs:
        -------
            state - (list) or (tuple) - state as list or tuple of color indices starting at 0

        returns:
        --------
            (list) of 0s and 1s - new state for the neural network input
        """
        return list(itertools.chain.from_iterable([self.COLOR_VECTOR_DICT[color] for color in state]))

    
    def gen_inverse_scramble(self, additional_data=0.01, max_moves=30, learning_rate=0.05, discount_factor=0.99):
        """
        add data to the Q-table based on inversed scambles
        inputs:
        -------
            additional_data - (float) >=0 - percentage of additional data generated from inverse scrambles
            max_moves - (int) - maximum number of moves to scramble
            learning_rate - (float) in [0,1] - Q-table values are adjusted by += learning_rate*discount_factor**n
            discount_factor - (float) in [0,1] - Q-table values are adjusted by += learning_rate*discount_factor**n
        """
        action_keys = list(self.ACTIONS_DICT.keys())
        if not hasattr(self, "INVERSE_ACTIONS"):
            self.gen_inverse_action_dict()
        for _ in range(int(len(self.Q_table)*additional_data)):
            state = deepcopy(self.SOLVED_STATE)
            for n in range(max_moves):
                action = random.choice(action_keys)
                perform_action(state, self.ACTIONS_DICT[action])
                try:
                    self.Q_table[(tuple(state), self.INVERSE_ACTIONS[action])] += learning_rate*discount_factor**n
                except KeyError:
                    self.Q_table[(tuple(state), self.INVERSE_ACTIONS[action])] = learning_rate*discount_factor**n


    def gen_inverse_action_dict(self):
        """
        generates a dictionary that maps every action to it'S inverse
        """
        self.INVERSE_ACTIONS = {action:self.get_inverse_action(action) for action in self.ACTIONS_DICT.keys()}


    def get_inverse_action(self, action_key):
        """
        inputs:
        -------
            action_key - (str) - an action given by its name that is either its own inverse,
                includes a ' at the end or it's inverse is given by action_key+"'"
        """
        if action_key[-1] == "'":
            return action_key[:-1]
        rev_action = action_key+"'"
        if rev_action in self.ACTIONS_DICT:
            return rev_action
        return action_key #if no inverse action exists, assume the action is its own inverse


    def initialize_nn(self):
        """
        initialize the network:
            inputs - current state of the puzzle
            hidden layers - one layer of size 2*(input_size+output_size)
            outputs - scores for all availiable actions

            compiled using optimizer 'adam',
                           loss function 'mean_squared_error'
        """
        input_size = len(self.COLOR_VECTOR_DICT)*len(self.SOLVED_STATE) + len(self.ACTIONS_DICT)
        output_size = 1
        self.model = keras.Sequential()
        self.model.add(layers.Input(shape=(input_size,)))
        self.model.add(layers.Dense((input_size+output_size)*2))
        self.model.add(layers.Dense(output_size))
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')


    def train_nn(self, epochs=1000, batch_size=30, additional_data=0.01):
        """
        inputs:
        -------
            epochs - (int) - number of training epochs for the network
            batch_size - (int) - number of training
            additional_data - (float) >=0 - percentage of additional data generated from inverse scrambles
        """
        if epochs > 0:
            if self.old_Q_table:
                print("preparing data...")
                self.prepare_data(additional_data=additional_data)
                self.old_Q_table = False
            else:
                print("data unchanged")
            inputs = np.array(list(self.Q_table.keys()))
            outputs = np.array(list(self.Q_table.values()))
            print("begin training")
            self.train_history = self.model.fit(inputs, outputs, epochs=epochs, batch_size=batch_size, use_multiprocessing=True, verbose=2)
            print("end training")
            self.save_network()
            print("saved network")


    def get_greedy_move(self, state, actions):
        """
        get a move from the neural network
        """
        values = [model.predict([self.prepare_state(state)+self.ACTION_VECTOR_DICT[action]], use_multiprocessing=True)[0] for action in actions]
        print(values)
        max_value = max(values)
        moves = []
        for move, value in zip(actions, values):
            if value == max_value:
                moves.append(move)

        return random.choice(moves)


    def choose_nn_move(self, state, actions, epsilon=0):
        """
        get a move based on an epsilon-greedy strategy with given epsilon
        """
        if random.random() < epsilon:
            return random.choice(actions) # random move
        else:
            return self.get_greedy_move(state, actions) # greedy move


    def import_q_table(self, filename="pickle_Q_table"):
        """
        import a Q-table from a file. Try using pickle to load 'pickle_Q_table', otherwise try loading 'Q_table.txt', which should be a sufficiently small dictionary
        """
        try:
            with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename), "rb") as file:
                self.Q_table = pickle.load(file)
        except FileNotFoundError:
            with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, "Q_table.txt"), "r") as file:
                self.Q_table = eval(file.read())


    def save_network(self, filename="neural_network"):
        """
        save the neural network to puzzle folder
        """
        try: # create a "puzzles" folder if it doesn't exist yet
            os.mkdir(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
        except FileExistsError:
            pass
        try: # create a folder for the given puzzle if it doesn't exist yet
            os.mkdir(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name))
        except FileExistsError:
            pass
        filepath = os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename)
        self.model.save(filepath)


    def load_network(self, filename="neural_network"):
        """
        load neural network from file
        """
        filepath = os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename)
        self.model = keras.models.load_model(filepath)
