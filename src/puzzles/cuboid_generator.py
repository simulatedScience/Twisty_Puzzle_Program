"""
This module provides functions to generate cuboid puzzles (a.k.a. n x m x k Rubik's cubes).
"""

import numpy as np
import matplotlib.pyplot as plt

def generate_cuboid(
        size: tuple[int, int, int],
        cuby_size: float = 1.,
        sticker_offset: float = 0.025,
    ):
    """
    Generate a cuboid of size `size[0] x size[1] x size[2]`, where each cuby has a size of `cuby_size` with stickers offset from the faces by `sticker_offset`.

    Args:
        size (tuple[int, int, int]): The size of the cuboid in the form (width, depth, height).
        cuby_size (float): The size of the cuby.
        sticker_offset (float): The offset of the stickers from the faces of the cuby.
    
    Returns:
        (np.ndarray): The vertices of the cuboid. (shape: (s, 4)), s = number of stickers, fourth component is an integer representing the sticker color by index in the list of the second output
        (np.ndarray): The colors of the stickers. (shape: (6, 3))
    """
    colors = np.array([
        [.1, .8, .1], # green
        [.9, .1, .1], # red
        [.1, .5, .9], # blue
        [1., .5, 0.], # orange
        [.9, .9, .9], # white
        [1., .8, 0.], # yellow
    ])
    
    # construct each face from 5 properties:
    #    start: the location of the first point on the face
    #    dir1: the direction in which the second point is located
    #    dir2: the direction in which the first point of the second row is located
    #    fixed: the axis that is fixed for all points on the face
    #    sign: the sign for the fixed axis (indicating location of the face along that axis)
    # cuby size and offset are automatically computed later
    sticker_coords = []
    face_configs = [
        # Green face (front)
        {
            'start': np.array((-size[0]/2, -size[1]/2, -size[2]/2)),
            'dir1': np.array((0, 0, 1)),
            'dir2': np.array((1, 0, 0)),
            'fixed': 1,
            'sign': -1,
            'color': 0},
        # Red face (right)
        {
            'start': np.array((size[0]/2, -size[1]/2, -size[2]/2)),
            'dir1': np.array((0, 0, 1)),
            'dir2': np.array((0, 1, 0)),
            'fixed': 0,
            'sign': 1,
            'color': 1},
        # Blue face (back)
        {
            'start': np.array((size[0]/2, size[1]/2, -size[2]/2)),
            'dir1': np.array((0, 0, 1)),
            'dir2': np.array((-1, 0, 0)),
            'fixed': 1,
            'sign': 1,
            'color': 2},
        # Orange face (left)
        {
            'start': np.array((-size[0]/2, size[1]/2, -size[2]/2)),
            'dir1': np.array((0, 0, 1)),
            'dir2': np.array((0, -1, 0)),
            'fixed': 0,
            'sign': -1,
            'color': 3},
        # White face (top)
        {
            'start': np.array((-size[0]/2, -size[1]/2, size[2]/2)),
            'dir1': np.array((0, 1, 0)),
            'dir2': np.array((1, 0, 0)),
            'fixed': 2,
            'sign': 1,
            'color': 4},
        # Yellow face (bottom)
        {
            'start': np.array((-size[0]/2, size[1]/2, -size[2]/2)),
            'dir2': np.array((1, 0, 0)),
            'dir1': np.array((0, -1, 0)),
            'fixed': 2,
            'sign': -1,
            'color': 5},
    ]

    for config in face_configs:
        # calculate offset to center the stickers on each cuby
        start_offset = (config['dir1'] + config['dir2']) * cuby_size / 2
        start_offset[config['fixed']] = 0
        # scale to cuby size and add offset
        start = config['start'] * cuby_size + start_offset
        dir1 = config['dir1'] * cuby_size
        dir2 = config['dir2'] * cuby_size
        # calculate coordinate of the fixed axis
        fixed_offset = config['sign'] * (size[config['fixed']] * cuby_size / 2 + sticker_offset)
        # calculate sticker coordinates
        for i in range(size[abs(config['dir1']).argmax()]): # iterate over the first direction
            for j in range(size[abs(config['dir2']).argmax()]): # iterate over the second direction
                pos = start + i * dir1 + j * dir2
                pos[config['fixed']] = fixed_offset
                sticker_coords.append([*pos, config['color']]) # combine coordinates and color index
    
    return np.array(sticker_coords), colors

def define_moves(
        size: tuple[int, int, int],
        sticker_coords: np.ndarray,
    ) -> dict[str, list[list[str]]]:
    """
    Define the base moves for a cuboid of the given shape (x, y, z).
    This method relies on points being ordered exactly as output by the `generate_cuboid` function.

    Args:
        size (tuple[int, int, int]): The size of the cuboid in the form (width, depth, height).
        sticker_coords (np.ndarray): The coordinates of the stickers (shape: (s, 4)), s = number of stickers, fourth component is an integer representing the sticker color by index in the list of the second output

    Returns:
        (dict[str, list[list[str]]]): The base moves for the cuboid with default names represented by permutations as lists of cycles acting on the stickers.
        https://rubiks.fandom.com/wiki/Notation
        https://jperm.net/3x3/moves
        F = turn green face clockwise (90° if x=z, otherwise 180°)
        B = turn blue face clockwise (90° if x=z, otherwise 180°)
        R = turn red face clockwise (90° if y=z, otherwise 180°)
        L = turn orange face clockwise (90° if y=z, otherwise 180°)
        U = turn white face clockwise (90° if x=y, otherwise 180°)
        D = turn yellow face clockwise (90° if x=y, otherwise 180°)
        
        # only for odd number of layers in the corresponding direction:
        M = Median slice. The slice in the middle between L and R in L direction.
        E = Equatorial slice. The slice in the middle between U and D in D direction.
        S = Standing slice. The slice in the middle between F and B in F direction.
        
        # for more than 3 layers in the corresponding direction:
        for faces that are further inwards, the name is prefixed by the number of layers that are further from the center than this face.
        e.g. moves of a 7x7x7 from left to right: L, 2L, 3L, M, 3R, 2R, R
    """
    x, y, z = size
    # 1. rotate puzzle around each major axis (x, y, z)
    rotation_axes: list[np.ndarray] = [vec for vec in np.eye(3)] # x, y, z standard basis vectors
    rotation_is_90: list[bool] = [y == z, x == z, x == y]
    my_sin = lambda angle_is_90: 1 if angle_is_90 else 0
    my_cos = lambda angle_is_90: 0 if angle_is_90 else -1
    # rotate in ngative direction due to cycle detection method
    rot_mat_x = np.array([
        [1, 0, 0],
        [0, my_cos(rotation_is_90[0]), my_sin(rotation_is_90[0])],
        [0, -my_sin(rotation_is_90[0]), my_cos(rotation_is_90[0])],
    ])
    points_rotated_x: np.ndarray = np.dot(sticker_coords[:, :3], rot_mat_x.T)

    rot_mat_y = np.array([
        [my_cos(rotation_is_90[1]), 0, -my_sin(rotation_is_90[1])],
        [0, 1, 0],
        [my_sin(rotation_is_90[1]), 0, my_cos(rotation_is_90[1])],
    ])
    points_rotated_y: np.ndarray = np.dot(sticker_coords[:, :3], rot_mat_y.T)

    rot_mat_z = np.array([
        [my_cos(rotation_is_90[2]), my_sin(rotation_is_90[2]), 0],
        [-my_sin(rotation_is_90[2]), my_cos(rotation_is_90[2]), 0],
        [0, 0, 1],
    ])
    points_rotated_z: np.ndarray = np.dot(sticker_coords[:, :3], rot_mat_z.T)

    # use static starting points for all cycles
    # choose faces with minimal index for each axis to avoid sorting later.
    # green face for x rotations, red face for y rotations, green face for z rotations
    # starting points for each face
    start_indices = {
        "red": x*z, # on red face
        "green": 0, # on green face
        "white": 2*x*z + 2*y*z, # on green face
    }
    move_names = [("L", "M", "R"), ("F", "S", "B"), ("D", "E", "U")]

    # for each starting face, find where each point gets mapped under a given rotation
    def find_rotation_cycles(
            start_indeces: tuple[int, int],
            start_face_sizes: tuple[int, int],
            points: np.ndarray,
            rotated_points: np.ndarray,
            sort_by_coordinate: int,
            move_names: tuple[str, str, str],
        ) -> list[list[list[int]]]:
        """
        
        """
        # add faces with internal rotations to start indices
        endpoints_pos,  = np.where(points[:, sort_by_coordinate] == max(points[:, sort_by_coordinate]))
        endpoints_neg,  = np.where(points[:, sort_by_coordinate] == min(points[:, sort_by_coordinate]))
        # find start indices and face sizes for the faces with internal rotations
        start_index_pos = np.min(endpoints_pos)
        start_index_neg = np.min(endpoints_neg)
        face_size_pos = len(endpoints_pos)
        face_size_neg = len(endpoints_neg)

        # discard extra faces if they are not single-colored
        if len(set(points[endpoints_pos, 3])) == 1:
            use_extra_faces: bool = True
            start_indeces: tuple[int, int, int, int] = (start_index_pos, start_index_neg, *start_indeces)
            start_face_sizes: tuple[int, int, int, int] = (face_size_pos, face_size_neg, *start_face_sizes)
        else:
            use_extra_faces: bool = False

        cycles: list[list[int]] = []
        skip_last_loop: bool = False
        for face_index, (start_index, face_size) in enumerate(zip(start_indeces, start_face_sizes)):
            for i in range(face_size):
                cycle = []
                current_index = start_index + i
                for existing_cycle in cycles:
                    if current_index in existing_cycle:
                        break
                else:
                    while current_index not in cycle:
                        cycle.append(current_index)
                        current_index = np.argmin(np.linalg.norm(rotated_points - points[current_index][:3], axis=1))
                    # if len(cycle) > 1:
                    cycles.append(cycle) # first index in cycle is index of first point in `points`
                    if start_indeces[1] in cycle:
                        skip_last_loop = True
            if face_index > 2 and skip_last_loop:
                break
        # group and sort cycles by coordinates of their first point.
        # if first_point[sort_by_coordinate] is the same, the cycle is in the same group.
        first_point_coords = np.array([points[cycle[0]][sort_by_coordinate] for cycle in cycles])
        # group cycles by first point coordinate
        cycle_groups: dict[float, list[list[int]]] = {}
        for first_point_coord, cycle in zip(first_point_coords, cycles):
            if first_point_coord not in cycle_groups:
                cycle_groups[first_point_coord] = []
            cycle_groups[first_point_coord].append(cycle)
        # merge first two and last two grouos to include all points belonging to the same pieces.
        # join first two groups
        if use_extra_faces:
            sorted_keys = sorted(list(cycle_groups.keys()))
            cycle_groups[sorted_keys[1]] += cycle_groups.pop(sorted_keys[0])
            # join last two groups
            if len(cycle_groups) > 1:
                cycle_groups[sorted_keys[-2]] += cycle_groups.pop(sorted_keys[-1])
        if len(cycle_groups) == 1:
            cycle_groups = {}
        # sort the groups by the first point coordinate
        sorted_cycle_groups: list[list[list[int]]] = [cycle_groups[coord] for coord in sorted(cycle_groups.keys())]

        # print(f"naming {len(sorted_cycle_groups)} moves")
        # name moves, invert cycles if necessary
        named_moves: dict[str, list[list[int]]] = {}
        midpoint: float = (len(sorted_cycle_groups)-1) / 2
        for i, group in enumerate(sorted_cycle_groups):
            dist_to_edge = min(i+1, len(sorted_cycle_groups) - i)
            if i < midpoint:
                prefix: str = f"{dist_to_edge}" if dist_to_edge > 1 else ""
                name: str = prefix + move_names[0]
            elif i == midpoint:
                name: str = move_names[1]
            else: # i > midpoint
                prefix: str = f"{dist_to_edge}" if dist_to_edge > 1 else ""
                name: str = prefix + move_names[2]
                # invert cycles
                group = [[cycle[0]] + cycle[-1:0:-1] for cycle in group]
            named_moves[name] = group
            # print(f"new move: {name} = {group}")
        # return named moves
        return named_moves

    moves_y = find_rotation_cycles(
        start_indeces=(start_indices["red"], start_indices["white"]), # red and white faces
        start_face_sizes=(y*z, x*y),
        points=sticker_coords,
        rotated_points=points_rotated_y,
        sort_by_coordinate=1,
        move_names=move_names[1],
    )
    moves_x = find_rotation_cycles(
        start_indeces=(start_indices["green"], start_indices["white"]), # green and white faces
        start_face_sizes=(x*z, x*y),
        points=sticker_coords,
        rotated_points=points_rotated_x,
        sort_by_coordinate=0,
        move_names=move_names[0],
    )
    moves_z = find_rotation_cycles(
        start_indeces=(start_indices["green"], start_indices["red"]), # green and red faces
        start_face_sizes=(x*z, y*z),
        points=sticker_coords,
        rotated_points=points_rotated_z,
        sort_by_coordinate=2,
        move_names=move_names[2],
    )
    moves: dict[str, list[list[int]]] = moves_x | moves_y | moves_z # merge dictionaries
    return moves




def plot_points(
        sticker_coords: np.ndarray,
        colors: np.ndarray,
        show_indices: bool = False,
    ):
    """
    Plot the given points and colors in 3D using matplotlib.
    """
    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")
    # set aspect ratio to 1
    color_indices = sticker_coords[:, 3].astype(int)
    ax.scatter(
        sticker_coords[:, 0],
        sticker_coords[:, 1],
        sticker_coords[:, 2],
        c=colors[color_indices],
        s=500,
        alpha=1,
    )
    # show sticker index as text at the sticker position
    if show_indices:
        for i, coords in enumerate(sticker_coords):
            if show_indices == "positive" and coords[3] in [2, 3, 5]:
                continue
            ax.text(
                *coords[:3], f"{i}",
                color="black",
                # bold
                weight="bold",
                # text alginment center
                ha="center",
                va="center",
            )
    ax.set_aspect("equal")
    # set background color
    ax.set_facecolor("#777") # mid gray
    fig.set_facecolor("#777") # mid gray
    plt.show()

if __name__ == "__main__":
    # generate 2x3x4 cuboid
    # shape = (6, 3, 5)
    # shape = (3, 3, 3)
    shape = (4, 4, 4)
    # shape = (9, 9, 9)
    # shape = (5, 5, 5)
    # shape = (6, 5, 6)
    # shape = (2, 3, 4)
    # shape = (2, 2, 2)
    # shape = (3, 3, 5)
    sticker_coords, colors = generate_cuboid(
        size=shape,
        cuby_size=1.,
        sticker_offset=0.,
    )
    moves = define_moves(shape, sticker_coords)
    if moves:
        for name, cycles in moves.items():
            print(name, cycles)
            # break
    plot_points(
        sticker_coords,
        colors,
        # show_indices=True,
        show_indices="positive",
        # show_indices=sticker_coords.shape[0] < 100,
    )
