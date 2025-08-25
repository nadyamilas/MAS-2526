from compas.geometry import Point, Box, Frame, Vector, Curve
import compas.geometry as cg
import math

class Brick:
    #class variables
    LENGTH = 32
    WIDTH = 15
    HEIGHT = 10

    def __init__(self, position, direction = None):
        """
        Constructor to create a brick
        position: compas.geometry.Point
        length: float
        width: float
        height: float
        """
        #instance variables
        self.position = position
        self.length = Brick.LENGTH
        self.width = Brick.WIDTH
        self.height = Brick.HEIGHT
        self.frame = Frame(position, Vector.Xaxis(), Vector.Yaxis())
        if direction:
            yaxis = Vector.Zaxis().cross(direction)
            self.frame = Frame(position, direction, yaxis)
        self.layer_no = None
        self.brick_no = None
        self.neighbors = None

    

    def geometry(self):
        return Box(self.length, self.width, self.height, self.frame)

    def rotate_brick(self, angle):
        T = cg.Rotation.from_axis_and_angle(self.frame.zaxis, math.radians(angle), self.frame.point)
        self.frame.transform(T)

    def get_pick_frame(self):
        T = cg.Translation.from_vector(Vector(0,0,self.height/2))
        pick_frame = self.frame.transformed(T)
        return pick_frame


#function to create wall
def create_wall(origin, num_layers, num_bricks_per_layer, gap):
    """
    creates wall out of brick class instances
    num_layers: int
    num_bricks_per_layer: int
    Returns:
    a list of bricks of type Brick class
    """
    all_bricks = []
    for layer_no in range(num_layers): #in height layers
        for brick_no in range(num_bricks_per_layer): #horizontally number of bricks
            if(layer_no%2 == 0):
                my_other_brick = Brick(position=origin + Point(brick_no*Brick.LENGTH + brick_no*gap,0,layer_no*Brick.HEIGHT))
                my_other_brick.rotate_brick(layer_no)
                all_bricks.append(my_other_brick)
            else:
                #get rid of last brick in row
                if brick_no!=num_bricks_per_layer-1:
                    my_other_brick = Brick(position=origin + Point(brick_no*Brick.LENGTH + brick_no*gap + Brick.LENGTH/2,0,layer_no*Brick.HEIGHT))
                    all_bricks.append(my_other_brick)
    return all_bricks

def create_curved_wall(curve, num_layers, gap):
    curve_length = curve.length()
    spacing = Brick.LENGTH + gap
    brick_count = curve_length // spacing

    my_bricks = []
    for layer_no in range(num_layers):
        parameters = curve.divide_by_count(brick_count*2)
        for i, t in enumerate(parameters):
            point_on_curve = curve.point_at(t)
            tangent = curve.tangent_at(t)
            if i % 2 == 0 and layer_no % 2 == 0:
                my_brick = Brick(Point(point_on_curve.x,point_on_curve.y,layer_no*Brick.HEIGHT), tangent)
                my_brick.layer_no = layer_no
                my_brick.brick_no = i
                my_bricks.append(my_brick)
            elif i % 2 == 1 and layer_no % 2 == 1:
                my_brick = Brick(Point(point_on_curve.x,point_on_curve.y,layer_no*Brick.HEIGHT), tangent)
                my_brick.layer_no = layer_no
                my_brick.brick_no = i
                my_bricks.append(my_brick)

    return my_bricks


def find_neighbors(target_index, all_bricks):

    neighbors = { "before":[], "after": [], "above_before":[],"above_after":[],"below_before":[],"below_after":[]} 

    target_brick = all_bricks[target_index]

    for i, brick in enumerate(all_bricks):
        if brick.layer_no == target_brick.layer_no:
            if i == target_index-1:
                neighbors["before"].append(brick)
            elif i == target_index+1:
                neighbors["after"].append(brick)
        
        elif brick.layer_no == target_brick.layer_no -1:
            if brick.brick_no == target_brick.brick_no -1:
                neighbors["below_before"].append(brick)
            elif brick.brick_no == target_brick.brick_no + 1:
                neighbors["below_after"].append(brick)
        
        elif brick.layer_no == target_brick.layer_no +1:
            if brick.brick_no == target_brick.brick_no -1:
                neighbors["above_before"].append(brick)
            elif brick.brick_no == target_brick.brick_no + 1:
                neighbors["above_after"].append(brick)

    target_brick.neighbors = neighbors
    return neighbors


def visualize(viewer, bricks):
    for brick in bricks:
        viewer.scene.add(brick.geometry())
    viewer.show()

def create_sequence(bricks):
    #method to get pick frame of each brick and save it in list
    pick_planes = []
    for brick in bricks:
        pick_planes.append(brick.get_pick_frame())
    return pick_planes


if __name__ == "__main__":

    from compas_viewer import Viewer

    viewer = Viewer()

    #global variables for walll design
    gap = 1.5
    n_layers = 5
    nper_layer = 10

    my_bricks = create_wall(Point(0,0,0),10,10, 1.5)
    visualize(viewer, my_bricks)
