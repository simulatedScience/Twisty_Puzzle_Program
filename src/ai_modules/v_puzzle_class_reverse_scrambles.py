import os
import time
import random
import pickle
from math import ceil, log10

if __name__ != "__main__":
    from .twisty_puzzle_model import scramble, perform_action
else:
    from twisty_puzzle_model import scramble, perform_action


class Puzzle_V_AI():
    def __init__(self,
                 ACTIONS_DICT,
                 SOLVED_STATE,
                 reward_dict={"solved":10, "timeout":-1, "move":-0.2},
                 name=None,
                 learning_rate=0.02,
                 discount_factor=0.95,
                 base_exploration_rate=0.7,
                 keep_v_table=True):
        """
        initialize a puzzle for training via v-learning (assign a value to each state)

        inputs:
        -------
            ACTIONS_DICT - (dict) - dictionary containing all possible actions as cycles
                keys are the names of the actions
            SOLVED_STATE - (list) of ints - the solved state. Each integer represents one color
            reward_dict - (dict) - dict containing rewards for certain events must have keys:
                - "solved" - reward for solving the puzzle
                - "timeout" - reward/penalty for not solving the puzzle within max_steps
                - "move" - reward/penalty for each move
            name - (str) - name of the puzzle
            learning_rate - (float) in range [0,1] - alpha
            discount_factor - (float) in range [0,1] - gamma
            base_exploration_rate - (float) - the starting exploration rate
        """
        if name is None:
            self.name = "twisty_puzzle #0"
        else:
            self.name = name
        
        self.ACTIONS_DICT = ACTIONS_DICT
        self.ACTION_KEYS = list(self.ACTIONS_DICT.keys())
        self.N_ACTIONS = len(self.ACTION_KEYS)
        self.SOLVED_STATE = SOLVED_STATE

        self.reward_dict = reward_dict
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.base_exploration_rate = base_exploration_rate

        if keep_v_table:
            try:
                self.v_table = dict()
                self.import_v_table()
            except FileNotFoundError:
                self.v_table = None
        else:
            self.v_table = None


    def train_v_learning(self,
            reward_dict=None,
            learning_rate=None,
            discount_factor=None,
            base_exploration_rate=None,
            keep_v_table=True,
            max_moves=500,
            num_episodes=1000):
        """
        try solving the given puzzle [num_episodes] times to learn using V-Learning with the given learning rate and discount_factor.

        training ends prematurely if the number of scramble moves is greater than `max_moves//2`

        use adaptive exploration rate, that decreases if the puzzle is solved correctly and increases otherwise

        inputs:
        -------
            learning_rate - (float) in range [0,1] - alpha
            discount_factor - (float) in range [0,1] - gamma
            base_exploration_rate - (float) - the starting exploration rate
            num_episodes - (int) - number of episodes for training
            reward_dict - (dict) - dict containing rewards for certain events must have keys:
                - "solved" - reward for solving the puzzle
                - "timeout" - reward/penalty for not solving the puzzle within max_steps
                - "move" - reward/penalty for each move
            max_moves - (int) - maximum number of moves played per episode
            keep_v_table - (bool) - whether or not to keep the existing V-table or retrain the AI from scratch

        returns:
        --------
            (list) or tuples - information about the training games:
                tuples include:
                    scramble - list of movenames
                    state_history - list of states in ai-format
                    action_history - list of movenames
        """
        self.update_settings(reward_dict=reward_dict,
                learning_rate=learning_rate,
                discount_factor=discount_factor,
                base_exploration_rate=base_exploration_rate,
                keep_v_table=keep_v_table)

        param_history = {
            "scramble_moves_increased":[0], # previously called `increased_difficulties` = list of episode numbers where number of scramble moves was increased.
            "exploration_rates":[float()]*num_episodes, # previously called `explo_rates` = list of eploration rates in each episode
            "x_values":[float()]*num_episodes, # list of x values used to calculate exploration rates
            "solved_hist":[bool()]*num_episodes # list of bools indicating for each episode whether it was solved or not.
            }

        n_tests = 30
        x_start = 0.2
        x_stepsize = 0.2
        x = x_start
        n_scramble_moves = 1 # previously called `max_scramble_moves`
        exploration_rate = base_exploration_rate
        if num_episodes <= 0:
            print("considered states of the puzzle:", len(self.v_table))
            return param_history
        # progress indicator variables:
        print_interval = min(25_000, num_episodes//4)
        start_time = time.time()
        for k in range(num_episodes//print_interval):
            for n in range(print_interval*k, print_interval*(k+1)):
                if n%20 == 19:
                    new_n_scramble_moves = self.get_new_scramble_moves(n_scramble_moves, param_history["solved_hist"], n, n_tests=n_tests) # previously called `new_max_moves`
                    if new_n_scramble_moves != n_scramble_moves:
                        n_tests += 3 # increase number of successfull solves required to increase difficulty
                        param_history["scramble_moves_increased"].append(n)
                        x = x_start
                        exploration_rate = base_exploration_rate
                        if n_scramble_moves >= max_moves//2: # end training if number of scramble moves gets too big
                            print(f"ended training after {n+1} episodes because the training goal was reached")
                            break
                        n_scramble_moves = new_n_scramble_moves

                # generate a starting state by scrambling the solved state
                start_state = self.SOLVED_STATE[:]
                # scramble puzzle in-place
                scramble(start_state, self.ACTIONS_DICT, max_moves=n_scramble_moves)
                # play episode
                state_hist, action_hist = self.play_episode(
                        start_state,
                        max_moves=max_moves,
                        exploration_rate=exploration_rate)

                # update x and solved_history for future exploration rate
                if state_hist[-1] == tuple(self.SOLVED_STATE):
                    # if puzzle was solved, decrease exploration rate
                    param_history["solved_hist"][n] = True
                    x -= x_stepsize * (exploration_rate)
                else:
                    # if puzzle was not solved, increase exploration rate
                    param_history["solved_hist"][n] = False
                    x += x_stepsize * (base_exploration_rate - exploration_rate)
                exploration_rate = base_exploration_rate * sigmoid(x)# * (0.999**(n-scramble_moves_increased[-1]))

                param_history["exploration_rates"][n] = exploration_rate
                param_history["x_values"][n] = x
            print(f"completed {n+1:{ceil(log10(num_episodes))}} episodes of training after {round(time.time() - start_time,0)} s.\n\
    Explored {len(self.v_table)} state-action pairs.\n\
    Current number of scramble moves: {n_scramble_moves}")

        print(f"completed training after {round(time.time() - start_time,0)} s")
        print("final exploration rate:", exploration_rate)
        print("final scramble moves:", n_scramble_moves)
        print("number of considered states of the puzzle:", len(self.v_table))
        self.export_v_table()
        print("saved v_table")
        training_info = {
                "num_episodes":n, #save the number of played episodes
                "max_moves":max_moves,
                "final_scramble_moves":n_scramble_moves,
                "learning_rate":self.learning_rate,
                "discount_factor":self.discount_factor,
                "base_exploration_rate":self.base_exploration_rate,
                "reward_dict":self.reward_dict,
                "keep_v_table":keep_v_table}
        self.export_param_hist(merge_dicts(param_history, training_info))
        print("saved training info")

        # print(list(self.v_table.values()))

        return param_history


    def update_settings(self,
            reward_dict=None,
            learning_rate=None,
            discount_factor=None,
            base_exploration_rate=None,
            keep_v_table=True):
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
            keep_v_table - (bool) - whether or not to keep the existing V-table or retrain the AI from scratch
        """
        if reward_dict != None:
            self.reward_dict = reward_dict
        if learning_rate != None:
            self.learning_rate = learning_rate
        if discount_factor != None:
            self.discount_factor = discount_factor
        if base_exploration_rate != None:
            self.base_exploration_rate = base_exploration_rate

        if self.v_table == None or not keep_v_table: # V_table doesn't yet exist or is to be overwritten
            self.v_table = dict()    # assign values to every visited state


    def get_new_scramble_moves(self,
            max_scramble_moves,
            solved_hist,
            episode_n,
            n_tests=30):
        """
        function which updates the number of moves for scrambling the puzzle
        """
        if False in solved_hist[episode_n-min(episode_n, n_tests):episode_n]:
            return max_scramble_moves
        else:
            return max_scramble_moves + 1


    def play_episode(self,
            start_state,
            max_moves=500,
            exploration_rate=0):
        """
        self-play an entire episode
        inputs:
        -------
            start_state - (list) - any scrambled state of the puzzle
            max_moves - (int) - maximum number of moves the AI has to solve the puzzle
        returns:
        --------
            (list) - state history
            (list) - action history

        action_dict is changed in-place
        """ 
        # state = deepcopy(start_state)
        state = start_state
        action_history = list()
        state_history = list()
        n_moves = 0
        while n_moves <= max_moves:
            state_tuple = tuple(state)
            state_history.append(state_tuple)

            if self.puzzle_solved(state, n_moves, max_moves=max_moves) == "solved":
                # print("solved", n_moves)
                break
            #choose next action based on an epsilon-greedy strategy with epsilon=exploration_rate
            action = self.choose_v_action(state, exploration_rate=exploration_rate**(n_moves+1))
            action_history.append(action)

            # if len(state_history) > 1:
            #     # we know the state that resulted from the last action
            #     self.update_v_table(state_history,
            #                    n_moves=n_moves,
            #                    max_moves=max_moves)


            perform_action(state, self.ACTIONS_DICT[action])
            n_moves += 1
        
        self.update_v_table(state_history,
                        n_moves=n_moves,
                        max_moves=max_moves)

        return state_history, action_history


    def update_v_table(self,
                       state_history,
                       n_moves=0,
                       max_moves=500):
        """
        update the last state in the V-table
        returns:
            None
        """
        updated_states = set()
        next_reward = 0
        # print("init reward:", self.get_reward(next_state, n_moves, max_moves=max_moves))
        # print("init reward:", self.puzzle_solved(next_state, n_moves, max_moves=max_moves))
        for state in reversed(state_history):
            if state in updated_states: # only update states according to the last visit.
                continue
            updated_states.add(state)
            state_list = list(state)
            # intitialize V-value
            if not state in self.v_table:
                self.v_table[state] = 0
            # update V-value
            step_reward = self.get_reward(state_list, n_moves, max_moves)
            # change = self.learning_rate * \
            #     (step_reward + self.discount_factor * next_reward - old_reward)
            # print("dv =", change)
            # self.v_table[state] += change
            self.v_table[state] += self.learning_rate * \
                (step_reward + self.discount_factor * next_reward - self.v_table[state])
            next_reward = self.v_table[state]
            n_moves -= 1
            # for action in self.ACTIONS_DICT.values():
            #     next_state = deepcopy(state)
            #     perform_action(next_state, action)
            #     if next_state in self.v_table:
            #         next_rewards.append(self.v_table[next_state])
            #     else:
            #         # next_rewards.append(0)
            #         next_rewards.append(sigmoid(-(state-end_pos).mag()))
        ### old q-update, slighly tweaked but still wrong ###
        # prev_state = state_history[-2] # S = state
        # prev_action = action_history[-2] # A = action
        # state = state_history[-1] # S' = next state after action A

        # reward = self.get_reward(list(state), n_moves, max_moves=max_moves) # R = Reward
        # next_rewards = list() # V(S') for all actions a'
        # for action in self.ACTIONS_DICT:
        #     try:
        #         next_rewards.append(self.v_table[state])
        #     except KeyError:
        #         # initialize V-values
        #         self.v_table[state] = 0
        #         next_rewards.append(0)

        # if not action in self.v_table.keys():
        #     self.v_table[prev_state] = 0
        # # actually update the V-value of the considered move
        # # V(S) += alpha*(R + gamma * max(S') - V(S))
        # self.v_table[prev_state] += self.learning_rate*(reward + self.discount_factor * max(next_rewards, default=0) - self.v_table[prev_state])
        # # self.N_table[(prev_state, prev_action)] += 1


    def get_reward(self,
                state,
                n_moves,
                max_moves=500):
        """
        return the reward for the given state and possible actions
        inputs:
        -------
            state - (tuple) or (list) - the state as a tuple or list
            n_moves - (int) - current number of moves performed
            max_moves - (int) - maximum allowed number of moves before timeout
        """
        puzzle_state = self.puzzle_solved(state,
                                    n_moves,
                                    max_moves=max_moves)
        if puzzle_state == "solved": #draw
            # print("solved reward")
            reward = self.reward_dict["solved"]
        elif puzzle_state == "timeout":
            # print("timeout")
            reward = self.reward_dict["timeout"]
        else:
            reward = self.reward_dict["move"]
        return reward


    def puzzle_solved(self,
                      state,
                      n_moves,
                      max_moves=500):
        """
        determine the current puzzle state:
        returns:
        --------
            (str) - 'solved' if the puzzle is solved according to SOLVED_STATE
                    'timeout' if n_moves >= max_moves
        """
        if state == self.SOLVED_STATE:
            return "solved"
        elif n_moves >= max_moves:
            return "timeout"


    def choose_v_action(self, state, exploration_rate=0):
        """
        choose an action based on the possible actions, the current V-table and the current exploration rate

        the V-table must be saved as self.v_table

        inputs:
        -------
            state - (tuple) - the state as a tuple
            exploration_rate - (float) in [0,1] - probability of choosing exploration rather than exploitation
        """
        if random.random() < exploration_rate:
            # explore environment through random move
            return random.choice(self.ACTION_KEYS)

        # exploit knowledge
        # action_values = list()
        best_actions = [str()]*self.N_ACTIONS
        max_value = -float("inf")
        best_action_len = 0
        for action_key, action in self.ACTIONS_DICT.items():
            next_state = state[:] # state is a (list) of (int) -> state[:] creates a deepcopy
            perform_action(next_state, action)
            state_tuple = tuple(next_state)
            try:
                state_value = self.v_table[state_tuple]
                if state_value > max_value:
                    max_value = state_value
                    best_actions[0] = action_key
                    best_action_len = 1
                elif state_value == max_value:
                    best_actions[best_action_len] = action_key
                    best_action_len += 1
            except KeyError:
                if 0 > max_value:
                    self.v_table[state_tuple] = 0
                    max_value = 0
                    best_actions[0] = action_key
                    best_action_len = 1
                # action_values.append(0) # initialize all values as 0
        # choose a random action with maximum value
        # max_value = np.amax(action_values)
        # best_actions = list()
        # for action_key, value in zip(self.ACTIONS_DICT.keys(), action_values):
        #     if value == max_value:
        #         best_actions.append(action_key)
        # return random action with maximum expected reward
        return random.choice(best_actions[:best_action_len])


    def export_v_table(self, filename="pickle_v_table"):
        """
        write the given V-table into a file using pickle
        """
        try: # create a "puzzles" folder if it doesn't exist yet
            os.mkdir(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
        except FileExistsError:
            pass
        try: # create a folder for the given puzzle if it doesn't exist yet
            os.mkdir(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name))
        except FileExistsError:
            pass
        with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename), "wb") as file:
            pickle.dump(self.v_table, file, protocol=4)


    def import_v_table(self, filename="pickle_V_table"):
        """
        import a V-table from a file. Try using pickle to load 'pickle_V_table'
        """
        path = os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename)
        try:
            with open(path, "rb") as file:
                self.v_table = pickle.load(file)
        except FileNotFoundError:
            return f'File "{filename}" not found at {path}'

    def export_param_hist(self, training_data, filename=None):
        """
        save information about the training process and settings used in a file using pickle. The filename will be 'v_param_hist_{save time}'.
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
            filename = f'v_param_hist_{time.strftime("%Y%m%d_%H%M%S")}'
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

# if __name__ == "__main__":
#     print()