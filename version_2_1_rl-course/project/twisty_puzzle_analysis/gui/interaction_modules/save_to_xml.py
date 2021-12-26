"""
methods to save information about a puzzle in an xml file
"""
# import xml.etree.ElementTree as ET
import lxml.etree as let
import os


def save_to_xml(puzzle):
    """
    saves the puzzle defined in 'puzzle_info_dict' in a file 'puzzle_definition.xml'

    inputs:
    -------
        puzzlename - (str) - the name of the puzzle
        puzzle_info_dict - (dict) - dictionary containing the keys:
            "point_dicts" - list of dictionaries containing point information:
                "coords" - list of x,y,z coordinates
                "vpy_color" - vpython color vector (r,g,b) in range 0-1
            "moves" - dictionary containing moveames as keys and lists of cycles as values

    returns:
    --------
        None

    outputs:
    --------
        creates a folder 'puzzlename' and in it a file 'puzzledefinition.xml'
            containing all important puzzle information
    """
    puzzle_name = puzzle.PUZZLE_NAME
    root_elem = let.Element("puzzledefinition", name=puzzle_name)
    root_elem.tail = "\n\t"
    save_points(root_elem, puzzle.POINT_INFO_DICTS)
    try:
        save_moves(root_elem, puzzle.moves)
    except KeyError:
        pass
    try: # create a "puzzles" folder if it doesn't exist yet
        os.mkdir(os.path.join(os.path.dirname(__file__), "..", "puzzles"))
    except FileExistsError:
        pass
    try: # create a folder for the given puzzle if it doesn't exist yet
        os.mkdir(os.path.join(os.path.dirname(__file__), "..", "puzzles", puzzle_name))
    except FileExistsError:
        pass
    puzzle_tree = let.ElementTree(root_elem)
    xml_string = let.tostring(puzzle_tree,
                              pretty_print=True,
                              xml_declaration=True,
                              encoding='UTF-8')
    with open(os.path.join(os.path.dirname(__file__), "..", "puzzles", puzzle_name, "puzzle_definition.xml"), "wb") as file:
        file.write(xml_string)
    # puzzle_tree.write(os.path.join(puzzlename, "puzzle_definition.xml"))


def save_points(root_elem, point_info_dicts):
    """
    adds the points to the given ElementTree 'puzzle_tree'

    inputs:
    -------
        root_elem - (let.?) - root object where points will be saved
        point_info_dicts - (list) - list of dictionaries containing point information:
            "coords" - list of x,y,z coordinates
            "vpy_color" - vpython color vector (r,g,b) in range 0-1

    returns:
    --------
        None
    """
    points_elem = let.SubElement(root_elem, "points")
    # points_elem.tail = "\n\t\t"
    #add all point information
    for point_dict in point_info_dicts:
        point = let.SubElement(points_elem, "point", size=str(point_dict["size"]))
        # point.tail = "\n\t\t"
        # adding point coordinates
        x, y, z = vpy_vec_to_triple(point_dict["coords"])
        coords = let.SubElement(point, "coords", x=x, y=y, z=z)
        # coords.tail = "\n\t\t\t"
        # adding point color
        r, g, b = vpy_vec_to_triple(point_dict["vpy_color"])
        color = let.SubElement(point, "color", r=r, g=g, b=b)
        # color.tail = "\n\t\t"


def save_moves(root_elem, moves_dict):
    """
    writes moves as SubElements of 'root_elem'

    inputs:
    -------
        root_elem - (let.Element) - 
        moves_dict - (dict) - dictionary with move information:
            keys: movenames
            values: list of lists of ints as cycles

    returns:
    --------
        None
    """
    moves_elem = let.SubElement(root_elem, "moves")
    for movename, movelist in moves_dict.items():
        move = let.SubElement(moves_elem, "move", name=movename)
        for cycle in movelist:
            cycle_elem = let.SubElement(move, "cycle")
            cycle_elem.text = str(cycle)[1:-1]


def vpy_vec_to_triple(vpy_vec):
    """
    converts a vpython vector to a python triple
    """
    return str(vpy_vec.x), str(vpy_vec.y), str(vpy_vec.z)