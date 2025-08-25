from compas.geometry import intersection_line_plane, Plane, Translation, distance_point_point, Frame, Scale
from compas.geometry import Point, bounding_box
import math

def sort_sticks_by_z(sticks):
    """
    Sorts a list of sticks by their z-coordinate.

    Args:
        sticks (list): A list of stick objects.

    Returns:
        list: A list of stick objects sorted by their z-coordinate.
    """
    return sorted(sticks, key=lambda x: min(x.axis.start.z, x.axis.end.z))


def shortest_distance(line1, line2):
    """
    Computes the eccentricity line between this stick and another stick.

    Args:
        other_stick (Stick): Another stick object.

    Returns:
        Line: The compas line representing the eccentricity between the two sticks.
    """
    cross_p = line1.direction.cross(line2.direction)
    q1 = intersection_line_plane(
        line1,
        Plane(
            point=line2.midpoint,
            normal=cross_p.cross(line2.direction),
        ),
    )
    q2 = intersection_line_plane(
        line2,
        Plane(point=line1.midpoint, normal=cross_p.cross(line1.direction)),
    )
    return distance_point_point(q1, q2)

def scale_and_move_to_point(assembly, center):

    scaled_assembly = assembly.copy()
    factor = 0.001 # 1mm to M

    #scale to 1mm
    for part in scaled_assembly.parts():
        S = Scale.from_factors([factor, factor, factor], frame=Frame.worldXY())
        part.transform(S)
        part.frame.transform(S)
        part.attributes["safe_frame"].transform(S)

    points = [p for part in scaled_assembly.parts() for p in part.shape.vertices]
    bbox = bounding_box(points)
    cur_center = Point(0,0,bbox[0][2])

    T = Translation.from_vector(center-cur_center)

    for part in scaled_assembly.parts():
        part.transform(T)
        part.frame.transform(T)
        part.attributes["midpoint"].transform(T)
        part.attributes["safe_frame"].transform(T)

    return scaled_assembly


def generate_default_tolerances(joints):
    DEFAULT_TOLERANCE_METERS = 0.001
    DEFAULT_TOLERANCE_RADIANS = math.radians(0.1)

    return [DEFAULT_TOLERANCE_METERS if j.is_scalable() else DEFAULT_TOLERANCE_RADIANS for j in joints]
