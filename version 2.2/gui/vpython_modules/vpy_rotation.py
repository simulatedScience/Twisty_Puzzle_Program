"""
methods to perform and animate rotations on a list of points
"""
import vpython as vpy
import time

def make_move(points, cycles, POINT_POS, PUZZLE_COM, sleep_time=5e-3, anim_steps=45):
    """
    applies a move given as several cycles to the given points

    inputs:
    -------
        points - (list) - list of points as vpython objects with .pos attribute
        cycle - (list) - list of indeces for the list of points in cycle notation
            e.g. (0,1,2) means the permutation 0->1->2->0

    outputs:
    --------
        the cycles are applied to points, permuting the objects in there.
    """
    move_points = []
    rot_info_list = []
    for cycle in cycles:
        cycle_points, rot_info = calc_rotate_cycle(points, cycle, POINT_POS, PUZZLE_COM=PUZZLE_COM)
        move_points += cycle_points
        rot_info_list += rot_info
    
    apply_rotation(move_points, rot_info_list, sleep_time=sleep_time, anim_steps=anim_steps)

    for cycle in cycles:
        apply_cycle(points, cycle)
        correct_positions(points, POINT_POS, cycle)


def calc_rotate_cycle(points, cycle, POINT_POS, PUZZLE_COM=vpy.vec(0, 0, 0)):
    """
    determines the CoM of all points in the cycle and rotates
        them accordingly.

    inputs:
    -------
        points - (list) - list of points as vpython objects with .pos attribute
        cycle - (list) - list of indeces for the list of points in cycle notation
            e.g. (0,1,2) means the permutation 0->1->2->0

    returns:
    --------
        (list) - list of points moved in this cycle
        (list) - list of rotation instructions as triples
            ('angle', 'axis', 'origin') for each moved point
    """
    COM = get_com([points[i] for i in cycle])

    cycle_points = []
    rot_info_list = []
    for i, j in zip(cycle, cycle[1:]+[cycle[0]]):
        point_A = points[i]
        point_B = points[j]
        rot_info_list.append(calc_rotate_pair(
            point_A, point_B, COM, PUZZLE_COM=PUZZLE_COM))
        cycle_points.append(point_A)

    return cycle_points, rot_info_list


def calc_rotate_pair(point_A, point_B, com, PUZZLE_COM=vpy.vec(0, 0, 0)):
    """
    calculate everything necessary to rotate 'point_A' to 'point_B' around
        the point 'com'

    inputs:
    -------
        point_A - (vpython 3d object) - a vpython object with .pos attribute
            this object will be moved
        point_B - (vpython 3d object) - a vpython object with .pos attribute
            this is the position of 'point_A' after the rotation
        com - (vpy.vector) - the point around which 'point_A' will be rotated

    returns:
    --------
        (float) - angle of rotation in radians
        (vpy.vector) - axis of rotation
        (vpy.vector) - origin for the rotation
    """
    v_A = point_A.pos - com
    v_B = point_B.pos - com
    # check for linear dependence
    if abs(abs(vpy.dot(v_A, v_B)) - v_A.mag * v_B.mag) <= 1e-12:
        mid_point = (point_A.pos + point_B.pos)/2
        axis = mid_point - PUZZLE_COM
        angle = vpy.pi
        return angle, axis, mid_point

    axis = vpy.cross(v_A, v_B)
    angle = vpy.diff_angle(v_A, v_B)
    return angle, axis, com


def apply_rotation(cycle_points, rot_info_list, sleep_time=5e-3, anim_steps=45):
    """
    animate the rotation of all points in 'cycle_points' as specified in 'rot_info_list'.
        the animation contains 'anim_steps' frames

    inputs:
    -------
        cycle_points - (list) - list of vpython objects that shall be rotated
        rot_info_list - (list) - list with rotation information triples:
            ('angle', 'axis', 'origin') of rotation for each object
        anim_steps - (int) - number of frames for the animation

    returns:
    --------
        None

    outputs:
    --------
        changes the position of every object in cycle_points by rotation
            as specified in 'rot_info_list'
    """
    for _ in range(anim_steps):
        for obj, rot_info in zip(cycle_points, rot_info_list):
            angle, axis, com = rot_info
            obj.rotate(angle=angle/anim_steps, axis=axis, origin=com)
            obj.rotate(angle=angle/anim_steps, axis=-axis)
        time.sleep(sleep_time)


def apply_cycle(points, cycle):
    """
    apply the permutation given in 'cycle' to the list 'points' in-place

    inputs:
    -------
        points - (list) - any list
        cycle - (tuple) of ints - a permutation given in cyclic notation
            as a tuple of list indeces (ints)

    returns:
    --------
        None

    outputs:
    --------
        changes the list 'points' in-place by applying the permutation
    """
    j = cycle[0]
    for i in cycle:
        points[i], points[j] = points[j], points[i] # swap points i and j


def correct_positions(points, positions, cycle=None):
    """
    snaps all objects in 'points' to the position specified in 'positions'
    if cycle is specified, only the points in the cycle are updated

    inputs:
    -------
        points - (list) - list of vpython objects
        positions - (list) - list of correct positions as vpython vectors
        cycle - (list) - optional ; indeces of points to be updated

    returns:
    --------
        None

    outputs:
    --------
        changes the position of the objects in 'points' according to 'positions'
    """
    if cycle == None:
        for point, pos in zip(points, positions):
            point.pos = pos
    else:
        for i in cycle:
            points[i].pos = positions[i]


def get_com(points):
    """
    determines the center of mass of all given points.

    inputs:
    -------
        points - (list) - list of points as vpython objects with .pos attribute

    returns:
    --------
        (vpy.vector) - the center of mass of the given objects
    """
    com = vpy.vec(0, 0, 0)
    for obj in points:
        com += obj.pos
    return com/len(points)


if __name__ == "__main__":
    def genCubes():
        """
        generate 8 cubes around (0,0,0) each cube has sidelength 0.5
        """
        offset = vpy.vector(.5, .5, .5)
        size = vpy.vector(.2, .2, .2)
        B1 = vpy.box(pos=vpy.vector(0, 0, 0)-offset,
                    color=vpy.vector(0, 0, 0), size=size, make_trail=True)
        B2 = vpy.box(pos=vpy.vector(0, 0, 1)-offset,
                    color=vpy.vector(0, 0, 1), size=size, make_trail=True)
        B3 = vpy.box(pos=vpy.vector(0, 1, 1)-offset,
                    color=vpy.vector(0, 1, 1), size=size, make_trail=True)
        B4 = vpy.box(pos=vpy.vector(0, 1, 0)-offset,
                    color=vpy.vector(0, 1, 0), size=size, make_trail=True)

        B5 = vpy.box(pos=vpy.vector(1, 0, 0)-offset,
                    color=vpy.vector(1, 0, 0), size=size, make_trail=True)
        B6 = vpy.box(pos=vpy.vector(1, 0, 1)-offset,
                    color=vpy.vector(1, 0, 1), size=size, make_trail=True)
        B7 = vpy.box(pos=vpy.vector(1, 1, 0)-offset,
                    color=vpy.vector(1, 1, 0), size=size, make_trail=True)
        B8 = vpy.box(pos=vpy.vector(1, 1, 1)-offset,
                    color=vpy.vector(1, 1, 1), size=size, make_trail=True)

        return [B1, B2, B3, B4, B5, B6, B7, B8]


    canvas = vpy.canvas(background=vpy.vector(0.8, 0.8, 0.8))
    canvas.lights = []
    vpy.rate(30)
    vpy.distant_light(direction=vpy.vector(-1, 0.8, 1.5),
                      color=vpy.vector(0.7, 0.7, 0.7))

    points = genCubes()
    POINT_POS = [vpy.vec(point.pos) for point in points] # copy of correct point positions for snapping
    PUZZLE_COM = get_com(points) #center of mass of all puzzle points

    # canvas.bind("keydown", lambda _: calc_rotate_cycle(points, [0,2,6,5], POINT_POS, PUZZLE_COM=PUZZLE_COM))
    # canvas.bind("keydown", lambda _: calc_rotate_cycle(points, [0,1,2,3], POINT_POS, PUZZLE_COM=PUZZLE_COM))
    # canvas.bind("keydown", lambda _: calc_rotate_cycle(points, [0,2,5], POINT_POS, PUZZLE_COM=PUZZLE_COM))
    # canvas.bind("keydown", lambda _: calc_rotate_cycle(points, [3,7,4], POINT_POS, PUZZLE_COM=PUZZLE_COM))
    # canvas.bind("keydown", lambda _: make_move(points, [[0,2,5], [3,7,4]], POINT_POS))
    canvas.bind("keydown", lambda _: make_move(points, [[0,2]], POINT_POS))

    # L = [0,1,2,3,4,5,6,7]
    # apply_cycle(L, [0,1,2,3])
    # print(L)
    # apply_cycle(L, [0,1,2,3])
    # print(L)
