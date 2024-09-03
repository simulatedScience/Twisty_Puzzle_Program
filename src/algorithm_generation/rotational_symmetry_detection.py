
"""
This moidule implements rotational symmetry detection for a 3D point cloud as described in [Hruda et. al.](https://doi.org/10.1016/j.cagd.2022.102138) [1].
author: Sebastian Jost
"""
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R
from scipy.spatial.transform import Slerp

from symmetry_plane_detection import find_symmetry_planes, dist_similarity_function, centroid

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
        tuple[np.ndarray, np.ndarray]: intersection line defined by a point and a normalized direction vector
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
    # TODO: Optimize by exploiting the locality of the symmetry measure (use cell-list or similar data structure)
    n: int = X.shape[0]  # number of points
    transformed_X = rotate_points(X, rotation[0], rotation[1])
    
    pairwise_distances = np.linalg.norm(transformed_X[:, np.newaxis] - X, axis=2)
    # Apply the distance similarity function to all distances
    similarity_measures = dist_similarity_function(pairwise_distances, alpha)
    # Sum all the similarity measures
    similarity_measure = np.sum(similarity_measures)
    
    # similarity_measure = 0
    # for i in range(n):
    #     distances = np.linalg.norm(transformed_X[i] - X, axis=1)
    #     similarity_measures = dist_similarity_function(distances, alpha)
    #     similarity_measure += np.sum(similarity_measures)
    
        # for j in range(n):
        #     distance = np.linalg.norm(transformed_X[i] - X[j])
        #     similarity_measure += dist_similarity_function(distance, alpha)
    # small angle penalization
    similarity_measure *= penalty(rotation[0])
    
    if hasattr(rotation_symmetry_measure, "run_count"):
        rotation_symmetry_measure.run_count += 1
    else:
        rotation_symmetry_measure.run_count = 1
    return similarity_measure

def find_rotational_symmetries(
        X: np.ndarray,
        num_planes: int = 3000,
        num_candidate_rotations: int = 30,
        threshold: float = 0.1,
        min_angle: float = np.pi / 12.5,
        num_best_rotations: int = 30,
        alpha: float = 1.0,
        epsilon_Q: float = 0.05,
        epsilon_s: float = 0.05, # should be 0.05 l_avg
        min_score_ratio: float = 0.7,
    ) -> list[tuple[np.ndarray, float]]:
    """
    Detect rotational symmetries in a 3D point cloud.

    Args:
        X (np.ndarray): set of points
        num_planes (int): number of planes to generate
        num_candidate_rotations (int): number of candidate rotations to generate
        threshold (float): threshold to check if a plane is too similar to existing planes
        min_angle (float): minimum angle between two planes to consider them for rotation detection in radians (Default: np.pi / 12.5 = just under 15°)
        num_best_rotations (int): number of best rotations to keep
        alpha (float): parameter to control the similarity function
        epsilon_Q (float): tolerance for quaternion similarity
        epsilon_s (float): tolerance for axis support similarity
        min_score_ratio (float): minimum score relative to the best score to keep a rotation
    Returns:
        list[tuple[np.ndarray, float]]: list of rotational symmetries (axis, angle) detected
    """
    # Step 0: center point cloud around origin
    X_shift = centroid(X)
    X = X - X_shift
    # Step 1: Find reflectional symmetry planes
    planes = find_symmetry_planes(X, num_planes, threshold, S=num_candidate_rotations)
    print(f"Found {len(planes)} symmetry planes.")
    print(f"Searching {((len(planes)-1)**2+len(planes)-1)//2} rotation candidates.")

    # Step 2: Find rotation candidates
    #   2.1 find intersections of pairs of planes
    #   2.2 prune candidates that are too similar to existing ones
    pruned_candidates = []
    k = 0
    for idx_1, plane_1 in enumerate(planes[:-1]):
        for idx_2, plane_2 in enumerate(planes[idx_1+1:]):
            k += 1
            # print(f"{np.dot(plane_1[1], plane_2[1]) = }")
            rotation_angle: float = 2*np.arccos(np.dot(plane_1[:3], plane_2[:3]))  # angle of rotation = 2*angle between normals
            # reject planes that are too similar (small rotation angle)
            if rotation_angle < min_angle:
                # print("Skipping due to low angle")
                continue
            intersection = find_plane_intersection(plane_1, plane_2)
            if intersection is None:
                # print("Skipping due to parallel planes")
                continue # planes are parallel (should never happen here)
            if not rotation_angle or np.isnan(rotation_angle):
                # This should never happen
                # raise ValueError("Encountered invalid rotation_angle")
                from symmetry_plane_detection import plane_distance
                print(f"dot product of plane normals: {np.dot(plane_1[:3], plane_2[:3])}")
                print(f"plane_1 {idx_1}: {(plane_1)}")
                print(f"plane_2 {idx_1+1+idx_2}: {(plane_2)}")
                print(f"Encountered invalid rotation_angle: {rotation_angle}")
                print(f"plane distance: {plane_distance(plane_1, plane_2)}")
                # print(f"plane intersection: {intersection}")
                print()
                import matplotlib.pyplot as plt
                from test_symmetry_plane_detection import draw_plane, set_equal_aspect_3d
                # create a 3D plot
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                # plot the points
                ax.scatter(X[:, 0], X[:, 1], X[:, 2], c='b', marker='o')
                # plot the planes
                draw_plane(ax, plane_1, show_normal=True)
                draw_plane(ax, plane_2, show_normal=True)
                # draw_plane(ax, p, n, show_normal=False)
                set_equal_aspect_3d(ax)
                plt.title("Initial planes for symmetry detection")
                plt.show()
                continue
            axis_support, axis = intersection
            # make sure rotation_angle is in [min_angle, pi]
            rotation_angle = rotation_angle % (2*np.pi)
            if rotation_angle > np.pi:
                rotation_angle = 2*np.pi - rotation_angle
            # Step 2.2: Prune rotation candidates if they are too similar to existing ones
            quaternion = R.from_rotvec(rotation_angle * axis).as_quat()
            # candidate: (quaternion, axis_support) = (Q,s) in paper [1]
            for i, (Q_i, s_i, w_i) in enumerate(pruned_candidates):
                
                if (rotation_distance(epsilon_Q, epsilon_s, axis_support, quaternion, Q_i, s_i)):
                    # Merge the candidates
                    new_weight = w_i + 1 # w(quarternion, axis_support) := 1
                    s_new = (w_i * s_i + axis_support) / new_weight
                    
                    # Use Slerp for quaternion interpolation
                    key_rots = R.from_quat([Q_i, quaternion])
                    slerp = Slerp([0, 1], key_rots)
                    Q_new = slerp(1 / new_weight).as_quat()
                    # check norm of quaternion
                    # if np.abs(np.linalg.norm(quaternion[:3]) - 1) > 1e-10:
                    #     print(f"Encountered Q_avg with norm < 1: {quaternion}, norm = {np.linalg.norm(quaternion[:3])}")
                    #     continue
                    pruned_candidates[i] = (Q_new, s_new, new_weight)
                    break
            else:
                # if np.abs(np.linalg.norm(quaternion[:3]) - 1) > 1e-10:
                #     print(f"Encountered Q_new with norm < 1: {quaternion}, norm = {np.linalg.norm(quaternion[:3])}")
                #     quaternion = quaternion / np.linalg.norm(quaternion[:3])
                # if float("nan") in quaternion:
                #     print(f"Encountered nan in quaternion: {quaternion}")
                # if np.nan in quaternion:
                #     print(f"Encountered nan in quaternion: {quaternion}")
                # # else:
                # axis2 = R.from_quat(quaternion)
                pruned_candidates.append((quaternion, axis_support, 1)) # (Q, s, w(Q, s))
    # Step 3: Evaluate candidate rotations and find best ones
    best_rotations = []
    best_scores = []
    for Q, s, _ in pruned_candidates: # weights (w(Q, s)) are no longer needed
        axis = R.from_quat(Q)
        axis = axis.as_rotvec()
        rotation_angle = np.linalg.norm(axis)
        axis /= rotation_angle
        X_translated = X - s
        score = rotation_symmetry_measure(X_translated, rotation=(rotation_angle, axis), alpha=alpha)
        if len(best_scores) < num_best_rotations or score > min(best_scores):
            if len(best_scores) >= num_best_rotations:
                min_index = np.argmin(best_scores)
                best_scores[min_index] = score
                best_rotations[min_index] = (rotation_angle, axis, s)
            else:
                best_scores.append(score)
                best_rotations.append((rotation_angle, axis, s))

    # Step 4: remove rotations with score < best_score * min_score_ratio
    best_score = max(best_scores)
    best_rotations = [rotation for rotation, score in zip(best_rotations, best_scores) if score >= best_score * min_score_ratio]
    del best_scores # best_scores no longer accurate since best_rotations has been pruned

    def objective(rotation_components):
        angle: float = rotation_components[0]
        axis: np.ndarray = rotation_components[1:4]
        # axis_support: np.ndarray = rotation_components[4:]
        X_translated: np.ndarray = X - axis_support
        return -rotation_symmetry_measure(X_translated, (angle, axis), alpha)
    def concat_rotation(rotation):
        # return np.array([rotation[0], *rotation[1], *rotation[2]])
        return np.array([rotation[0], *rotation[1]])
    symmetry_rotations = []
    for rotation in best_rotations:
        result = minimize(objective, concat_rotation(rotation), method="L-BFGS-B")
        # symmetry_rotations.append((result.x[0], result.x[1:4], result.x[4:]))
        symmetry_rotations.append((result.x[0], result.x[1:4], np.zeros(3)))
    # Step 5: Prune rotations that are too similar to existing ones
    
    # Step 6: Find all possible rotation angles for each axis
    
    # Step 7: Shift back to original coordinates
    symmetry_rotations = [(angle, axis, axis_support + X_shift) for angle, axis, axis_support in symmetry_rotations]
    return symmetry_rotations

def rotation_distance(epsilon_Q, epsilon_s, axis_support, quaternion, Q_i, s_i):
    return np.linalg.norm(
        quaternion - Q_i * np.sign(np.dot(quaternion, Q_i))) < epsilon_Q and \
        np.linalg.norm(axis_support - s_i) < epsilon_s

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
    rotation = R.from_rotvec(angle * axis)
    return rotation.apply(X)
