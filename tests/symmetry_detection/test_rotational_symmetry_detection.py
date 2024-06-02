import cProfile
import pstats
import time


import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

from rotational_symmetry_detection import find_plane_intersection, penalty, find_rotational_symmetries, rotation_symmetry_measure
from symmetry_plane_detection import dist_similarity_function
from test_symmetry_plane_detection import draw_plane, set_equal_aspect_3d

def test_find_plane_intersection(plane_1: tuple[np.ndarray, np.ndarray], plane_2: tuple[np.ndarray, np.ndarray]) -> tuple[np.ndarray, np.ndarray]:
    """
    Test the find_plane_intersection function.
    """
    intersection = find_plane_intersection(plane_1, plane_2)
    if intersection is None:
        print(f"Planes are parallel: Normals: {plane_1[1]}, {plane_2[1]}")
        return None
    point, direction = intersection
    # create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    draw_plane(ax, *plane_1, show_normal=False, size=3)
    draw_plane(ax, *plane_2, show_normal=False, size=3)
    draw_line(ax, point, direction, length=3)
    set_equal_aspect_3d(ax)
    plt.show()
    return intersection

def plot_penalty_function():
    x = np.linspace(-4*np.pi, 4*np.pi, 10000)
    # x = np.linspace(0.925, 1, 10000)
    # x = np.linspace(0.8, 1, 10000)
    y = penalty(x, alpha=.1)#, min_angle=np.deg2rad(15), max_angle=np.deg2rad(21.5))
    # x = np.cos(x)
    # y = dist_similarity_function(x, alpha=20)
    plt.plot(x, y, label="penalty function")
    plt.legend()
    plt.show()

def test_find_rotational_symmetries(
        X: np.ndarray,
        num_planes: int = 3000,
        num_candidate_rotations: int = 5000,
        threshold: float = 0.1,
        min_angle: float = np.pi / 12.5,
        num_best_rotations: int = 40,
        alpha: float = 1.0,
        anim_time: float = 1,
        anim_steps: int = 60,
        anim_pause: float = 2,
        edges: np.ndarray = None,
    ) -> list[tuple[np.ndarray, float]]:
    profile = cProfile.Profile()
    rotations = profile.runcall(
        find_rotational_symmetries,
            X=X,
            num_planes=num_planes,
            num_candidate_rotations=num_candidate_rotations,
            threshold=threshold,
            min_angle=min_angle,
            num_best_rotations=num_best_rotations,
            alpha=alpha,
    )
    print(f"Found {len(rotations)} rotational symmetries.")
    ps = pstats.Stats(profile)
    ps.sort_stats(("tottime"))
    ps.print_stats(10)
    # create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # show point cloud X
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], s=200)
    set_equal_aspect_3d(ax)
    plt.ion()
    # show edges if available
    if edges is not None:
        for edge in edges:
            draw_edge(
                ax,
                X[edge[0]],
                X[edge[1]],
                color="#000",
            )
    plt.pause(anim_pause)
    # show all rotation axes. Wait for user confirmation
    rot_axes = []
    for rotation in rotations:
        # draw rotation axis
        rot_axes.append(draw_line(ax, rotation[2], rotation[1], length=4)[0])
    plt.pause(anim_pause)
    input("Press Enter to show individual rotations.")
    for line in rot_axes:
        line.remove()
    # plt.show()
    
    # show rotations one after the other. Wait for user confirmation
    i = 0
    while i < len(rotations):
        print(f"Showing rotation {i+1}/{len(rotations)}: Angle: {np.rad2deg(rotations[i][0]):.2f}°, symmetry measure: {rotation_symmetry_measure(X, rotations[i], alpha=alpha):.2f}, Axis: {rotations[i][1]}, Support: {rotations[i][2]}.")
        angle, axis, axis_support = rotations[i]
        plt.pause(anim_pause)
        show_rotation(
                ax,
                X,
                angle,
                axis,
                axis_support,
                anim_time=anim_time,
                anim_steps=anim_steps)
        # user_response = input("Press Enter to show next animation, or type anything to repeat last animation.")
        # if user_response:
        #     continue
        i += 1
    return rotations

def show_rotation(
        ax: plt.Axes,
        X: np.ndarray,
        angle: float,
        axis: np.ndarray,
        axis_support: np.ndarray,
        anim_time: float = 1,
        anim_steps: int = 30,
        anim_pause: float = 2):
    """
    Show the given rotation of a point cloud X around an axis as an animated 3D plot.
    
    Args:
        ax (plt.Axes): matplotlib axis to plot on
        X (np.ndarray): point cloud
        axis (np.ndarray): rotation axis
        angle (float): rotation angle in radians
        anim_time (float, optional): duration of the animation in seconds. Defaults to 1.
    """
    # translate X by axis_support
    X_translated = X - axis_support
    # Create a rotation matrix
    # print(f"Rotating by {np.rad2deg(angle):.2f}° around axis {axis}.")
    rotation = Rotation.from_rotvec(axis * angle/anim_steps)
    # draw rotation axis
    rot_axis_line = draw_line(ax, axis_support, axis, length=4)
    # draw copy of point cloud X_translated
    rotation_points = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c="r", s=150)
    start_time = time.time()
    for i in range(anim_steps):
        # print(f"rotating by {np.rad2deg(angle/anim_steps):.2f}°. Step {i+1}/{anim_steps}.")
        # apply one rotation step
        X_translated = rotation.apply(X_translated)
        # update plot
        rotation_points.remove()
        X_rotated = X_translated + axis_support
        rotation_points = ax.scatter(X_rotated[:, 0], X_rotated[:, 1], X_rotated[:, 2], c="r", s=150)
        # wait for remaining time to next step
        remaining_time = anim_time - time.time() + start_time
        pause_time = max(remaining_time / (anim_steps - i), 0.01)
        plt.draw()
        # time.sleep(pause_time)
        # if pause_time > 0:
        plt.pause(pause_time)
    # remove points after animation
    plt.pause(anim_pause)
    rotation_points.remove()
    for line in rot_axis_line:
        line.remove()

def draw_line(ax: plt.Axes, point: np.ndarray, direction: np.ndarray, length: float = 2, color: str = "#f85"):
    """
    Draw a line in 3D. going `direction*length/2` in either direction of `point`.
    
    Args:
        ax (plt.Axes): matplotlib axis
        point (np.ndarray): point on the line
        direction (np.ndarray): direction vector of the line
        length (float, optional): length of the line. Defaults to 2.
    """
    # Calculate line endpoints
    endpoint1 = point - direction * (length / 2)
    endpoint2 = point + direction * (length / 2)

    # Plot the line
    return ax.plot([endpoint1[0], endpoint2[0]], 
            [endpoint1[1], endpoint2[1]], 
            [endpoint1[2], endpoint2[2]], 
            linestyle='-',
            color=color,)

def draw_edge(ax: plt.Axes, point1: np.ndarray, point2:np.ndarray, color: str = "#000", linewidth: float = 3.0):
    """
    Draw a line connecting two points in 3D.

    Args:
        ax (plt.Axes): matplotlib axis
        point1 (np.ndarray): first point
        point2 (np.ndarray): second point
        color (str, optional): line color. Defaults to "#000".
    return:
        (list[Line3D]): list of lines representing the edge
    """
    return ax.plot(
        [point1[0], point2[0]],
        [point1[1], point2[1]],
        [point1[2], point2[2]],
        linestyle='-',
        linewidth=linewidth,
        color=color,
    )

def main(X, edges=None):
    # # Example Usage
    plane_1 = (np.array([0, 0, 0], dtype=np.float32), np.array([1, 1, 0], dtype=np.float32))
    plane_2 = (np.array([0, 1, 0], dtype=np.float32), np.array([0, 1, 1], dtype=np.float32))
    # plane_2 = (np.array([0, 1, 1], dtype=np.float32), np.array([-1, 2, 1], dtype=np.float32))
    # test_find_plane_intersection(plane_1, plane_2)
    # plot_penalty_function()
    test_find_rotational_symmetries(X, anim_time=1, anim_steps=40, anim_pause=0.5, edges=edges)
    # test_find_rotational_symmetries(X, anim_time=0, anim_steps=6, anim_pause=0.001)

def axis_tetragedron_vertices():
    vertices = np.array([
        [ 1, 0, 0],
        [ 0, 1, 0],
        [ 0, 0, 1],
        [ 0, 0, 0],
    ])
    vertices = vertices - np.mean(vertices, axis=0)
    edges = np.array([
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 3)
    ])
    return vertices, edges

def tetrahedron_vertices():
    vertices = np.array([
        [ 0, 0, 0],
        [ 1, 1, 0],
        [ 1, 0, 1],
        [ 0, 1, 1],
    ])
    # vertices = vertices - np.mean(vertices, axis=0)
    edges = np.array([
        (0, 1), (0, 2), (0, 3),
        (1, 2), (1, 3),
        (2, 3)
    ])
    return vertices, edges

def cube_vertices():
    vertices = np.array([
        [ 1, 1, 1],
        [ 1, 1,-1],
        [ 1,-1, 1],
        [ 1,-1,-1],
        [-1, 1, 1],
        [-1, 1,-1],
        [-1,-1, 1],
        [-1,-1,-1],
    ])
    edges = np.array([
        (0, 1), (0, 2), (0, 4),
        (1, 3), (1, 5),
        (2, 3), (2, 6),
        (3, 7),
        (4, 5), (4, 6),
        (5, 7),
        (6, 7)
    ])
    return vertices, edges

def dodecahedron_vertices():
    """
    Calculates the vertices of a regular dodecahedron centered at the origin 
    and with edge length 2.
    
    Returns:
        np.ndarray: A (20, 3) array where each row represents a vertex (x, y, z).
    """

    phi = (1 + np.sqrt(5)) / 2  # Golden ratio

    vertices = np.array([
        (1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1),
        (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1),
        (0, phi, 1/phi), (0, phi, -1/phi), (0, -phi, 1/phi), (0, -phi, -1/phi),
        (1/phi, 0, phi), (1/phi, 0, -phi), (-1/phi, 0, phi), (-1/phi, 0, -phi),
        (phi, 1/phi, 0), (phi, -1/phi, 0), (-phi, 1/phi, 0), (-phi, -1/phi, 0)
    ])
    edges = np.array([
        (0, 8), (0, 12), (0, 16),
        (1, 9), (1, 13), (1, 16),
        (2, 10), (2, 12), (2, 17),
        (3, 11), (3, 13), (3, 17),
        (4, 8), (4, 14), (4, 18),
        (5, 9), (5, 15), (5, 18),
        (6, 10), (6, 14), (6, 19),
        (7, 11), (7, 15), (7, 19),
        (8, 9),
        (10, 11),
        (12, 14),
        (13, 15),
        (16, 17),
        (18, 19),
        ])

    return vertices, edges

if __name__ == "__main__":
    # tetrahedron corners
    # X, edges = axis_tetragedron_vertices()
    # regular tetrahedron
    # X, edges = tetrahedron_vertices()
    # cube corners
    X, edges = cube_vertices()
    # dodecahedron points
    # X, edges = dodecahedron_vertices()
    # X = X
    main(X, edges)