"""
methods to extract the improtant information about points given as xml Elements generated from a geogebra.xml file.
"""
def get_points_info(points):
    """
    generates a list of dictionaries containing information about each point

    inputs:
    -------
        points - (list) of xml Elements - a list of point Elements from a geogebra.xml file

    returns:
    --------
        (list) of dicts - see 'get_point_info_dict()' for more info about these dicts
    """
    return [get_point_info_dict(point) for point in points]


def get_point_info_dict(point):
    """
    generates a dictionary containing information about the given point

    inputs:
    -------
        point - (xml Element) - the xml Element of a 3d point from a geogebra.xml file
    returns:
    --------
        (dict) - a dictionary containing info about the point:
            "name" - (str) - the name of the point
            "coords" - (triple) - cartesian x,y,z coordinates
            "color" - (triple) - r,g,b values in range 0-255
            "hex_color" - (str) - a -7-digit string of the form '#00ff00'
            "vpy_color" - (triple) r,g,b values in range 0-1
            "size" - (int) - the size of the point
    """
    color = get_color(point)
    return {"name": get_name(point),
            "coords": get_coords(point),
            "color": color,
            "hex_color": hex_color(color),
            "vpy_color": vpy_color(color),
            "size": get_size(point)}


def get_name(point):
    """
    returns:
    --------
        (str) - the name of the point
    """
    return point.get("label")


def get_coords(point):
    """
    returns:
    --------
        (triple) of floats - cartesian x,y,z coordinates
    """
    coords = point.find("coords")
    return tuple(float(coords.get(coord)) for coord in ["x", "y", "z"])


def get_size(point):
    """
    returns:
    --------
        (int) - the size of the point
    """
    return int(point.find("pointSize").get("val"))


def get_color(point):
    """
    returns:
    --------
        (triple) of ints - r,g,b values in range 0-255
    """
    coords = point.find("objColor")
    return tuple(int(coords.get(coord)) for coord in ["r", "g", "b"])



def hex_color(color):
    """
    return the hexadecimal color code of the given color

    inputs:
    -------
        color - (triple) - a triple of integers in range 0-255
            representing r,g,b values
    returns:
    --------
        (str) - the hex-code for the given color
    """
    return f"#{my_hex(color[0])}{my_hex(color[1])}{my_hex(color[2])}"

def my_hex(n):
    """
    return the 2-digit hexadecimal representation of n
    inputs:
    -------
        n - (int) - an integer in range 0-255
    returns:
    --------
        (str) - the 2-digit hexadecimal representation of n
    """
    return hex(n)[2:] if n>=16 else "0"+hex(n)[2:]


def vpy_color(color):
    """
    convert given color to r,g,b triple in range 0-1

    inputs:
    -------
        color - (triple) - a triple of integers in range 0-255
            representing r,g,b values
    returns:
    --------
        (triple) - color triple with r,g,b values in range 0-1
    """
    return tuple(comp/255 for comp in color)


if __name__ == "__main__":
    from ggb_to_python import *
    tree = get_tree_from_folder("mixup cube points.zip")
    points = points_from_xml_tree(tree)
    points = filter_points(points)
    print(f"found {len(points)} visible, non-auxiliary 3d points")
    print(get_points_info(points)[0])