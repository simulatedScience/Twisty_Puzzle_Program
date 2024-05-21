"""
This moidule implements rotational symmetry detection for a 3D point cloud as described in https://doi.org/10.1016/j.cagd.2022.102138.
author: Gemini Advanced (Gemini 1.5 Pro) (17.05.2024) & Sebastian Jost
"""

import numpy as np
from scipy.spatial import distance_matrix
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R

def detect_rotational_symmetry(points, num_candidates=5, angle_threshold=30):
    """
    Detects rotational symmetries in a 3D point cloud.

    Args:
        points: A numpy array of shape (n, 3) representing the 3D point cloud.
        num_candidates: The number of candidate rotations to consider.
        angle_threshold: The minimum rotation angle to consider (in degrees).

    Returns:
        A list of tuples, where each tuple contains:
            - The axis of rotation (a numpy array of shape (3,)).
            - The angle of rotation (in degrees).
    """

    # Step 1: Simplify Point Cloud (Not needed for small point clouds)
    Xsimp = points  # Use the original points directly

    # Step 2: Generate Candidate Planes
    distances = distance_matrix(Xsimp, Xsimp)
    pairs = np.argwhere(distances < 0.1 * np.mean(distances))  # Adjust threshold as needed
    candidate_planes = []
    for i, j in pairs:
        if i < j:  # Avoid duplicates
            midpoint = (Xsimp[i] + Xsimp[j]) / 2
            normal = Xsimp[i] - Xsimp[j]
            candidate_planes.append((midpoint, normal))

    # Step 3: Evaluate Candidate Planes (Simplified for small point clouds)
    def symmetry_measure(plane):
        midpoint, normal = plane
        reflected_points = Xsimp - 2 * np.dot(Xsimp - midpoint, normal)[:, np.newaxis] * normal
        return -np.sum(np.linalg.norm(reflected_points - Xsimp, axis=1))  # Negative for minimization

    candidate_planes = sorted(candidate_planes, key=symmetry_measure, reverse=True)[:num_candidates]

    # Step 4: Create Candidate Rotations
    candidate_rotations = []
    for i in range(num_candidates):
        for j in range(i + 1, num_candidates):
            midpoint1, normal1 = candidate_planes[i]
            midpoint2, normal2 = candidate_planes[j]
            axis = np.cross(normal1, normal2)
            angle = 2 * np.arccos(np.dot(normal1, normal2)) * 180 / np.pi

            if angle > angle_threshold:
                # Calculate origin as the closest point on the axis to the centroid
                centroid = np.mean(points, axis=0)
                origin = midpoint1 + np.dot(centroid - midpoint1, axis) / np.dot(axis, axis) * axis
                candidate_rotations.append((axis, angle, origin))

    # Step 5: Prune Candidate Rotations (Not needed for small number of candidates)

    # Step 6: Evaluate Candidate Rotations (Simplified for small point clouds)
    candidate_rotations = sorted(candidate_rotations, key=lambda rot: symmetry_measure((rot[0], rot[1])), reverse=True)[:num_candidates]

    # Step 7: Optimize Rotations (Simplified for small point clouds)
    def rotation_cost(params):
        axis = params[:3]
        angle = params[3]
        origin = params[4:7]  # Extract origin from parameters
        rotated_points = rotate_points(Xsimp, axis, angle, origin)
        return -np.sum(np.linalg.norm(rotated_points - Xsimp, axis=1))

    symmetries = []
    for axis, angle in candidate_rotations:
        result = minimize(rotation_cost, np.hstack([axis, angle]), method='L-BFGS-B')
        symmetries.append((result.x[:3], result.x[3]))

    return symmetries

def rotate_points(points, axis, angle, origin):
    """
    Rotates 3D points around an axis passing through an origin.

    Args:
        points: A numpy array of shape (n, 3) representing the 3D points.
        axis: A numpy array of shape (3,) representing the rotation axis.
        angle: The rotation angle in degrees.
        origin: A numpy array of shape (3,) representing a point on the rotation axis.

    Returns:
        A numpy array of shape (n, 3) representing the rotated points.
    """
    r = R.from_rotvec(np.radians(angle) * axis)
    return r.apply(points - origin) + origin

if __name__ == "__main__":
    # Example Usage
    points = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]])
    symmetries = detect_rotational_symmetry(points)
    for axis, angle in symmetries:
        print(f"Axis: {axis}, Angle: {angle}")
    # make 3D plot of points and rotation axes
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(points[:, 0], points[:, 1], points[:, 2])
    for axis, angle in symmetries:
        ax.quiver(*np.mean(points, axis=0), *axis, length=0.5, color='r')
    plt.show()
