"""
this module explores the creation of custom 3d shapes with vpython.
more specifically the main goal is to create polyhedra and maybe also surface sections of spheres and cylinders.
"""
import time
import vpython as vpy
from vpy_rotation import get_com


class Polyhedron():
    """
    class implementing convex 3D polyhedra using vpython triangle objects
    this is not guaranteed to work for non-convex polyhedra but if they are not too extreme cases, it certainly works too
    """

    def __init__(self, corners, faces,
                 color=vpy.vec(.3, .3, .8),
                 opacity=1,
                 show_faces=True,
                 show_edges=True,
                 sort_faces=True,
                 debug=False):
        """
        inputs:
        -------
            corners - (list) of vpython.vectors- list of 3d coordinates of the corners of the polyhedron
            faces - (list) of lists - lists of corner indices. one sub-list per face of the polyhedron

        examples:
        ---------
            # create a small pyramid
            >>> corners = [(0,0,0), (1,0,0), (0,1,0), (0,0,1)]
            >>> corners = [vpy.vec(*corner) for corner in corners]
            >>> faces = [[0,1,2], [1,2,3], [0,1,3], [0,2,3]]
            >>> poly = polyhedron(corners, faces)
        """
        self.debug = debug
        self.color = color
        self._objects = []
        self.vertices = [vpy.vertex(
            pos=corner, color=self.color, opacity=opacity) for corner in corners]
        # self.vertices = [vpy.vertex(pos=corner, color=corner, opacity=opacity) for corner in corners]
        self.pos = get_com(self.vertices)

        self.faces = faces
        self.face_centers = self._get_face_centers()
        if sort_faces:  # sort the faces so that the polygons are displayed without holes
            self._sort_faces()
        if show_edges:
            self.draw_all_edges()
        if show_faces:
            self.draw_faces()
        # if self.debug:
        #     self.show_faces()
        self.obj = vpy.compound(self._objects)
        for obj in self._objects:
            obj.visible = 0


    def _get_face_centers(self):
        """
        calculate the center point for each face

        returns:
        --------
            (list) of vpython.vectors - center of mass of all points of each face
        """
        face_coms = []
        for face_indices in self.faces:
            face_com = vpy.vec(0, 0, 0)
            face_vertices = [self.vertices[i].pos for i in face_indices]
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
        # print(self.faces)
        # self.show_faces()
        for face_com, face_indices in zip(self.face_centers, self.faces):
            if len(face_indices) > 3:
                start_vec = self.vertices[face_indices[0]].pos - face_com
                face_normal = vpy.cross(
                    start_vec, self.vertices[face_indices[1]].pos - face_com)
                if vpy.diff_angle(face_normal, face_com-self.pos) > vpy.pi/2:
                    face_normal *= -1
                if self.debug:
                    vpy.arrow(axis=face_normal/face_normal.mag*5,
                              pos=face_com, color=vpy.vec(0, 0.8, 0))

                def sort_face(vertex_index):
                    """
                    return the angle between the starting vector and 'self.vertices[vertex_index] - face_com'
                    """
                    current_vec = self.vertices[vertex_index].pos - face_com
                    angle = vpy.diff_angle(start_vec, current_vec) * \
                        sign(vpy.dot(vpy.cross(start_vec, current_vec), face_normal))
                    return angle
                face_indices.sort(key=sort_face)
                del(sort_face) # clean up the internal function
        # print(self.faces)


    def show_faces(self):
        """
        debugging method to check the sorting of the face indices
        """
        for face_com, face_indices in zip(self.face_centers, self.faces):
            for vertex_index in face_indices:
                current_vec = self.vertices[vertex_index].pos - face_com
                arrow = vpy.arrow(pos=face_com, axis=current_vec)
                time.sleep(0.6)
                arrow.visible = 0
                del(arrow)


    def draw_faces(self):
        """
        create triangles for every given face
        """
        for face in self.faces:
            self._draw_face(self.vertices, face)


    def _draw_face(self, vertices, face_indices):
        """
        draw a single face of the polyhedron using vpython triangles
        face_indices must be sorted either clockwise or counterclockwise
        """
        for i in range(1, len(face_indices)-1):
            obj = vpy.triangle(v0=vertices[face_indices[0]],
                               v1=vertices[face_indices[i]],
                               v2=vertices[face_indices[i+1]])
            self._objects.append(obj)


    def draw_all_edges(self):
        """
        draw all face edges of the polyhedron
        """
        for face in self.faces:
            if not -1 in face:
                self._draw_face_edges(self.vertices, face)


    def _draw_face_edges(self, vertices, face, color=vpy.vec(.2, .2, .2), radius=0.025):
        """
        inputs:
        -------
            vor - (scipy.spatial.Voronoi) - a voronoi object
            color - (vpython.vector) - a vpython color vector
            radius - (float) > 0 - radius (= half thickness) of the connecting lines (cylinders)
        """
        for i, j in zip(face, face[1:]+face[:1]):
            point_1 = vertices[i].pos
            point_2 = vertices[j].pos
            obj = vpy.cylinder(pos=point_1, axis=point_2 -
                               point_1, color=color, radius=radius)
            self._objects.append(obj)


    def __and__(self, other):
        """
        define intersection of two polyhedra 
        equal to the intersection of the sets of all points inside the polyhedra

        edge cases are treated as empty intersections:
            if the intersection has no volume (i.e. if it is just a point or line),
            returns None

        inputs:
        -------
            other - (Polyhedron) - another 3D polyhedron

        returns:
        --------
            (NoneType) or (Polyhedron) - None if the intersection is empty,
                otherwise return a new Polyhedron object
        """
        # if not isinstance(other, Polyhedron):
        #     raise TypeError(f"second object should be of type 'Polyhedron' but is of type {type(other)}.")
        dist_vec = other.obj.pos - self.obj.pos
        # check for bounding box overlap. This is very quick and can eliminate lots of cases with empty intersections
        if abs(dist_vec.x) > other.obj.size.x/2 + self.obj.size.x/2 \
                and abs(dist_vec.y) > other.obj.size.y/2 + self.obj.size.y/2 \
                and abs(dist_vec.z) > other.obj.size.z/2 + self.obj.size.z/2:
            return None
        del(dist_vec)
        changed_polyhedron = False # variable to check if the polyhedron was changed
        # We will work on the list of faces but the faces are lists of vpython vectors,
        #   not just refrences to self.vertices
        new_poly_faces = [[self.vertices[i].pos for i in face] for face in self.faces]
        for clip_center, clip_face in zip(other.face_centers, other.faces):
            # calculate normal vector of the clip plane
            clip_vec_0 = other.vertices[clip_face[0]].pos - clip_center
            clip_vec_1 = other.vertices[clip_face[1]].pos - clip_center
            clip_normal_vec = vpy.cross(clip_vec_0, clip_vec_1)
            del(clip_vec_0, clip_vec_1) #cleanup
            # calculate for each point whether it's above or below the clip plane
            relation_dict = get_vertex_plane_relations(new_poly_faces, clip_normal_vec, clip_center)
            # skip calculation if this plane does not intersect the polyhedron
            relation_set = set(relation_dict.values())
            if relation_set == {False}: # all points are above the clip plane
                return None
            if len(relation_set) == 1: # all point are below the clip plane
                continue
            del(relation_set)
            changed_polyhedron = True
            intersected_vertices = list()
            for face in new_poly_faces: # loop over all faces of the polyhedron
                point_1 = face[-1]
                new_face = list()
                for point_2 in face: # loop over all edges of each face
                    point_1_rel = relation_dict[vpy_vec_tuple(point_1)]
                    point_2_rel = relation_dict[vpy_vec_tuple(point_2)]

                    if point_1_rel: #point_1 is below the clip face -> possibly still in the clip polyhedron
                        if not point_1 in new_face:
                            new_face.append(point_1)
                    if (point_1_rel, point_2_rel).count(True) == 1:
                        # if one point is above and the other below, calculate the intersection point:
                        edge_vec = point_2 - point_1
                        t = vpy.dot(clip_center-point_1, clip_normal_vec) / vpy.dot(edge_vec, clip_normal_vec)
                        intersect_point = point_1 + t*edge_vec
                        if not intersect_point in new_face:
                            new_face.append(intersect_point)
                        if not intersect_point in intersected_vertices:
                            intersected_vertices.append(intersect_point)
                        relation_dict[vpy_vec_tuple(intersect_point)] = True

                    point_1 = point_2 # go to next edge

                if len(new_face) > 2:
                    face[:] = new_face
                else:
                    face.clear()#

            if len(intersected_vertices) > 2:
                new_poly_faces.append(intersected_vertices) # add a single new face

            del_empties(new_poly_faces) # delete empty faces

        if not changed_polyhedron: # no faces of 'self' and 'other intersected'
            if set(relation_dict) == set([True]):
                return self # 'self' is completely inside of 'other'
            return None # 'self' is completely outside of 'other'

        return poly_from_faces(new_poly_faces) # the intersection is a new polyhedron


    def __str__(self):
        """
        print some information about the polyhedron self
        """
        info = f"Polyhedron object with {len(self.vertices)} corners and {len(self.faces)} faces."
        return info


def sign(n):
    """
    return sign of the given number n. -1 for negative numbers, +1 for all edge cases (0, nan, ...)
    """
    if n < 0:
        return -1
    return 1


def vpy_vec_tuple(vec):
    """
    return the given vpython vector's coordinates as a tuple
    """
    return (vec.x, vec.y, vec.z)


def del_empties(array, dtype=list):
    """
    delete all instances of dtype() from array. This is done in-place!
    inputs:
    -------
        array - (list) - any python list or similar mutable container
        dtype - (class) - any datatype class that can be called without arguments.
    """
    del_is = []
    for i, sub_list in enumerate(array):
        if sub_list == dtype():
            del_is.append(i)
    for i in reversed(del_is):
        del(array[i])


def get_vertex_plane_relations(faces, plane_normal, plane_anchor):
    """
    given a plane in normal form, calculate a dictionary,
        that stores whether or not each vertex is above (False) or below (True) or on (True) the plane.
    """
    relation_dict = dict()
    # debug_list = list()
    # debug_list.append(vpy.arrow(pos=plane_anchor, axis=plane_normal/plane_normal.mag))
    for face in faces:
        for corner in face:
            vec = vpy_vec_tuple(corner)
            if not vec in relation_dict:
                relation_dict[vec] = vertex_is_inside(corner, plane_normal, plane_anchor)
                # debug_list.append(vpy.sphere(pos=corner, radius=0.1, color=vpy.vec(relation_dict[vec],1-relation_dict[vec],0)))
    # print()
    # for s in debug_list:
    #     s.visible = False
    return relation_dict


def vertex_is_inside(vertex, plane_normal, plane_anchor):
        """
        Checks whether or not a given vertex is below (True) or above (False) a given plane.
        The planes normal vector points towards the 'above' side of the plane.
        If the point is on the plane, also returns True

        inputs:
        -------
            vertex - (vpy.vector) - any 3D point as a vpython vector
            plane_normal - (vpy.vector) - the normal vector of the plane of interest
            plane_anchor - (vpy.vector) - any point on the plane

        returns:
        --------
            (bool) - True if vertex is below or on the plane, 
                False if it is above the plane
        """
        if vpy.diff_angle(vertex-plane_anchor, plane_normal) >= vpy.pi/2:
            return True
        return False


def poly_from_faces(faces):
    """
    create a Polyhedron object with the given faces and the implicitely given corners

    inputs:
    -------
        faces - (list) of (list) of (vpython.vector) - list of faces
            represented by their corners given as 3D vpython vectors

    returns:
    --------
        (Polyhedron) - the polyhedron formed by the faces
    """
    vertex_dict = dict()
    new_faces = list()
    new_corners = list()
    for face in faces:
        new_face = list()
        for corner in face:
            corner_tuple = vpy_vec_tuple(corner)
            if not corner_tuple in vertex_dict:
                vertex_dict[corner_tuple] = len(new_corners)
                new_corners.append(corner)
            new_face.append(vertex_dict[corner_tuple])
        new_faces.append(new_face)
    return Polyhedron(new_corners, new_faces, color=vpy.vec(1,0.6,0), opacity=0.5)


if __name__ == "__main__":
    def my_cube(center, sidelength):
        """
        create a custom cube with the given parameters.
        """
        points = []
        for x in (-1, 1):
            for y in (-1, 1):
                for z in (-1, 1):
                    point = vpy.vec(x, y, z)
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
                            faces.append([i, j, l, k])
        return points, faces


    def my_octahedron(center, radius):
        """
        generate the information to create an octahedron with the given center and radius.
        radius is the radius of the circumsphere passing through all corners
        """
        corners = [(1, 0, 0), (0, 1, 0), (0, 0, 1),
                (-1, 0, 0), (0, -1, 0), (0, 0, -1)]
        corners = [vpy.vec(*corner)*radius+center for corner in corners]
        faces = [[0, 1, 2], [3, 1, 2], [3, 4, 2], [0, 4, 2],
                [0, 1, 5], [3, 1, 5], [3, 4, 5], [0, 4, 5]]
        return corners, faces

    test_shapes = list()


    canvas = vpy.canvas(background=vpy.vec(0.7, 0.7, 0.7), width=1080, height=720)
    # tetrahedron
    corners = [(0,0,0), (1,0,0), (0,1,0), (0,0,1)]
    corners = [vpy.vec(*corner) for corner in corners]
    faces = [[0,1,2], [1,2,3], [0,3,1], [0,2,3]]
    test_shapes.append(Polyhedron(corners, faces, opacity=0.8, show_edges=True))

    #some other shape
    center = vpy.vec(1,.5,1)
    corners = [(0,.5,0), (1,0,0), (0,-.5,0), (0,-.25,1), (-.5,0,-.5)]
    corners = [vpy.vec(*corner)+center for corner in corners]
    faces = [[2,3,4], [0,3,4], [0,1,3], [2,1,3], [1,2,4], [0,1,4]]
    test_shapes.append(Polyhedron(corners, faces, opacity=0.8, show_edges=True, show_faces=True))

    # regular cube
    test_shapes.append(Polyhedron(*my_cube(vpy.vec(2,2,0), 1), opacity=0.8, show_edges=True, show_faces=True))
    test_shapes.append(Polyhedron(*my_cube(vpy.vec(-2,-2,0), .5), opacity=0.8, show_edges=True, show_faces=True))

    # regular octahedron
    test_shapes.append(Polyhedron(*my_octahedron(vpy.vec(.25,.25,1.5), .5), opacity=0.8, show_edges=True, show_faces=True))

    # heptagonal prism
    # center = vpy.vec(0,-.5,-1.3)
    center = vpy.vec(0, -1, 0)
    corners = [(1, 0, 0), (0.5, 0, 0.6), (0, 0, 1), (-0.5, 0, 0.6), (-0.8, 0, 0.1), (-0.4, 0, -0.4), (0.3, 0, -0.4),
               (1, 2, 0), (0.5, 2, 0.6), (0, 2, 1), (-0.5, 2, 0.6), (-0.8, 2, 0.1), (-0.4, 2, -0.4), (0.3, 2, -0.4)]
    corners = [(vpy.vec(*corner)+center)*2 for corner in corners]
    for pos in corners:
        vpy.sphere(pos=pos, radius=0.1)
        # time.sleep(0.1)
    faces = [[5, 0, 6, 3, 4, 1, 2],
             [7, 8, 9, 10, 11, 12, 13],
             [0, 1, 7, 8],
             [1, 2, 8, 9],
             [2, 3, 9, 10],
             [3, 4, 10, 11],
             [5, 4, 11, 12],
             [5, 6, 12, 13],
             [6, 0, 13, 7],
             ]
    # time.sleep(1)
    test_shapes.append(Polyhedron(corners, faces, opacity=0.2, show_edges=True, show_faces=True, sort_faces=True, debug=False))

    intersections = list()
    for shape in test_shapes[:-1]:
        time.sleep(1)
        intersections.append(shape & test_shapes[-1])
        if intersections[-1] != None:
            shape.obj.visible = False

    for inter in intersections:
        print(inter)