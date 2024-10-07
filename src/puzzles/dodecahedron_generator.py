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
"""

import numpy as np

COLORS: dict[str, str] = {
    "F": "#ff66ff", # fuchsia
    "P": "#800080", # purple
    "L": "#88ff00", # lime
    "O": "#888800", # olive
    "T": "#11bbaa", # turquoise
    "B": "#3355dd", # blue
    "R": "#ff0000", # red
    "C": "#aa1133", # crimson
    "Y": "#ffee00", # yellow
    "A": "#ee9900", # amber
    "W": "#eeeeee", # white
    "G": "#999999", # grey
}

# def generate_dodecahedron_points(radius: float = 1, sidelength: int = 2) -> tuple[np.ndarray, np.ndarray]:
#     """
#     Generate the points and colors of a dodecahedron puzzle.

#     Args:
#         radius (float): the radius of the dodecahedron (Default: 1)
#         sidelength (int): the sidelength of the dodecahedron (Default: 2 -> Megaminx)

#     Returns:
#         tuple[np.ndarray, np.ndarray]: the points and colors of the dodecahedron
#     """
#     # golden ratio as useful constant
#     phi = (1 + np.sqrt(5)) / 2

#     # define base face points
#     corner = np.array([1., 0., 0.])
#     ## rotate corner to get five


def generate_pentagon_points(center: np.ndarray, normal: np.ndarray, radius: float, sidelength: int) -> np.ndarray:
    """
    Generate the points of a regular pentagon given the center, normal, and sidelength.
    
    Args:
        center (np.ndarray): The center of the pentagon.
        normal (np.ndarray): The normal vector for the pentagon plane.
        radius (float): Radius of the dodecahedron (distance from the center of the dodecahedron to the center of each pentagon).
        sidelength (int): Number of divisions along each edge (2 for Megaminx, 1 for Kilominx, etc.).

    Returns:
        np.ndarray: A set of points representing the pentagon stickers.
    """
    # Define the 2D pentagon vertices (centered at the origin)
    angle = 2 * np.pi / 5
    vertices_2d = np.array([[np.cos(i * angle), np.sin(i * angle)] for i in range(5)]) * radius
    
    # If the sidelength is more than 1 (e.g., Kilominx), subdivide each pentagon edge
    if sidelength > 1:
        subdivisions = []
        for i in range(5):
            start = vertices_2d[i]
            end = vertices_2d[(i + 1) % 5]
            for j in range(sidelength):
                subdivisions.append(start + (end - start) * j / sidelength)
        vertices_2d = np.array(subdivisions)

    # Project the 2D pentagon into 3D by rotating it to match the normal
    up_vector = np.array([0, 0, 1])
    if not np.allclose(normal, up_vector):
        # Create a rotation matrix to rotate the pentagon from the XY plane to the plane defined by the normal
        axis = np.cross(up_vector, normal)
        axis = axis / np.linalg.norm(axis)
        angle = np.arccos(np.dot(up_vector, normal))
        rotation_matrix = rotation_matrix_from_axis_angle(axis, angle)
        vertices_3d = np.dot(rotation_matrix, np.hstack((vertices_2d, np.zeros((vertices_2d.shape[0], 1)))).T).T
    else:
        vertices_3d = np.hstack((vertices_2d, np.zeros((vertices_2d.shape[0], 1))))

    # Translate the pentagon to the specified center
    vertices_3d += center

    return vertices_3d

def rotation_matrix_from_axis_angle(axis: np.ndarray, angle: float) -> np.ndarray:
    """
    Compute the rotation matrix for a given axis and angle using Rodrigues' rotation formula.
    
    Args:
        axis (np.ndarray): The axis of rotation.
        angle (float): The angle of rotation in radians.
        
    Returns:
        np.ndarray: The 3x3 rotation matrix.
    """
    K = np.array([[0, -axis[2], axis[1]],
                  [axis[2], 0, -axis[0]],
                  [-axis[1], axis[0], 0]])
    I = np.eye(3)
    return I + np.sin(angle) * K + (1 - np.cos(angle)) * np.dot(K, K)

def icosahedron_corners(radius: float = 1) -> np.ndarray:
    """
    Generate the corners of an icosahedron with the given radius.
    
    Args:
        radius (float): The radius of the icosahedron. (Default: 1)
        
    Returns:
        np.ndarray: The icosahedron corners.
    """
    phi = (1 + np.sqrt(5)) / 2
    
    # Vertices of a unit icosahedron, unscaled
    vertices = np.array([
        [-1,  phi,  0], [ 1,  phi,  0], [-1, -phi,  0], [ 1, -phi,  0],
        [ 0, -1,  phi], [ 0,  1,  phi], [ 0, -1, -phi], [ 0,  1, -phi],
        [ phi,  0, -1], [ phi,  0,  1], [-phi,  0, -1], [-phi,  0,  1]
    ])

    # Normalize and scale by the radius
    vertices = radius * vertices / np.linalg.norm(vertices[0])

    return vertices

def generate_dodecahedron_points(radius: float = 1, offset_fac=2) -> np.ndarray:
    """
    Generate the points of a dodecahedron puzzle given the radius.
    
    Args:
        radius (float): The radius of the dodecahedron. (Default: 1)
        
    Returns:
        np.ndarray: The dodecahedron points.
    """
    face_centers: np.ndarray = icosahedron_corners(radius)
    reference_pentagon: np.ndarray = generate_pentagon_points(
        center=np.zeros(3),
        normal=np.array([0, 0, 1]),
        radius=radius,
        sidelength=2,
    )
    # translate and rotate a copy of the reference pentagon to each face center
    dodecahedron_points: list[np.ndarray] = []
    for i, center in enumerate(face_centers):
        # pentagon normal
        normal = center / np.linalg.norm(center)
        # rotate the reference pentagon to the face normal
        rotation_matrix = rotation_matrix_from_axis_angle(np.cross([0, 0, 1], normal), np.arccos(np.dot([0, 0, 1], normal)))
        rotated_pentagon = np.dot(rotation_matrix, reference_pentagon.T).T
        # translate to the face center
        rotated_pentagon += center
        # rotate pentagon around the face normal
        #  ensure the pentagon edges line up with each other
        # TOOD
        ???
        # translate outwards along the face normal
        rotated_pentagon += offset_fac * normal
        # add to the list of dodecahedron points
        dodecahedron_points += [point for point in rotated_pentagon]
    return np.array(dodecahedron_points)

if __name__ == "__main__":
    # points = generate_pentagon_points(
    #     center=np.array([0, 0, 0]),
    #     normal=np.array([0, 0, 1]),
    #     radius=1,
    #     sidelength=2,
    # )
    # points = icosahedron_corners(radius=1)
    points = generate_dodecahedron_points(radius=1)
    
    colors = [COLORS["F"]]*len(points)
    # plot points in  3d
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2], c=colors, s=100, alpha=1)
    ax.set_aspect("equal")
    plt.show()
