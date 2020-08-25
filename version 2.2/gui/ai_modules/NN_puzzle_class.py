import os
import random
import pickle
import numpy as np
import keras
from keras import layers

class puzzle_NN():
    def __init__(self, ACTIONS_DICT, SOLVED_STATE, name=None):
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

        self.ACTION_INDEX_DICT = {action:i for i, action in enumerate(list(self.ACTIONS_DICT.keys()))}

        try:
            self.Q_table = dict()
            self.import_q_table()
        except FileNotFoundError:
            print("cannot train without Q-table")


    def prepare_data(self):
        """
        prepare the data given in a Q-table for passing it to the neural network

        returns:
        --------
            (np.ndarray) - input data (state-action vectors)
            (np.ndarray) - ouput data (target Q-values)
        """
        inputs = []
        outputs = []
        for state_action, value in self.Q_table.items() :
            state, action = state_action

            inputs.append( state + self.action_to_vector(action) )
            outputs.append( value )

        return np.array(inputs), np.array(outputs)


    def action_to_vector(self, action):
        """
        converts an action key into the action vector that is passed to the neural network:
            each action is assigned an index.

        inputs:
        -------
            action - (str) - the key of an action in self.ACTIONS_DICT

        returns:
        --------
            (list) of ints - every entry is 0 except for that with the index assigned to the given action. That entry is 1
        """
        action_vector = [0 for _ in self.ACTIONS_DICT.keys()]
        action_vector[self.ACTION_INDEX_DICT[action]] = 1 # write 1 to the correct index in the vector
        return action_vector


    def initialize_nn(self):
        """
        initialize the network:
            inputs - current state of the puzzle
            hidden layers - one layer of size 2*(input_size+output_size)
            outputs - scores for all availiable actions

            compiled using optimizer 'adam',
                           loss function 'mean_squared_error'
        """
        input_size = len(self.SOLVED_STATE) + len(self.ACTIONS_DICT)
        output_size = 1
        self.model = keras.Sequential()
        self.model.add(layers.Input(shape=(input_size,)))
        self.model.add(layers.Dense((input_size+output_size)*2))
        self.model.add(layers.Dense(output_size))
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')


    def train_nn(self, epochs=100, batch_size=30):
        self.initialize_nn()
        inputs, outputs = self.prepare_data()
        self.train_history = model.fit(inputs, outputs, epochs=epochs, batch_size=batch_size,
                     use_multiprocessing=True, verbose=1)


    def nn_get_greedy_move(self, state, actions):
        """
        get a move from the neural network
        """
        values = [model.predict([state+self.action_to_vector(action)], use_multiprocessing=True)[0] for action in actions]
        print(values)
        max_value = max(values)
        moves = []
        for move, value in zip(actions, values):
            if value == max_value:
                moves.append(move)

        return random.choice(moves)


    def nn_get_move(self, state, actions, epsilon=0):
        """
        get a move based on an epsilon-greedy strategy with given epsilon
        """
        if random.random() < epsilon:
            return random.choice(actions) # random move
        else:
            return self.nn_get_greedy_move(state, actions) # greedy move


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