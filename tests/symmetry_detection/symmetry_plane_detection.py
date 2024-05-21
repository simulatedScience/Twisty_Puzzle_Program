"""
Detect reflectional symmetries in a 3D point cloud. Implemented Algorithm based on (Hruda et. al.)[https://doi.org/10.1007/s00371-020-02034-w]
author: Sebastian Jost
"""
import numpy as np
from scipy.optimize import minimize

def init_planes(X: np.ndarray, num_planes: int = 1000, threshold: float = 0.1) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Generate a set of random planes for symmetry detection by choosing two random points from X and computing the normal vector of the plane spanned by these points. The plane passes through the midpoint between these two points. Repeat `num_planes` times and only keep planes that are not too similar to the existing planes.
    """
    def plane_distance(plane1, plane2):
        """
        Compute the distance between two planes defined by a support point and a normal vector.
        Here, we define distance as the angle between the normal vectors of the planes.
        """
        return np.arccos(np.dot(plane1[1], plane2[1]))
    n: int = X.shape[0]
    found_planes = []
    for _ in range(num_planes):
        # choose two random points
        idx1: int = np.random.randint(0, n-1)
        idx2: int = np.random.randint(idx1 + 1, n)
        # compute normal vector of plane across which one point is reflected to the other
        p1, p2 = X[idx1], X[idx2]
        diff_vector: np.ndarray = p2 - p1
        normal: np.ndarray = diff_vector / np.linalg.norm(diff_vector)
        # compute midpoint
        midpoint: np.ndarray = p1 + diff_vector / 2
        # TODO: check if plane is not too similar to existing planes
        new_plane = (midpoint, normal)
        for plane in found_planes:
            # print(f"{plane_distance(new_plane, plane) = }")
            if plane_distance(new_plane, plane) < threshold:
                break
        else:
            found_planes.append((midpoint, normal))
    return found_planes

def symmetry_measure(X: np.ndarray, plane: tuple[np.ndarray, np.ndarray], alpha: float) -> float:
    """
    Compute the symmetry measure for a set of points X reflected across a plane defined by a midpoint and normal vector.
    Higher symmetry measure indicates higher symmetry.

    Args:
        X (np.ndarray): set of points
        plane (tuple[np.ndarray, np.ndarray]): plane defined by a midpoint and normal vector
        alpha (float): parameter to control the similarity function

    Returns:
        float: symmetry measure in range [0, inf)   (see (Hruda et. al.) Eq. (2))
    """
    def similarity_function(l, alpha):
        """
        measure the similarity of two points based on their distance and the alpha parameter.
        If alpha * distance > 2.6, the similarity is 0.

        Args:
            l (float): distance between two points
            alpha (float): parameter to control the similarity function
        Returns:
            float: similarity between two points
        """
        value = (1 - l / 2.6 * alpha * l)**5 * (8 * (1 / 2.6 * alpha * l)**2 + 5 * (1 / 2.6 * alpha * l) + 1)
        return np.where(alpha * l <= 2.6, value, 0)

    n: int = X.shape[0] # number of points
    transformed_X = reflect_points_across_plane(X, plane[0], plane[1])
    similarity_measure = 0
    for i in range(n):
        for j in range(n):
            distance = np.linalg.norm(transformed_X[i] - X[j])
            similarity_measure += similarity_function(distance, alpha)
    return similarity_measure

def find_symmetry_planes(
        X: np.ndarray,
        num_planes: int = 1000,
        threshold: float = 0.1,
        alpha: float = 1.0,
        S: int = 5,
    ) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Find the best symmetry planes and optimize over them.

    Args:
        X (np.ndarray): set of points
        num_planes (int): number of planes to generate
        threshold (float): threshold to check if a plane is too similar to existing planes
        alpha (float): parameter to control the similarity function
        S (int): number of best planes to keep

    Returns:
        list[tuple[np.ndarray, np.ndarray]]: list of best symmetry planes
    """
    planes = init_planes(X, num_planes, threshold)
    best_planes = []
    best_scores = []
    # choose planes with best symmetry measure
    for plane in planes:
        score = symmetry_measure(X, plane, alpha)
        if len(best_scores) < S or score > min(best_scores):
            if len(best_scores) >= S:
                min_index = np.argmin(best_scores)
                best_scores[min_index] = score
                best_planes[min_index] = plane
            else:
                best_scores.append(score)
                best_planes.append(plane)
    # optimize with the best planes as starting points
    def objective(plane_components):
        support: np.ndarray = plane_components[:3]
        normal: np.ndarray = plane_components[3:]
        plane = (support, normal)
        return -symmetry_measure(X, plane, alpha)
    for plane in best_planes:
        minimize(objective, np.concatenate(plane), method="L-BFGS-B")
    return best_planes

def reflect_points_across_plane(X: np.ndarray, support: np.ndarray, normal: np.ndarray):
    """
    Given a plane defined by a point `support` and normal vector `normal`, reflect a set of points `X` across the plane.

    Args:
        X (np.ndarray): set of points to be reflected across the plane
        support (np.ndarray): point on the plane
        normal (np.ndarray): normal vector of the plane (normalized)

    Returns:
        np.ndarray: set of reflected points
    """
    # Ensure the normal vector is a unit vector
    normal = normal / np.linalg.norm(normal)
    # Calculate the vector from point p to each point in X
    X_minus_p = X - support
    # Project X_minus_p onto the normal vector n
    projection = np.dot(X_minus_p, normal)[:, np.newaxis] * normal
    # Reflect X across the plane
    X_reflected = X - 2 * projection
    return X_reflected

def calculate_centroid(X: np.ndarray) -> np.ndarray:
    """
    Calculate the centroid of a set of points.

    Args:
        X (np.ndarray): set of points

    Returns:
        np.ndarray: centroid of the points
    """
    return np.mean(X, axis=0)
