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


def tetrahedron(radius=1, center=vpy.vec(0,0,0)):
    """
    Create a regular tetrahedron which corners are on a sphere of given radius
        and with the given centerpoint.
    A regular tetrahedron can be generated using four non-adjacent corners of a cube.
        That's how this tetrahedron is created.
    The tetrahedron edges are parallel to the angle bisectors of the x, y and z axes.
    """
    corners = [vpy.vec(1,1,1),
               vpy.vec(0,0,1),
               vpy.vec(1,0,0),
               vpy.vec(0,1,0)]
    corners = [(corner-vpy.vec(.5,.5,.5))*radius*2/vpy.sqrt(3)+center for corner in corners]
    faces = [[0,1,2], [1,0,3], [0,2,3], [1,3,2]]
    return corners, faces


def cube(sidelength=2, center=vpy.vec(0,0,0)):
    """
    create a custom cube with the given parameters.
    The cube's edges are aligned with the x, y and z axes.
    """
    return cuboid(size=vpy.vec(sidelength,sidelength,sidelength), center=center)


def octahedron(radius=1, center=vpy.vec(0,0,0)):
    """
    generate the information to create an octahedron with the given center and radius.
    radius is the radius of the circumsphere passing through all corners

    the diagonals of the returned octahedron are aligned with the x, y and z axes
    """
    corners = [( 1, 0, 0), (0,  1, 0), (0, 0,  1),
               (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
    corners = [vpy.vec(*corner)*radius+center for corner in corners]
    faces = [[0, 1, 2], [3, 1, 2], [3, 4, 2], [0, 4, 2],
            [0, 1, 5], [3, 1, 5], [3, 4, 5], [0, 4, 5]]
    return corners, faces


def cuboid(size=vpy.vec(1,2,3), center=vpy.vec(0,0,0)):
    """
    create a cuboid with the given size in x, y and z direction and the given center.
    The cuboid will be aligned with the x, y and z axes
    """
    corners = []
    for x in (-size.x, size.x):
        for y in (-size.y, size.y):
            for z in (-size.z, size.z):
                point = vpy.vec(x, y, z)
                point /= 2
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


def cylinder(radius=1, height=2, center=vpy.vec(0,0,0), segments=90):
    """
    create a cylinder aligned with the vertical (z-)axis.
    radius or the base and height are the given parameters
    """
    if segments < 3:
        raise ValueError(f"Number of segments cannot be below 3 but was {segments}.")
    rot_vec = vpy.vec(radius,0,0)
    axis = vpy.vec(0,0,1)
    corners_1 = list()
    corners_2 = list()
    for _ in range(segments):
        corners_1.append(rot_vec-vpy.vec(0,0,height/2))
        corners_2.append(rot_vec+vpy.vec(0,0,height/2))
        rot_vec = vpy.rotate(rot_vec, axis=axis, angle=2*vpy.pi/segments)
        # corners_2.append(point_2.rotate(axis=axis, angle=2*vpy.pi/segments, origin=center))
    corners = corners_1 + corners_2
    faces = [list(range(segments)), list(range(segments, 2*segments))]
    for i in range(segments):
        p1 = i
        p2 = (i + 1) % segments
        p3 = (i + 1) % segments + segments
        p4 = i + segments
        faces.append([p1,p2,p3,p4])
    return corners, faces



shapes = {"tetrahedron": tetrahedron,
          "cube": cube,
          "octahedron": octahedron,
          "cuboid": cuboid,
          "cylinder": cylinder}