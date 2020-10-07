"""
module to automatically calculate 3D polyhedra as pieces of a twisty puzzle
intputs are points representing the color stickers

The polyhedra are calculated with a 3D voronoi diagram generated with scipy.spatial.Voronoi
"""
from scipy.spatial import Voronoi
import numpy as np
import vpython as vpy
from .polyhedra import Polyhedron, vpy_vec_tuple


def draw_3d_pieces(vpy_objects, clip_poly, show_edges=True, edge_color=vpy.vec(0,0,0)):
    """
    draw one polyhedron for each object in vpy_objects

    inputs:
    -------
        vpy_objects - (list) - list of vpython objects with .pos attribute.
        clip_poly - (Polyhedron) - a polyhedron restricting the shape 

    returns:
    --------
        (list) of (Polyhedron) - of the 
        (list) of (Polyhedron) - list of the original, uncut polyhedra.
    """
    polyhedra = draw_voronoi_3d(vpy_objects)
    pieces = list()
    for i, poly in enumerate(polyhedra):
        # poly.draw_faces()
        # poly.draw_all_edges()
        # poly.visible=True
        pieces.append(poly.intersect(
                clip_poly,
                color=poly.color,
                sort_faces=True,
                show_edges=show_edges,
                show_corners=show_edges,
                edge_color=edge_color,
                edge_radius=poly.edge_radius/2,
                corner_radius=poly.edge_radius,
                debug=False))
        # poly.toggle_visible(True)
        # poly.toggle_visible(False)
        if pieces[i] == None: # replace pieces that were completely cut away
            obj = vpy_objects[i]
            pieces[i] = vpy.sphere(
                    pos=obj.pos,
                    opacity=0.05,
                    color=obj.color,
                    radius=poly.edge_radius)
        else:
            pieces[i].pos = vpy_objects[i].pos
            # print(pieces[i], pieces[i].color)
            # pieces[i].toggle_visible(False)
    for obj in vpy_objects: # hide given objects
        if isinstance(obj, Polyhedron):
            obj.toggle_visible(False)
        else:
            obj.visible = False
    return pieces, polyhedra


def draw_voronoi_3d(vpy_objects):
    """
    points_3d - (iter) - any iterable of numpy.ndarrays
    """
    vpy_points = [obj.pos for obj in vpy_objects]
    # calculate points far away from all given objects
    far_point = 100*max([vec.mag for vec in vpy_points])
    # convert vpython vectors to numpy array
    points_3d = np.array([vpy_vec_tuple(vec) for vec in vpy_points])
    points_3d = np.append(points_3d,
                          [[far_point,0,0], [-far_point,0,0],
                           [0,far_point,0], [0,-far_point,0],
                           [0,0,far_point], [0,0,-far_point]],
                          axis = 0)
    del(vpy_points)
    vor = Voronoi(points_3d, incremental=False)

    vpy_vertices = [vpy.vec(*list(pos)) for pos in vor.vertices]
    ridge_sets = [set(ridge) for ridge in vor.ridge_vertices]
    polyhedra = list()
    for i, region_i in enumerate(vor.point_region):
        region_set = set(vor.regions[region_i])
        if not -1 in region_set and len(region_set) > 0:
            vertices, faces = get_polyhedron(vor, region_set, ridge_sets, vpy_vertices)
            color = vpy_objects[i].color
            poly = Polyhedron(
                    vertices,
                    faces,
                    color=color,
                    opacity=0.5,
                    show_faces=False,
                    show_edges=False,
                    show_corners=False,
                    sort_faces=True,
                    edge_radius=0.01)
            polyhedra.append(poly)
    return polyhedra


def get_polyhedron(vor, region_set, ridge_sets, vpy_vertices):
    """
    get the necessary information to create the polyhedron
        associated with the 'region_i'-th region in the given Voronoi diagram

    inputs:
    -------
        region_set - (set) - set of all vertex indices,
            that belong to the polyhedron
        vor - (scipy.spatial.Voronoi) - a 3D Voronoi diagram
    """
    poly_faces = list()
    poly_vertices = list()
    for ridge, ridge_set in zip(vor.ridge_vertices, ridge_sets):
        poly_face = list()
        if ridge_set <= region_set: # is subset of region
            for i in ridge:
                try:
                    k = poly_vertices.index(vpy_vertices[i])
                except ValueError:
                    k = len(poly_vertices)
                    poly_vertices.append(vpy_vertices[i])
                poly_face.append(k)
            poly_faces.append(poly_face)
    # poly_vertices = [vpy_vertices[i] for i in region_set]
    return poly_vertices, poly_faces