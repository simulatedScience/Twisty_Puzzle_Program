"""
implementation of an A* algorithm for solving a given twisty puzzle
"""
import time
from copy import deepcopy
from .ai_modules.twisty_puzzle_model import perform_action
from .ai_modules.q_puzzle_class import Puzzle_Q_AI
from .ai_modules.nn_puzzle_class import Puzzle_Network

def solve_puzzle(starting_state, ACTIONS_DICT, SOLVED_STATE, ai_class, max_time=60, WEIGHT=0.1):
    """
    inputs:
    -------
        starting_state - (list) - scrambled state of the puzzle, that shall be solved
        ACTIONS_DICT - (dict) - dictionary containing all availiable moves for the puzzle
        SOLVED_STATE - (list) - solved state representation as for the Q-Learning
        ai_class - (Puzzle_Q_AI) or (Puzzle_Network) - an instance of the Q-learning puzzle class or the puzzle network class
            this determines what is used for the solving process
            the Q-table or neural network should already be loaded.
        max_time - (float) - maximum time (in seconds) allowed for finding the solution
        WEIGHT - (float) - weight for weighted A* search. 1 for normal A*

    returns:
    --------
        - list/tuple/str of moves chosen to solve the puzzle
    """
    end_time = time.time() + max_time

    open_states = {():(0,starting_state)} # init starting state with value 0, no actions taken so far
    closed_states = dict()

    def _get_key(key):
        """
        helper function for max() to get the best action from open_states
        """
        return open_states[key][0]

    while time.time() < end_time:
        best_action_seq = max(open_states, key=_get_key)
        value, puzzle_state = open_states[best_action_seq]
        solution_sequence = expand_node(best_action_seq,
                                        open_states,
                                        closed_states,
                                        ACTIONS_DICT,
                                        SOLVED_STATE,
                                        ai_class,
                                        WEIGHT=WEIGHT)
        if solution_sequence is not None:
            print(f"Searched {len(closed_states) + len(open_states)} state-action pairs to find a solution.")
            print(f"Maximum search depth was {len(max(open_states.keys(), key=len))} moves.")
            return " ".join(solution_sequence)
    print(f"Searched {len(closed_states) + len(open_states)} state-action pairs but found no solution.")
    print(f"Maximum search depth was {len(max(open_states.keys(), key=len))} moves.")
    return ""


def expand_node(action_seq,
                open_states,
                closed_states,
                ACTIONS_DICT,
                SOLVED_STATE,
                ai_class,
                WEIGHT=0.1):
    """
    for all possible actions in [ACTIONS_DICT], add the action to [action_seq] and add that to open_states, unless the state resulting from that action was already visited and had a better value than it has now.

    inputs:
    -------
        action_seq - (tuple) - 
        open_states - (dict) - 
        closed_states - (dict) - 
        ACTIONS_DICT - (dict) - 
        SOLVED_STATE - (list) - 
        ai_class - (Puzzle_Q_AI) or (Puzzle_Network) - an instance of the Q-learning puzzle class or the puzzle network class
            this determines what is used for the solving process
            the Q-table or neural network should already be loaded.
        WEIGHT - (float) - weight factor in [0,1] for weighted A*. 
            default value 1

    returns:
    --------
        None if no solution was found,
        (tuple) action sequence of the solution if it was found.
    """
    prev_value, prev_state = open_states.pop(action_seq)
    for action, cycles in ACTIONS_DICT.items():
        puzzle_state = deepcopy(prev_state)
        perform_action(puzzle_state, cycles)
        new_key = action_seq + (action,)
        if puzzle_state == SOLVED_STATE:
            return new_key
        # start_time = time.perf_counter()
        value = get_a_star_eval(action, prev_value, prev_state, ai_class, WEIGHT=WEIGHT)
        # end_time = time.perf_counter()
        # print(f"evaluation of state took {(end_time-start_time)*1000:5} ms.")

        state_tuple = tuple(puzzle_state)
        if not state_tuple in closed_states:
            open_states[new_key] = (value, puzzle_state)
        else:
            if value > closed_states[state_tuple]:
                # found better path to a state visited before.
                # delete from closed_states and add to open_states
                del(closed_states[state_tuple])
                open_states[new_key] = (value, puzzle_state)
        closed_states[tuple(prev_state)] = prev_value


def get_a_star_eval(action, prev_value, prev_state, ai_class, WEIGHT=0.1):
    """
    evaluate the current sequence of actions according to the usual formula of weighted A*:
        f(s) = lambda * g(s) + h(s)
    
    inputs:
    -------
        action - (str) - new action added to the currently investigated action sequence
        prev_value - (float) - value of the current action sequence without [action] added to it
        prev_state - (list) - resulting state of the current action sequence without [action] added to it
        ai_class - (Puzzle_Q_AI) or (Puzzle_Network) - an instance of the Q-learning puzzle class or the puzzle network class
            this determines what is used for the solving process
            the Q-table or neural network should already be loaded.
        WEIGHT - (float) - weight in [0,1] representing lambda in the above equation.

    returns:
    --------
        (float) - representing f(s)
    """
    if isinstance(ai_class, Puzzle_Q_AI):
        return WEIGHT*prev_value-WEIGHT + get_q_value(tuple(prev_state), action, ai_class)
    if isinstance(ai_class, Puzzle_Network):
        return WEIGHT*prev_value-WEIGHT + get_nn_value(prev_state, action, ai_class)
    # return WEIGHT*prev_value-WEIGHT + get_ai_eval(prev_state, action, ai_class)


# def get_ai_eval(prev_state, action, ai_class):
#     """
#     this is the heuristic used in the A* algorithm
#     calculates the estimated value of the given state-action pair based in the Q-table or Neural Network

#     inputs:
#     -------
#         prev_state - (list) - 
#         action - (str) - 
#         ai_class - ()
#     """
#     if isinstance(ai_class, Puzzle_Q_AI):
#         return get_q_value(tuple(prev_state), action, ai_class.Q_table)
#     if isinstance(ai_class, Puzzle_Network):
#         return get_nn_value(prev_state, action, ai_class)


def get_q_value(state, action, ai_class):
    """
    calculates the q-values assigned to the given state-action pair by the given Q-table

    inputs:
    -------
        state - (tuple) - the current puzzle state as a tuple
        action - (str) - the action of interest
        Q_table - (dict) - 

    returns:
    --------
        (float) - value of the given state-action pair in range [0,1]. 
            0 if the key doesn't exist
    """
    try:
        return ai_class.Q_table[(state, action)]
    except KeyError:
        return 0
    except TypeError:
        return ai_class.Q_table[(tuple(state), action)]


def get_nn_value(state, action, ai_class):
    """
    calculates the value of the given state-action pair with the neural network given in ai_class

    inputs:
    -------
        state - (list) - the current puzzle state as a list
        action - (str) - the action of interest
        ai_class - (Puzzle_Network) - puzzle Network class instance with trained network ai_class.model
    """
    start_time = time.time()
    value = ai_class.model.predict([ai_class.prepare_state(state) + ai_class.ACTION_VECTOR_DICT[action] for action in ai_class.ACTION_VECTOR_DICT], use_multiprocessing=True)[0]
    end_time = time.time()
    print(f"Neural network prediction took {(end_time-start_time)*1000:5} ms.")
    return value