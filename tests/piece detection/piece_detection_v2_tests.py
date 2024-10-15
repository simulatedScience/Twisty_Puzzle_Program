"""
Calculate the pieces of a twisty puzzle based on the defined moves.
This is version 2, version 1 had too many cases that did not work correctly.

Author: Sebastian Jost

"""
import random
import time

def perform_action(
        state: list[int],
        action: list[list[int]]) -> list[int]:
    """
    perform the given action on the given state in-place
    for twisty puzzles this means applying the permutations of a move

    inputs:
    -------
        state - (list) of (int) - list representing the state
        action - (list) of (list) of (int) - list representing an action, here as a list of cycles
            cycles are lists of list indices of the state list.
            
    returns:
    --------
        (list[int]) - the new state
    """
    for cycle in action: # loop over all cycles in the move
        j = cycle[0]
        for i in cycle:  # apply cycle
            state[i], state[j] = state[j], state[i]
    return state

def detect_pieces(
        puzzle: "Twisty_Puzzle",
        moves: list[list[list[int]]],
        n_points: int,
        inverse_dict=None,
        max_moves=1000
        ):
    """
    calculate all pieces of a puzzle, including those only seperable through move sequences that are longer than one move.
    This is achieved by randomly performing [max_moves] moves and cutting pieces every time it's possible. This takes a little bit of time but shouldn't exceed 1s on most common puzzles.
    Due to the choice of using random moves, it is possible that not all pieces are calculated correctly, but that's very, very unlikely unless the puzzle is built specifically to break this algorithm. In that case, just use more moves.
    
    
    """
    start_time = time.perf_counter()
    visited_states = set()
    current_state = list(range(n_points))
    current_pieces: list[set[int]] =(get_piece_template(moves, n_points,\
            inverse_dict=inverse_dict))
    moves_list = list(moves.values())
    for _ in range(max_moves):
        show_pieces_on_puzzle(puzzle, current_pieces)
        print(f"Showing pieces after {_} iterations (moves).")
        input("Press Enter to continue...")
        # choose and apply random move
        move = random.choice(moves_list)
        perform_action(current_state, move)
        # save state, if it is a new state.
        state_tuple = tuple(current_state)
        if not state_tuple in visited_states:
            visited_states.add(state_tuple)
            # split up the new puzzle state according to the current pieces.
            # assume piece cutting lines stay in fixed positions while making moves.
            new_pieces = list()
            for piece in current_pieces:
                new_piece = {current_state[i] for i in piece}
                if not new_piece in current_pieces:
                    new_pieces.append(new_piece)
            # if new pieces were found, intersect them with the previous ones.
            if len(new_pieces) > 0:
                current_pieces = (intersect_pieces([current_pieces, new_pieces], n_points))
    end_time = time.perf_counter()
    print(f"calculation of {max_moves} moves took {end_time - start_time:7} s.")
    anaylse_pieces(current_pieces)
    return current_pieces


def get_piece_template(
        moves: dict[str, list[list[int]]],
        n_points: int,
        inverse_dict=None):
    """
    calculate all puzzle pieces necessary to perform each move at least once.
    """
    move_pieces, movesets, cycle_sets = \
            split_moves(moves, n_points, inverse_dict=inverse_dict)
    puzzle_pieces = intersect_pieces(move_pieces, n_points)
    
    # # generate one piece for the unchanged part of the puzzle
    # unchanged_piece = set()
    # for n in range(n_points):
    #     for piece in puzzle_pieces:
    #         if n in piece:
    #             break
    #     else:
    #         unchanged_piece.add(n)
    # puzzle_pieces.append(unchanged_piece)

    return puzzle_pieces


def intersect_pieces(move_pieces: list[list[set[int]]], n_points):
    """
    Given a list of partitions `move_pieces`, calculate the largest partition Pi such that every given partition can be formed by joining elements of Pi.
    
    calculate the puzzle pieces with all moves taken into consideration.
    the pieces enforced by each move are given.
    
    Args:
        move_pieces (list[list[set[int]]): list of partitions of the point set.
    """
    current_pieces = move_pieces[0]
    empty_set = set()
    for pieces in move_pieces[1:]:
        for piece in pieces:
            # show_pieces_on_puzzle(puzzle, current_pieces)
            # print(f"Showing pieces after intersecting {piece}")
            # input("Press Enter to continue...")
            i = 0
            n_pieces = len(current_pieces)
            while i != n_pieces:
                intersect = current_pieces[i] & piece # calculate intersection A&B
                if intersect != empty_set:
                    if intersect != current_pieces[i]:
                        current_pieces[i] -= intersect   # replace piece A with A\B
                        current_pieces.append(intersect) # add piece A&B
                        n_pieces += 1
                    # if intersect != piece:          # add piece B\A
                    #     puzzle_pieces.append(piece-intersect)
                    #     n_pieces += 1
                i += 1
    return current_pieces


def split_moves(moves: dict[str, list[list[int]]], n_points: int, inverse_dict: dict[str, str]=None):
    """
    calculate the pieces necessary to make each move at least once.

    Args:
        moves (dict[str, list[list[int]]]): dictionary with move names and cycle lists
            every move is represented as a list of cycles
                describing the move
        n_points (int): number of points in the puzzle
        inverse_dict (dict[str, str]): dictionary that assigns inverse moves
            for each move where one exists.
            keys and values are both move names and therefore (str)s

    Returns:
        (list[set]): list of pieces as sets of integers
    """
    movesets = list()
    cycle_sets = set()
    move_pieces = list()
    if inverse_dict != None:
        calculated_moves: set[str] = set()
    for move_name, cycles in moves.items():
        if inverse_dict != None:
            # skip move if it's inverse was already investigated
            if inverse_dict[move_name] in calculated_moves:
                continue
            calculated_moves.add(move_name)
        pieces, moveset, new_cycle_sets = \
                split_move(cycles, n_points)
        # save sets of all points affected by each move
        movesets.append(moveset)
        # save sets of all points affected by each cycle in any move
        cycle_sets |= new_cycle_sets
        # save pieces forced by each move
        move_pieces.append(pieces)
    return move_pieces, movesets, cycle_sets


def split_move(move, n_points):
    """
    calculate the pieces that are enforced just by applying the given move.

    inputs:
    -------
        move (list[list[int]]): list of cycles as lists of integers representing a move
        moveset (set[int]): set of all indices changed by the move
        n_points (int): number of points in the puzzle

    returns:
    --------
        (list) of (set)s of (int)s - list of pieces as sets of integers
        (set) of (int)s - set of all points affected by the given move
        (set) of (frozenset)s - set of all cycles as sets of all affected points
    """
    moveset = set()
    cycle_sets = set()
    pieces = list()
    sorted_cycles = sorted(move, key=len)
    last_len = 0
    for cycle in sorted_cycles:
        if len(cycle) == 1:
            continue
        if last_len != len(cycle):
            pieces.append(set())
        cycle_set = frozenset(cycle)
        pieces[-1] |= cycle_set
        moveset |= cycle_set
        cycle_sets.add(cycle_set)
        last_len = len(cycle)
    del(last_len, sorted_cycles)

    # generate one piece for the unchanged part of the puzzle
    unchanged_piece = set()
    for n in range(n_points):
        if not n in moveset:
            unchanged_piece.add(n)
    pieces.append(unchanged_piece)
    del(unchanged_piece)

    return pieces, moveset, cycle_sets


def anaylse_pieces(pieces):
    """
    categorize pieces by how many points are on them.
    """
    piece_lengths = [len(piece) for piece in pieces]
    for n in set(piece_lengths):
        print(f"Found {piece_lengths.count(n)} pieces with {n} stickers.")

if __name__ == "__main__":
    from test_piece_detection import load_puzzle, show_pieces_on_puzzle
    puzzle = load_puzzle()
    pieces = detect_pieces(puzzle, puzzle.moves, n_points=len(puzzle.vpy_objects))
    # show_pieces_on_puzzle(puzzle, pieces)