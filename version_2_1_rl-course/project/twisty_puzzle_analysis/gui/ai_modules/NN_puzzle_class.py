import keras
from keras import layers

class puzzle_NN():
    def __init__(self, ACTIONS_DICT, SOLVED_STATE, name=None):
        """
        initialize a puzzle for training via q-learning

        inputs:
        -------
            ACTIONS_DICT - (dict) - dictionary containing all possible actions as cycles
                keys are the names of the actions
            SOLVED_STATE - (list) of ints - the solved state. Each integer represents one color
            name - (str) - name of the puzzle
        """
        if not name == None:
            self.name = name
        else:
            self.name = "twisty_puzzle #0"
        self.ACTIONS_DICT = ACTIONS_DICT
        self.SOLVED_STATE = SOLVED_STATE

        try:
            self.Q_table = dict()
            self.import_q_table()
        except FileNotFoundError:
            print("cannot train without Q-table")


    def action_num(action):
        for i, act in enumerate(list(self.ACTIONS_DICT.keys())):
            if action == act :
                return i


    def prepare_data(self):
        training_table = dict()
        output_template = [0 for _ in range(len(self.ACTIONS_DICT))]
        for state_action, value in q_table.items() :
            (state, action) = state_action
            state += tuple(state_for_ai(puzzle.SOLVED_STATE)[0])
            inner = training_table.get(state) or output_template.copy()
            inner[self.action_num(action)] = value
            training_table[state] = inner
        return list(training_table.keys()) , list(training_table.values())


    def import_q_table(self, filename="Q_table.txt"):
        with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename), "r") as file:
            self.Q_table = eval(file.read())


    def initialize_nn (self):
        """
        initialize the network:
            inputs - current state of the puzzle
            hidden layers - 2, each of size (input_size+output_size)/2
            outputs - scores for all availiable actions

            compiled using optimizer 'adam',
                           loss function 'mean_squared_error'
        """
        input_size = len(self.SOLVED_STATE)
        output_size = len(self.ACTIONS_DICT)
        self.model = keras.Sequential()
        self.model.add(layers.Input(shape=(input_size,)))
        self.model.add(layers.Dense((input_size+output_size)/2))
        self.model.add(layers.Dense((input_size+output_size)/2))
        self.model.add(layers.Dense(output_size))
        
        self.model.compile(optimizer='adam', loss='mean_squared_error')

    def train_nn (self, epochs=100, batch_size=30):
        self.train_history = model.fit(samples, labels, epochs=epochs, batch_size=batch_size,
                     use_multiprocessing=True, verbose=False)