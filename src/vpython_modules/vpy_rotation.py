"""
methods to perform and animate rotations on a list of points
"""
import vpython as vpy
import time

def animate_move(
        points: list[vpy.baseObj],
        cycles: list[list[int]],
        POINT_POS: list[vpy.vector],
        PUZZLE_COM: vpy.vector = vpy.vec(0, 0, 0),
        animation_time: float = 0.25,
        target_fps: float = 60,
    ) -> None:
    """
    applies a move given as several cycles to the given points

    Args:
        points (list[vpy.baseOby]): list of points as vpython objects with .pos attribute
        cycles (list[list[int]]): a move's permutation in cyclic form
            e.g. (0,1,2) means the permutation 0->1->2->0
        POINT_POS (list[vpy.vector]): correct positions of the points for snapping. Order must match `points`.

    Returns:
        None

    Side Effects:
        the cycles are applied to points, permuting the objects in there.
    """
    move_points = []
    rot_info_list = []
    affeced_points: set[int] = set()
    max_cycle_order = max([len(cycle) for cycle in cycles])
    avg_rotation_axis = vpy.vec(0, 0, 0)
    for cycle in cycles:
        if len(cycle) < 2: # skip 1-cycles for now
            continue
        cycle_points, rot_info = calc_rotate_cycle(
                points,
                cycle,
                # POINT_POS,
                PUZZLE_COM=PUZZLE_COM)
        affeced_points.update(set(cycle))
        move_points += cycle_points
        rot_info_list += rot_info
        if len(cycle) > 2:
            avg_rotation_axis += rot_info[0][1]
    if max_cycle_order == 2:
        axis = get_order_2_axis(points, cycles)
        move_com = get_com(move_points)
        for i, rot_info in enumerate(rot_info_list):
            rot_info_list[i] = (rot_info[0], axis, rot_info[2])
    
        
        
    # flip rotation axis of 2-cycles if necessary
    rot_info_index = 0
    for cycle in cycles:
        if len(cycle) < 2: # skip 1-cycles for now
            continue
        if len(cycle) > 2:
            rot_info_index += len(cycle)
            continue
        for _ in range(len(cycle)):
            rot_info = rot_info_list[rot_info_index]
            if vpy.dot(avg_rotation_axis, rot_info[1]) < 0:
                rot_info_list[rot_info_index] = (
                    rot_info[0], -rot_info[1], rot_info[2]
                )
            rot_info_index += 1
    # apply rotations to points displayed in 3D
    apply_rotation(
        move_points,
        rot_info_list,
        animation_time=animation_time,
        target_fps=target_fps)
    # apply permutations to internal list of points
    for cycle in cycles:
        if len(cycle) < 2: # skip 1-cycles for now
            continue
        apply_cycle(points, cycle)
        # snap affected points to correct positions
        correct_positions(points, POINT_POS, cycle)
    
def get_order_2_axis(
        points: list[vpy.baseObj],
        cycles: list[list[int]],
    ) -> vpy.vector:
    """
    Get a suitable rotation axis if the move contains only 2-cycles by finding a rotation axis using multiple 2-cycles.
    The rotation axis will be chosen such that the rotation direction is no more than 90° from (1,1,1).

    Args:
        points (list[vpy.baseObj]): list of points as vpython objects with .pos attribute
        cycles (list[list[int]]): a move's permutation in cyclic form
            e.g. (0,1,2) means the permutation 0->1->2->0
    
    Returns:
        vpy.vector: a suitable rotation axis for the move
    """
    if len(cycles) == 1:
        # this method does not work if only one 2-cycle exists
        return vpy.vec(0, 0, 0)
    average_axis: vpy.vector = vpy.vec(0, 0, 0)
    for idx_1, cycle_1 in enumerate(cycles):
        if len(cycle_1) != 2:
            continue
        vec_1 = points[cycle_1[1]].pos - points[cycle_1[0]].pos
        for cycle_2 in cycles[idx_1+1:]:
            if len(cycle_2) != 2:
                continue
            vec_2 = points[cycle_2[1]].pos - points[cycle_2[0]].pos
            vec_3 = vpy.cross(vec_1, vec_2)
            if vpy.dot(average_axis, vec_3) < 0:
                vec_3 *= -1
            average_axis += vec_3
    # bias the average axis towards positive values to make rotation direction independent of cycle ordering
    bias_direction: vpy.vector = vpy.vec(1, 1, 1)
    if vpy.dot(average_axis, bias_direction) < 0:
        average_axis *= -1
    # return normalized average axis
    return average_axis.norm()

def calc_rotate_cycle(
        points: list[vpy.baseObj],
        cycle: list[int],
        PUZZLE_COM: vpy.vector = vpy.vec(0, 0, 0),
    ) -> tuple[list[vpy.baseObj], list[tuple[float, vpy.vector, vpy.vector]]]:
    """
    determines the CoM of all points in the cycle and rotates
        them accordingly.

    Args:
        points (list[vpy.baseObj]): list of points as vpython objects with .pos attribute
        cycles (list[int]): a single cycle of a move's permutation in cyclic form
            e.g. (0,1,2) means the permutation 0->1->2->0

    Returns:
        list[vpy.baseObj]: list of points moved in this cycle
        list[tuple[float, vpy.vector, vpy.vector]]: list of rotation instructions as triples
            (`angle`, `axis`, `origin`) for each moved point
    """
    COM = get_com([points[i] for i in cycle])

    cycle_points = []
    rot_info_list = []
    for i, j in zip(cycle[1:]+[cycle[0]], cycle):
        point_A = points[i]
        point_B = points[j]
        rot_info_list.append(
            calc_rotate_pair(
                point_A,
                point_B,
                COM,
                PUZZLE_COM=PUZZLE_COM,
            )
        )
        cycle_points.append(point_A)

    return cycle_points, rot_info_list


def calc_rotate_pair(point_A, point_B, com, PUZZLE_COM=vpy.vec(0, 0, 0)):
    """
    calculate everything necessary to rotate 'point_A' to 'point_B' around
        the point 'com'

    Args:
        point_A (vpython 3d object): a vpython object with .pos attribute
            this object will be moved
        point_B (vpython 3d object): a vpython object with .pos attribute
            this is the position of 'point_A' after the rotation
        com (vpy.vector): the point around which 'point_A' will be rotated

    Returns:
        float: angle of rotation in radians
        vpy.vector: axis of rotation
        vpy.vector: origin for the rotation
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


def apply_rotation(
        cycle_points: list[vpy.baseObj],
        rot_info_list: list[tuple[float, vpy.vector, vpy.vector]],
        animation_time: float = 0.25,
        target_fps: float = 60):
    """
    animate the rotation of all points in 'cycle_points' as specified in 'rot_info_list'.
        the animation contains 'anim_steps' frames

    Args:
        cycle_points (list[vpy.baseObj]): list of vpython objects that will be rotated
        rot_info_list (list[tuple[float, vpy.vector, vpy.vector]]): list with rotation information triples:
            (`angle`, `axis`, `origin`) of rotation for each object
        animation_time (float): time in seconds for the animation
        target_fps (int): target frames per second for the animation

    Returns:
        None

    Side effects:
        changes the position atttribute of every object in cycle_points according to the rotation described in `rot_info_list`
    """
    # calculate steps for 60 fps given animation time
    anim_steps: int = int(target_fps*animation_time)
    anim_steps: int = max(1, anim_steps)
    start_time = time.time()
    for step in range(anim_steps):
        # rotate each object individually
        for obj, rot_info in zip(cycle_points, rot_info_list):
            angle, axis, com = rot_info
            obj.rotate(angle=angle/anim_steps, axis=axis, origin=com)
            # obj.rotate(angle=angle/anim_steps, axis=-axis)
        sleep_until = start_time + (step+1)*animation_time/anim_steps
        time.sleep(max(0, sleep_until - time.time()))


def apply_cycle(
        points: list[any],
        cycle: list[int],
    ) -> None:
    """
    apply the permutation given in 'cycle' to the list `points` in-place

    Args:
        points (list[any]): List of objects that will be permuted
        cycle (list[int]): A single cycle of a permutation in cyclic form

    Returns:
        None

    Side Effects:
        changes the list `points` in-place by applying the permutation
    """
    j = cycle[0]
    # for i in cycle:
    for i in cycle[-1:0:-1]:
        points[i], points[j] = points[j], points[i] # swap points i and j


def correct_positions(
        points: list[vpy.baseObj],
        positions: list[vpy.vector],
        cycle: list[int] = None) -> None:
    """
    Snap all objects in `points` to the position specified in `positions`
    if cycle is specified, only the points in the cycle are updated

    Args:
        points (list): list of vpython objects
        positions (list): list of correct positions as vpython vectors
        cycle (list): optional ; indeces of points to be updated

    Returns:
        None

    Side Effects:
        changes the position of the objects in `points` according to `positions`
    """
    if not cycle:
        for point, pos in zip(points, positions):
            point.pos = pos
    else:
        for i in cycle:
            points[i].pos = positions[i]


def get_com(points: list[vpy.baseObj]) -> vpy.vector:
    """
    determines the center of mass of the given points. (sum of points / number of points)

    Args:
        points (list[vpy.baseObj]): list of points as vpython objects with .pos attribute

    Returns:
        vpy.vector: the center of mass of the given objects
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
    canvas.bind("keydown", lambda _: animate_move(points, [[0,2]], POINT_POS))

    # L = [0,1,2,3,4,5,6,7]
    # apply_cycle(L, [0,1,2,3])
    # print(L)
    # apply_cycle(L, [0,1,2,3])
    # print(L)
