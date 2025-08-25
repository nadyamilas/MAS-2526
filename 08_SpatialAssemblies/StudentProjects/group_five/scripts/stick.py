from compas.geometry import Plane, Circle, Cylinder, Line, Vector, Frame, Rotation
from compas.geometry import intersection_line_plane, Scale
import math
import Rhino.Geometry as rg
import copy

class Stick:
    # class attributes
    RADIUS = 2.0
    # constructor with axis and radius
    def __init__(self, axis, radius_stick=RADIUS):
        self.axis = axis
        self.radius = radius_stick
        self.frame = None

    # constructor to create a stick between two other sticks
    @classmethod
    def from_two_sticks(cls, stick0, stick1, param0, param1, max_iterations=50, length = None):
        """
        Creates a stick between two other sticks so that they touch but not intersect.

        Args:
            cls (Stick): The Stick class.
            stick0 (Stick): The first stick object.
            stick1 (Stick): The second stick object.
            param0 (float): Parameter indicating the position on stick0.
            param1 (float): Parameter indicating the position on stick1.
            max_iterations (int, optional): Maximum number of iterations. Defaults to 50.

        Returns:
            Stick: A new stick object created between stick0 and stick1.
        """
        # Find point on stick0 at param0
        start = stick0.axis.point(param0)
        end = stick1.axis.point(param1)
        # create a plane on the line connecting p0 and p1
        vec01 = Vector.from_start_end(start, end)
        # create a plane on the line connecting p0 and p1 using only normal and origin
        cross0 = stick0.axis.direction.cross(vec01)
        p0 = Plane(point=start, normal=cross0)
        cross1 = stick1.axis.direction.cross(vec01)
        p1 = Plane(point=end, normal=cross1)

        stick = cls(Line(start, end))

        # solver properties
        buffer0 = buffer1 = cls.RADIUS
        counter = 0
        max_clearance = cls.RADIUS * 2
        condition = [True, True]

        while condition[0] or condition[1]:
            # if the favorable position cannot be found, break the loop after max_iterations
            if counter > max_iterations:
                break
            # move the axes along the plane of each stick
            pt0 = start + p0.normal.scaled(buffer0)
            pt1 = end - p1.normal.scaled(buffer1)
            # update the axis of the stick
            stick.axis = Line(pt0, pt1)
            # check eccentricity
            clearance0 = stick.eccentricity(stick0).length
            clearance1 = stick.eccentricity(stick1).length
            # update condition
            condition = [clearance0 < max_clearance, clearance1 < max_clearance]
            # update buffer
            if condition[0]:
                buffer0 += 0.1
            if condition[1]:
                buffer1 += 0.1
            counter += 1  # control how many times the loop has been run

        message = (
            "solution found in %i iterations" % (counter)
            if counter <= max_iterations + 1
            else "solution not found"
        )
        print(message)  # print message

        if(length is not None):
            # scale stick to length
            S = Scale.from_factors(
                [
                    length / stick.axis.length,
                    length / stick.axis.length,
                    length / stick.axis.length,
                ],
                frame=Frame(
                    point=stick.axis.midpoint,
                    xaxis=stick.axis.direction,
                    yaxis=stick.axis.direction.cross(Vector(0, 0, 1)),
                ),
            )
            stick.axis.transform(S)
            stick.frame = Frame(
                point=stick.axis.midpoint,
                xaxis=-stick.axis.direction,
                yaxis=stick.axis.direction.cross(stick0.axis.direction)
            )
        return stick

    @classmethod
    def from_two_corners(cls, c0_s0, c0_s1, c1_s0, c1_s1, max_iterations=50, length = None):
        """
        Creates a stick between two corners of two sticks.
        c0_s0: stick 0 of corner 0
        c0_s1: stick 1 of corner 0
        c1_s0: stick 0 of corner 1
        c1_s1: stick 1 of corner 1
        """
        # find intersection of stick 0 of corner 0 and stick 1 of corner 0
        start = c0_s0.eccentricity(c0_s1).midpoint
        # find intersection of stick 0 of corner 1 and stick 1 of corner 1
        end = c1_s0.eccentricity(c1_s1).midpoint
        # create stick
        stick = cls(Line(start, end))

        vec01 = Vector.from_start_end(start, end)
        c0s0_norm = c0_s1.axis.direction.unitized()#c0_s0.axis.direction.cross(vec01).unitized()
        c1s1_norm = -c1_s0.axis.direction.unitized()#c1_s0.axis.direction.cross(vec01).unitized()
        c0s1_norm = -c0_s0.axis.direction.unitized()#c0_s1.axis.direction.cross(vec01).unitized()
        c1s0_norm = c1_s1.axis.direction.unitized()#c1_s1.axis.direction.cross(vec01).unitized()
        # solver properties
        buffers = [cls.RADIUS] * 4
        counter = 0
        max_clearance = cls.RADIUS * 2
        condition = [True, True, True, True]

        while any(condition):
            # if the favorable position cannot be found, break the loop after max_iterations
            if counter > max_iterations:
                break
            # move the axes along the plane of each stick
            pt0 = start + c0s0_norm.scaled(buffers[0]) + c0s1_norm.scaled(buffers[1])
            pt1 = end + c1s0_norm.scaled(buffers[2]) + c1s1_norm.scaled(buffers[3])
            # update the axis of the stick
            stick.axis = Line(pt0, pt1)
            # check eccentricity
            clearance00 = stick.eccentricity(c0_s0).length
            clearance10 = stick.eccentricity(c0_s1).length
            clearance01 = stick.eccentricity(c1_s0).length
            clearance11 = stick.eccentricity(c1_s1).length
            clearances = (clearance00, clearance01, clearance10, clearance11)
            # update condition
            condition = [clearance00 < max_clearance,
                            clearance01 < max_clearance,
                            clearance10 < max_clearance,
                            clearance11 < max_clearance]

            # update buffer
            for i in range(4):
                if condition[i]:
                    buffers[i] += 0.1 * clearances[i] / max_clearance
            counter += 1  # control how many times the loop has been run

        message = (
            "solution found in %i iterations" % (counter)
            if counter <= max_iterations + 1
            else "solution not found"
        )
        print(message)  # print message

        if(length is not None):
            # scale stick to length
            S = Scale.from_factors(
                [
                    length / stick.axis.length,
                    length / stick.axis.length,
                    length / stick.axis.length,
                ],
                frame=Frame(
                    point=stick.axis.midpoint,
                    xaxis=Vector.Xaxis(),
                    yaxis=Vector.Yaxis(),
                ),
            )
            stick.axis.transform(S)
            stick.frame = Frame(
                point=stick.axis.midpoint,
                xaxis=-stick.axis.direction,
                yaxis=stick.axis.direction.cross(c0_s1.axis.direction)
            )
        return stick

    @classmethod
    def from_path_interpolation(cls, curve, length_stick, radius_stick=RADIUS):
        """
        Creates a series of sticks following a curve using the tangents on the curve in a way that the sticks touch but not intersect.

        Args:
            cls (Stick): The Stick class.
            curve (Curve): The Curve to follow.
            stick_length (float): The Length of the Sticks.
            radius_stick (float): The Radius of the Sticks.

        Returns:
            list[Stick]: A series of stick objects created following the path of the curve.
        """
        # divide the curve by length
        param = curve.DivideByLength(length_stick/2, False)
        # find the tangent at each point
        sticks = []
        for p in param:
            tangent = curve.TangentAt(p)
            tangent.Unitize()
            mid = curve.PointAt(p)
            # compas_tangent = Vector(tangent.X, tangent.Y, tangent.Z)

            t_start = rg.Transform.Translation(tangent * length_stick/2)
            t_end = rg.Transform.Translation(tangent * -length_stick/2)

            tangent_start = copy.deepcopy(mid)
            tangent_end = copy.deepcopy(mid)

            tangent_start.Transform(t_start)
            tangent_end.Transform(t_end)


            axis = Line(tangent_end, tangent_start)
            stick = Stick(axis, radius_stick)
            sticks.append(stick)
        return sticks

    @property
    def geometry(self):
        """
        Computes the geometry of the stick as a cylinder based on its axis and radius.

        Returns:
            Cylinder: A compas cylinder object representing the stick's geometry.
        """
        plane = Plane(self.axis.midpoint, self.axis.direction)
        circle = Circle(plane, self.radius)
        return Cylinder(circle, self.axis.length)

    def eccentricity(self, other_stick):
        """
        Computes the eccentricity line between this stick and another stick.

        Args:
            other_stick (Stick): Another stick object.

        Returns:
            Line: The compas line representing the eccentricity between the two sticks.
        """
        cross_p = self.axis.direction.cross(other_stick.axis.direction)
        q1 = intersection_line_plane(
            self.axis,
            Plane(
                point=other_stick.axis.midpoint,
                normal=cross_p.cross(other_stick.axis.direction),
            ),
        )
        q2 = intersection_line_plane(
            other_stick.axis,
            Plane(point=self.axis.midpoint, normal=cross_p.cross(self.axis.direction)),
        )
        return Line(q1, q2)

    def shift(self, length):
        """
        Shifts the stick along its axis by a specified length.

        Args:
            length (float): The amount to shift the stick along its axis.
        """
        self.axis.end = self.axis.end + self.axis.direction * length
        self.axis.start = self.axis.start + self.axis.direction * length

    def rotate_stick(self, angle, rotation_axis=None):
        """
        Rotates the stick around its axis by a specified angle.

        Args:
            angle (float): The angle in radians for the stick's rotation.
            rotation_axis (Vector, optional): The axis of rotation. If not provided,
                defaults to a vector perpendicular to the stick's axis in the z-direction.
        """
        if not rotation_axis:
            rotation_axis = self.axis.direction.cross(Vector(0,0,1))
        R = Rotation.from_axis_and_angle(rotation_axis, angle, self.axis.midpoint)
        self.axis.transform(R)

    def eccentricity_rotation_angle(self, alpha):
        """
        Computes the rotation angle for the stick to ensure a perpendicular eccentricity.

        Args:
            alpha (float): half of the interior angle in radians of a regular polygon

        Returns:
            float: The rotation angle computed.
        """
        teta = self.radius/math.sqrt((self.axis.length/2.0)**2 - ((self.radius**2.0)/math.sin(alpha)**2))
        return math.atan(teta)

    def set_length(self, length):
        """
        Sets the length of the stick by adjusting the start position of the axis.

        Args:
        - length (float): The new length to set for the stick.

        """
        self.axis.start = self.axis.end - self.axis.direction * length

    def scale(self, factor):
        """
        Scales the stick by a specified factor.

        Args:
            factor (float): The factor by which to scale the stick.
        """
        S = Scale.from_factors(
            [factor, factor, factor],
            frame=Frame.worldXY(),
        )
        self.axis.transform(S)
        self.radius = self.radius * factor

