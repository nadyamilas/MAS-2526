from compas.geometry import Point, Plane, Frame, Polygon, Vector, Cylinder, Box, Translation, Brep
from compas_viewer import Viewer

viewer = Viewer()

class Table:
    def __init__(self, length, width, height, leg_size, thickness=1):
        self.length = length
        self.width = width
        self.height = height
        self.thickness = thickness
        self.leg_size = leg_size


        # self.num_legs = num_legs

    def get_table_top(self):
        top = Box(self.length, self.width, self.thickness, Frame([0,0,self.height], [1,0,0], [0,1,0]))
        return top

    def get_void_table(self):
        return Box(self.length-self.leg_size, self.width-self.leg_size, self.thickness, Frame([0,0,self.height], [1,0,0], [0,1,0]))

    def get_table_legs(self):
        void_box = self.get_void_table()
        bottom_pts = []
        for i in void_box.bottom:
            bottom_pts.append(void_box.points[i])

        legs = []
        for pt in bottom_pts:
            T = Translation.from_vector([0, 0, -pt.z/2])
            #pt.transform(T)
            frames_in_pt = Frame(pt, [1,0,0], [0,1,0])
            leg = Box(self.leg_size, self.leg_size, self.height-0.5, frames_in_pt)
            legs.append(leg)
        return legs
  




table = Table(50, 30, 10, 5)
geom = table.get_table_top()
geom_1 = table.get_void_table()
geom_2 = table.get_table_legs()



viewer.scene.add(geom)
viewer.scene.add(geom_1)
viewer.scene.add(geom_2)



viewer.show()
