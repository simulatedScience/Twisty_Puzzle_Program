def detect_pieces(moves, n_points):
    """
    detect the pieces of a puzzle based on the given moves.

    inputs:
    -------
        moves - (dict) - dictionary with all possible moves
        n_points - (int) - number of points (color stickers) in the puzzle
            this can be determined with `len(puzzle.solved_state)`

    returns:
    --------
        (list) - list of lists of point indeces that cannot be seperated with the given moves
    """
    pieces = [{n for n in range(n_points)}] #initialize whole puzzle as one piece

    if isinstance(moves, dict):
        move_lists = list(moves.values())
    elif isinstance(moves, (list, tuple)):
        move_lists = moves
    move_sets, cycle_sets = get_move_sets(move_lists)

    changed_pieces = True
    loops = 0
    # comps, intersections = 0, 0
    while changed_pieces:
        # changed_pieces, n_comps, n_intersections = split_pieces(move_sets, pieces)
        # comps += n_comps
        # intersections += n_intersections
        changed_pieces = split_pieces(move_sets, cycle_sets, pieces)
        loops += 1

    print(f"finished calculation after {loops} loops.")
    # print(f"calculated {intersections:3} intersections using {comps:3} comparisons.")
    # print(f"arrived at {len(pieces)} pieces:\n{pieces}")
    return pieces


def get_move_sets(move_lists):
    """
    convert each given move into the set of all point indices changed by the move.

    inputs:
    -------
        moves - (list) - list of all possible moves as their cycles

    returns:
    --------
        (list) - list of sets containing all point indices changed by each move
    """
    move_sets = list()
    cycle_sets = set()
    for move in move_lists:
        move_set = set()
        for cycle in move:
            move_set |= set(cycle)
            cycle_sets.add(frozenset(cycle))
        move_sets.append(move_set)
    return move_sets, cycle_sets


def split_pieces(move_sets, cycle_sets, pieces):
    """
    for each move check if it would split points assigned to the same piece for any piece

    inputs:
    -------
        moves - (dict) - dictionary with all possible moves
        pieces - (list) of (set)s of (int)s - list of all currently detected pieces
            as sets of indices of all points in that piece.
            This list will be changed in-place.

    returns:
    --------
        (bool) - whether or not any piece was changed

    outputs:
    --------
        `pieces` will be changed in-place
    """
    changed_pieces = False
    changed_pieces = split_static(pieces, move_sets, changed_pieces)
    changed_pieces = split_gears(pieces, cycle_sets, changed_pieces)
    return changed_pieces#, n_comps, n_intersections


def split_static(pieces, move_sets, changed_pieces=False):
    """
    split 

    inputs:
    -------
        pieces - (list) of (set)s of (int)s - list of all current pieces.
            This list will be changed in-place.
        move_sets - (iter) any iterable of (set)s of (int)s - iterable of all moves
            as sets or frozensets of point indices affected by each move.
            For performance optimisation no set should be included twice.
        changed_pieces - (bool) - a variable to keep track of whether or not
            pieces were changed. If it is given as True, it will always remain True.

    returns:
    --------
        (bool) - whether or not pieces were changed. If changed_pieces was given as True,
            return True.
    """
    # Algorithm 1
    i = 0
    n_pieces = len(pieces)
    empty_set = set()
    # n_intersections = 0
    # n_comps = 0
    while i != n_pieces:
        # n_comps += 1
        for move_set in move_sets:
            intersect = move_set & pieces[i]
            # n_intersections += 1
            # n_comps += 1
            if intersect != pieces[i]:
                # n_comps += 1
                if intersect != empty_set:
                    pieces.append(intersect)
                    pieces[i] -= intersect
                    n_pieces += 1
                    changed_pieces = True
        i += 1
    return changed_pieces


def split_gears(pieces, cycle_sets, changed_pieces=False):
    """
    Detect points on a piece that are moving relative to other points on the same piece.
        If any move includes a cycle, that only affects points on one piece but not
        the whole piece, then that cycle must be a seperate piece.
    In the documentation this is the implementation of rule 2.

    inputs:
    -------
        pieces - (list) of (set)s of (int)s - list of all current pieces.
            This list will be changed in-place.
        cycle_sets - (iter) any iterable of (set)s of (int)s - iterable of all cycles
            as sets or frozensets of point indices affected by each cycle.
            For performance optimisation no set should be included twice.
        changed_pieces - (bool) - a variable to keep track of whether or not
            pieces were changed. If it is given as True, it will always remain True.

    returns:
    --------
        (bool) - whether or not pieces were changed. If changed_pieces was given as True,
            return True.
    """
    # Algorithm 2
    n_pieces = len(pieces)
    i = 0
    while i != n_pieces:
        # n_comps += 2
        if len(pieces[i]) >= 3:
            for cycle in cycle_sets:
                if cycle < pieces[i]:
                    intersect = cycle & pieces[i]
                    # n_intersections += 1
                    # n_comps += 1
                    # if intersect != pieces[i]:
                        # n_comps += 1
                    if i+1 == n_pieces:
                        pieces.append(intersect)
                        n_pieces += 1
                    else:
                        pieces[i+1] |= intersect
                    pieces[i] -= intersect
                    changed_pieces = True
        i += 1
    return changed_pieces


if __name__ == "__main__":
    # define Skewb for testing
    # wbr = [(0, 8, 7), (24, 25, 26), (4, 17, 10), (5, 15, 11), (6, 16, 9)]
    # wbr2 = [(7, 8, 0), (26, 25, 24), (10, 17, 4), (11, 15, 5), (9, 16, 6)]
    # wgo = [(1, 2, 3), (24, 27, 28), (9, 22, 5), (11, 21, 4), (10, 23, 6)]
    # wgo2 = [(3, 2, 1), (28, 27, 24), (5, 22, 9), (4, 21, 11), (6, 23, 10)]
    # ryg = [(13, 12, 14), (26, 29, 27), (16, 23, 11), (17, 21, 9), (15, 22, 10)]
    # ryg2 = [(14, 12, 13), (27, 29, 26), (11, 23, 16), (9, 21, 17), (10, 22, 15)]
    # oyb = [(19, 20, 18), (28, 29, 25), (21, 15, 6), (5, 23, 17), (4, 22, 16)]
    # oyb2 = [(18, 20, 19), (25, 29, 28), (6, 15, 21), (17, 23, 5), (16, 22, 4)]

    # # skewb_moves = [wbr2, wgo, wgo2, ryg, ryg2, oyb, oyb2, wbr]
    # skewb_moves = [wgo, ryg, oyb, wbr]
    # print(detect_pieces(skewb_moves, 30))
    # def f():
    #     detect_pieces(skewb_moves, 30)
    # from timeit import timeit
    # print(timeit(f, number=100000))
    
    example_move = [[1, 2], [3, 4, 5], [6, 7, 0]]
    example_puzzle_moves = [example_move]
    print(detect_pieces(example_puzzle_moves, 8))
    