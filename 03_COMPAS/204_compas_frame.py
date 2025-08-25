"""There are several ways to construct a `Frame`.
"""
import math
from compas.geometry import Point
from compas.geometry import Vector
from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Rotation
from compas_viewer import Viewer

# Frame autocorrects axes to be orthonormal
F = Frame(Point(1, 0, 0), Vector(-0.45, 0.1, 0.3), Vector(1, 0, 0))

F = Frame([1, 0, 0], [-0.45, 0.1, 0.3], [1, 0, 0])

F_points = Frame.from_points([1, 1, 1], [2, 3, 6], [6, 3, 0])

F_plane = Frame.from_plane(Plane([0, 0, 0], [0.5, 0.2, 0.1]))

R = Rotation.from_axis_and_angle(Vector.Xaxis(), math.radians(90))

F_rotated = Frame.from_rotation(R, Point(0,0,0))

F_world = Frame.worldXY()

viewer = Viewer()

viewer.config.renderer.show_grid = False
viewer.scene.add(F_points)
viewer.scene.add(F_plane)
viewer.scene.add(F_rotated)
viewer.scene.add(F_world)

viewer.show()