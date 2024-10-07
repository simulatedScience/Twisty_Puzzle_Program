"""
This module generates the colored points for a dedecahedron puzzle.

Moves are named according to the colors of the faces they affect with carefully chosen colors:  
| letters |      color names    |    color codes    |
|---------|---------------------|-------------------|
| F - P   | fuchsia   - purple  | #ff66ff - #800080 |
| L - O   | lime      - olive   | #88ff00 - #888800 |
| T - B   | turquoise - blue    | #11bbaa - #3355dd |
| R - C   | red       - crimson | #ff0000 - #aa1133 |
| Y - A   | yellow    - amber   | #ffee00 - #ee9900 |
| W - G   | white     - grey    | #eeeeee - #999999 |

Authors: Sebastian Jost & GPT-4o (07.10.2024)
"""

import numpy as np
from collections import defaultdict

COLORS: dict[str, str] = {
    "W": "#ffffff", # white
    "L": "#88ff00", # lime
    "O": "#888800", # olive
    "G": "#999999", # grey
    "R": "#ff0000", # red
    "F": "#ff66ff", # fuchsia
    "P": "#800080", # purple
    "C": "#aa1133", # crimson
    "Y": "#ffee00", # yellow
    "B": "#3355dd", # blue
    "T": "#11bbaa", # turquoise
    "A": "#ee9900", # amber
}


# Helper functions
def normalize(v):
    """ Normalize a 3D vector. """
    return v / np.linalg.norm(v)

def mid_point(p1, p2):
    """ Calculate the midpoint between two 3D points. """
    return (p1 + p2) / 2.0

def angle_between_vectors(v1, v2, com):
    """ Calculate the angle between two vectors in the xy-plane. """
    angle = np.arccos(
        np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
    # check if rotation is clockwise or counterclockwise
    if np.dot(np.cross(v1, v2), com) < 0:
        angle = 2 * np.pi - angle
    if np.isnan(angle):
        angle = 0
    return angle

def center_of_mass(points):
    """ Calculate the center of mass of a set of 3D points. """
    return np.mean(points, axis=0)

def scale_towards_com(points, com, face_scale_factor=0.8):
    """ Scale points toward the center of mass. """
    return com + face_scale_factor * (points - com)

def sort_counterclockwise(points, com):
    """ Sort points counterclockwise relative to the COM and the first point. """
    v_ref = points[0] - com
    angles = [angle_between_vectors(v_ref, p - com, com) for p in points]
    sorted_points = points[np.argsort(angles)]
    return sorted_points

# Step 1: Construct a regular dodecahedron
def dodecahedron_vertices():
    """
    Define vertices of a regular dodecahedron.

    Returns:
        np.ndarray: 3D coordinates of the vertices of a regular dodecahedron.
    """
    phi = (1 + np.sqrt(5)) / 2  # golden ratio
    dodecahedron_points = np.array([
        # 8 vertices of embedded cube
        [-1, -1, -1], [-1, -1, 1], [-1, 1, -1], [-1, 1, 1],
        [1, -1, -1], [1, -1, 1], [1, 1, -1], [1, 1, 1],
        # pairs of vertices above each cube face
        [0, -1 / phi, -phi], [0, -1 / phi, phi],
        [0, 1 / phi, -phi], [0, 1 / phi, phi],
        [-1 / phi, -phi, 0], [-1 / phi, phi, 0],
        [1 / phi, -phi, 0], [1 / phi, phi, 0],
        [-phi, 0, -1 / phi], [phi, 0, -1 / phi],
        [-phi, 0, 1 / phi], [phi, 0, 1 / phi]
    ])
    return dodecahedron_points

# Step 2: Construct a regular icosahedron
def icosahedron_vertices():
    phi = (1 + np.sqrt(5)) / 2  # golden ratio
    icosahedron_points = np.array([
        [0,  phi,  1],
        [0,  phi, -1],
        [0, -phi,  1],
        [0, -phi, -1],
        [ 1, 0,  phi],
        [-1, 0,  phi],
        [ 1, 0, -phi],
        [-1, 0, -phi],
        [ phi,  1, 0],
        [ phi, -1, 0],
        [-phi,  1, 0],
        [-phi, -1, 0],
    ])
    return icosahedron_points

# Step 3: Find the active pentagons using icosahedron vertex as direction
def find_active_pentagons(dodecahedron_points, icosahedron_points, face_scale_factor=0.8):
    pentagons = defaultdict(list)
    for i, dir in enumerate(icosahedron_points):
        distances = np.dot(dodecahedron_points, dir)
        indices = np.argsort(distances)[-5:]  # Get the top 5 points furthest in the direction
        pentagon_points = dodecahedron_points[indices]
        com = center_of_mass(pentagon_points)
        scaled_pentagon = scale_towards_com(pentagon_points, com, face_scale_factor=face_scale_factor)
        sorted_pentagon = sort_counterclockwise(scaled_pentagon, com)
        pentagons[i].append((sorted_pentagon, com))
    return pentagons

# Step 7: Add midpoints between consecutive points
def add_midpoints_to_pentagon(pentagon, com):
    num_points = len(pentagon)
    midpoints = [mid_point(pentagon[i], pentagon[(i + 1) % num_points]) for i in range(num_points)]
    return np.vstack((pentagon, midpoints, com))

# Step 8: Add colors to pentagons and compile final megaminx points
def generate_dodecahedron_points(face_scale_factor=0.7):
    dodecahedron_points = dodecahedron_vertices()
    icosahedron_points = icosahedron_vertices()
    pentagons = find_active_pentagons(dodecahedron_points, icosahedron_points, face_scale_factor=face_scale_factor)
    megaminx_points: list[np.ndarray] = []
    point_colors: list[str] = []
    color_keys = list(COLORS.keys())
    
    for i, (pentagon_data) in pentagons.items():
        pentagon, com = pentagon_data[0]
        # Add midpoints
        pentagon_with_midpoints = add_midpoints_to_pentagon(pentagon, com)
        # Assign color and store the result
        color = COLORS[color_keys[i % len(COLORS)]]
        megaminx_points += pentagon_with_midpoints.tolist()
        point_colors += [color] * len(pentagon_with_midpoints)
    
    return np.array(megaminx_points), point_colors

# Step 9: add moves for each face
def add_moves(dodecahedron_points, point_colors):
    color_keys = list(COLORS.keys())
    icosahedron_points = icosahedron_vertices()
    
    # For each axis defined by an icosahedron vertex, find the points that are furthest (and second furthest) in that direction. These are points affected by the move.
    moves: dict[str, list[int]] = {}
    
    for i, dir in enumerate(icosahedron_points):
        move_name = color_keys[i]
        distances = np.dot(dodecahedron_points, dir)
        # sort color list by distance
        indices = np.argsort(distances)
        # group distances
        distances = np.round(distances, 3)
        unique_distances = np.unique(distances)
        # find all points for each distance
        distance_indices: dict[float, list[int]] = {d: [] for d in unique_distances}
        for i, d in enumerate(distances):
            distance_indices[d].append(i)
            plt.scatter(x=[d], y=[len(distance_indices[d])], c=point_colors[i], s=50)
        distance_colors: dict[float, list[str]] = {d: [point_colors[i] for i in distance_indices[d]] for d in unique_distances}
        plt.show()
        # plot distance_colors
        # 2d plot: x=distance, y=index of point at that distance, color=point color
        
        

if __name__ == "__main__":
    # plot points in  3d
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')

    # # show icosahedron vertices
    # points = icosahedron_vertices()
    # colors = [COLORS["F"]]*len(points)
    # ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=100, alpha=1)
    
    # # show dodecahedron vertices
    # points = dodecahedron_vertices()
    # colors = [COLORS["F"]]*len(points)
    # ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=100, alpha=1)

    points, colors = generate_dodecahedron_points()
    moves = add_moves(points, colors)
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=300, alpha=1)
    
    ax.set_aspect("equal")
    plt.show()
