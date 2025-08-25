from compas.geometry import Box
from compas.geometry import Circle
from compas.geometry import Cylinder
from compas.geometry import Frame
from compas.geometry import Plane
from compas.geometry import Sphere
from compas.geometry import Point

from compas_viewer import Viewer

# Box
b1 = Box(5, 1, 3, Frame.worldXY())          # xsize, ysize, zsize
b2 = Box.from_width_height_depth(5, 3, 1)   # width=xsize, height=zsize, depth=ysize
assert str(b1) == str(b2)
print(b1)

# Sphere
s1 = Sphere(5, Frame.worldXY(), Point(0, 0, 0))
print(s1)

# Cylinder
circle = Circle(5, Frame.worldXY())
c1 = Cylinder.from_circle_and_height(circle, height=4)
print(c1)

viewer = Viewer()

viewer.scene.add(b1)
viewer.scene.add(s1)
viewer.scene.add(c1)
viewer.show()