from compas.geometry import Point, Polyline

from compas_viewer import Viewer


controlpoints = [Point(0, 0, 0), Point(4, 2.5, 0), Point(6, -2.5, 0), Point(10, 0, 0)]

controlpoly = Polyline(controlpoints)

# ==============================================================================
# Visualization
# ==============================================================================
viewer = Viewer()

for point in controlpoints:
    viewer.scene.add(point)

viewer.scene.add(controlpoly)
viewer.show()

