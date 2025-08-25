import math

from compas.geometry import Frame, Plane, Point, Polygon, Polyline, Vector
from compas.geometry import Transformation, Translation, Rotation, Quaternion

from compas_viewer import Viewer
viewer = Viewer()

# Point, Vector & Plane
point  = Point(0, 0, 0)
vector = Vector(0, 0, 1)
plane  = Plane(point, vector)
print(point)
print(vector)
print(plane)

# Frame
xaxis = [1, 0, 0]
yaxis = [0, 1, 0]
frame = Frame(point, xaxis, yaxis)
print(frame)

# Polyline
p1 = [0, 0, 0]
p2 = [1, 0, 0]
p3 = [1, 1, 0]
p4 = [0, 0, 0]
polyline = Polyline([p1, p2, p3, p4])
print(polyline)

# Polygon
polygon = Polygon([p1, p2, p3])
print(polygon)

viewer.scene.add(polyline)
viewer.show()

"""
Operations
"""
# Point
p1  = Point(1, 2, 3)
assert p1 ** 3 == [1, 8, 27]
assert p1 + [0, 2, 1] == [1, 4, 4]

# Vector
u = Vector(1, 0, 0)
v = Vector(0, 1, 0)
assert u + v == [1, 1, 0]
assert u.dot(v) == 0.0
assert u.cross(v) == [0, 0, 1]
assert (u * 2).unitized() == [1, 0, 0]


"""
Constructors
"""
a = Vector(1, 0, 0)
b = Vector.from_start_end([1, 0, 0], [2, 0, 0])
assert a == b

a = Plane([0, 0, 0], [0, 0, 1])
b = Plane.from_three_points([0, 0, 0], [1, 0, 0], [0, 1, 0])
assert a == b

a = Frame([0, 0, 0], [3, 0, 0], [0, 2, 0])
b = Frame.from_points([0, 0, 0], [5, 0, 0], [1, 2, 0])
assert a == b


"""
Equivalence
"""
# Point
assert [0, 5, 1] == Point(0, 5, 1)

# Vector
assert [0, 0, 1] == Vector(0, 0, 1)

# Plane
point = [0, 0, 0]
vector = [1, 0, 0]
assert (point, vector) == Plane(point, vector)

# Frame
point = [5, 0, 0]
xaxis = [1, 0, 0]
yaxis = [0, 1, 0]
assert (point, xaxis, yaxis) == Frame(point, xaxis, yaxis)

# Polyline
p1 = [0, 0, 0]
p2 = [1, 0, 0]
p3 = [1, 1, 0]
p4 = [0, 0, 0]
assert [p1, p2, p3, p4] == Polyline([p1, p2, p3, p4])

# Polygon
assert [p1, p2, p3] == Polygon([p1, p2, p3])



"""
Transform
"""
# transform with identity matrix
x = Transformation()
a = Point(1, 0, 0)
b = a.transformed(x)
assert a == b

# translate
t = Translation.from_vector([5, 1, 0])
b = a.transformed(t)
assert b == [6, 1, 0]

# in-place transform
r = Rotation.from_axis_and_angle([0, 0, 1], math.pi)
a.transform(r)
assert str(a) == str(Point(-1.0, 0.0, 0.0))
