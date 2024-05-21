"""
author: GPT-4o & Sebastian Jost
algorithm by Hruda et. al. in https://doi.org/10.1016/j.cagd.2022.102138
"""
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation as R

def reflection_matrix(plane_normal):
    """
    Compute the reflection matrix across a plane with the given normal.
    """
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    I = np.eye(3)
    reflection = I - 2 * np.outer(plane_normal, plane_normal)
    return reflection

def symmetry_measure(X, T, alpha):
    """
    Compute the symmetry measure for a transformation T of point set X.
    """
    def similarity_function(l, alpha):
        val = (1 - l / 2.6 * alpha * l)**5 * (8 * (1 / 2.6 * alpha * l)**2 + 5 * (1 / 2.6 * alpha * l) + 1)
        return np.where(alpha * l <= 2.6, val, 0)

    n = X.shape[0]
    transformed_X = X @ T.T
    s = 0
    for i in range(n):
        for j in range(n):
            distance = np.linalg.norm(transformed_X[i] - X[j])
            s += similarity_function(distance, alpha)
    return s

def random_planes(X, num_planes=1000, threshold=0.1):
    """
    Generate a set of random planes for symmetry detection.
    """
    planes = []
    n = X.shape[0]
    for _ in range(num_planes):
        idx1, idx2 = np.random.choice(n, 2, replace=False)
        p1, p2 = X[idx1], X[idx2]
        normal = np.cross(p1, p2)
        normal = normal / np.linalg.norm(normal)
        if all(np.linalg.norm(np.dot(plane, normal)) < threshold for plane in planes):
            planes.append(normal)
    return planes

def optimize_planes(X, planes, alpha, S=5):
    """
    Find the best symmetry planes and optimize over them.
    """
    best_planes = []
    best_scores = []

    for plane in planes:
        reflection = reflection_matrix(plane)
        score = symmetry_measure(X, reflection, alpha)
        if len(best_scores) < S or score > min(best_scores):
            if len(best_scores) >= S:
                min_index = np.argmin(best_scores)
                best_scores[min_index] = score
                best_planes[min_index] = plane
            else:
                best_scores.append(score)
                best_planes.append(plane)

    return best_planes, best_scores

def rotational_symmetry_measure(X, Q, s, alpha):
    """
    Compute the rotational symmetry measure for a quaternion Q and point s.
    """
    def similarity_function(l, alpha):
        val = (1 - l / 2.6 * alpha * l)**5 * (8 * (1 / 2.6 * alpha * l)**2 + 5 * (1 / 2.6 * alpha * l) + 1)
        return np.where(alpha * l <= 2.6, val, 0)

    rot = R.from_quat(Q)
    n = X.shape[0]
    rotated_X = rot.apply(X - s) + s
    s = 0
    for i in range(n):
        for j in range(n):
            distance = np.linalg.norm(rotated_X[i] - X[j])
            s += similarity_function(distance, alpha)
    return s

def penalty_function(angle):
    """
    Penalty function that penalizes rotations by small angles.
    """
    if angle <= 30:
        return 0
    else:
        return min(1, (angle - 30) / 13)

def optimize_rotational_symmetry(X, planes, alpha):
    """
    Optimize to find the best rotational symmetries.
    """
    best_rotations = []

    for i, p1 in enumerate(planes):
        for p2 in planes[i+1:]:
            line_direction = np.cross(p1, p2)
            if np.linalg.norm(line_direction) == 0:
                continue
            line_direction = line_direction / np.linalg.norm(line_direction)
            centroid = np.mean(X, axis=0)
            s = centroid - np.dot(centroid, line_direction) * line_direction

            def objective(params):
                q = params[:4]
                s = params[4:]
                angle = 2 * np.arccos(q[0]) * 180 / np.pi
                penalty = penalty_function(angle)
                return -rotational_symmetry_measure(X, q, s, alpha) * penalty

            q_initial = R.from_rotvec(np.pi / 4 * line_direction).as_quat()
            result = minimize(objective, np.hstack([q_initial, s]), method='L-BFGS-B')
            best_rotations.append(result.x)

    return best_rotations

# Main algorithm
def detect_rotational_symmetries(X, num_planes=1000, S=5, alpha_factor=20):
    centroid = np.mean(X, axis=0)
    X_centered = X - centroid
    l_avg = np.mean(np.linalg.norm(X_centered, axis=1))
    alpha = alpha_factor / l_avg

    initial_planes = random_planes(X_centered, num_planes)
    best_planes, _ = optimize_planes(X_centered, initial_planes, alpha, S)

    best_rotations = optimize_rotational_symmetry(X_centered, best_planes, alpha)

    return best_rotations

# Example usage
if __name__ == "__main__":
    # Example: corners of a cube
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
    # Example: corners of a tetrahedron
    X = np.array([
        [ 1, 0, 0],
        [ 0, 1, 0],
        [ 0, 0, 1],
        [ 0, 0, 0],
    ])
    
    
    rotations = detect_rotational_symmetries(X, num_planes=2500, S=30, alpha_factor=20)
    for rot in rotations:
        print("Rotation:", rot)
        
    # make 3D plot of points and rotation axes
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X[:, 0], X[:, 1], X[:, 2])
    for rot in rotations:
        axis = rot[1:4]
        angle = 2 * np.arccos(rot[0]) * 180 / np.pi
        ax.quiver(*rot[4:], *axis, length=2, color='r')
    plt.show()
