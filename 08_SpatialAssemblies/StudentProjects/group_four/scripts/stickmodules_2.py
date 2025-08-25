from compas.geometry import Line, Vector, Point, Rotation, Plane, Translation, mirror_point_plane
from stick import Stick
import copy
import math


class NStickModule:
    def __init__(self, sticks=[]):
        self.sticks = sticks


    @classmethod
    def create_3stick_module(cls, pt, stick_length, stick_radius, offset, angle_x, angle_z):
        sticks = []
        offsetpt_x = (pt - Vector(offset, 0, 0))
        offsetpt_y = (pt - Vector(0, offset, 0) - Vector(0, 0, 2 * stick_radius))

        #create Stick1
        stick_1 = Stick(Line(offsetpt_x, offsetpt_x + Vector(stick_length, 0, 0)), stick_radius)
        sticks.append(stick_1)

        #create Stick2
        stick_2 = Stick(Line(offsetpt_y, offsetpt_y + Vector(0, stick_length, 0)), stick_radius)
        R_x = Rotation.from_axis_and_angle(Vector(stick_radius*2, 0, 0), angle_x, stick_1.axis.start)
        stick_2.axis.transform(R_x)
        axisxy = stick_1.eccentricity(stick_2)
        e_vectorxy = Vector(axisxy.end.x - axisxy.start.x, axisxy.end.y - axisxy.start.y, axisxy.end.z - axisxy.start.z)
        R_z = Rotation.from_axis_and_angle(e_vectorxy, angle_z, axisxy.start)
        stick_2.axis.transform(R_z)
        sticks.append(stick_2)

        #create Stick3
        stick_3 = Stick(
            Line(offsetpt_x*2 - offsetpt_y + Vector(stick_length, 0, 0), offsetpt_x*2 - offsetpt_y + Vector(stick_length, 0, 0) - Vector(0, stick_length, 0))
            , stick_radius
            )
        R_x = Rotation.from_axis_and_angle(Vector(stick_radius*2, 0, 0), angle_x, stick_1.axis.end)
        stick_3.axis.transform(R_x)
        e_axisxz = stick_3.eccentricity(stick_1)
        e_vectorxy = Vector(e_axisxz.end.x - e_axisxz.start.x, e_axisxz.end.y - e_axisxz.start.y, e_axisxz.end.z - e_axisxz.start.z)
        R_z = Rotation.from_axis_and_angle(e_vectorxy, angle_z, e_axisxz.start)
        stick_3.axis.transform(R_z)
        sticks.append(stick_3)

        return cls(sticks)

    @classmethod
    def next_module(cls, module):
        sticks = []
        e_line = module.sticks[0].eccentricity(module.sticks[1])
        e_vector = Vector(e_line.end.x - e_line.start.x, e_line.end.y - e_line.start.y, e_line.end.z - e_line.start.z)




        return cls(sticks)



    @property
    def geometry(self):
        return [stick.geometry for stick in self.sticks]

    @property
    def center(self):
        x = sum([s.axis.end.x for s in self.sticks])/len(self.sticks)
        y = sum([s.axis.end.y for s in self.sticks])/len(self.sticks)
        z = (self.sticks[0].axis.end.z + self.sticks[0].axis.start.z)/2.0
        return Point(x,y,z)

    def rotate(self, angle):
        R = Rotation.from_axis_and_angle(Vector(0, 1, 0), angle, (0,0,0))
        for stick in self.sticks:
            stick.axis.transform(R)

    def move(self, vector):
        T = Translation.from_vector(vector)
        for stick in self.sticks:
            stick.axis.transform(T)

    def flip(self):
        for stick in self.sticks:
            start_z = stick.axis.start.z
            stick.axis.start.z = stick.axis.end.z
            stick.axis.end.z = start_z

