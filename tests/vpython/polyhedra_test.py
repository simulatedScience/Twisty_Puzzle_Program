"""
this module explores the creation of custom 3d shapes with vpython.
more specifically the main goal is to create polyhedra and maybe also surface sections of spheres and cylinders.
"""
import time
from numpy import sign
import vpython as vpy
from vpy_rotation import get_com


class polyhedron():
    """
    class implementing convex 3D polyhedra using vpython triangle objects
    this is not guaranteed to work for non-convex polyhedra but if they are not too extreme cases, it certainly works too
    """
    def __init__(self, corners, faces, color=vpy.vec(.3,.3,.8), opacity=1, show_faces=True, show_edges=True, sort_faces=True, debug=False):
        """
        inputs:
        -------
            corners - (list) of vpython.vectors- list of 3d coordinates of the corners of the polyhedron
            faces - (list) of lists - lists of corner indices. one sub-list per face of the polyhedron

        examples:
        ---------
            >>> corners = [(0,0,0), (1,0,0), (0,1,0), (0,0,1)]
            >>> corners = [vpy.vec(*corner) for corner in corners]
            >>> faces = [[0,1,2], [1,2,3], [0,1,3], [0,2,3]]
            >>> poly = polyhedron(corners, faces)
        """
        self.debug=debug
        self.color = color
        self._objects = []
        self._vertices = [vpy.vertex(pos=corner, color=self.color, opacity=opacity) for corner in corners]
        # self._vertices = [vpy.vertex(pos=corner, color=corner, opacity=opacity) for corner in corners]
        self.pos = get_com(self._vertices)

        self._faces = faces
        self._face_centers = self._get_face_centers()
        if sort_faces:
            self._sort_faces()
        if show_faces:
            self._draw_faces()
        if show_edges:
            self._draw_all_edges()
        self.obj = vpy.compound(self._objects)


    def _get_face_centers(self):
        """
        calculate the center point for each face

        returns:
        --------
            (list) of vpython.vectors - center of mass of all points of each face
        """
        face_coms = []
        for face_indices in self._faces:
            face_com = vpy.vec(0,0,0)
            face_vertices = [self._vertices[i].pos for i in face_indices]
            for vertex in face_vertices:
                face_com += vertex
            face_coms.append(face_com/len(face_vertices))
        return face_coms


    def _sort_faces(self):
        """
        sort the vertex indices for every face such that they are listed clockwise as seen from the inside

        since the faces of a convex polyhedron are convex polygons, the center of a face is always inside this polygon.
        therefor the angles between the vectors connecting each vertex to the face center are unique
        """
        # print(self._faces)
        # self.show_faces()
        for face_com, face_indices in zip(self._face_centers, self._faces):
            if len(face_indices) > 3:
                start_vec = self._vertices[face_indices[0]].pos - face_com
                face_normal = vpy.cross(start_vec, self._vertices[face_indices[2]].pos - face_com)

                def sort_face(vertex_index):
                    """
                    return the angle between the starting vector and 'self.vertices[vertex_index] - face_com'
                    """
                    current_vec = self._vertices[vertex_index].pos - face_com
                    angle = vpy.diff_angle(start_vec, current_vec) \
                        * sign(vpy.dot(vpy.cross(start_vec, current_vec), face_normal))
                    # print(vertex_index, angle)
                    return angle
                # print("before", face_indices)
                # print("\nnew\n")
                face_indices.sort(key=sort_face)
                # print("after ", face_indices)
        # print(self._faces)
        if self.debug:
            self.show_faces()


    def show_faces(self):
        """
        debugging method to check the sorting of the face indices
        """
        for face_com, face_indices in zip(self._face_centers, self._faces):
            for vertex_index in face_indices:
                current_vec = self._vertices[vertex_index].pos - face_com
                arrow = vpy.arrow(pos=face_com, axis=current_vec)
                time.sleep(0.6)
                arrow.visible = 0
                del(arrow)


    def _draw_faces(self):
        """
        create triangles for every given face
        """
        for face in self._faces:
            draw_face(self._vertices, face, obj_list=self._objects)


    def _draw_all_edges(self):
        """
        draw all face edges of the polyhedron
        """
        for face in self._faces:
            if not -1 in face:
                draw_face_edges(self._vertices, face, obj_list=self._objects)


def draw_face(vertices, face_indices, obj_list=[]):
    """
    draw a single face of the polyhedron using vpython triangles
    face_indices must be sorted either clockwise or counterclockwise
    """
    for i in range(1, len(face_indices)-1):
        obj = vpy.triangle(v0=vertices[face_indices[0]],
                        v1=vertices[face_indices[i]],
                        v2=vertices[face_indices[i+1]])
        obj_list.append(obj)


def draw_face_edges(vertices, face, color=vpy.vec(.2,.2,.2), radius=0.25, obj_list=[]):
    """
    inputs:
    -------
        vor - (scipy.spatial.Voronoi) - a voronoi object
        color - (vpython.vector) - a vpython color vector
        radius - (float) > 0 - radius (= half thickness) of the connecting lines (cylinders)
    """
    for i, j in zip(face, face[1:]+face[:1]):
        A = vertices[i].pos
        B = vertices[j].pos
        obj = vpy.cylinder(pos=A, axis=B-A, color=color, radius=radius)
        obj_list.append(obj)


def my_cube(center, sidelength):
    """
    create a custom cube with the given parameters.
    """
    points = []
    for x in (-1,1):
        for y in (-1,1):
            for z in (-1,1):
                point = vpy.vec(x,y,z)
                point *= sidelength/2
                point += center
                points.append(point)
    faces = []
    for i, point1 in enumerate(points[:-2]):
        for j, point2 in enumerate(points[i+1:-1], i+1):
            for k, point3 in enumerate(points[j+1:], j+1):
                for l, point4 in enumerate(points[k+1:], k+1):
                    if (point1.x == point2.x == point3.x == point4.x) \
                        or (point1.y == point2.y == point3.y == point4.y) \
                        or (point1.z == point2.z == point3.z == point4.z):
                        # print(point1.x,point2.x,point3.x)
                        # print(i,j,k)
                        faces.append([i,j,l,k])
    return points, faces

def my_octahedron(center, sidelength):
    """
    """
    corners = [(1,0,0), (0,1,0), (0,0,1), (-1,0,0), (0,-1,0), (0,0,-1)]
    corners = [vpy.vec(*corner)*sidelength+center for corner in corners]
    faces = [[0,1,2], [3,1,2], [3,4,2], [0,4,2],
             [0,1,5], [3,1,5], [3,4,5], [0,4,5]]
    return corners, faces


if __name__ == "__main__":
    canvas = vpy.canvas(background=vpy.vec(0.7,0.7,0.7))
    # tetrahedron
    corners = [(0,0,0), (1,0,0), (0,1,0), (0,0,1)]
    corners = [vpy.vec(*corner) for corner in corners]
    faces = [[0,1,2], [1,2,3], [0,3,1], [0,2,3]]
    poly = polyhedron(corners, faces, show_edges=False)

    #some other shape
    center = vpy.vec(1,.5,1)
    corners = [(0,.5,0), (1,0,0), (0,-.5,0), (0,-.25,1), (-.5,0,-.5)]
    corners = [vpy.vec(*corner)+center for corner in corners]
    faces = [[2,3,4], [0,3,4], [0,1,3], [2,1,3], [1,2,4], [0,1,4]]
    poly = polyhedron(corners, faces, show_edges=False)

    # regular cube
    cube = polyhedron(*my_cube(vpy.vec(2,.5,0), 1), show_edges=False)

    # regular octahedron
    octahedron = polyhedron(*my_octahedron(vpy.vec(.25,.25,1.5), .5), show_edges=False)

    # heptagonal prism
    center = vpy.vec(0,-.5,-1.3)
    corners = [(1,0,0), (0.5,0,0.4), (0,0,1), (-0.3,0,0.6), (-0.8,0,0.1), (-0.4,0,-0.4), (0.3, 0, -0.4),
               (1,2,0), (0.5,2,0.4), (0,2,1), (-0.3,2,0.6), (-0.8,2,0.1), (-0.4,2,-0.4), (0.3, 2, -0.4)]
    corners = [vpy.vec(*corner)+center for corner in corners]
    for pos in corners:
        vpy.sphere(pos=pos, radius=0.1)
        time.sleep(0.1)
    faces = [[ 5, 0, 6, 3, 4, 1, 2],
             [ 7, 8, 9,10,11,12,13],
             [0,1,7,8],
             [1,2,8,9],
             [2,3,9,10],
             [3,4,10,11],
             [4,5,11,12],
             [5,6,12,13],
             [6,0,13,7],
             ]
    poly = polyhedron(corners, faces, show_edges=False, sort_faces=True)
