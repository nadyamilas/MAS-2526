from compas.geometry import Point, Box, Frame, Vector, KDTree
import compas.geometry as cg
import math
import random

class Brick:
    #class variables
    LENGTH = 32
    WIDTH = 15
    HEIGHT = 10

    def __init__(self, position, direction=None):
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
            yaxis = direction.cross(Vector.Zaxis())
            self.frame = Frame(position, direction, yaxis)
        
        self.layer_no = None
        self.layer_index = None
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
    """
    Creates a curved wall along a given curve using Brick class instances.
    curve: compas.geometry.Curve
    num_layers: int, number of vertical layers
    num_bricks_per_layer: int, number of bricks per layer horizontally
    gap: float, space between bricks
    """
    all_bricks = []
    curve_length = curve.length()
    brick_spacing = Brick.LENGTH + gap
    num_bricks_per_layer = int(curve_length//brick_spacing)

    for layer_no in range(num_layers):  # in height layers
        parameters = curve.divide_by_count(num_bricks_per_layer*2)
        for i, t in enumerate(parameters):
            point_on_curve = curve.point_at(t)
            tangent = curve.tangent_at(t)

            if layer_no % 2 == 0 and i % 2 == 0:
                # Regular brick placement
                brick_position = Point(point_on_curve.x, point_on_curve.y, layer_no * Brick.HEIGHT)
                brick = Brick(position=brick_position, direction=tangent)
                brick.layer_no = layer_no
                brick.layer_index = i
                all_bricks.append(brick)
            elif layer_no % 2 == 1 and i % 2 == 1:
                brick_position = Point(point_on_curve.x, point_on_curve.y, layer_no * Brick.HEIGHT)
                brick = Brick(position=brick_position, direction=tangent)
                brick.layer_no = layer_no
                brick.layer_index = i
                all_bricks.append(brick)
        
    return all_bricks

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

def find_dependency_chain(brick, all_bricks):
    dependencies = set()  
    
    def find_supporting_bricks(brick):
        supporting_bricks = []
        for other_brick in all_bricks:
            if other_brick.position.z == brick.position.z - Brick.HEIGHT:  # line bellow brick
                x_overlap = False
                y_overlap = False

                if (
                    other_brick.position.x <= brick.position.x <= other_brick.position.x + Brick.LENGTH
                    or other_brick.position.x <= brick.position.x + Brick.LENGTH <= other_brick.position.x + Brick.LENGTH
                ):
                    x_overlap = True

                if (
                    other_brick.position.y <= brick.position.y <= other_brick.position.y + Brick.LENGTH
                    or other_brick.position.y <= brick.position.y + Brick.LENGTH <= other_brick.position.y + Brick.LENGTH
                ):
                    y_overlap = True

                if x_overlap and y_overlap:
                    supporting_bricks.append(other_brick)
        return supporting_bricks
    
    # Recursive function to collect dependencies
    def collect_dependencies(brick):
        supporting_bricks = find_supporting_bricks(brick)
        for support in supporting_bricks:
            if support not in dependencies:
                dependencies.add(support)
                collect_dependencies(support)
    
    # Start the recursion
    collect_dependencies(brick)

    neighbors = list(dependencies)
    brick.neighbors = neighbors
    
    return neighbors

def find_neighbors_kdtree(target_brick, all_bricks, num_neighbors=4):
    #method to find neighbors of a brick using KDTree from compas.geometry

    #build KDTree
    points = KDTree([brick.position for brick in all_bricks])
    #use KDTree existing method to find nearest neighbors
    neighbors = points.nearest_neighbors(target_brick.position, num_neighbors, False)
    print(neighbors)
    # Notice that the return value is a list[[[float, float, float], int or str, float]] of the nearest neighbors
    neighbors = [all_bricks[i[1]] for i in neighbors]
    # that's why we need to extract the index [1] to get the list of indexes of the nearest neighbors
    target_brick.neighbors = neighbors

    return neighbors

def find_neighbors(target_index, all_bricks):
    #find neighbors using brick.layer_no and index
    neighbors = {"before":[], "after":[], "above_before":[], "above_after":[], "below_before":[], "below_after":[]}
    target_brick = all_bricks[target_index]  

    for i, brick in enumerate(all_bricks):
        if brick.layer_no == target_brick.layer_no:  
            if i == target_index-1:
                neighbors["before"].append(brick)
            elif i == target_index+1:
                neighbors["after"].append(brick)

        elif brick.layer_no == target_brick.layer_no-1:  
            if brick.layer_index == target_brick.layer_index-1:
                neighbors["below_before"].append(brick)
            elif brick.layer_index == target_brick.layer_index+1:
                neighbors["below_after"].append(brick)

        elif brick.layer_no == target_brick.layer_no+1:
            if brick.layer_index == target_brick.layer_index-1:
                neighbors["above_before"].append(brick)
            elif brick.layer_index == target_brick.layer_index+1:
                neighbors["above_after"].append(brick)

    target_brick.neighbors = neighbors  
    return neighbors
        

def find_neighbors_by_vec(target_brick, all_bricks):
    """
    Find neighbors
    target_brick: brick class instance
    all_bricks: list of brick class instances
    """	
    neighbors = {
        "before":[],
        "after":[],
        "above_before":[],
        "above_after":[],
        "below_before":[],
        "below_after":[],
    }
    for brick in all_bricks:
        if brick is target_brick:
            continue

        to_brick = Vector.from_start_end(target_brick.position, brick.position)
        to_brick.unitize()
        dz = brick.position.z - target_brick.position.z

        # Dot product with the X-axis of the target brick's frame
        dot_x = to_brick.dot(target_brick.frame.xaxis)

        # Same layer neighbors
        if dz == 0:
            if dot_x < 0:  
                neighbors["after"].append(brick)
            elif dot_x > 0:  
                neighbors["before"].append(brick)

        # Above neighbors
        elif dz == Brick.HEIGHT:
            if dot_x < 0:
                neighbors["above_after"].append(brick)
            elif dot_x > 0:
                neighbors["above_before"].append(brick)

        # Below neighbors
        elif dz == -Brick.HEIGHT:
            if dot_x < 0:
                neighbors["below_after"].append(brick)
            elif dot_x > 0:
                neighbors["below_before"].append(brick)

    target_brick.neighbors = neighbors
    return neighbors

if __name__ == "__main__":

    from compas_viewer import Viewer
    from compas.colors import Color

    viewer = Viewer()

    #global variables for walll design
    gap = 1.5
    n_layers = 5
    nper_layer = 10

    wall_bricks = create_wall(Point(0,0,0),10,10, 1.5)
    target_brick = wall_bricks[-1]  # Topmost brick
    
    

    # Find dependency chain
    dependency_chain = find_dependency_chain(target_brick, wall_bricks)
  
    
    viewer.scene.add(target_brick.geometry(), color=Color(1, 0, 0))  # Target in red
    for brick in dependency_chain:
        viewer.scene.add(brick.geometry(), color=Color(0, 1, 0))  # Dependencies in green
    viewer.show()
