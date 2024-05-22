import time

import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial.transform import Rotation

from rotational_symmetry_detection import find_plane_intersection, penalty, find_rotational_symmetries, rotation_symmetry_measure
from symmetry_plane_detection import dist_similarity_function
from test_symmetry_plane_detection import draw_plane

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
    plt.show()
    return intersection

def plot_penalty_function():
    x = np.linspace(0, np.pi, 10000)
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
        num_candidate_rotations: int = 30,
        threshold: float = 0.1,
        min_angle: float = np.pi / 12.5,
        num_best_rotations: int = 30,
        alpha: float = 1.0,
        anim_time: float = 1,
        anim_steps: int = 60,
        anim_pause: float = 2,
    ) -> list[tuple[np.ndarray, float]]:
    rotations = find_rotational_symmetries(
        X=X,
        num_planes=num_planes,
        num_candidate_rotations=num_candidate_rotations,
        threshold=threshold,
        min_angle=min_angle,
        num_best_rotations=num_best_rotations,
        alpha=alpha,
    )
    print(f"Found {len(rotations)} rotational symmetries.")
    # create 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # show point cloud X
    ax.scatter(X[:, 0], X[:, 1], X[:, 2])
    # for rotation in rotations:
    #     # draw rotation axis
    #     draw_line(ax, rotation[2], rotation[1], length=2)
    # plt.show()
    plt.ion()
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
    rot_axis_line = draw_line(ax, axis_support, axis, length=2)
    # draw copy of point cloud X_translated
    rotation_points = ax.scatter(X[:, 0], X[:, 1], X[:, 2], c="r")
    start_time = time.time()
    for i in range(anim_steps):
        # print(f"rotating by {np.rad2deg(angle/anim_steps):.2f}°. Step {i+1}/{anim_steps}.")
        # apply one rotation step
        X_translated = rotation.apply(X_translated)
        # update plot
        rotation_points.remove()
        X_rotated = X_translated + axis_support
        rotation_points = ax.scatter(X_rotated[:, 0], X_rotated[:, 1], X_rotated[:, 2], c="r")
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

def draw_line(ax: plt, point: np.ndarray, direction: np.ndarray, length: float = 2):
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
            'r-')

def main():
    # # Example Usage
    # plane_1 = (np.array([0, 0, 0], dtype=np.float32), np.array([1, 1, 0], dtype=np.float32))
    # # plane_2 = (np.array([0, 1, 0], dtype=np.float32), np.array([0, 1, 1], dtype=np.float32))
    # plane_2 = (np.array([0, 1, 1], dtype=np.float32), np.array([-1, 2, 1], dtype=np.float32))
    # test_find_plane_intersection(plane_1, plane_2)
    # tetrahedron corners
    # X = np.array([
    #     [ 1, 0, 0],
    #     [ 0, 1, 0],
    #     [ 0, 0, 1],
    #     [ 0, 0, 0],
    # ])
    # regular tetrahedron
    X = np.array([
        [ 0, 0, 0],
        [ 1, 1, 0],
        [ 1, 0, 1],
        [ 0, 1, 1],
    ])
    # cube corners
    # X = np.array([
    #     [ 1, 1, 1],
    #     [ 1, 1,-1],
    #     [ 1,-1, 1],
    #     [ 1,-1,-1],
    #     [-1, 1, 1],
    #     [-1, 1,-1],
    #     [-1,-1, 1],
    #     [-1,-1,-1],
    # ])
    # dodecahedron points
    X = dodecahedron_vertices()
    test_find_rotational_symmetries(X, anim_time=1, anim_steps=60, anim_pause=2)
    # test_find_rotational_symmetries(X, anim_time=0, anim_steps=6, anim_pause=0.001)

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

    return vertices

if __name__ == "__main__":
    # plot_penalty_function()
    main()