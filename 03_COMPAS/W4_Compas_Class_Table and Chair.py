# Create a class for a Table_ASSIGNMENT
from compas.geometry import Box, Frame, Polygon
from compas.geometry import Translation
from compas.geometry import Rotation
from compas.geometry import mirror_point_plane
from compas.geometry import distance_point_point
from compas_viewer import Viewer
import math 
import copy 

# CALL COMPAS VIEWER_______________________________________
compas_viewer = Viewer()

# GENERATE CLASSES_________________________________________
class Table:
    def __init__(self, width, length, height, thickness, leg_size, color, leg_color):
        self.length = length
        self.width = width
        self.height = height
        self.thickness = thickness 
        self.leg_size = leg_size
        self.color = color
        self.leg_color = leg_color

    def get_top(self):
        top = Box(self.width, self.length, self.thickness)
        return top

    def get_offset_box (self):
        # Find the distance between the center and the vertix (hypotenuse of a square)
        dist = distance_point_point ([0,0,0], [self.leg_size, self.leg_size, 0])
        offset_box = Box(self.width-dist, self.length-dist, self.thickness)
        return offset_box
 
    def get_lower_box (self):
        dist = distance_point_point ([0,0,0], [self.leg_size, self.leg_size, 0])
        thickness = self.thickness*5
        lower_box = Box(self.width-dist, self.length-dist, thickness)
        z = -thickness/2.5-self.thickness
        T = self.move_box(0,0,z)  # IDK why but if I make the function including the item and call here the item "leg", doesn't work correectly.
        lower_box.transform (T)
        return lower_box
    
    def move_box (self, x, y, z):
        T = Translation.from_vector ([x,y,z])
        return T

    def rotate_legs (self, angle, point):
        axis = (0,0,1)
        alpha = math.radians (angle)
        T = Rotation.from_axis_and_angle (axis, alpha, point)
        return T

    def get_legs(self):
        
        # 01 - Get the bottom part of the offset_box
        boundary = self.get_offset_box ()
        bottom = boundary.bottom
        
        # 02 - Get the points only from the bottom part of the boundary
        points = []
        for i in bottom:
            vertices = boundary.points[i]   # Gets the points from the bottom, regardless of the geometry/nbr of points in the bottom.
            points.append(vertices)

        # 03 - Create legs in each of the points
        legs = []

        for pt in points:
            # Create the legs in these points
            leg = Box(self.leg_size, self.leg_size, self.height)
            leg.frame.point = pt
            # Move the legs half its height
            z = -self.height/2
            T = self.move_box(0,0,z)  # IDK why but if I make the function including the item and call here the item "leg", doesn't work correectly.
            leg.transform (T)
            # Rotate each leg arount its pt
            T2 = self.rotate_legs(45, pt)
            leg.transform (T2)
            # Append the legs to its list
            legs.append (leg)
                
        return legs          

    def show_table(self):
        # Initialize the viewer
        compas_viewer = Viewer()

        # Get table components
        geom_top = self.get_top()
        geom_lower_box = self.get_lower_box()
        geom_legs = self.get_legs()

        # Add components to the viewer scene, and colors for the preview
        compas_viewer.scene.add(geom_top, color=self.color)
        compas_viewer.scene.add(geom_lower_box, color=self.color)
        compas_viewer.scene.add(geom_legs, color=self.leg_color)

class Chair:
    def __init__(self, width, length, height, thickness, leg_size, color):
        self.length = length
        self.width = width
        self.height = height
        self.thickness = thickness 
        self.leg_size = leg_size
        self.color = color

    def get_top(self):
        top = Box(self.width, self.length, self.thickness)
        # Move half the length in the y axis and half the height in the Z Axis.
        y = self.length
        z = - (76-self.length)
        T = self.move_box(0,y,z)
        top.transform (T)
        return top
    
    def get_back(self):
        dist = distance_point_point ([0,0,0], [self.leg_size, self.leg_size, 0])
        thickness = self.thickness*2
        height = self.length/2
        width = self.width - dist 
        back = Box(width, height, thickness)
        # Rotate along the XAxis
        pt = back.frame.point
        T2 = self.rotate_legs([1,0,0], 90, pt)
        back.transform (T2)
        # Move half the length in the y axis and half the height in the Z Axis.
        y = self.length*1.5 - dist + thickness
        z = 0
        T = self.move_box(0,y,z)
        back.transform (T)

        return back

    def get_offset_box (self):
        # Find the distance between the center and the vertix (hypotenuse of a square)
        dist = distance_point_point ([0,0,0], [self.leg_size, self.leg_size, 0])
        offset_box = Box(self.width-dist, self.length-dist, self.thickness)
        return offset_box

    def get_lower_box (self):
        dist = distance_point_point ([0,0,0], [self.leg_size, self.leg_size, 0])
        thickness = self.thickness*5
        lower_box = Box(self.width-dist, self.length-dist, thickness)
        y = self.length
        z = - ((76-self.length) + self.thickness*2.5)
        T = self.move_box(0,y,z)  
        lower_box.transform (T)
        return lower_box
    
    def move_box (self, x, y, z):
        T = Translation.from_vector ([x,y,z])
        return T
    
    def rotate_legs (self, axis, angle, point):
        
        alpha = math.radians (angle)
        T = Rotation.from_axis_and_angle (axis, alpha, point)
        return T
    
    def get_legs(self):
        
        # 01 - Get the bottom part of the offset_box
        boundary = self.get_offset_box ()
        bottom = boundary.bottom
        
        # 02 - Get the points only from the bottom part of the boundary
        points = []
        for i in bottom:
            vertices = boundary.points[i]   # Gets the points from the bottom, regardless of the geometry/nbr of points in the bottom.
            points.append(vertices)

        # 03 - Create legs in each of the points
        legs = []

        for i, pt in enumerate (points):
            # Create the legs in these points
            if i == 1:
                height = self.height*2 
                leg = Box(self.leg_size, self.leg_size, height)
                leg.frame.point = pt
                # Rotate each leg arount its pt
                T2 = self.rotate_legs([0,0,1], 45, pt)
                leg.transform (T2)
                # Move the legs half its height
                x = 0
                y = self.length
                z = - (76-self.length)
                T = self.move_box(x,y,z)  
                leg.transform (T)
            elif i == 2:
                height = self.height*2 
                leg = Box(self.leg_size, self.leg_size, height)
                leg.frame.point = pt
                # Rotate each leg arount its pt
                T2 = self.rotate_legs([0,0,1], 45, pt)
                leg.transform (T2)
                # Move the legs half its height
                x = 0
                y = self.length
                z = - (76-self.length)
                T = self.move_box(x,y,z)  
                leg.transform (T)
            else:
                leg = Box(self.leg_size, self.leg_size, self.height)
                leg.frame.point = pt
                # Rotate each leg arount its pt
                T2 = self.rotate_legs([0,0,1], 45, pt)
                leg.transform (T2)
                # Move the legs half its height
                x = 0
                y = self.length
                z = - ((self.height/2) + (76-self.length))
                T = self.move_box(x,y,z)  
                leg.transform (T)
           
            # Append the legs to its list
            legs.append (leg)
                
        return legs

    def rotate_chair(self, angle, point):

        # Convert the angle to radians
        alpha = math.radians(angle)
        
        # Create the rotation matrix
        T = Rotation.from_axis_and_angle([0,0,1], alpha, point)
        
        # Apply this rotation to all chair components
        top = self.get_top ()
        back = self.get_back ()
        lower_box = self.get_lower_box ()
        legs = self.get_legs ()

        top.transform(T)
        back.transform(T)
        lower_box.transform(T)
        #for leg in legs:
            #leg.transform(T)

    def show_chair(self):
        # Initialize the viewer
        compas_viewer = Viewer()

        # Get table components
        geom_top = self.get_top()
        geom_lower_box = self.get_lower_box()
        geom_legs = self.get_legs()
        geom_back = self.get_back()

        # Add components to the viewer scene, and colors for the preview
        compas_viewer.scene.add(geom_top, color=self.color)
        compas_viewer.scene.add(geom_lower_box, color=self.color)
        compas_viewer.scene.add(geom_legs, color=self.color)
        compas_viewer.scene.add(geom_back, color=self.color)


# TABLES___________________________________________________
#table_1 = Table(120, 75, 20, 1, 10, [161,136,127], [215,204,200])
table_2 = Table(160, 80, 70, 1, 5, [161,136,127], [215,204,200])

# CHAIRS___________________________________________________
chair_1 = Chair(45, 45, 43, 1, 3, [161,136,127])

# ADDITIONAL OPERATIONS ___________________________________
chair_2 = copy.deepcopy (chair_1)
chair_2.rotate_chair (90, [0,0,0])


# CALLINGS_________________________________________________
#table_1.show_table()
table_2.show_table()
chair_1.show_chair()
chair_2.show_chair() # It doesn't show, IDK why

# SHOW THE VIEWER__________________________________________
compas_viewer.show()