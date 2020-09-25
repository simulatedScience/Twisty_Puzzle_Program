"""
module to provide some different pre-defined polyhedra
so far inclduded:
    - cube
    - octahedron
planned:
    - regular tetrahedron
    - regular dodecahedron
    - sphere?
    - cylinder?
"""
import vpython as vpy


def cube(sidelength=2, center=vpy.vec(0,0,0)):
    """
    create a custom cube with the given parameters.
    """
    corners = []
    for x in (-1, 1):
        for y in (-1, 1):
            for z in (-1, 1):
                point = vpy.vec(x, y, z)
                point *= sidelength/2
                point += center
                corners.append(point)
    faces = []
    for i, point1 in enumerate(corners[:-2]):
        for j, point2 in enumerate(corners[i+1:-1], i+1):
            for k, point3 in enumerate(corners[j+1:], j+1):
                for l, point4 in enumerate(corners[k+1:], k+1):
                    if (point1.x == point2.x == point3.x == point4.x) \
                            or (point1.y == point2.y == point3.y == point4.y) \
                            or (point1.z == point2.z == point3.z == point4.z):
                        # print(point1.x,point2.x,point3.x)
                        # print(i,j,k)
                        faces.append([i, j, l, k])
    return corners, faces


def octahedron(radius=1, center=vpy.vec(0,0,0)):
    """
    generate the information to create an octahedron with the given center and radius.
    radius is the radius of the circumsphere passing through all corners
    """
    corners = [( 1, 0, 0), (0,  1, 0), (0, 0,  1),
               (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
    corners = [vpy.vec(*corner)*radius+center for corner in corners]
    faces = [[0, 1, 2], [3, 1, 2], [3, 4, 2], [0, 4, 2],
            [0, 1, 5], [3, 1, 5], [3, 4, 5], [0, 4, 5]]
    return corners, faces


shapes = {"cube": cube,
          "octahedron": octahedron}