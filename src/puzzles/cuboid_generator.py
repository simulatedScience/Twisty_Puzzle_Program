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

def define_moves(size: tuple[int, int, int]) -> dict[str, list[list[str]]]:
    """
    Define the base moves for a cuboid of the given shape (x, y, z).
    This method relies on points being ordered exactly as output by the `generate_cuboid` function.

    Args:
        size (tuple[int, int, int]): The size of the cuboid in the form (width, depth, height).

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
    
    # calculate number of stickers on each face
    n_stickers = {
        "green": size[0]*size[2],
        "blue": size[0]*size[2],
        "red": size[1]*size[2],
        "orange": size[1]*size[2],
        "white": size[0]*size[1],
        "yellow": size[0]*size[1],
    }
    moves = {}
    x, y, z = size

    def calculate_face_cycles_90(
            start_index: int,
            face_size: int,
            face_height_offset: int = None,
        ) -> list[list[int]]:
        """
        Recursively define the cycles for a single colored face. Each iteration adds cycles for the outermost ring of stickers.
        
        Args:
            start_index (int): The index of the first sticker on the face.
            face_size (int): The width and height of the face (must be equal for 90° moves).
            face_height_offset (int): The index offset between adjacent stickers in the height direction.
                The offset to the next sticker in width direction is always 1.
        """
        if face_height_offset is None:
            face_height_offset = face_size
        if face_size < 2: # no cycles for faces with less than 2 stickers per direction
            return []
        cycles = []
        # add corner cycle
        cycles.append([
            start_index,
            start_index + face_height_offset*(face_size-1),
            start_index + face_height_offset*(face_size-1) + face_size - 1,
            start_index + face_size - 1,
        ])
        # add edge cycles
        for i in range(1, face_size-1):
            cycles.append([
                start_index + i,
                start_index + (face_size-1-i) * face_height_offset,
                start_index + (face_size-1) * face_height_offset + face_size - 1 - i,
                start_index + i * face_height_offset + face_size - 1,
            ])
        return cycles + calculate_face_cycles_90(
            start_index + face_height_offset + 1,
            face_size - 2,
            face_height_offset,
        )
    
    def calculate_face_cycles_180():
        pass
    
    def calculate_off_face_cycles_90(
        size: tuple[int, int, int],
        faces_start_indices: list[int],
        face_1_width: int,
        face_2_width: int,
        shared_axis_width: int,
    ) -> list[list[int]]:
        """
        Define the cycles of slice moves involving four different-colored faces.
        """
    
    start_index = 0
    moves["F"] = calculate_face_cycles_90(
        start_index=start_index,
        face_size=x,
        face_size=z,
    )
    start_index += x*z
    moves["R"] = calculate_face_cycles_90(
        start_index=start_index,
        face_size=y,
        face_size=z,
    )
    start_index += y*z
    moves["B"] = calculate_face_cycles_90(
        start_index=start_index,
        face_size=x,
        face_size=z,
    )
    start_index += x*z
    moves["L"] = calculate_face_cycles_90(
        start_index=start_index,
        face_size=y,
        face_size=z,
    )
    start_index += y*z
    moves["U"] = calculate_face_cycles_90(
        start_index=start_index,
        face_size=x,
        face_size=y,
    )
    start_index += x*y
    moves["D"] = calculate_face_cycles_90(
        start_index=start_index,
        face_size=x,
        face_size=y,
    )
    start_index += x*y
    return moves

    # x, y, z = size
    
    # def _define_face_cycles(width: int, height: int, offset: int) -> list[list[int]]:
    #     """
    #     Define the cycles for a single face.

    #     Args:
    #         width (int): The width of the face.
    #         height (int): The height of the face.
    #         offset (int): The index offset for the starting point of the face.

    #     Returns:
    #         list[list[int]]: A list of cycles representing how the stickers on a single face are permuted by a 90° rotation.
    #     """
    #     cycles = []
    #     layer_count = min(width, height) // 2

    #     for layer in range(layer_count):
    #         cycle = []
    #         # Top row, left to right
    #         for i in range(layer, width - layer - 1):
    #             cycle.append(offset + layer * width + i)
    #         # Right column, top to bottom
    #         for i in range(layer, height - layer - 1):
    #             cycle.append(offset + (i + 1) * width - layer - 1)
    #         # Bottom row, right to left
    #         for i in range(layer, width - layer - 1):
    #             cycle.append(offset + (height - layer - 1) * width + (width - i - 1))
    #         # Left column, bottom to top
    #         for i in range(layer, height - layer - 1):
    #             cycle.append(offset + (height - i - 1) * width + layer)
    #         if len(cycle) > 1:  # Ensure only valid cycles are included
    #             cycles.append(cycle)

    #     return cycles
    
    # def _define_side_cycles(
    #     face_size: int,
    #     layers: int,
    #     move_direction: int,
    #     fixed_face_idx: int,
    #     side_offsets: list[int]
    # ) -> list[list[int]]:
    #     """
    #     Define the cycles for stickers on the adjacent faces when rotating a face.

    #     Args:
    #         face_size (int): Size of the face in the direction of movement.
    #         layers (int): The number of layers to rotate.
    #         move_direction (int): The direction to rotate the face.
    #         fixed_face_idx (int): The fixed index (U, F, L, etc.).
    #         side_offsets (list[int]): Offsets for the adjacent faces.

    #     Returns:
    #         list[list[int]]: A list of cycles representing how the stickers on adjacent faces are permuted.
    #     """
    #     cycles = []

    #     for layer in range(layers):
    #         for i in range(face_size):
    #             cycle = []
    #             base = layer * face_size + i + fixed_face_idx
    #             for offset in side_offsets:
    #                 current_idx = base + offset
    #                 if current_idx not in cycle:  # Ensure no duplicates
    #                     cycle.append(current_idx)
    #             if len(cycle) > 1:  # Ensure only valid cycles are included
    #                 cycles.append(cycle)
        
    #     return cycles

    # def _generate_moves():
    #     """
    #     Generate the moves for the cuboid based on its dimensions.

    #     Returns:
    #         dict[str, list[list[int]]]: The moves for the cuboid.
    #     """
    #     moves = {}
        
    #     # Each entry corresponds to a face (U, D, F, B, L, R) in the following order:
    #     # U (white), D (yellow), F (green), B (blue), L (orange), R (red)
    #     face_info = [
    #         {'face_name': 'U', 'face_dims': (x, y), 'fixed_axis': 2, 'sign': 1, 'offset': 0},
    #         {'face_name': 'D', 'face_dims': (x, y), 'fixed_axis': 2, 'sign': 1, 'offset': 5 * x * y},
    #         {'face_name': 'F', 'face_dims': (x, z), 'fixed_axis': 1, 'sign': 1, 'offset': x * y},
    #         {'face_name': 'B', 'face_dims': (x, z), 'fixed_axis': 1, 'sign': 1, 'offset': 4 * x * y},
    #         {'face_name': 'L', 'face_dims': (y, z), 'fixed_axis': 0, 'sign': 1, 'offset': 2 * x * y},
    #         {'face_name': 'R', 'face_dims': (y, z), 'fixed_axis': 0, 'sign': 1, 'offset': 3 * x * y}
    #     ]
        
    #     # Offsets for adjacent faces corresponding to (U, D, F, B, L, R)
    #     adj_face_offsets = {
    #         'U': [0, x * y, 4 * x * y, 3 * x * y],
    #         'D': [5 * x * y, x * y, 4 * x * y, 3 * x * y],
    #         'F': [x * y, 2 * x * y, 5 * x * y, 0],
    #         'B': [4 * x * y, 2 * x * y, 5 * x * y, 0],
    #         'L': [2 * x * y, 3 * x * y, 4 * x * y, x * y],
    #         'R': [2 * x * y, 0, 4 * x * y, x * y]
    #     }
        
    #     # Create moves for each face
    #     for info in face_info:
    #         face_name = info['face_name']
    #         width, height = info['face_dims']
    #         fixed_idx = info['offset']

    #         # Define face cycles (single face rotation)
    #         face_cycles = _define_face_cycles(width, height, fixed_idx)
    #         moves[face_name] = face_cycles

    #         # Define side cycles (adjacent faces affected by the move)
    #         side_cycles = _define_side_cycles(width, height, 1, fixed_idx, adj_face_offsets[face_name])
    #         moves[face_name].extend(side_cycles)

    #         # Define inner layer moves (like M, E, S for odd layers)
    #         for layer in range(2, min([x, y, z]) // 2 + 1):
    #             layer_name = f'{layer}{face_name}'
    #             side_cycles = _define_side_cycles(width, height, layer, fixed_idx, adj_face_offsets[face_name])
    #             moves[layer_name] = side_cycles

    #     return moves
    
    # # Generate all moves
    # return _generate_moves()







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
    # ax.set_box_aspect([1, 1, 1])
    ax.set_aspect("equal")
    plt.show()
    
if __name__ == "__main__":
    # generate 2x3x4 cuboid
    # shape = (2, 3, 5)
    # shape = (3, 3, 3)
    shape = (4, 4, 4)
    # shape = (9, 9, 9)
    # shape = (5, 5, 5)
    # shape = (6, 5, 6)
    # shape = (2, 2, 2)
    sticker_coords, colors = generate_cuboid(shape)
    moves = define_moves(shape)
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