"""
this module implements a class for training a neural network for twisty puzzles
    based on V-learning and using Hindsight Experience Replay (HER)
coded using python 3.8.5 and tensorflow 2.3.0
"""
import os
import random
import time
import pickle
from copy import deepcopy
import numpy as np
import tensorflow.keras as keras
from tensorflow.keras.optimizers import Adam
from .twisty_puzzle_model import perform_action, scramble

class Puzzle_NN_V_HER_AI():
    def __init__(self,
                 ACTIONS_DICT,
                 SOLVED_STATE,
                 reward_dict={"solved":1, "timeout":0, "move":-0.01},
                 name=None,
                 learning_rate=0.02,
                 discount_factor=0.95,
                 base_exploration_rate=0.7,
                 keep_nn=True):
        
        if name is None:
            self.name = "twisty_puzzle #0"
        else:
            self.name = name

        self.ACTIONS_DICT = ACTIONS_DICT
        self.SOLVED_STATE = SOLVED_STATE

        self.reward_dict = reward_dict
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.base_exploration_rate = base_exploration_rate

        self.neural_net = None
        if keep_nn:
            try:
                self.load_network()
                print("loaded existing network")
            except:
                pass


    def initialize_nn(self):
        """
        initialize the neural network: S² -> R
            inputs - current state of the puzzle and goal state
            hidden layers:
                - one dense layer of size `len(SOLVED_STATE)`
                - 
            outputs - score of the given state considering the given goal

            optimizer: `adam`
            loss function: `mean_absolute_error`
        """
        input_size = len(self.SOLVED_STATE)*2
        output_size = 1
        self.neural_net = keras.Sequential()
        self.neural_net.add(keras.layers.Input(shape=(input_size,)))
        # self.neural_net.add(keras.layers.Dense(input_size))
        self.neural_net.add(keras.layers.Dense(max(1, input_size), activation="relu"))
        if input_size >= 16:
            self.neural_net.add(keras.layers.Dense(max(1, input_size//4), activation="relu"))
        self.neural_net.add(keras.layers.Dense(output_size))
        
        self.neural_net.compile(optimizer=Adam(learning_rate=0.05), loss='mean_absolute_error')


    def initialize_nn_conv(self):
        """
        initialize convolutional neural network: S² -> R
            inputs - current state of the puzzle and goal state
            hidden layers:
                - one dense layer of size `len(SOLVED_STATE)`
                - 
            outputs - score of the given state considering the given goal

            optimizer: `adam`
            loss function: `mean_squared_error`
        """
        input_size = len(self.SOLVED_STATE)*2
        output_size = 1
        self.neural_net = keras.Sequential()
        self.neural_net.add(keras.layers.Input(shape=(input_size,)))
        self.neural_net.add(keras.layers.Conv1D(input_size//8, input_size//2, activation="relu"))
        self.neural_net.add(keras.layers.Dense(max(1, input_size//8), activation="relu"))
        if input_size >= 16:
            self.neural_net.add(keras.layers.Dense(max(1, input_size//8), activation="relu"))
        self.neural_net.add(keras.layers.Dense(1))
        
        self.neural_net.compile(optimizer=Adam(lr=0.1), loss='mean_squared_error')


    def train_nn_her(self,
            num_episodes=1000,
            max_moves=50,
            reward_dict=None,
            learning_rate=None,
            discount_factor=None,
            base_exploration_rate=None,
            k_for_her=5,
            keep_nn=True):
        """
        train a neural network S² -> R
        the network learns to evaluate states of the puzzle through V-learning and HER.


        """
        self.update_settings(
                reward_dict=reward_dict,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                base_exploration_rate=base_exploration_rate,
                keep_nn=keep_nn)
        self.neural_net.summary()
        param_history = {
            "scramble_moves_increased":[0], # previously called `increased_difficulties`
            "exploration_rates":list(), # previously called `explo_rates`
            "x_values":list(),
            "solved_hist":list() # track which episodes reached the goal
            }
        x_start = 0.2
        x = x_start
        x_stepsize = 0.2
        # ai needs to successfully solve `n_tests` episodes in a row before the difficulty is increased
        n_tests = 30
        episodes_since_fail = 0
        n_scramble_moves = 1
        exploration_rate = base_exploration_rate
        start_time = time.time()
        for n in range(num_episodes):
            # consider increasing the difficulty
            new_n_scramble_moves = self.get_new_scramble_moves(n_scramble_moves, episodes_since_fail, n_tests)
            if new_n_scramble_moves != n_scramble_moves: # n_scramble_moves increased
                param_history["scramble_moves_increased"].append(n)
                x = x_start
                exploration_rate = base_exploration_rate
            n_scramble_moves = new_n_scramble_moves
            # generate starting state by scrambling the solved state
            start_state = deepcopy(self.SOLVED_STATE)
            scramble(start_state, self.ACTIONS_DICT, n_scramble_moves)
            # play episode with new start_state
            n_moves, is_solved = self.play_episode(start_state, max_moves, exploration_rate, k_for_her)
            # update parameter tracking
            param_history["solved_hist"].append(is_solved)
            param_history["exploration_rates"].append(exploration_rate)
            param_history["x_values"].append(x)
            # update exlporation rate based on the result of the last episode
            if is_solved:
                episodes_since_fail += 1
                x -= x_stepsize * (exploration_rate)
            else:
                episodes_since_fail = 0
                x += x_stepsize * (base_exploration_rate - exploration_rate)
            exploration_rate = base_exploration_rate * sigmoid(x)

            # print info
            print(f"finished episode {n+1} after {round(time.time() - start_time,0)} s ; difficulty = {n_scramble_moves}")
        print(f"completed training after {round(time.time() - start_time,0)}s")
        print("final exploration rate:", exploration_rate)
        print("final scramble moves:", n_scramble_moves)
        self.save_network()
        print("saved network")
        training_info = {
                "num_episodes":n, # save the number of played episodes
                "max_moves":max_moves,
                "final_scramble_moves":n_scramble_moves,
                "learning_rate":self.learning_rate,
                "discount_factor":self.discount_factor,
                "base_exploration_rate":self.base_exploration_rate,
                "reward_dict":self.reward_dict,
                "keep_nn":keep_nn,
                "k_for_her":k_for_her}
        self.export_param_hist(merge_dicts(param_history, training_info))
        print("saved training info")


    def get_new_scramble_moves(self, n_scramble_moves, episodes_since_fail, n_tests):
        """
        generate a new number of scramble moves based on the current number of scramble moves and how often the puzzle was successfully solved in the past.

        inputs:
        -------
            n_scramble_moves
            solved_hist
        """
        if episodes_since_fail >= n_tests:
            return n_scramble_moves + 1
        else:
            return n_scramble_moves


    def play_episode(self,
            start_state,
            max_moves=500,
            exploration_rate=0,
            k_for_her=5):
        """
        play one episode (try solving the given `start_state` of a twisty puzzle). actions during play are chosen based on an epsilon-greedy strategy using the given `exploration_rate` and the current neural network S²->R for state evaluation.

        after playing the episode, extra training data is generated from the episdoe to use for Hindsight Experience Replay (HER).

        network is updated using the experience from this episode

        self.SOLVED_STATE is used as the default goal state.

        inputs:
        -------
            start_state - (list) of (int) - scrambled state of a puzzle
            max_moves - (int) - maximum number of moves allowed for solving the puzzle. 
            exploration_rate - (float) in [0,1] - chance of choosing a random action
            k_for_her - (int) - number of extra experiences generated using HER.
                Set `k_for_her=0` to disable HER.

        returns:
        --------
            (int) - number of actions performed this episode
            (bool) - whether or not the puzzle was solved successfully
        """
        # TODO: play episode, implement HER
        state_history = list()
        for move_number in range(1, max_moves+1):
            state_history.append(tuple(start_state))
            if start_state == self.SOLVED_STATE:
                # print("solved", n_moves)
                break
            # choose an action using epsilon-greedy strategy
            action = self.choose_nn_move(
                    state=start_state,
                    goal=self.SOLVED_STATE,
                    action_keys=list(self.ACTIONS_DICT.keys()),
                    epsilon=exploration_rate)
            # lower exploration rate during episode -> exploration mostly in the beginning
            exploration_rate = exploration_rate**move_number
            # apply action to current state
            perform_action(start_state, self.ACTIONS_DICT[action]) # `start_state` is changed in-place
        else: # add last state if 
            state_history.append(tuple(start_state))

        self.update_network_her(
                state_history,
                move_number=move_number,
                max_moves=max_moves,
                k_for_her=k_for_her)

        return move_number, start_state==self.SOLVED_STATE


    def update_settings(self,
            reward_dict=None,
            learning_rate=None,
            discount_factor=None,
            base_exploration_rate=None,
            keep_nn=True):
        """
        update important class variables before training

        inputs:
        -------
            learning_rate - (float) in range [0,1] - alpha
            discount_factor - (float) in range [0,1] - gamma
            base_exploration_rate - (float) - the starting exploration rate
            reward_dict - (dict) - dict containing rewards for certain events must have keys:
                - "solved" - reward for solving the puzzle
                - "timeout" - reward/penalty for not solving the puzzle within max_steps
                - "move" - reward/penalty for each move
            keep_nn - (bool) - whether or not to keep the existing neural network or retrain the AI from scratch
        """
        if reward_dict != None:
            self.reward_dict = reward_dict
        if learning_rate != None:
            self.learning_rate = learning_rate
        if discount_factor != None:
            self.discount_factor = discount_factor
        if base_exploration_rate != None:
            self.base_exploration_rate = base_exploration_rate

        if self.neural_net is None or not keep_nn: # V_table doesn't yet exist or is to be overwritten
            self.initialize_nn()


    def choose_nn_move(self, state, goal, action_keys, epsilon=0):
        """
        get a move based on an epsilon-greedy strategy with given epsilon

        inputs:
        -------
            state - (list) of (int) - state represented as list of integers
            goal - (list) of (int) - goal state represented as list of integers
            action_keys - (list) of (str) - list of all currently possible action keys.
            epsilon - (float) in [0,1] - probability of choosing a random move
        """
        if random.random() < epsilon:
            return random.choice(action_keys) # random move
        else:
            return self.get_greedy_move(state, goal, action_keys) # greedy move


    def get_greedy_move(self, state, goal, action_keys):
        """
        get a move from the neural network: S² -> R

        inputs:
        -------
            state - (list) of (int) - state represented as list of integers
            goal - (list) of (int) - goal state represented as list of integers
            action_keys - (list) of (str) - list of all currently possible action keys.

        returns:
        --------
            (str) - action_key of an optimal action according to the current network
        """
        next_nn_states = list()
        for action_key in action_keys:
            action = self.ACTIONS_DICT[action_key]
            next_state = state[:] # copy of state
            perform_action(next_state, action)
            next_nn_states.append(next_state + goal) # concat next_state with goal
            
        values = self.neural_net.predict(next_nn_states, use_multiprocessing=True) # calculate predictions for all next states
        # print(values)
        # choose a random action with maximum value
        max_value = max(values)
        best_moves = list()
        for move, value in zip(action_keys, values):
            if value == max_value:
                best_moves.append(move)

        return random.choice(best_moves)


    def update_network_her(self,
            state_history,
            move_number,
            max_moves=50,
            k_for_her=5):
        """
        generate new experiences using HER and train self.neural_net based on all experiences from this episode.
        """
        solved_state_tuple = tuple(self.SOLVED_STATE)
        next_state = None
        next_rewards = np.array([0])
        for t, state in enumerate(reversed(state_history)):
            inputs = [np.array(state + solved_state_tuple)]
            if t > 0:
                next_inputs = [np.array(next_state + solved_state_tuple)]
            for k in range(min(t, k_for_her)):
                new_goal = random.choice(state_history[move_number-t-1:])
                inputs.append( np.array(state + new_goal) )
                if t > 0:
                    next_inputs.append( np.array(next_state + new_goal) )
            if t > 0:
                next_inputs = np.array(next_inputs)
                next_rewards = self.neural_net.predict(next_inputs, use_multiprocessing=True)
            inputs = np.array(inputs)
            # calculate expected values of current inputs
            rewards = self.get_rewards(inputs, move_number, max_moves)
            # calculate old target values
            old_targets = self.neural_net.predict(inputs, use_multiprocessing=True)
            # calculate new target values using bellman-equation
            new_targets = old_targets + self.learning_rate* \
                (rewards + self.discount_factor*next_rewards - old_targets)
            # train neural network with new inputs and targets
            self.neural_net.fit(inputs, new_targets, use_multiprocessing=True, verbose=0)
            # update variables for next
            next_state = state
            move_number -= 1


    def get_rewards(self, nn_inputs, move_number, max_moves):
        """
        calculate the rewards for a list of inputs of the neural network
        rewards are based on self.reward_dict:
            - reward_dict["solved"] if state == goal
            - reward_dict["timeout"] if move_number >= max_moves
            - reward_dict["move"] otherwise

        inputs:
        -------
            nn_inputs - (list) of (np.array) of (int) - list of numpy arrays consisting of state and goal as inputs for `self.neural_net`
            move_number - (int) - number of moves in the episode
            max_moves - (int) - number of moves allowed per episode before timeout

        returns:
        --------
            (np.array) of (float) - array of the rewards corresponding to the given inputs
        """
        n = len(self.SOLVED_STATE)
        rewards = np.zeros(len(nn_inputs))
        for i, nn_input in enumerate(nn_inputs):
            state, goal = nn_input[:n], nn_input[n:]
            if np.array_equal(state, goal):
                reward = self.reward_dict["solved"]
            elif move_number >= max_moves:
                reward = self.reward_dict["timeout"]
            else:
                reward = self.reward_dict["move"]
            rewards[i] = reward
        return rewards

    def save_network(self, filename="her_neural_network"):
        """
        save the neural network `self.neural_net` to puzzle folder: 
            "puzzles/`self.name`/`filename`"
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
        self.neural_net.save(filepath)


    def load_network(self, filename="her_neural_network"):
        """
        load neural network from "puzzles/`self.name`/`filename`"
        network will be saved as `self.neural_net`
        """
        filepath = os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename)
        self.neural_net = keras.models.load_model(filepath)


    def export_param_hist(self, training_data, filename=None):
        """
        save 
        """
        puzzlespath = os.path.join(os.path.dirname(__file__), "..", "puzzles")
        try: # create a "puzzles" folder if it doesn't exist yet
            os.mkdir(puzzlespath)
        except FileExistsError:
            pass
        try: # create a folder for the given puzzle if it doesn't exist yet
            os.mkdir(os.path.join(puzzlespath, self.name))
        except FileExistsError:
            pass
        if filename is None:
            filename = f'nn_param_hist_{time.strftime("%Y%m%d_%H%M%S")}'
        with open(os.path.join(puzzlespath, self.name, filename), "wb") as file:
            pickle.dump(training_data, file, protocol=4)




def sigmoid(x):
    """
    the sigmoid function 
    """
    return 1/(1+2.718281828**(-x))

def merge_dicts(dict_1, dict_2):
    """
    add all entries of dict_2 to dict_1.
    keys that already exist will be overwritten.
    """
    for key, val in dict_2.items():
        dict_1[key] = val
    return dict_1