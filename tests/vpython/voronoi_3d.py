from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import matplotlib.pyplot as plt
import vpython as vpy
from polyhedra_test import polyhedron, draw_face


def draw_voronoi_3d(points_3d, pointsize=1):
    """
    points_3d - (iter) - any iterable of numpy.ndarrays
    """
    canvas = vpy.canvas(width=1920, height=1080, background=vpy.vec(0.7,0.7,0.7))

    draw_points(points_3d, color=vpy.vec(.3,.3,.8), radius=pointsize)
    vor = Voronoi(points_3d, incremental=False)
    print(vor.points)
    print(vor.vertices)
    draw_points(vor.vertices, color=vpy.vec(.9,.5,0), radius=pointsize/2)

    vertices = [vpy.vec(*list(pos)) for pos in vor.vertices]
    faces = [ridge for ridge in vor.ridge_vertices if not -1 in ridge]
    # print(faces, len(faces))
    poly = polyhedron(vertices, faces, color=vpy.vec(.9,.5,0), opacity=0.4)
    # draw_edges(vor, radius=pointsize/4)


def draw_points(points_3d, color=vpy.vec(.3,.3,.8), radius=1):
    for point in points_3d:
        coords = vpy.vec(*point)
        vpy.sphere(pos=coords, color=color, radius=radius)


if __name__=="__main__":
    # points = [(10, 0, 0), (-10,  0,  0),
    #           ( 0,10, 0), (  0,-10,  0),
    #           ( 0, 0,10), (  0,  0,-10),
    #           (5,0,0), (-5, 0, 0),
    #           (0,5,0), ( 0,-5, 0),
    #           (0,0,5), ( 0, 0,-5),
    #           (0,0,0)]
    np.random.seed(12)
    points = np.random.uniform(-30,30, (15, 3))
    # points = np.append(points, [[999,0,0], [-999,0,0], [0,999,0], [0,-999,0], [0,0,999], [0,0,-999]], axis = 0)
    draw_voronoi_3d(points)
