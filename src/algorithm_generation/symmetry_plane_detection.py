"""
Detect reflectional symmetries in a 3D point cloud. Implemented Algorithm based on [1]

author: Sebastian Jost

References:
[1] [Hruda et. al.](https://doi.org/10.1007/s00371-020-02034-w)
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

def init_planes(
        X: np.ndarray,
        plane_similarity_threshold: float = 0.1,
        num_planes: int = 100_000,
        verbosity: int = 1,
    ) -> list[np.ndarray]:
    """
    Generate a set of random planes for symmetry detection by choosing two random points from X and computing the normal vector of the plane spanned by these points. The plane passes through the midpoint between these two points. Repeat `num_planes` times and only keep planes that are not too similar to the existing planes.

    Args:
        X (np.ndarray): set of points as array of shape (n, 3)
        plane_similarity_threshold (float): threshold for distance between planes to consider them equal
        num_planes (int): number of random planes to generate (ignored if `X` has no more than 500 points. In that case, consider all possible planes defined by two points)

    Returns:
        list[np.ndarray]: list of planes in standard form (a, b, c, -d) (ax + by + cz + d = 0)
    """
    n_points: int = X.shape[0]
    found_planes: dict[tuple[float, float, float, float], tuple[np.ndarray, int]] = {}
    if n_points > 500: # if there are too many points, only calculate a fixed number of random planes
        if verbosity > 0:
            print(f"Searching {num_planes} random planes for symmetries.")
        for _ in range(num_planes):
            # choose two random points
            idx1: int = np.random.randint(0, n_points-1)
            idx2: int = np.random.randint(idx1 + 1, n_points)
            point_1, point_2 = X[idx1], X[idx2]
            add_plane(
                point_1=point_1,
                point_2=point_2,
                found_planes=found_planes,
                plane_similarity_threshold=plane_similarity_threshold,
                )
    else: # use all pairs of points to calculate planes
        if verbosity > 0:
            print(f"Searching all {X.shape[0] * (X.shape[0] - 1) // 2} planes for symmetries.")
        for idx_1, point_1 in enumerate(X[:-1]):
            for point_2 in X[idx_1+1:]:
                add_plane(
                    point_1=point_1,
                    point_2=point_2,
                    found_planes=found_planes,
                    plane_similarity_threshold=plane_similarity_threshold,
                    )
    planes: list[np.ndarray] = [plane for plane, _ in found_planes.values()] # extract planes in standard form
    return planes

def add_plane(
        point_1: np.ndarray,
        point_2: np.ndarray,
        found_planes: dict[tuple[float, float, float, float], tuple[np.ndarray, int]],
        plane_similarity_threshold: float = 0.1,
        ):
    """
    Given two points and a list of current planes, compute the plane between the two points and add it to the list of planes if it is not too similar to the existing planes.
    If it is similar, average the similar planes and update the list of planes accordingly.

    Args:
        point_1 (np.ndarray): first point
        point_2 (np.ndarray): second point
        found_planes (dict[tuple[float, float, float, float], tuple[np.ndarray, int]]): dictionary of found planes
        plane_similarity_threshold (float): threshold for distance between planes to consider them equal
    """
    # compute normal vector of plane as the normalized difference vector between the two points
    diff_vector: np.ndarray = point_2 - point_1
    normal: np.ndarray = diff_vector / np.linalg.norm(diff_vector)
    # compute midpoint
    midpoint: np.ndarray = point_1 + diff_vector / 2
    # TODO: check if plane is not too similar to existing planes
    new_plane = plane_point_normal2standard_form((midpoint, normal))
    new_plane_key = tuple(new_plane)
    # plane_key is a 4-tuple describing the plane in standard form (0 = ax+by+cz+d)
    # values: plane as 4D numpy vector and int counting how many planes were averaged to get this one
    add_new_plane: bool = True
    for plane_key, (plane, num) in list(found_planes.items()):
        # print(f"{plane_distance(new_plane, plane) = }")
        if (dist := plane_distance(new_plane, plane)) < plane_similarity_threshold:
            if dist < plane_similarity_threshold/10: # planes are almost identical, no furhter averaging needed
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
    alpha_term = 1 / 2.6 * alpha * dist
    value = (1 - alpha_term)**5 * \
        (8 * (alpha_term)**2 + 5 * (alpha_term) + 1)
    return np.where(alpha * dist <= 2.6, value, 0) # clamp to 0 if distance is > 2.6/alpha
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
    # if hasattr(reflect_symmetry_measure, "run_count"):
    #     reflect_symmetry_measure.run_count += 1
    # else:
    #     reflect_symmetry_measure.run_count = 1
    return similarity_measure

def find_symmetry_planes(
        X: np.ndarray,
        plane_similarity_threshold: float = 0.1,
        S: int = 5,
        min_score_ratio: float = 0.99,
        num_init_planes: int = 100_000,
        verbosity: int = 1,
    ) -> list[tuple[np.ndarray, np.ndarray]]:
    """
    Find the best symmetry planes and optimize over them.

    Args:
        X (np.ndarray): set of points
        threshold (float): threshold to check if a plane is too similar to existing planes
        alpha (float): parameter to control the similarity function
        S (int): number of best planes to keep

    Returns:
        list[tuple[np.ndarray, np.ndarray]]: list of best symmetry planes
    """
    # translate to the origin
    X = X - np.mean(X, axis=0)
    # calculate alpha as 15/l_avg, the average distance between points in X
    alpha = 15 / np.mean(np.linalg.norm(X[:, np.newaxis] - X, axis=2))
    print(f"Set alpha to {alpha:.3f}.")
    # normalize X scaling such that points are at most distance 1 from the origin
    # # scale to unit sphere
    # X = X / np.max(np.linalg.norm(X, axis=1))
    # print parameters
    print(f"find_symmetry_planes(X, {plane_similarity_threshold}, {alpha}, {S}, {min_score_ratio}, {num_init_planes}, {verbosity})")
    planes: list[tuple[np.ndarray, np.ndarray]] = init_planes(X, plane_similarity_threshold, num_planes=num_init_planes, verbosity=verbosity)
    print(f"Initalized {len(planes)} planes.")
    best_planes = []
    best_scores = []
    # choose planes with best symmetry measure
    for plane in planes:
        score = reflect_symmetry_measure(X, plane, alpha)
        if len(best_planes) < S or score == min(best_scores):
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

    symmetry_planes: list[np.ndarray] = prune_by_symmetry_measure(X, symmetry_planes, alpha, min_score_ratio, verbosity)
    # prune similar planes
    pruned_symmetry_planes = []
    for plane in symmetry_planes:
        for other_plane in pruned_symmetry_planes:
            if (dist := plane_distance(plane, other_plane)) < plane_similarity_threshold:
                # if dist < 0:
                #     print(f"unexpected plane distance: {dist} between planes\n[{plane}]\n[{other_plane}]")
                # else:
                #     print(f"plane distance: {dist} between planes\n[{plane}]\n[{other_plane}]")
                break
        else:
            pruned_symmetry_planes.append(plane)
    # DEBUG: plot symmetry planes
    # plot_symmetry_planes(2*X, pruned_symmetry_planes)
    return pruned_symmetry_planes

def prune_by_symmetry_measure(
    X: np.ndarray,
    planes: list[np.ndarray],
    alpha: float = 1.0,
    min_score_ratio: float = 0.99,
    verbosity: int = 1,
    ) -> list[np.ndarray]:
    """
    Prune a list of planes by their symmetry measure. Keep only the planes whose symmetry measure is at least `min_score_ratio` times the best symmetry measure among the planes.

    Args:
        X (np.ndarray): set of points
        planes (list[np.ndarray]): list of planes
        alpha (float): parameter to control the similarity function
        min_score_ratio (float): minimum score ratio between best and other planes
        verbosity (int): verbosity level

    Returns:
        list[np.ndarray]: pruned list of planes
    """
    all_scores: list[float] = [reflect_symmetry_measure(X, plane, alpha) for plane in planes]
    scores_string: str = '\n  '.join([f'plane {i} {score:.3f}' for i, score in enumerate(all_scores)])
    print(f"symmetry_measures:\n  {scores_string}")
    best_score: float = max(all_scores)
    pruned_planes: list[np.ndarray] = [plane for plane, score in zip(planes, all_scores) if score >= best_score * min_score_ratio]
    if verbosity > 0:
        print(f"Keeping {len(pruned_planes)}/{len(planes)} planes with symmetry measures > {min_score_ratio:6.1%} of {best_score:.3f}.")
    return pruned_planes

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

def plot_symmetry_planes(X, symmetry_planes):
    print(f"found {len(symmetry_planes)} best planes.")
    # create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    # plot the points
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], c='b', marker='o')
    plt.show()
    # plot the best planes
    for i, plane in enumerate(symmetry_planes):
        # plot the plane
        print(f"Plotting plane {i+1}/{len(symmetry_planes)}: {plane.round(3)}")
        ax_plane = draw_plane(ax, plane, show_normal=False)
        print(f"Symmetry measure: {reflect_symmetry_measure(X, plane, 1)}")
        # update plot
        plt.draw()
        input("Press Enter to show next plane")
        ax_plane.remove()
    set_equal_aspect_3d(ax)
    plt.title("Best planes for symmetry detection")
    plt.show()
    return symmetry_planes

def draw_plane(
        ax: plt.Axes,
        ax_plane: np.ndarray,
        size: float = 1,
        show_normal: bool = True,
        transparency: float = 1.0,
        ):
    """
    Draw a plane in 3D given in standard form (a, b, c, d) (ax + by + cz + d = 0).
    
    Args:
        ax (plt.Axes): matplotlib axis to plot on
        plane (np.ndarray): plane in standard form (a, b, c, d)
        size (float): size of the plane to draw
        show_normal (bool): whether to plot the normal vector
    """
    # Extract plane coefficients
    a, b, c, d = ax_plane
    
    # Normal vector of the plane
    normal = np.array([a, b, c])
    
    # Ensure the normal vector is a unit vector
    normal = normal / np.linalg.norm(normal)
    
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
    
    # Define a grid in the plane
    d = np.linspace(-size, size, 10)
    D1, D2 = np.meshgrid(d, d)
    
    # Find a third vector perpendicular to the normal vector
    n1 = np.array([1, 0, 0])
    if np.allclose(normal, n1) or np.allclose(normal, -n1):
        n1 = np.array([0, 1, 0])
    v1 = np.cross(normal, n1)
    v1 /= np.linalg.norm(v1)
    
    # Find another vector in the plane
    v2 = np.cross(normal, v1)
    v2 /= np.linalg.norm(v2)
    
    # Plane points
    plane_points = support + D1[..., np.newaxis] * v1 + D2[..., np.newaxis] * v2
    ax_plane = ax.plot_surface(plane_points[..., 0], plane_points[..., 1], plane_points[..., 2], color='g', alpha=transparency, rstride=100, cstride=100)
    
    if show_normal:
        # plot the normal vector
        ax.quiver(support[0], support[1], support[2], normal[0], normal[1], normal[2], color='r')
    return ax_plane

def set_equal_aspect_3d(ax):
    """
    Sets equal scaling for all three axes of a 3D plot.

    Parameters:
    ax (Axes3D): A Matplotlib 3D Axes object.
    """
    # Get the current limits
    x_limits = ax.get_xlim()
    y_limits = ax.get_ylim()
    z_limits = ax.get_zlim()

    # Determine the new limits that make the axes scaled equally
    all_limits = np.array([x_limits, y_limits, z_limits])
    min_limit = all_limits[:, 0].min()
    max_limit = all_limits[:, 1].max()

    # Set the new limits
    ax.set_xlim([min_limit, max_limit])
    ax.set_ylim([min_limit, max_limit])
    ax.set_zlim([min_limit, max_limit])

    # Set the same scale for all axes
    ax.set_box_aspect([1, 1, 1])  # aspect ratio is 1:1:1
