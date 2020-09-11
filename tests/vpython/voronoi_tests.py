from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import matplotlib.pyplot as plt
import vpython as vpy
from polyhedra_test import polyhedron


def draw_voronoi(points_3d, pointsize=1):
    """
    points_3d - (iter) - any iterable of numpy.ndarrays
    """
    canvas = vpy.canvas(width=1280, height=720, background=vpy.vec(0.7,0.7,0.7))

    draw_points(points_3d, color=vpy.vec(.3,.3,.8), radius=pointsize)
    vor = Voronoi(points_3d, incremental=False)
    if len(vor.vertices[0]) == 2:
        points = []
        for point in vor.vertices:
            points.append(np.append(point, 0))
        vor.vertices = points
    draw_points(vor.vertices, color=vpy.vec(.9,.5,0), radius=pointsize/2)

    draw_edges(vor, radius=pointsize/4)


def draw_points(points_3d, color=vpy.vec(.3,.3,.8), radius=1):
    if len(points_3d[0]) == 2:
        points = []
        for point in points_3d:
            points.append(np.append(point, 0))
        points_3d = points
    for point in points_3d:
        coords = vpy.vec(*point)
        vpy.sphere(pos=coords, color=color, radius=radius)


def draw_edges(vor, color=vpy.vec(.2,.2,.2), radius=0.25):
    """
    inputs:
    -------
        vor - (scipy.spatial.Voronoi) - a voronoi object
        color - (vpython.vector) - a vpython color vector
        radius - (float) > 0 - radius (= half thickness) of the connecting lines (cylinders)
    """
    points_3d = vor.ridge_vertices
    # if len(points_3d[0]) == 2:
    #     points = []
    #     for point in points_3d:
    #         point.append(0)
    # print(points_3d)
    for points in points_3d:
        n = len(points)
        for i in range(n-1):
            A = vpy.vec(*vor.vertices[points[i]])
            B = vpy.vec(*vor.vertices[points[(i+1)%n]])
            if not -1 in points[i:i+2]:
                vpy.cylinder(pos=A, axis=B-A, color=color, radius=radius)


if __name__=="__main__":
    np.random.seed(6)
    points = np.random.uniform(-30,30, (15, 2))
    points = np.append(points, [[999,0], [-999,0], [0,999], [0,-999]], axis = 0)
    # np.random.seed(12)
    # points = np.random.uniform(-30,30, (15, 3))
    # points = np.append(points, [[999,0,0], [-999,0,0], [0,999,0], [0,-999,0], [0,0,999], [0,0,-999]], axis = 0)
    draw_voronoi(points)

    # import numpy as np
    # import matplotlib.pyplot as plt
    # from scipy.spatial import Voronoi, voronoi_plot_2d

    # np.random.seed(1234)
    # # make up data points
    # points = np.random.rand(15,2)

    # # add 4 distant dummy points
    # points = np.append(points, [[999,0], [-999,0], [0,999], [0,-999]], axis = 0)

    # # compute Voronoi tesselation
    # vor = Voronoi(points)

    # # plot
    # fig = voronoi_plot_2d(vor)

    # child = fig.get_children()[1]
    # child.set_aspect(1)


    # # colorize
    # for region in vor.regions:
    #     if not -1 in region:
    #         polygon = [vor.vertices[i] for i in region]
    #         plt.fill(*zip(*polygon))

    # # fix the range of axes
    # plt.xlim([0,1])
    # plt.ylim([0,1])

    # plt.show()