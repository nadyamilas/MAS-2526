from compas.geometry import Point, Vector, Frame, Box, Translation,Rotation

import math
class Brick:
    LENGTH = 32
    WIDTH = 15.2
    HEIGHT = 9.87
    def __init__(self, center):
        self.center = center
        self.frame = Frame(point=center, xaxis = Vector.Xaxis(), yaxis = Vector.Yaxis())
        self.length = Brick.LENGTH
        self.width = Brick.WIDTH
        self.height = Brick.HEIGHT
        self.x_index = None
        self.y_index = None
    def rotate_brick(self, angle):
        transformation = Rotation.from_axis_and_angle(axis=Vector.Zaxis(), angle = math.radians(angle), point = self.center)
        self.frame.transform(transformation)

    def geometry(self):
        box = Box(xsize=self.length, ysize=self.width, zsize=self.height, frame=self.frame)
        return box
    def generate_pick_frame(self):
        pick_frame = self.frame.transformed(Translation.from_vector(Vector(0,0,self.height/2)))
        return pick_frame

def create_wall(origin, length, height,gap):
    number_of_layers = int(height // Brick.HEIGHT)
    number_x = int(length // Brick.LENGTH)
    all_bricks = []
    for i in range(number_of_layers):
        for j in range(number_x):
            if i%2 == 0:
                my_brick = Brick(center=Point(j*Brick.LENGTH + j*gap,0,i*Brick.HEIGHT+i*gap))
            else:
                my_brick = Brick(center=Point(j*Brick.LENGTH + Brick.LENGTH/2+ j*gap,0,i*Brick.HEIGHT+i*gap))
            my_brick.rotate_brick(i)
            my_brick.x_index = j
            my_brick.y_index = i
            all_bricks.append(my_brick)
    return all_bricks

if __name__ == "__main__":
    from compas_viewer import Viewer
    def visualize_brick_wall(my_bricks):
        viewer = Viewer()
        for brick in my_bricks:
            viewer.scene.add(brick.geometry())
        
        viewer.show()


# my_wall = create_wall(Point(0,0,0), length=150, height=150,gap=1)
# visualize_brick_wall(my_wall)