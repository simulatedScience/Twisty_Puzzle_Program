"""
Detect reflectional symmetries in a 3D point cloud. Implemented Algorithm based on [1]

author: Sebastian Jost

References:
[1] [Hruda et. al.](https://doi.org/10.1007/s00371-020-02034-w)
"""
import numpy as np
from scipy.optimize import minimize

def init_planes(
        X: np.ndarray,
        num_planes: int = 1000,
        threshold: float = 0.1,
    ) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Generate a set of random planes for symmetry detection by choosing two random points from X and computing the normal vector of the plane spanned by these points. The plane passes through the midpoint between these two points. Repeat `num_planes` times and only keep planes that are not too similar to the existing planes.
    """
    n: int = X.shape[0]
    found_planes: dict[tuple[float, float, float, float], tuple[np.ndarray, int]] = {}
    # for idx_1, p1 in enumerate(X[:-1]):
    #     for p2 in X[idx_1+1:]:
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
            new_plane = plane_point_normal2standard_form((midpoint, normal))
            new_plane_key = tuple(new_plane)
            # plane_key is a 4-tuple describing the plane in standard form (0 = ax+by+cz+d)
            # values: plane as 4D numpy vector and int counting how many planes were averaged to get this one
            add_new_plane: bool = True
            for plane_key, (plane, num) in list(found_planes.items()):
                # print(f"{plane_distance(new_plane, plane) = }")
                if (dist := plane_distance(new_plane, plane)) < threshold:
                    if dist < threshold/10: # planes are almost identical, no furhter averaging needed
                        # print(f"Planes are almost identical: {new_plane} and {plane},\n\tdistance: {dist}")
                        add_new_plane: bool = False
                        break
                    avg_plane: np.ndarray = average_planes(new_plane, plane)
                    avg_plane_key: tuple[float] = tuple(avg_plane)
                    found_planes[avg_plane_key] = (avg_plane, num + 1)
                    if not avg_plane_key == plane_key:
                        del found_planes[plane_key]
                    new_plane_key = avg_plane_key
                    new_plane = avg_plane
                    add_new_plane: bool = False
                    # break
            if add_new_plane:
                found_planes[new_plane_key] = (new_plane, 1)
            # if prev_len == len(found_planes):
            #     print(f"Added plane: {new_plane}")
            # else:
            #     print(f"Old planes: {prev_len}, new planes: {len(found_planes)}")
    planes = [plane for plane, _ in found_planes.values()] # extract planes in standard form
    return planes

def average_planes(
        plane_1: np.ndarray,
        plane_2: np.ndarray,
    ) -> np.ndarray:
    """
    Average two planes in standard form by adding their coefficients.
    Given two planes in standard form 0=<(a,b,c,d),(x,y,z,1)>, we add the coefficients to get the average plane.
    If the angle between the planes normal vectors (a,b,c) is greater than 90 degrees, we subtract the coefficients to get a new plane that is closer to both planes.

    Args:
        plane_1 (np.ndarray): plane in standard form (a,b,c,d)
        plane_2 (np.ndarray): plane in standard form (a,b,c,d)

    Returns:
        np.ndarray: average plane in standard form (a,b,c,d)
    """
    # print(f"averaging {plane_1} and {plane_2}")
    if np.dot(plane_1[:3], plane_2[:3]) >= 0:
        new_plane = plane_1 + plane_2
        # normalize first three components
        new_plane[:3] = new_plane[:3] / np.linalg.norm(new_plane[:3])
        return new_plane
    new_plane = plane_1 - plane_2
    # normalize first three components
    new_plane[:3] = new_plane[:3] / np.linalg.norm(new_plane[:3])
    return new_plane

def plane_distance(plane_1: np.ndarray, plane_2: np.ndarray, l_avrg=1) -> float:
    """
    Given two planes in standard form 0=<(a,b,c,d),(x,y,z,1)>, compute the distance between them as described in [1] Eq. 4.:
    D(p_1, p_2) = ||p_1 - p_2|| if <n_1, n_2> >=0 or ||p_1 + p_2|| otherwise.
    """
    normal_1: np.ndarray = plane_1[:3]
    normal_2: np.ndarray = plane_2[:3]
    if np.dot(normal_1, normal_2) >= 0:
        return np.linalg.norm(plane_1 - plane_2)
    else:
        return np.linalg.norm(plane_1 + plane_2)

def plane_point_normal2standard_form(plane: tuple[np.ndarray, np.ndarray], l_avrg=1) -> np.ndarray:
    """
    Convert a plane defined by a support point q_p and a normal vector n_p into standard form 0=<(a,b,c,-d),(x,y,z,1)>.
    With these coefficients, define the plane p as the vector (a,b,c,d/l_avrg).

    Args:
        plane (tuple[np.ndarray, np.ndarray]): plane defined by a support point and a normal vector
        l_avrg (float): average distance between points in the point cloud

    Returns:
        np.ndarray: plane in standard form (a,b,c,-d/l_avrg) / ||n_p||
    """
    standard_plane = np.append(plane[1], np.dot(plane[1], plane[0]) / l_avrg)
    # normalize the normal vector
    standard_plane[:3] = standard_plane[:3] / np.linalg.norm(standard_plane[:3])
    return standard_plane

def dist_similarity_function(dist: float, alpha: float = 15) -> float:
    """
    measure the similarity of two points based on their distance and an `alpha` parameter.
    If alpha * distance > 2.6, the similarity is 0.

    Args:
        l (float): distance between two points
        alpha (float): parameter to control the similarity function
    Returns:
        float: similarity between two points
    """
    value = (1 - 1 / 2.6 * alpha * dist)**5 * \
        (8 * (1 / 2.6 * alpha * dist)**2 + 5 * (1 / 2.6 * alpha * dist) + 1)
    return np.where(alpha * dist <= 2.6, value, 0)
    # if alpha * dist > 2.6:
    #     return 0
    # else:
    #     value = (1 - 1 / 2.6 * alpha * dist)**5 * \
    #         (8 * (1 / 2.6 * alpha * dist)**2 + 5 * (1 / 2.6 * alpha * dist) + 1)
    #     return value

def reflect_symmetry_measure(X: np.ndarray, plane: np.ndarray, alpha: float) -> float:
    """
    Compute the symmetry measure for a set of points X reflected across a plane defined by a midpoint and normal vector.
    Higher symmetry measure indicates higher symmetry.

    Args:
        X (np.ndarray): set of points
        plane (np.ndarray): plane defined by a midpoint and normal vector
        alpha (float): parameter to control the similarity function

    Returns:
        float: symmetry measure in range [0, inf)   (see Ref.[1] Eq. (2))
    """
    n: int = X.shape[0] # number of points
    transformed_X = reflect_points_across_plane(X, plane)
    # transformed_X = reflect_points_across_plane(X, plane[0], plane[1])
    # similarity_measure = 0
    pairwise_distances = np.linalg.norm(transformed_X[:, np.newaxis] - X, axis=2)
    # Apply the distance similarity function to all distances
    similarity_measures = dist_similarity_function(pairwise_distances, alpha)
    # Sum all the similarity measures
    similarity_measure = np.sum(similarity_measures)
    if hasattr(reflect_symmetry_measure, "run_count"):
        reflect_symmetry_measure.run_count += 1
    else:
        reflect_symmetry_measure.run_count = 1
    return similarity_measure

def find_symmetry_planes(
        X: np.ndarray,
        num_planes: int = 1000,
        threshold: float = 0.1,
        alpha: float = 1.0,
        S: int = 5,
        min_score_ratio: float = 0.95,
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
    print(f"Initalized {len(planes)} planes.")
    best_planes = []
    best_scores = []
    # choose planes with best symmetry measure
    for plane in planes:
        score = reflect_symmetry_measure(X, plane, alpha)
        if len(best_planes) < S:
            best_scores.append(score)
            best_planes.append(plane)
        elif score > min(best_scores):
            min_index = np.argmin(best_scores)
            best_scores[min_index] = score
            best_planes[min_index] = plane
    print(f"Selected {len(best_planes)}/{S} possible symmetry planes.")
    best_score = max(best_scores)
    best_planes = [plane for plane, score in zip(best_planes, best_scores) if score >= best_score * min_score_ratio]
    del best_scores # free memory, this list is no longer accurate or needed.
    print(f"Optimizing {len(best_planes)} best planes.")
    # optimize with the best planes as starting points
    def objective(plane):
        # normalize the normal vector
        plane[:3] = plane[:3] / np.linalg.norm(plane[:3])
        return -reflect_symmetry_measure(X, plane, alpha)
    symmetry_planes = []
    for plane in best_planes:
        result = minimize(objective, plane, method="L-BFGS-B")
        symmetry_plane = result.x
        # normalize the normal vector
        symmetry_plane[:3] = symmetry_plane[:3] / np.linalg.norm(symmetry_plane[:3])
        # TODO: sort symmetry_planes by decreasing -results.fun
        symmetry_planes.append(symmetry_plane)
    # prune similar planes
    pruned_symmetry_planes = []
    for plane in symmetry_planes:
        for other_plane in pruned_symmetry_planes:
            if plane_distance(plane, other_plane) < threshold:
                break
        else:
            pruned_symmetry_planes.append(plane)
    return pruned_symmetry_planes

def reflect_points_across_plane(X: np.ndarray, plane: np.ndarray) -> np.ndarray:
    """
    Reflect a set of points X across a plane given in standard form (a,b,c,d) (s.t. ax + by + cz + d = 0)

    Args:
        X (np.ndarray): set of points to be reflected across the plane
        plane (np.ndarray): plane in standard form (a,b,c,d) with normalized normal ||(a,b,c)||_2 = 1

    Returns:
        np.ndarray: set of reflected points
    """
    a, b, c, d = plane
    # Normal vector of the plane
    normal = np.array([a, b, c])
    
    # Ensure the normal vector is a unit vector
    # if abs(norm := np.linalg.norm(normal)) - 1 > 1e-5:
    #     normal = normal / norm
    #     print(f"Normal vector had length {norm}.")
    # norm = np.linalg.norm(normal)
    # if abs(norm - 1) > 1e-2:
    #     print(f"Normal vector length: {norm}")
    # normal = normal / norm
    
    # Find a support vector (a point on the plane)
    # We choose the point (x0, 0, 0) if a != 0
    if a != 0:
        support = np.array([-d / a, 0, 0])
    elif b != 0:
        support = np.array([0, -d / b, 0])
    elif c != 0:
        support = np.array([0, 0, -d / c])
    else:
        raise ValueError("Invalid plane coefficients. At least one of a, b, c must be non-zero.")
    
    # Calculate the vector from point p to each point in X
    X_minus_p = X - support
    
    # Project X_minus_p onto the normal vector n
    projection = np.dot(X_minus_p, normal)[:, np.newaxis] * normal
    
    # Reflect X across the plane
    X_reflected = X - 2 * projection
    
    return X_reflected
    # a, b, c, d = plane
    # return X - 2 * (np.dot(X, np.array([a, b, c])) + d)[:, np.newaxis] * np.array([a, b, c])


def centroid(X: np.ndarray) -> np.ndarray:
    """
    Calculate the centroid of a set of points.

    Args:
        X (np.ndarray): set of points

    Returns:
        np.ndarray: centroid of the points
    """
    return np.mean(X, axis=0)
