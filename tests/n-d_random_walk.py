import numpy as np
import matplotlib.pyplot as plt
import random as rnd

def nd_random_walk(n_steps, dims=2, restricted=False):
    """
    generate a list of points of a [dims]-dimensional random walk

    inputs:
    -------
        restricted - prevents taking the same step twice
    """
    step_choices = gen_steps(dims=dims)    # list of all possible steps
    pos = np.zeros(dims) # current position of the point
    pos_list = [pos]
    last_step = np.array([])

    for _ in range(n_steps):
        step = rnd.choice(step_choices)
        if restricted:
            while np.array_equal(step, last_step):
                step = rnd.choice(step_choices)
                if np.array_equal(last_step, np.array([])):
                    break
        pos += step
        last_step = -step
        pos_list.append(tuple(pos))

    return pos_list


def gen_steps(dims=2):
    """
    generate all possible steps in the cardinal directions of a [dims]-dimensional cartesian space
    """
    steps = []
    for i in range(dims):
        step = np.zeros(dims)
        step[i] = 1
        steps.append(step)
        steps.append(-step)
    return steps


def get_distance_list(points):
    """
    calculates the euclidean distance from  the origin for each point in points
    inputs:
        points - (list of iterables) - a list of points as tuples, lists or vectors
    outputs:
        (list of numbers) - list of numbers representing the distance from the origin
    """ 
    dist_list = []
    dims = len(points[0])
    for p in points:
        dist = np.sqrt(sum([p[i]**2 for i in range(dims)]))
        dist_list.append(dist)
    return dist_list


def plot_nd_walk_distance(dims=8, n_steps=5000, restricted=False):
    points = nd_random_walk(n_steps=n_steps, dims=dims, restricted=restricted)
    dist_list = get_distance_list(points)
    plt.plot(list(range(len(dist_list))), dist_list, label=f"restricted={restricted}")


# def plot_2d_walk(n_steps=50):
#     pass

if __name__ == "__main__":
    dims = 8
    n_steps = 20
    plot_nd_walk_distance(dims, n_steps, restricted=True)
    plot_nd_walk_distance(dims, n_steps, restricted=False)
    plt.plot([np.sqrt(n) for n in range(n_steps)])

    plt.legend()
    plt.show()