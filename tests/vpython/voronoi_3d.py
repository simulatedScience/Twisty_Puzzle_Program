from scipy.spatial import Voronoi, voronoi_plot_2d
import numpy as np
import matplotlib.pyplot as plt
import vpython as vpy
from polyhedra_test import polyhedron, draw_face


def draw_voronoi_3d(points_3d, pointsize=1):
    """
    points_3d - (iter) - any iterable of numpy.ndarrays
    """
    canvas = vpy.canvas(width=1280, height=720, background=vpy.vec(0.7,0.7,0.7))

    draw_points(points_3d, color=vpy.vec(.3,.3,.8), radius=pointsize)
    vor = Voronoi(points_3d, incremental=False)
    # print(vor.points)
    # print(vor.vertices)
    draw_points(vor.vertices, color=vpy.vec(.9,.5,0), radius=pointsize/2)

    vertices = [vpy.vec(*list(pos)) for pos in vor.vertices]
    for poly_faces in get_polyhedra(vor):
        # print(faces, len(faces))
        poly = polyhedron(
                vertices,
                poly_faces,
                color=vpy.vec(*np.random.rand(3)),
                # color=vpy.vec(.9,.5,0),
                opacity=1,
                sort_faces=True)


def get_polyhedra(vor):
    """
    get a list of all the closed polyhedra in a (3D) voronoi diagram [vor].
    Each polyhedron is represented as a list of lists of vertex indices forming each face.

    inputs:
    -------
        vor - (scipy.spatial.Voronoi) - a scipy Voronoi diagram
    
    returns:
    --------
        (list) of lists of lists of ints - representing each closed polyhedron in the voronoi diagram
    """
    poly_faces_list = list()
    # poly_vertex_list = list()
    ridge_sets = [set(ridge) for ridge in vor.ridge_vertices]
    region_sets = [set(region) for region in vor.regions]
    for region in region_sets:
        if not -1 in region and len(region) > 0:
            poly_faces = list()
            for ridge, ridge_set in zip(vor.ridge_vertices, ridge_sets):
                if ridge_set <= region: # is subset of region
                    poly_faces.append(ridge)
            poly_faces_list.append(poly_faces)
            # poly_vertex_list.append(region)
    return poly_faces_list


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
    # # SKEWB points:
    # points = [( 4, 4, 7), ( 4,-4, 7), (-4, 4, 7), (-4,-4, 7), ( 0, 0, 7),
    #           ( 4, 4,-7), ( 4,-4,-7), (-4, 4,-7), (-4,-4,-7), ( 0, 0,-7),
    #           ( 4, 7, 4), ( 4, 7,-4), (-4, 7, 4), (-4, 7,-4), ( 0, 7, 0),
    #           ( 4,-7, 4), ( 4,-7,-4), (-4,-7, 4), (-4,-7,-4), ( 0,-7, 0),
    #           ( 7, 4, 4), ( 7, 4,-4), ( 7,-4, 4), ( 7,-4,-4), ( 7, 0, 0),
    #           (-7, 4, 4), (-7, 4,-4), (-7,-4, 4), (-7,-4,-4), (-7, 0, 0)]
    # points = np.append(points, [[25,0,0], [-25,0,0], [0,25,0], [0,-25,0], [0,0,25], [0,0,-25]], axis = 0)
    # # IVY CUBE points:
    # points = [            ( 4,-4, 7), (-4, 4, 7),             ( 0, 0, 7),
    #           ( 4, 4,-7),                         (-4,-4,-7), ( 0, 0,-7),
    #                       ( 4, 7,-4), (-4, 7, 4),             ( 0, 7, 0),
    #           ( 4,-7, 4),                         (-4,-7,-4), ( 0,-7, 0),
    #                       ( 7, 4,-4), ( 7,-4, 4),             ( 7, 0, 0),
    #           (-7, 4, 4),                         (-7,-4,-4), (-7, 0, 0)]
    # points = np.append(points, [[25,0,0], [-25,0,0], [0,25,0], [0,-25,0], [0,0,25], [0,0,-25]], axis = 0)
    # # 2x2 Rubiks cube points:
    # points = [( 4, 4, 7), ( 4,-4, 7), (-4, 4, 7), (-4,-4, 7),
    #           ( 4, 4,-7), ( 4,-4,-7), (-4, 4,-7), (-4,-4,-7),
    #           ( 4, 7, 4), ( 4, 7,-4), (-4, 7, 4), (-4, 7,-4),
    #           ( 4,-7, 4), ( 4,-7,-4), (-4,-7, 4), (-4,-7,-4),
    #           ( 7, 4, 4), ( 7, 4,-4), ( 7,-4, 4), ( 7,-4,-4),
    #           (-7, 4, 4), (-7, 4,-4), (-7,-4, 4), (-7,-4,-4),]
    # points = np.append(points, [[100,0,0], [-100,0,0], [0,100,0], [0,-100,0], [0,0,100], [0,0,-100]], axis = 0)
    np.random.seed(12)
    points = np.random.uniform(-30,30, (15, 3))
    # points = np.append(points, [[999,0,0], [-999,0,0], [0,999,0], [0,-999,0], [0,0,999], [0,0,-999]], axis = 0)
    draw_voronoi_3d(points)
