"""
methods to load a puzzle from an .xml file
"""
import xml.etree.ElementTree as ET
import os
import vpython as vpy

def load_puzzle(puzzlename):
    """
    load puzzle from .xml

    inputs:
    -------
        puzzlename - (str) - the name of the puzzle

    returns:
    --------
        (list) of dicts - list of dictionaries describing points of the puzzle
        (dict) - dict of moves with movenames as keys and 
            list of lists of ints as cycles
    """
    with open(os.path.join("puzzles", puzzlename, "puzzle_definition.xml")) as puzzle_file:
        puzzle_tree = ET.parse(puzzle_file)
    point_dicts = get_points(puzzle_tree)
    moves_dict = get_moves(puzzle_tree)

    return point_dicts, moves_dict


def get_points(puzzle_tree):
    """
    load points from xml tree

    inputs:
    -------
        puzzle_tree - (ElementTree) - ET.ElementTree containing the puzzle info

    returns:
    --------
        (list) of dicts - list of dictionaries describing the puzzle points
            keys:
            'coords' - (vpython vector) - coordinates of the point
            'vpy_color' - (vpython vector) - color of the point
            'size' - (float) - size of the point
    """
    point_elements = puzzle_tree.findall("points/point")
    point_dicts = []
    for point in point_elements:
        coord_elem = point.find("coords")
        coords = get_float_attr(coord_elem, ["x", "y", "z"])
        
        color_elem = point.find("color")
        color = get_float_attr(color_elem, ["r", "g", "b"])

        size = float(point.get("size"))
        point_dicts.append({"coords":coords, "vpy_color":color, "size":size})
    return point_dicts


def get_float_attr(xml_elem, attributes):
    """
    return attribute values for all 'attributes' of 'xml_elem'

    inputs:
    -------
        xml_elem - (ET.Element) - an xml tree element with the given attributes
        attributes - (iter) - an iterable of attributes of 'xml_elem' with values
            that can be converted to float
    returns:
    --------
        (vpython vector) - vpython vector of all requested attributes as floats
    """
    attrib_values = []
    for attr in attributes:
        attrib_values.append(float(xml_elem.get(attr)))
    return vpy.vec(*attrib_values)


def get_moves(puzzle_tree):
    """
    load mpves from xml tree

    inputs:
    -------
        puzzle_tree - (ElementTree) - ET.ElementTree containing the puzzle info

    returns:
    --------
        (dict) - dictionary containing movenames as keys and a
            list of lists of ints as cycles as values
    """
    move_elems = puzzle_tree.findall("moves/move")
    moves_dict = dict()
    for move_elem in move_elems:
        moves_dict[move_elem.get("name")] = get_cycles(move_elem)
    return moves_dict


def get_cycles(move_elem):
    """
    get a list of all cycles in the given xml element

    inputs:
    -------
        move_elem - (ET.Element) - an xml tree element containing 'cycle' elements

    returns:
    --------
        (list) of lists - list containing all cycles in the move
    """
    cycles = move_elem.findall("cycle")
    cycle_list = []
    for cycle_elem in cycles:
        cycle_str_list = cycle_elem.text.split(", ")
        cycle_int_list = [int(i) for i in cycle_str_list]
        cycle_list.append(cycle_int_list)
    return cycle_list