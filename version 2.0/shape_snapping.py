"""
This module provides methods to snap a set of points to different shapes.
At first there will only be a sphere and a cube implemented.
"""
import vpython as vpy
import ggb_import.ggb_to_vpy as ggb_vpy

def snap_to_sphere(points, radius=1, show_sphere=True):
    """
    projects all points to a sphere with the given 'radius' centered at (0,0,0)

    inputs:
    -------
        points - (list) of dicts or of vpython objects -
            list of dictionaries specifying coordinates,
                color and size of each point with keys
                'coords', 'vpy_color' (and 'size') respectively
            or list of vpython objects with .pos attribute
        radius - (float) - a positive radius of the sphere

    returns:
    --------
        (list) of dicts - the same list with changed point coordinates
    """
    if show_sphere:
        snap_obj = vpy.sphere(pos=vpy.vec(0,0,0),
                              color=vpy.vec(.8,.8,.8),
                              radius=radius,
                              opacity=0.8,
                              shininess=0)

    if isinstance(points[0], dict):
        for point_dict in points:
            if not isinstance(point_dict["coords"], vpy.vector):
                ggb_vpy.dict_to_vpy(point_dict)
            point_dict["coords"] /= point_dict["coords"].mag * radius

        return point_dicts

    else:
        for obj in points:
            obj.pos /= obj.pos.mag * radius
        if show_sphere:
            return snap_obj


def snap_to_cube(points, sidelength=2, show_cube=True):
    """
    projects all points to a cube with the given sidelength centered at (0,0,0)

    inputs:
    -------
        points - (list) of dicts or of vpython objects -
            list of dictionaries specifying coordinates,
                color and size of each point with keys
                'coords', 'vpy_color' (and 'size') respectively
            or list of vpython objects with .pos attribute
        sidelength - (float) - a positive sidelength of the cube

    returns:
    --------
        (list) of dicts - the same list with changed point coordinates
    """
    if show_cube:
        snap_obj = vpy.box(pos=vpy.vec(0,0,0),
                           color=vpy.vec(.8,.8,.8),
                           size=vpy.vec(sidelength,sidelength,sidelength),
                           opacity=0.8,
                           shininess=0)

    if isinstance(points[0], dict):
        for point_dict in points:
            if not isinstance(point_dict["coords"], vpy.vector):
                ggb_vpy.dict_to_vpy(point_dict)
            point_dict["coords"] /= max_coord(point_dict["coords"]) * sidelength/2

        return point_dicts

    else:
        for obj in points:
            obj.pos /= max_coord(obj.pos) * sidelength/2
        if show_cube:
            return snap_obj


def max_coord(vector):
    """
    returns maximum absolute value of the coordinates of the vector

    inputs:
    -------
        vector - (vpy.vector) - a vpython vector

    returns:
    --------
        (float) - maximum absolute value of the coordinates of the vector
    """
    return max(abs(vector.x), abs(vector.y), abs(vector.z))


if __name__ == "__main__":
    canvas = vpy.canvas(background = vpy.vector(0.8,0.8,0.8),
                        up = vpy.vector(0,0,1),
                        forward = vpy.vector(-1,0,0))
    canvas.lights = []
    canvas.ambient = vpy.vec(1,1,1)*0.4
    vpy.distant_light(direction = vpy.vector( 1, 1, 1), color = vpy.vector(0.7,0.7,0.7))
    vpy.distant_light(direction = vpy.vector(-1,-1,-1), color = vpy.vector(0.7,0.7,0.7))

    # points = ggb_vpy.get_point_dicts("ggb_files/mixup cube points.ggb")
    # points = ggb_vpy.get_point_dicts("ggb_files/rubiks cube points.ggb")
    points = ggb_vpy.get_point_dicts("../ggb_files/gear cube points.ggb")


    points = snap_to_sphere(points)
    ggb_vpy.draw_cones(points)
    # points = snap_to_cube(points)
    # ggb_vpy.draw_points(points)