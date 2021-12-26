"""
This module provides methods to read the points from a .ggb file
"""
import os
import xml.etree.ElementTree as ET
import shutil
import zipfile

def copy_rename(old_path, new_path = "."):
    """
    copy the *.ggb file to new_path and rename it to *.zip instead of *.ggb

    inputs:
    -------
        old_path - (str) - the path to a .ggb file (including the complete filename)
        new_path - (str) - the folder where the file shall be copied to

    returns:
    --------
        the new path including the zip folder name

    outputs:
    --------
        copies the file from old_path to new_path and change the file ending from .ggb to .zip
    
    errors:
    -------
        raise a ValueError if old_path does not include a .ggb file
    """
    new_name = old_path.split("/")[-1]
    if new_name[-4:] != ".ggb":
        raise ValueError("the given path does not lead to a .ggb file")
    # rename to .zip
    new_name = new_name[:-3] + "zip"
    new_path = os.path.join(new_path, new_name)
    # copy to new_path
    shutil.copy(old_path, new_path)
    return new_path


def get_tree_from_folder(folder_path):
    """
    read the xml tree from geogebra.xml in the zip file given by folder_path
    inputs:
    -------
        folderpath - (str) - a path to a .ggb file renamed as .zip
    returns:
    --------
        (xml.ElementTree) - the contents of the geogebra.xml file
    """
    with zipfile.ZipFile(folder_path, "r") as zip_file:
        #access zipped file
        geogebra_xml = zip_file.extract("geogebra.xml")
        return ET.parse(geogebra_xml)


def points_from_xml_tree(xml_tree):
    """ TODO
    get all points from a given xml tree
    inputs:
    -------
        filepath - (str) - a path to a .ggb file renamed as .zip
    returns:
    --------
        (list) - list of xml Element objects representing all 3d points in the xml file
    """
    elements = xml_tree.findall("construction/element")
    print(f"{__name__}:\tfound {len(elements)} elements")
    points = []
    for elem in elements:
        if elem.get("type") == "point3d":
            points.append(elem)
    print(f"{__name__}:\tfound {len(points)} 3d points")
    return points

def filter_aux_points(points):
    """
    delete all auxiliary points from the given list
    inputs:
    -------
        points - (list) of (xml._.Elements) - a list of all points as xml tree elements
    returns:
    --------
        (list) - list of all non-auxiliary points
    """
    new_points = []
    for point in points:
        if point.find("auxiliary") == None:
            new_points.append(point)
    return new_points

def filter_invis_points(points):
    """
    delete all invisible points from the given list
    inputs:
    -------
        points - (list) of (xml._.Elements) - a list of all points as xml tree elements
    returns:
    --------
        (list) - list of all visible points
    """
    new_points = []
    for point in points:
        if point.find("show").get("object") == "true":
            new_points.append(point)
    return new_points


def filter_points(points):
    """
    delete all invisible or auxiliary points from the given list
    inputs:
    -------
        points - (list) of (xml._.Elements) - a list of all points as xml tree elements
    returns:
    --------
        (list) - list of all visible, non-auxiliary points
    """
    return filter_aux_points(filter_invis_points(points))

if __name__ == "__main__":
    new_path = copy_rename("mixup cube points.ggb")
    tree = get_tree_from_folder(new_path)
    points = points_from_xml_tree(tree)
    points = filter_aux_points(points)
    print(f"found {len(points)} non-auxiliary 3d points")
    points = filter_invis_points(points)
    print(f"found {len(points)} visible, non-auxiliary 3d points")