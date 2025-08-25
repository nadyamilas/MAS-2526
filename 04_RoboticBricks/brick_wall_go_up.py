# -*- coding: utf-8 -*-
from compas.geometry import Box, Frame, Point, Vector,Translation, Rotation
import math

class Brick:
    #class variables, they do not change by the user every time the class is called
    LENGTH = 32
    WIDTH = 15.2
    HEIGHT = 9.87

    def __init__(self, center):
        self.center = center
        self.frame = Frame(point = center, xaxis = Vector.Xaxis(), yaxis = Vector.Yaxis())
        self.length = Brick.LENGTH
        self.width = Brick.WIDTH
        self.height = Brick.HEIGHT
        self.x_index = None
        self.z_index = None
    
    def rotate_brick(self, origin, angle, tilt_axis="y"):
        # Choose the axis of rotation: 'x' for domino tilting
        axis = self.frame.yaxis if tilt_axis == "y" else Vector.Zaxis()
        transformation = Rotation.from_axis_and_angle(axis=axis,
                                                      angle=math.radians(angle),
                                                      point=(Point(origin.x + self.length / 2, origin.y, origin.z - self.height / 2)))
        self.frame.transform(transformation)
    
    def align_to_baseline(self, angle):
        # Calculate the vertical displacement required to keep the brick's bottom edge at the same baseline level
        a1 = (Brick.LENGTH/2) * math.sin(math.radians(angle))
        a2 = math.sin(math.radians(90 - angle)) / Brick.HEIGHT / 2
        vertical_shift = a1 + a2
        
        # Apply the vertical shift to align with the baseline
        alignment_translation = Translation.from_vector(Vector(0, 0, vertical_shift)) 
        self.frame.transform(alignment_translation)
    
    def x_displacement(self, displacement):

        alignment_translation = Translation.from_vector(Vector(displacement, 0, 0))
        self.frame.transform(alignment_translation)

    def geometry(self):
        box = Box(xsize = self.length, ysize = self.width, zsize = self.height, frame = self.frame)
        return box
    
    def generate_pick_frame(self):
        pick_frame = self.frame.copy()
        pick_frame.transform(Translation.from_vector(Vector(0, 0, self.height/2)))
        #alternative for transform with transformed which doesn't require to copy the object
        #pick_frame = self.frame.transformed(ranslation.from_vector(Vector(0,0,self.height/2)))
        return pick_frame
    
def create_support_wall(origin, brick_layers, offset_per_row):
    wall_bricks = []
    bricks_per_layer = brick_layers - int(brick_layers / 2) - 1
    base_spacing = Brick.LENGTH + 0.5  # Add a small gap between bricks in the base wall
    start_x = 0
    for layer in range(brick_layers):
        for i in range(bricks_per_layer):
            x_offset = i * base_spacing + start_x
            z_offset = layer * Brick.HEIGHT
            center = Point(origin.x - x_offset, origin.y, origin.z + z_offset)
            wall_brick = Brick(center=center)
            wall_bricks.append(wall_brick)
        if layer % 2 == 1:
            bricks_per_layer -= 1 
        start_x += offset_per_row  

    theta = math.atan(Brick.HEIGHT / offset_per_row)
    theta_degrees = math.degrees(theta)
    
    return wall_bricks, theta_degrees

def create_inclined_wall(origin, brick, brick_layers, inclination, angle_step, max_tilt_angle, gap, scale_x = 5.0):
    
    rotated_bricks = []
    
    # Create the first brick 
    my_brick = brick
    # rotated_bricks.append(my_brick)

    offset_z = math.sin(math.radians(inclination)) * (Brick.LENGTH + gap) + math.cos(math.radians(angle_step)) * Brick.HEIGHT
    offset_x = math.cos(math.radians(inclination)) * (Brick.LENGTH + gap) - math.sin(math.radians(angle_step)) * Brick.HEIGHT
    
    # + math.sin(math.radians(angle_step)) * Brick.HEIGHT/2
    gap_z = gap
    gap_x = gap * scale_x
    angle_step *= 2.0

    for i in range(1, brick_layers):
        inclination += angle_step
        if inclination > max_tilt_angle:
            inclination = max_tilt_angle
            offset_z = math.sin(math.radians(inclination)) * (Brick.LENGTH + gap) 
            offset_x = math.cos(math.radians(inclination)) * (Brick.LENGTH + gap) 
        else:
            offset_z = math.sin(math.radians(inclination)) * (Brick.LENGTH + gap) + gap_z
            offset_x = math.cos(math.radians(inclination)) * (Brick.LENGTH + gap) + gap_x

        # Create a new brick at the ORIGINAL POSITION
        new_brick = Brick(center = origin)
        new_brick.rotate_brick(origin = origin, angle = inclination, tilt_axis="y")

        from_center = my_brick.frame.point 
        to_center = Point(from_center.x - offset_x, from_center.y, from_center.z + offset_z)
        new_brick.frame.point = to_center
               
        # Add the new brick to the list and update my_brick to the new brick
        rotated_bricks.append(new_brick)
        my_brick = new_brick  # Update reference for the next iteration

    return rotated_bricks

def create_domino_row(origin, number_of_bricks, max_tilt_angle, offset_per_row, angle_step, gap):
    # Calculate incremental angle change for a domino effect
    # angle_step = max_tilt_angle / (number_of_bricks - 2) if number_of_bricks > 2 else 0
    spacing = 0
    is_horizontal = False
    domino_bricks = []
    spacings = []
    horizontal_row = []
    for i in range(number_of_bricks):
            # Place tilted bricks with incremental angles for the falling effect
            center = origin
            my_brick = Brick(center=center)
            
            # Apply the tilt angle to each successive brick
            tilt_angle = max_tilt_angle - (i * angle_step)
            if tilt_angle < 25:
                last_domino_brick = find_last_brick
                last_domino_brick_angle = tilt_angle + angle_step
                if is_horizontal == False:
                    is_horizontal = True
                    spacing += 5
                spacing += Brick.LENGTH + gap
                center = Point(origin.x + spacing, origin.y, origin.z)
                my_brick = Brick(center=center)
                horizontal_row.append(my_brick)
            else:
                my_brick.rotate_brick(origin, tilt_angle, tilt_axis = "y")
                
                #displacement in x direction to match the previous one
                if i == 0:
                    spacing += offset_per_row
                else:
                    previous_angle = tilt_angle + angle_step
                    a = Brick.HEIGHT / math.sin(math.radians(previous_angle))
                    b = (Brick.LENGTH * math.sin(math.radians(angle_step))) / math.sin(math.radians(180 - tilt_angle))
                    spacing += a + b
                my_brick.x_displacement(spacing)
                domino_bricks.append(my_brick)
                spacings.append(spacing)
                find_last_brick = my_brick
    return domino_bricks, spacings, last_domino_brick, last_domino_brick_angle, horizontal_row

#rhino doesn't recognise the compas_viewer...so we do that
if __name__ == "__main__":
    from compas_viewer import Viewer
    def visualize_bricks(my_bricks):
        viewer = Viewer()
        for brick in my_bricks:
            viewer.scene.add(brick.geometry())
        viewer.show()

offset_per_row = Brick.LENGTH / 3
angle_step = 5
gap = 0.5
brick_layers = 4

#SUPPORT
my_wall, max_inclination = create_support_wall(origin = Point(0,0,0), brick_layers = 9, offset_per_row = 10)
print(max_inclination)

#DOMINO WALL
domino_wall, spacings, last_domino_brick, last_domino_brick_angle, horizontal_row = create_domino_row(origin = Point(0,0,0), number_of_bricks = 11, max_tilt_angle = max_inclination, offset_per_row = 10, angle_step = angle_step, gap = gap)
my_wall.extend(domino_wall)
my_wall.extend(horizontal_row)

#COPY EACH BRICK FROM THE DOMINO WALL
new_inclination = max_inclination
for index, brick in enumerate(domino_wall):
    inclined_wall = create_inclined_wall(origin = Point(0,0,0), brick = brick, brick_layers = brick_layers, inclination = new_inclination, angle_step = angle_step, max_tilt_angle = max_inclination, gap = gap)
    my_wall.extend(inclined_wall)
    new_inclination -= angle_step
    
#COPY THE WALL FROM INCINED TO HORIZONTAL

angle_steps = (max_inclination - 25) / angle_step
last_domino_brick_angle = max_inclination - angle_steps*angle_step
#SET THE MOVE
move_z = Brick.HEIGHT
move_x = math.cos(math.radians(last_domino_brick_angle)) * Brick.HEIGHT
num_rows = 4


for i in range(num_rows):
    
    from_point = last_domino_brick.frame.point
    new_brick = Brick(from_point)
    new_brick.rotate_brick(origin=from_point, angle = last_domino_brick_angle, tilt_axis="y")
    
    
    to_point = Point(from_point.x + move_x, from_point.y, from_point.z + move_z)
    new_brick.frame.point = to_point
    my_wall.append(new_brick)
    last_domino_brick = new_brick

    iterate_bricks = []
    minus = -1
    list_length = len(horizontal_row)
    for index, brick in enumerate(horizontal_row):
        from_point = brick.frame.point
        to_point = Point(from_point.x + move_x, from_point.y, from_point.z + move_z)
        my_brick = Brick(to_point)
        if index != list_length-1:
            iterate_bricks.append(my_brick)
            my_wall.append(my_brick)
    horizontal_row = iterate_bricks

    new_inclination = last_domino_brick_angle + 5
    inclined_wall = create_inclined_wall(origin = Point(0,0,0), brick = last_domino_brick, brick_layers = brick_layers, inclination = new_inclination, angle_step = 5, max_tilt_angle = max_inclination, gap = gap, scale_x = 10.0)
    my_wall.extend(inclined_wall)
    if i % 2 == 1 :
        brick_layers -= 1

# visualize_bricks(my_wall)