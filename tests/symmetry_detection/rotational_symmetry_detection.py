
"""
This moidule implements rotational symmetry detection for a 3D point cloud as described in (Hruda et. al.) [https://doi.org/10.1016/j.cagd.2022.102138].
author: Sebastian Jost
"""

import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation

from symmetry_plane_detection import find_symmetry_planes, dist_similarity_function

def find_plane_intersection(
        plane_1: np.ndarray,
        plane_2: np.ndarray,
        tol=1e-15) -> tuple[np.ndarray, np.ndarray]:
    """
    Given two planes defined by coefficients (a, b, c, d), find their intersection line.
    If the planes are parallel, return None.

    Args:
        plane_1 (np.ndarray): coefficients of the first plane equation (a, b, c, d)
        plane_2 (np.ndarray): coefficients of the second plane equation (a, b, c, d)
        tol (float, optional): tolerance for detecting parallel planes. Defaults to 1e-15.

    Returns:
        tuple[np.ndarray, np.ndarray]: intersection line defined by a point and a direction vector
    """
    # Extract plane coefficients
    a1, b1, c1, d1 = plane_1
    a2, b2, c2, d2 = plane_2
    # Normal vectors of the planes
    normal1 = plane_1[:3]
    normal2 = plane_2[:3]
    # Ensure the normal vectors are unit vectors
    normal1 = normal1 / np.linalg.norm(normal1)
    normal2 = normal2 / np.linalg.norm(normal2)
    # Calculate the direction vector of the line (cross product of normals)
    direction = np.cross(normal1, normal2)
    norm = np.linalg.norm(direction)
    if norm < tol:
        # If the direction vector is nearly zero, the planes are parallel
        return None
    direction = direction / norm
    # To find a point on the line, solve the system of equations
    # a1*x + b1*y + c1*z + d1 = 0
    # a2*x + b2*y + c2*z + d2 = 0
    A = np.array([[a1, b1, c1], [a2, b2, c2]])
    b = np.array([-d1, -d2])
    # Find a particular solution using least squares (there are infinitely many solutions)
    point = np.linalg.lstsq(A, b, rcond=None)[0]

    return point, direction

def closest_point_on_line(ref_point, line_point, line_direction):
    """Finds the closest point on a line to a reference point.

    Args:
        ref_point (np.ndarray): The reference point (shape: (3,))
        line_point (np.ndarray): A point on the line (shape: (3,))
        line_direction (np.ndarray): The direction vector of the line (shape: (3,))

    Returns:
        np.ndarray: The closest point on the line to the reference point (shape: (3,))
    """
    v = ref_point - line_point
    t = np.dot(v, line_direction) / np.dot(line_direction, line_direction)
    closest_point = line_point + t * line_direction
    return closest_point

def rotation_symmetry_measure(X: np.ndarray, rotation: tuple[float, np.ndarray], alpha: float) -> float:
    """
    Compute the symmetry measure for a set of points X rotated around an axis by a certain angle (in radians).
    Higher symmetry measure indicates higher symmetry.
    
    Args:
        X (np.ndarray): set of points
        rotation (tuple[float, np.ndarray]): rotation defined by an angle and an axis
        alpha (float): parameter to control the similarity function
        
    Returns:
        float: symmetry measure in range [0, inf) (see (Hruda et. al.) Eq. (3))
    """
    
    n: int = X.shape[0]  # number of points
    transformed_X = rotate_points(X, rotation[0], rotation[1])
    similarity_measure = 0
    for i in range(n):
        for j in range(n):
            distance = np.linalg.norm(transformed_X[i] - X[j])
            similarity_measure += dist_similarity_function(distance, alpha)
    # small angle penalization
    similarity_measure *= penalty(rotation[0])
    return similarity_measure

def find_rotational_symmetries(
        X: np.ndarray,
        num_planes: int = 3000,
        num_candidate_rotations: int = 30,
        threshold: float = 0.1,
        min_angle: float = np.pi / 12.5,
        num_best_rotations: int = 30,
        alpha: float = 1.0,
    ) -> list[tuple[np.ndarray, float]]:
    """
    Detect rotational symmetries in a 3D point cloud.

    Args:
        X (np.ndarray): set of points
        num_planes (int): number of planes to generate
        threshold (float): threshold to check if a plane is too similar to existing planes

    Returns:
        list[tuple[np.ndarray, float]]: list of rotational symmetries (axis, angle) detected
    """
    # Step 1: Find reflectional symmetry planes
    planes = find_symmetry_planes(X, num_planes, threshold, S=num_candidate_rotations)

    # Step 2: Find intersections of the planes
    best_rotations = []
    best_scores = []
    for _ in range(num_planes//10):
        idx_1: int = np.random.randint(len(planes) - 1)
        idx_2: int = np.random.randint(idx_1 + 1, len(planes))
        plane_1 = planes[idx_1]
        plane_2 = planes[idx_2]
        # print(f"{np.dot(plane_1[1], plane_2[1]) = }")
        intersection_angle: float = np.arccos(np.dot(plane_1[:3], plane_2[:3]))  # angle between normals
        # reject planes that are too similar (small rotation angle)
        if intersection_angle < min_angle/2:
            continue
        intersection = find_plane_intersection(plane_1, plane_2)
        if intersection is None:
            continue # planes are parallel (should never happen here)
        axis_support, axis = intersection
        rotation_angle: float = 2*intersection_angle
        # make sure rotation_angle is in [-pi, pi]
        rotation_angle = rotation_angle % (2*np.pi)
        if rotation_angle > np.pi:
            rotation_angle -= 2*np.pi
        # translate X by line_support
        X_translated: np.ndarray = X - axis_support
        score = rotation_symmetry_measure(X_translated, rotation=(rotation_angle, axis), alpha=alpha)
        if len(best_scores) < num_best_rotations or score > min(best_scores):
            if len(best_scores) >= num_best_rotations:
                min_index = np.argmin(best_scores)
                best_scores[min_index] = score
                best_rotations[min_index] = (rotation_angle, axis, axis_support)
            else:
                best_scores.append(score)
                best_rotations.append((rotation_angle, axis, axis_support))
    def objective(rotation_components):
        angle: float = rotation_components[0]
        axis: np.ndarray = rotation_components[1:4]
        axis_support: np.ndarray = rotation_components[4:]
        X_translated: np.ndarray = X - axis_support
        return -rotation_symmetry_measure(X_translated, (angle, axis), alpha)
    def concat_rotation(rotation):
        return np.array([rotation[0], *rotation[1], *rotation[2]])
    symmetry_rotations = []
    for rotation in best_rotations:
        result = minimize(objective, concat_rotation(rotation), method="L-BFGS-B")
        symmetry_rotations.append((result.x[0], result.x[1:4], result.x[4:]))
    return symmetry_rotations

def penalty(angle, min_angle=np.pi/25, max_angle=np.pi/13, alpha: float = 0.1):
    """
    Calculates a penalty based on the distance of an angle (or angles in a NumPy array) from a desired range.
    Penalty is 0 if the angle is smaller than `min_angle` and 1 if the angle is larger than `max_angle`. Differentiably and monotonically changes in between.

    Args:
        angle (float or np.ndarray): angle(s) to calculate the penalty for
        min_angle (float, optional): minimum angle in the desired range. Defaults to np.pi/25.
        max_angle (float, optional): maximum angle in the desired range. Defaults to np.pi/13.
        alpha (float, optional): spread parameter to control the smoothness of the penalty function. Defaults to 0.1.
    """
    if isinstance(angle, np.ndarray):
        return np.array([penalty(a, min_angle, max_angle, alpha) for a in angle])
    angle = angle % (2*np.pi)
    if angle > np.pi:
        angle -= 2*np.pi
    if abs(angle) > max_angle:
        return 1
    else:
        return dist_similarity_function(alpha * ((abs(angle) - max_angle) * 2.6 / (min_angle - max_angle)))

def rotate_points(X: np.ndarray, angle: float, axis: np.ndarray, tol: float = 1e-15) -> np.ndarray:
    """
    Rotate a set of points around an axis by a certain angle (in radians).

    Args:
        X (np.ndarray): set of points
        angle (float): angle to rotate by (in radians)
        axis (np.ndarray): axis to rotate around

    Returns:
        np.ndarray: rotated points
    """
    norm = np.linalg.norm(axis)
    if norm - 1 > tol:
        # normalize axis
        axis = axis / norm
    rotation = Rotation.from_rotvec(angle * axis)
    return rotation.apply(X)
