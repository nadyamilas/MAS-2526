import compas_rrc as rrc
import os
import sys
from compas.geometry import Frame, Point, Vector, Box, Polyline, Rotation, bounding_box
from compas import json_load
from compas_viewer import Viewer
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
dire = os.path.join(parentdir, 'rrc_custom_instructions')
sys.path.append(parentdir)
print("Appended to sys path", parentdir)
from brick_class import Brick


# ==============================================================================
# Load data from json file
# ==============================================================================

DATA_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
PRINT_FILE_NAME = 'pickplace_bricks.json'

dict_data = json_load(os.path.join(DATA_OUTPUT_FOLDER, PRINT_FILE_NAME))
print('Print data loaded :', os.path.join(DATA_OUTPUT_FOLDER, PRINT_FILE_NAME))

# ==============================================================================
# Get fabrication data from json file and create abb_print_frames
# ==============================================================================

abb_frames = []
if dict_data:
    print (len(dict_data), "frames loaded")
    for i in range(len(dict_data)):
        
        frame_data = dict_data[i]
        #print(frame_data)
        abb_frame = frame_data
        abb_frames.append(abb_frame)

print("ABB printframes created:", len(abb_frames))

# ==============================================================================
# Move brickwall to workspace (offset & optional flip of axes)
# ==============================================================================

x_offset = 100
y_offset = 100
z_offset = 25  
offset_vec = Vector(x_offset, y_offset, z_offset)

points = [frame.point for frame in abb_frames]
min_point = Vector(*bounding_box(points)[0])

translation_vec = -min_point + offset_vec

moved_frames = []
for frame in abb_frames:
    moved = frame.translated(translation_vec)

    moved.yaxis *= -1
    moved_frames.append(moved)

# ==============================================================================
# Parameters & helpers
# ==============================================================================

SAFE_DZ = 60.0   # height above pick/place (along that frame's +Z) for safe approach
SPEED_APPROACH = 300  # mm/s for travel between safe frames
SPEED_TOUCH = 100     # mm/s for final pick/place
ZONE_TRAVEL = rrc.Zone.Z10
ZONE_TOUCH = rrc.Zone.FINE

# Constant pick frame (on pallet)
PICK_FRAME = Frame(Point(68.5, 48.5, 36), Vector(0, -1, 0), Vector(-1, 0, 0))

def safe_above(frame: Frame, dz: float) -> Frame:
    """Return a frame dz above the given frame along its local +Z, same orientation."""
    p = frame.point + frame.zaxis * dz
    return Frame(p, frame.xaxis, frame.yaxis)

# ==============================================================================
# (Optional) quick viz helpers (no effect on robot)
# ==============================================================================
VIZ_ON = False  # Set to True to visualize the brick wall in a viewer
ROBOT_ON = False  # Set to False to skip robot code execution

if VIZ_ON and not ROBOT_ON:
    viewer = Viewer()

    pframe = Frame(Point(0, 0, 0), Vector(1, 0, 0), Vector(0, 1, 0))
    print_bed = Box.from_corner_corner_height(Point(0, 0, 0), Point(2800, 1450, 0), 1)
    viewer.scene.add(pframe, settings={'color': (255, 0, 0), 'width': 2})
    viewer.scene.add(print_bed, settings={'color': (0, 255, 0), 'opacity': 0.5})

    wall = []
    for frame in moved_frames:
        brick = Brick(frame.point)
        brick.frame = frame
        wall.append(brick.geometry())
    viewer.scene.add(wall, settings={'color': (0, 0, 255), 'opacity': 0.5})
    viewer.show()

# ==============================================================================
# Robot program
# ==============================================================================
# End if robot is not on
if not ROBOT_ON:
    # End
    print("ROBOT OFF: Finish code without moving robot")
    exit()
else:
    print("ROBOT ON: Start code")
    if __name__ == '__main__':
        # Create ROS + ABB clients
        ros = rrc.RosClient()
        ros.run()
        abb = rrc.AbbClient(ros, '/rob1')
        print('Connected.')

        # IO reset
        abb.send(rrc.SetDigital('doNewBrick', 0))
        abb.send(rrc.SetDigital('doVacuumOn', 0))

        # Tool
        abb.send(rrc.SetTool('t_RRC_Vacuum_Gripper'))

        # Precompute safe frames
        safe_pick = safe_above(PICK_FRAME, SAFE_DZ)

        # Loop over every target place frame
        for idx, place_frame in enumerate(moved_frames):
            print("=== Brick {} of {} ===".format(idx + 1, len(moved_frames)))
            safe_place = safe_above(place_frame, SAFE_DZ)

            # --- PICK SEQUENCE (pallet workobject)
            abb.send(rrc.SetWorkObject('ob_RRC_Brick_Pallet'))

            # Ask feeder for a new brick (pulse each cycle if needed)
            abb.send_and_wait(rrc.PulseDigital('doNewBrick', 0.2))

            # Move above pick
            abb.send(rrc.MoveToFrame(safe_pick, SPEED_APPROACH, ZONE_TRAVEL))
            # Down to pick
            abb.send(rrc.MoveToFrame(PICK_FRAME, SPEED_TOUCH, ZONE_TOUCH))
            # Vacuum ON
            abb.send(rrc.SetDigital('doVacuumOn', 1))
            abb.send(rrc.WaitTime(0.15))
            # Back up to safe pick
            abb.send(rrc.MoveToFrame(safe_pick, SPEED_APPROACH, ZONE_TRAVEL))

            # --- PLACE SEQUENCE (build space workobject)
            #abb.send(rrc.SetWorkObject('ob_RRC_Build_Space'))

            # Move above place
            abb.send(rrc.MoveToFrame(safe_place, SPEED_APPROACH, ZONE_TRAVEL))
            # Down to place
            abb.send(rrc.MoveToFrame(place_frame, SPEED_TOUCH, ZONE_TOUCH))
            # Vacuum OFF (release)
            abb.send(rrc.SetDigital('doVacuumOn', 0))
            abb.send(rrc.WaitTime(0.15))
            # Back up to safe place
            abb.send(rrc.MoveToFrame(safe_place, SPEED_APPROACH, ZONE_TRAVEL))

            # (Optional) small settle time between bricks
            # abb.send(rrc.WaitTime(0.1))

        print('Finished building wall with {} bricks.'.format(len(moved_frames)))

        # Close client
        ros.close()
        ros.terminate()
