"""
author: GPT-4o & Sebastian Jost
algorithm by Hruda et. al. in https://doi.org/10.1007/s00371-020-02034-w
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def reflection_matrix(plane_normal):
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    I = np.eye(3)
    reflection = I - 2 * np.outer(plane_normal, plane_normal)
    return reflection

def similarity_function(l, alpha):
    val = (1 - l / 2.6 * alpha * l)**5 * (8 * (1 / 2.6 * alpha * l)**2 + 5 * (1 / 2.6 * alpha * l) + 1)
    return np.where(alpha * l <= 2.6, val, 0)

def symmetry_measure(X, T, alpha):
    n = X.shape[0]
    transformed_X = X @ T.T
    s = 0
    for i in range(n):
        for j in range(n):
            distance = np.linalg.norm(transformed_X[i] - X[j])
            s += similarity_function(distance, alpha)
    return s

def random_planes(X, num_planes=1000, threshold=0.1):
    planes = []
    n = X.shape[0]
    while len(planes) < num_planes:
        idx1, idx2 = np.random.choice(n, 2, replace=False)
        p1, p2 = X[idx1], X[idx2]
        normal = np.cross(p1 - p2, [0, 0, 1])
        if np.linalg.norm(normal) == 0:
            normal = np.cross(p1 - p2, [0, 1, 0])
        normal = normal / np.linalg.norm(normal)
        if all(np.linalg.norm(np.dot(plane, normal)) > threshold for plane in planes):
            planes.append(normal)
    return np.array(planes)

def optimize_planes(X, planes, alpha, S=5):
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

def detect_symmetry_planes(X, num_planes=1000, S=5, alpha_factor=20):
    centroid = np.mean(X, axis=0)
    X_centered = X - centroid
    l_avg = np.mean(np.linalg.norm(X_centered, axis=1))
    alpha = alpha_factor / l_avg

    initial_planes = random_planes(X_centered, num_planes)
    best_planes, _ = optimize_planes(X_centered, initial_planes, alpha, S)

    return best_planes

if __name__ == '__main__':
    # tetrahedron corners
    X = np.array([
        [1, 0, 0],
        [0, 1, 0],
        [0, 0, 1],
        [0, 0, 0],
    ])

    planes = detect_symmetry_planes(X, num_planes=2500, S=5, alpha_factor=20)

    # Plotting the points and symmetry planes
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(X[:, 0], X[:, 1], X[:, 2], color='b')

    centroid = np.mean(X, axis=0)

    for plane in planes:
        print(f"{plane = }")
        d = -np.dot(plane, centroid)
        xx, yy = np.meshgrid(range(-1, 2), range(-1, 2))
        zz = (-plane[0] * xx - plane[1] * yy - d) * 1. / plane[2]
        ax.plot_surface(xx, yy, zz, alpha=0.5)

    plt.show()
