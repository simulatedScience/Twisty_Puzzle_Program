import random
import os
from math import ceil
from copy import deepcopy
from .twisty_puzzle_model import scramble, perform_action

class puzzle_ai():
    def __init__(self, 
                 ACTIONS_DICT,
                 SOLVED_STATE,
                 reward_dict={"solved":10, "timeout":-1, "move":-0.2},
                 name="twisty_puzzle #0",
                 learning_rate=0.02,
                 discount_factor=0.95,
                 base_exploration_rate=0.7,
                 keep_Q_table=True):
        """
        initialize a puzzle for training via q-learning

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
        if not name == None:
            self.name = name
        else:
            self.name = "twisty_puzzle #0"
        self.ACTIONS_DICT = ACTIONS_DICT
        self.SOLVED_STATE = SOLVED_STATE

        self.reward_dict = reward_dict
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.base_exploration_rate = base_exploration_rate
        # self.N_table = None

        if keep_Q_table:
            try:
                self.Q_table = dict()
                self.import_q_table()
            except FileNotFoundError:
                self.Q_table = None
        else:
            self.Q_table = None


    def train_q_learning(self, reward_dict=None, learning_rate=None, discount_factor=None, base_exploration_rate=None, keep_Q_table=True, max_moves=500, num_episodes=1000):
        """
        play Tic Tac Toe [num_episodes] times to learn using Q-Learning with the given learning rate and discount_factor.

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
            keep_Q_table - (bool) - whether or not to keep the existing Q-table or retrain the AI from scratch

        returns:
        --------
            (list) or tuples - information about the training games:
                tuples include:
                    scramble - list of movenames
                    state_history - list of states in ai-format
                    action_history - list of movenames
        """
        self.update_settings(reward_dict=reward_dict, learning_rate=learning_rate, discount_factor=discount_factor, base_exploration_rate=base_exploration_rate, keep_Q_table=keep_Q_table)

        games = []
        scramble_hist = []
        solved_hist = []
        increased_difficulties = [0]
        explo_rates = []
        n_tests = 30
        start_x = 0.2
        x = start_x
        max_scramble_moves = 1
        exploration_rate = base_exploration_rate
        for n in range(num_episodes):
            if n%20 == 19:
                new_max_moves = self.get_new_scramble_moves(max_scramble_moves, solved_hist, n_tests=n_tests)
                if not new_max_moves == max_scramble_moves:
                    n_tests += 1
                    increased_difficulties.append(n)
                    x = start_x
                    exploration_rate = base_exploration_rate
                max_scramble_moves = new_max_moves

            # generate a starting state
            start_state = deepcopy(self.SOLVED_STATE)
            scramble_hist.append(scramble(start_state, self.ACTIONS_DICT, max_moves=max_scramble_moves))
            # play episode
            state_hist, action_hist = self.play_episode(start_state, max_moves=max_moves, exploration_rate=exploration_rate)

            if state_hist[-1] == tuple(self.SOLVED_STATE):
                solved_hist.append(True)
                x -= 0.2 * (exploration_rate)
            else:
                solved_hist.append(False)
                x += 0.2 * (base_exploration_rate - exploration_rate)
            exploration_rate = base_exploration_rate * self.sigmoid(x)# * (0.999**(n-increased_difficulties[-1]))

            # save results and prepare for next episode
            games.append((scramble_hist[-1], state_hist, action_hist))
            # exploration_rate = self.get_new_exploration_rate(exploration_rate, n, num_episodes)
            explo_rates.append(exploration_rate)

        print("final exploration rate:", exploration_rate)
        print("final scramble moves:", max_scramble_moves)
        print(f"considered states of the puzzle:", len(self.Q_table))
        if len(self.Q_table) > 0:
            self.export_Q_table()
        print("saved Q_table")

        return games, solved_hist, increased_difficulties, explo_rates


    def sigmoid(self, x):
        """
        the sigmoid function 
        """
        return 1/(1+2.718281828**(-x))


    def update_settings(self, reward_dict=None, learning_rate=None, discount_factor=None, base_exploration_rate=None, keep_Q_table=True):
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
            keep_Q_table - (bool) - whether or not to keep the existing Q-table or retrain the AI from scratch
        """
        if reward_dict != None:
            self.reward_dict = reward_dict
        if learning_rate != None:
            self.learning_rate = learning_rate
        if discount_factor != None:
            self.discount_factor = discount_factor
        if base_exploration_rate != None:
            self.base_exploration_rate = base_exploration_rate

        if self.Q_table == None or not keep_Q_table: # Q_table doesn't exist yet or shall be overwritten
            self.Q_table = dict()    # assign values to every visited state-action pair
        # if self.N_table == None or not keep_Q_table: # N_table doesn't exist yet or shall be overwritten
        #     self.N_table = dict()    # counting how often each state-action pair was visited


    def get_new_exploration_rate(self,exploration_rate, n, num_episodes):
        """
        function which updates the exploration rate
        """
        return exploration_rate - self.base_exploration_rate/(2*num_episodes)


    def get_new_scramble_moves(self, max_scramble_moves, solved_hist, n_tests=30):
        """
        function which updates the number of moves for scrambling the puzzle
        """
        if False in solved_hist[-min(len(solved_hist), n_tests):]:
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
        state = start_state
        sign = 1
        action_history = []
        state_history = []
        n_moves = 0
        while n_moves <= max_moves:
            state_tuple = tuple(state)
            state_history.append(state_tuple)

            #choose next action based on an epsilon-greedy strategy with epsilon=exploration_rate
            action = self.choose_Q_action(state_tuple, exploration_rate=exploration_rate**(n_moves+1))
            action_history.append(action)

            if len(state_history) > 1:
                # we know the state that resulted from the last action
                self.update_q_table(state_history,
                               action_history,
                               n_moves=n_moves,
                               max_moves=max_moves)

            if self.puzzle_solved(state, n_moves, max_moves=max_moves) == "solved":
                break

            perform_action(state, self.ACTIONS_DICT[action])
            n_moves += 1
            # print(n_moves, max_moves)
        # if puzzle_solved(state, self.SOLVED_STATE, n_moves, max_moves=max_moves) == "solved":
        #     print("won", n_moves)
        # else:
        #     print("lost", n_moves)
        return state_history, action_history


    def update_q_table(self,
                       state_history,
                       action_history,
                       n_moves=0,
                       max_moves=500):
        """
        update the last state in the Q-table
        returns:
            None
        """
        prev_state = state_history[-2] # S = state
        prev_action = action_history[-2] # A = action
        state = state_history[-1] # S' = next state after action A

        reward = self.get_reward(list(state), n_moves, max_moves=max_moves) # R = Reward
        next_rewards = [] # Q(S', a') for all actions a'
        for action in self.ACTIONS_DICT:
            try:
                next_rewards.append(self.Q_table[(state, action)])
            except KeyError:
                # initialize Q-values
                self.Q_table[(state, action)] = 0
                # self.N_table[(state, action)] = 0
                next_rewards.append(0)

        if not action in self.Q_table.keys():
            self.Q_table[(prev_state, prev_action)] = 0
            # self.N_table[(prev_state, prev_action)] = 0
        # actually update the q-value of the considered move
        # Q(S,A) += alpha*(R + gamma * max(S', a') - Q(S,A))
        self.Q_table[(prev_state, prev_action)] += self.learning_rate*(reward + self.discount_factor * max(next_rewards, default=0) - self.Q_table[(prev_state, prev_action)])
        # self.N_table[(prev_state, prev_action)] += 1


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
            # print("won")
            reward = self.reward_dict["solved"]
        elif puzzle_state == "timeout":
            print("timeout")
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
                    'timeout' if n_moves > max_moves
        """
        if state == self.SOLVED_STATE:
            return "solved"
        elif n_moves > max_moves:
            return "timeout"


    def choose_Q_action(self, state, exploration_rate=0):
        """
        choose an action based on the possible actions, the current Q-table and the current exploration rate
        inputs:
        -------
            state - (tuple) - the state as a tuple
            Q_table - (dict) - dictionary storing all known Q-values
            exploration_rate - (float) in [0,1] - probability of choosing exploration rather than exploitation
        """
        r = random.random()
        if r > exploration_rate:
            # exploit knowledge
            action_values = []
            for action_key in self.ACTIONS_DICT.keys():
                try:
                    action_values.append(self.Q_table[(state,action_key)])
                except KeyError:
                    action_values.append(0)
            max_value = max(action_values)
            best_actions = []
            for action_key, value in zip(self.ACTIONS_DICT, action_values):
                if value == max_value:
                    best_actions.append(action_key)
            # return random action with maximum expected reward
            return random.choice(best_actions)
        # explore environment through random move
        return random.choice(list(self.ACTIONS_DICT.keys()))


    def export_Q_table(self, filename="Q_table.txt"):
        """
        write the given Q-table into a file
        """
        with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename), "w") as file:
            file.write("{\n")
            for key, value in self.Q_table.items():
                file.write(str(key) + ":" + str(value) + ",\n")
            file.write("}")


    def import_q_table(self, filename="Q_table.txt"):
        with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", self.name, filename), "r") as file:
            self.Q_table = eval(file.read())