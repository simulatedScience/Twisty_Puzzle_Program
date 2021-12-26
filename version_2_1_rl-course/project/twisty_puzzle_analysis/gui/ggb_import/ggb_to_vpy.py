"""
This module provides methods to load points
    from a .ggb file and display them in vpython
"""
import vpython as vpy
from . import ggb_to_python as ggb_py
from . import xml_point_info as xml_point

def get_point_dicts(filepath, new_path = "."):
    """
    load points from .ggb file to a list of dictionaries

    inputs:
    -------
        filepath - (str) - a path to a .ggb file
        new_path - (str) - path where the file renamed to .zip
            shall be saved

    returns:
    --------
        (list) of dicts - containing information for each
            loaded point
    """
    new_path = ggb_py.copy_rename(filepath, new_path = new_path)
    tree = ggb_py.get_tree_from_folder(new_path)
    points = ggb_py.points_from_xml_tree(tree)
    # delete auxiliary and invisible points
    points = ggb_py.filter_points(points)
    print(f"{__name__}:\tfound {len(points)} visible, non-auxiliary 3d points")
    #get point infos as dicts
    return xml_point.get_points_info(points)


def draw_points(point_dicts):
    """
    draw a vpython sphere for every point in point_dicts

    inputs:
    -------
        point_dicts - (list) - list of dictionaries specifying
            coordinates, color and size of each point with keys
            'coords', 'vpy_color' (and 'size') respectively

    returns:
    --------
        (list) - list of all vpython objects created
    """
    objects = []
    for point_dict in point_dicts:
        objects.append(draw_point(point_dict))
    return objects


def draw_point(point_dict, radius=None):
    """
    draw a vpython sphere for the given point information

    inputs:
    -------
        point_dict - (dict) - dictionary specifying
            coordinates, color and size of the point with keys
            'coords', 'vpy_color' (and 'size') respectively
        radius - (float) - alternative method to specify
            the radius of the drawn sphere

    returns:
    --------
        None

    outputs:
    --------
        draws a vpython sphere for the given point
    """
    if radius == None:
        radius = point_dict["size"]/50

    if not isinstance(point_dict["coords"], vpy.vector):
        dict_to_vpy(point_dict)
    return vpy.sphere(pos=point_dict["coords"],
                      color=point_dict["vpy_color"],
                      radius=radius)


def dicts_to_vpy(point_dicts):
    """
    converts the 'coords' and 'vpy_color' etries of the given
        dictionaries to vpython vectors

    inputs:
    -------
        point_dicts - (list) - list of dictionaries specifying
            coordinates, color and size of each point with keys
            'coords', 'vpy_color' (and 'size') respectively

    returns:
    --------
        None
    """
    for point_dict in point_dicts:
        dict_to_vpy(point_dict)


def dict_to_vpy(point_dict):
    """
    converts the 'coords' and 'vpy_color' etries of the given
        dictionary to vpython vectors

    inputs:
    -------
        point_dict - (dict) - dictionary specifying
            coordinates, color and size of the point with keys
            'coords', 'vpy_color' (and 'size') respectively
        radius - (float) - alternative method to specify
            the radius of the drawn sphere

    returns:
    --------
        None
    """
    if not isinstance(point_dict["coords"], vpy.vector):
        point_dict["coords"] = vpy.vector(*point_dict["coords"])
    if not isinstance(point_dict["vpy_color"], vpy.vector):
        point_dict["vpy_color"] = vpy.vector(*point_dict["vpy_color"])


def draw_cones(point_dicts, PUZZLE_COM=vpy.vec(0,0,0)):
    """
    draw a vpython cone for every point in point_dicts

    inputs:
    -------
        point_dicts - (list) - list of dictionaries specifying
            coordinates, color and size of each point with keys
            'coords', 'vpy_color' (and 'size') respectively

    returns:
    --------
        (list) - list of all vpython objects created
    """
    objects = []
    for point_dict in point_dicts:
        objects.append(draw_cone(point_dict, PUZZLE_COM=PUZZLE_COM))
    return objects


def draw_cone(point_dict, radius=None, PUZZLE_COM=vpy.vec(0,0,0)):
    """
    draw a vpython cone for the given point information

    inputs:
    -------
        point_dict - (dict) - dictionary specifying
            coordinates, color and size of the point with keys
            'coords', 'vpy_color' (and 'size') respectively
        radius - (float) - alternative method to specify
            the radius of the drawn sphere

    returns:
    --------
        None

    outputs:
    --------
        draws a vpython cone for the given point
    """
    if radius == None:
        radius = point_dict["size"]/50

    if not isinstance(point_dict["coords"], vpy.vector):
        dict_to_vpy(point_dict)
    return vpy.cone(pos=point_dict["coords"],
                    color=point_dict["vpy_color"],
                    radius=radius,
                    axis=PUZZLE_COM-point_dict["coords"])


if __name__ == "__main__":
    canvas = vpy.canvas(background = vpy.vector(0.8,0.8,0.8),
                        up = vpy.vector(0,0,1),
                        forward = vpy.vector(-1,0,0))
    canvas.lights = []
    vpy.distant_light(direction = vpy.vector( 1, 1, 1), color = vpy.vector(0.7,0.7,0.7))
    vpy.distant_light(direction = vpy.vector(-1,-1,-1), color = vpy.vector(0.7,0.7,0.7))

    # draw_points(get_point_dicts("mixup cube points.ggb"))
    draw_points(get_point_dicts("rubiks cube points.ggb"))