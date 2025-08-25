import os
import sys
import time
import math
import compas_rrc as rrc

from compas.geometry import Polyline, Box, Rotation
from compas_viewer import Viewer

from compas import json_load
from compas.geometry import Frame, Vector, Point, Transformation, Translation, bounding_box

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
dire = os.path.join(parentdir, 'rrc_custom_instructions')
sys.path.append(dire)
print("Appended to sys path", dire)

from compas_rrc_a065_instructions import *

# ==============================================================================
# Set parameters
# ==============================================================================

# Switches
ROBOT_ON = True
PRINT_ON = True
COOLING_ON = False
HC_ON = True
GO_HOME_AFTER_PRINT = False

# Home position
HOME_POSITION = [-90.00, -65.00, 65.00, 190.00, 25.00, -12.00]

# Gantry position
GANTRY_X = 30350.00
GANTRY_Y = -10800.00
GANTRY_Z = -2600.00
GANTRY_Z_MAX = -4900
EXTERNAL_AXES = [GANTRY_X, GANTRY_Y, GANTRY_Z]

# layer at which the z axis of the gantry 
# will start going up together with the print
EXT_AXES_START_LAYER = 1 #15 #42
MOVE_EXT_AXES_Z = True

# Velocities
MAX_SPEED = 100
SPEED_HOME_TO_PRINT = 100

# time to extrude before print start and time to stop before moving to home position
START_TIME = 5
END_TIME = 10

HC_MATERIAL_CONSTANT = 0.045

# Robot configuration
ROBOT_TOOL = 't_A065_T1_ExtNozzle_Measured_T2'
ROBOT_WORK_OBJECT = 'ob_A065_Nik_PrintBed' 
IO_EXTRUDER = 'doA065_E1ExtOn'
IO_COOLING = 'doA065_E1AirOn'

IO_HC_AIR = 'doUnitR22ValveA1'
IO_HC_AIR_PRESSURE = 'aoA065_T1HoCoAir' #values from 4.09 to 4.5 (real range 4.20)
#IO_HC_AP_OVERRIDE = 'aoA065_T1HoCoAir_Override'

# ==============================================================================
# Extruder parameters
# ==============================================================================
extruder_state = 0 # do not modify this 

# ==============================================================================
# Saftey Distance
# ==============================================================================
# distance for 24mm nozzle
x_offset = 100
y_offset = 100
z_offset = 25 #65 calibration #80 skylight

offset_vec = Vector(x_offset, y_offset, z_offset)


# ==============================================================================
# Load data from json file
# ==============================================================================

# Define location of print data
DATA_OUTPUT_FOLDER = os.path.join(os.path.dirname(__file__), 'data')
# PRINT_FILE_NAME = "T_d1G_2.json"
PRINT_FILE_NAME =  'print_file_half_half.json'

# Open print data
dict_data = json_load(os.path.join(DATA_OUTPUT_FOLDER, PRINT_FILE_NAME))

# Print file loaded
print('Print data loaded :', os.path.join(DATA_OUTPUT_FOLDER, PRINT_FILE_NAME))

# ==============================================================================
# Get fabrication data from json file and create abb_print_frames
# ==============================================================================

# print frames
abb_print_frames = []
layer_indexes = []

# fabrication data
velocities = []
extruder_toggles = []
zones = []
hc_set_points=[]
air_pressures = []
gantry_z_values = []
first_point_z_value = dict_data[str(1)]["frame"]


if dict_data:
    for i in range(len(dict_data)):

        data_point = dict_data[str(i)]
        #print (data_point)

        abb_print_frame = data_point["frame"]
        abb_print_frames.append(abb_print_frame)

        # gantry z values
        gzval = GANTRY_Z - (abb_print_frame.point.z - first_point_z_value.point.z)
        gantry_z_values.append(gzval)
            

        if (data_point["blend"]) < 0.3:
            zones.append(rrc.Zone.FINE)
        elif (data_point["blend"]) <= 1:
            zones.append(rrc.Zone.Z1) # CHANGED THIS ONE
        elif (data_point["blend"]) <= 5:
            zones.append(rrc.Zone.Z5)
        elif (data_point["blend"]) <= 10:
            zones.append(rrc.Zone.Z10)
        else:
            zones.append(rrc.Zone.Z10)

        # fabrication related data
        velocities.append(data_point["velocity"])
        air_pressures.append(data_point["air_pressure"])
        hc_set_points.append(data_point["hc_set_point"])
        layer_indexes.append(data_point['layer_idx'])  

        if PRINT_ON: # append extruder toggles if extruder should be on
            extruder_toggles.append(data_point["toggle"])
        else:
            extruder_toggles.append(0)

print("ABB printframes created")

# move geometry to the origin of the platform (0,0,0) and apply the offset
# opctionally check if you also need to rotate your geometry
points = [frame.point for frame in abb_print_frames]
min_point = Vector(*bounding_box(points)[0] )
print ("Min point of the print frames: ", min_point)
translation_vec = -min_point + offset_vec  

moved_abb_print_frames = []
for frame in abb_print_frames:
    moved_frame = frame.translated(translation_vec)
    # moved_frame = moved_frame.transformed(Rotation.from_axis_and_angle(moved_frame.zaxis, math.pi/2, point=moved_frame.point))
    #moved_frame.xaxis *= -1
    moved_frame.yaxis *= -1
    moved_abb_print_frames.append(moved_frame)

# visualise in compas_viewer
polyline = Polyline([frame.point for frame in moved_abb_print_frames])
points = [frame.point for frame in moved_abb_print_frames]
#get the velocity of each point and map the color from blue to red to the velocity value, them each point should have the respective color
def remap(old_val, old_min, old_max, new_min, new_max):
    return (new_max - new_min)*(old_val - old_min) / (old_max - old_min) + new_min
remaped_velocities = [ remap(val, min(velocities), max(velocities), 50, 200) for val in velocities]
#print(remaped_velocities)

# ==============================================================================
pframe = Frame(Point(0,0,0), Vector(1,0,0), Vector(0,1,0))
print_bed = Box.from_corner_corner_height(Point(0,0,0), Point(2800, 1450, 0), 1)

# ==============================================================================

if not PRINT_ON and not ROBOT_ON:
    from compas.geometry import Line
    from compas.colors import Color, ColorMap
    
    color_mp = ColorMap.from_two_colors(Color.blue(), Color.red())
    print (len(color_mp.colors))
    viewer = Viewer()
    viewer.unit = 'mm'
    # viewer.scene.attributes()
    for point, vel in zip(points, remaped_velocities):
        viewer.scene.add(point, color = color_mp.colors[int(vel)], pointsize= 30)  
    #viewer.scene.add(points, settings={'color': (0, 0, 255), 'width': 5})
    viewer.scene.add(polyline, settings={'color': (0, 0, 255), 'width': 2})
    viewer.scene.add(moved_abb_print_frames[0])
    # add line for X axis
    # viewer.scene.add(Line(moved_abb_print_frames[0].point, moved_abb_print_frames[0].point.translated(moved_abb_print_frames[0].xaxis*1000)), settings={'color': (255, 0, 0), 'width': 2})
    viewer.scene.add(pframe, settings={'color': (255, 0, 0), 'width': 2})
    viewer.scene.add(print_bed, settings={'color': (0, 255, 0), 'width': 2})
    viewer.show()

print("ABB printframes moved to origin")
print(moved_abb_print_frames[1])

# ==============================================================================
# start and stop index for print points 
# ==============================================================================
# USE THIS TO CONTINUE WHEN STOPPED INSTEAD OF WRITING NEW CODE
# Check .gh file for the index of first point in layer we want to continue -
# - and change the START_INDEX to that.
START_INDEX = 0
STOP_INDEX = len(moved_abb_print_frames)

# Split lists with start and stop index
abb_print_frames = moved_abb_print_frames[START_INDEX:STOP_INDEX]
velocities = velocities[START_INDEX:STOP_INDEX]
zones = zones[START_INDEX:STOP_INDEX]
extruder_toggles = extruder_toggles[START_INDEX:STOP_INDEX]

hc_set_points = hc_set_points[START_INDEX:STOP_INDEX]
air_pressures = air_pressures[START_INDEX:STOP_INDEX]
layer_indexes = layer_indexes[START_INDEX:STOP_INDEX]
gantry_z_values = gantry_z_values[START_INDEX:STOP_INDEX]

print(f'Number of frames in loaded printpoints: {len(abb_print_frames)}')
print(f'Executing from frame {START_INDEX} to {STOP_INDEX}')

# End if robot is not on
if not ROBOT_ON:
    # End
    print('ROBOT OFF: Finish code without moving robot')
    exit()
else:
    print('ROBOT ON: Start code')

    # ==============================================================================
    # Main robotic control function
    # ==============================================================================

    if __name__ == '__main__':

        # Create Ros Client
        ros = rrc.RosClient()
        ros.run()

        # Create ABB Client
        abb = rrc.AbbClient(ros, '/rob1')
        print('Connected')

        # Set Tool
        abb.send(rrc.SetTool(ROBOT_TOOL))

        # Set Work Object
        abb.send(rrc.SetWorkObject(ROBOT_WORK_OBJECT))

        # Set Acceleration
        acc = 50  # Unit [%] 
        ramp = 50 # Unit [%] was 50
        abb.send(rrc.SetAcceleration(acc, ramp))

        # Set Max Speed
        override = 100  # Unit [%]
        max_tcp = 100  # Unit [mm/s]
        abb.send(rrc.SetMaxSpeed(override, max_tcp))

        # User message -> basic settings send to robot
        print('Tool, Wobj, Acc and MaxSpeed sent to robot')

        # ===========================================================================
        # Robot movement
        # ===========================================================================
        print("Starting print")

        # Send I/Os
        abb.send(rrc.SetDigital(IO_EXTRUDER, 0)) # make sure extruder is off

        abb.send_and_wait(rrc.CustomInstruction('r_A065_Enable_Hollow_Core', [], []))
        abb.send(rrc.SetDigital(IO_HC_AIR, 1)) # make sure extruder is on
        print('HC mode activated')

        abb.send_and_wait(rrc.CustomInstruction('r_A065_Enable_Hollow_Core_Air', [], []))
        abb.send(rrc.SetAnalog(IO_HC_AIR_PRESSURE, 4.09)) # setting extruder 4.09
        print('HC air pressure active')

        #if AP_OVERRIDE:
        #    abb.send(rrc.SetAnalog(IO_HC_AP_OVERRIDE, air_pressure_override)) # turn air on
        #else:
        #    abb.send(rrc.SetAnalog(IO_HC_AP_OVERRIDE, 0))

        if COOLING_ON:
            abb.send(rrc.SetDigital(IO_COOLING, 1)) # turn air on

        if START_INDEX == 0:
            # 1. Move robot to home position
            startmsg = abb.send_and_wait(rrc.PrintText('STARTED: Moving to home position'))
            start = abb.send_and_wait(rrc.MoveToJoints(HOME_POSITION, EXTERNAL_AXES, MAX_SPEED, rrc.Zone.FINE))

        # 2. Print motion
        printmsg = abb.send_and_wait(rrc.PrintText('PRINTING'))


        for i, (frame, v, z, ext_tg, hc_setpt, airp, li, gzv) in enumerate(zip(\
                moved_abb_print_frames, velocities,  zones, extruder_toggles,\
                    hc_set_points, air_pressures, layer_indexes, gantry_z_values)):
            
            # Optional sleep time in loop
            time.sleep(0.1)

            # For simulation
            # v = v*10

            # Get external axes z value
            EXTERNAL_AXES[2] = gzv

            # Check if gantry z is not in the max z range
            if EXTERNAL_AXES[2] < GANTRY_Z_MAX:

                # Max z value reached
                EXTERNAL_AXES[2] = GANTRY_Z_MAX



            if extruder_state == 0 and ext_tg == 1:
                # MOVE TO PRINT START (Start printing > turn extruder on)
                extruder_state = 1
                abb.send(MoveToHcPrintStart(  frame, 
                                            EXTERNAL_AXES, 
                                            SPEED_HOME_TO_PRINT,   
                                            z, 
                                            hc_setpt, 
                                            airp, 
                                            start_setpoint = 0,  # not in use
                                            start_time=START_TIME,
                                            follow_speed=velocities[i+1], 
                                            motion_type=rrc.Motion.LINEAR))
            
            elif extruder_state == 1 and ext_tg == 0:
                # MOVE TO PRINT END (Stop printing > turn extruder off)
                extruder_state = 0
                abb.send(MoveToHcPrintEnd(    frame, 
                                            EXTERNAL_AXES, 
                                            v, 
                                            z, 
                                            hc_setpt,
                                            airp,
                                            end_time=END_TIME,
                                            motion_type=rrc.Motion.LINEAR))
            else:
                # MOVE TO PRINT POINT (Printing motion > do not change extruder status)
                abb.send(MoveToHcPrint(       frame, 
                                            EXTERNAL_AXES, 
                                            v, 
                                            z,
                                            hc_setpt,
                                            airp,
                                            motion_type=rrc.Motion.LINEAR))
            
        # 3. Move robot back to home position

        # Turn air and extruder off
        abb.send(rrc.SetDigital(IO_COOLING, 0))     # turn air off
        abb.send(rrc.SetDigital(IO_EXTRUDER, 0))    # make sure extruder is off

        # abb.send_and_wait(rrc.CustomInstruction('r_A065_Disable_Hollow_Core_Air', [], []))
        abb.send(rrc.SetAnalog(IO_HC_AIR_PRESSURE, 4)) # setting extruder 4.09
        print('HC air pressure reduced')

        abb.send_and_wait(rrc.CustomInstruction('r_A065_Disable_Hollow_Core', [], []))
        print('HC mode deactivated')

        # send back to home position
        if GO_HOME_AFTER_PRINT:
            endmsg = abb.send_and_wait(rrc.PrintText('FINISHED: Moving to home position'))
            end = abb.send_and_wait(rrc.MoveToJoints(HOME_POSITION, EXTERNAL_AXES, MAX_SPEED, rrc.Zone.FINE))
        else:
            endmsg = abb.send_and_wait(rrc.PrintText('FINISHED: Staying at last position'))

        # Print Text
        done = abb.send_and_wait(rrc.PrintText('Executing commands finished.'))
        print('Executing commands finished.')

        # End of Code
        print('Finished')

        # Close client
        ros.close()
        ros.terminate()