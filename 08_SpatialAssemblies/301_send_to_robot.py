from compas.datastructures import Assembly, Mesh
from compas.geometry import Frame, Point, Translation, Transformation
from compas_fab.backends import RosClient
from compas_fab.robots import Tool, PlanningScene, CollisionMesh
import os, sys
from compas import json_load, json_dump
import time

# Constants
APPROACH_DISTANCE = 0.01 #Meters
start_configuration = None

# Specify the path to the assembly file and the path to the output file
path = os.path.dirname(__file__)
dire = os.path.join(path, "scripts")
sys.path.append(dire)

import rtde_wrapper as rtde

# Load the assembly from the json file
json_path = os.path.join(path, "data", "stick_assembly_with_trajectories.json")
assembly = json_load(json_path)

for i in range(assembly.attributes["num_parts"]):
    IP_ADDRESS = "192.168.10.10"
    part = assembly.find_by_key(i)
    pick_config = part.attributes["pick_config"]
    approach_pick_config = part.attributes["approach_pick_config"]
    pick_trajectory = part.attributes["pick_trajectory"]
    move_trajectory = part.attributes["move_trajectory"]
    exit_trajectory = part.attributes["exit_trajectory"]

    # make sure gripper is open
    rtde.set_digital_io(0, False, ip = IP_ADDRESS)

    # pick up stickg
    rtde.move_trajectory(pick_trajectory, 0.5, 0.5, 0.01, ip = IP_ADDRESS)

    # close gripper
    rtde.set_digital_io(0, True, ip = IP_ADDRESS)
    time.sleep(1)

    # move stick to approach pick config
    rtde.move_to_joints(approach_pick_config, 0.5, 0.5, nowait=False, ip = IP_ADDRESS)

    # move to move trajectory
    rtde.move_trajectory(move_trajectory, 0.5, 0.5, 0.01, ip = IP_ADDRESS)
    # wait here until user presses enter
    input("Press Enter to continue...")
    time.sleep(1)
    # open gripper
    rtde.set_digital_io(0, False, ip = IP_ADDRESS)
    time.sleep(1)

    # move to exit trajectory
    rtde.move_trajectory(exit_trajectory, 0.5, 0.5, 0.01, ip = IP_ADDRESS)

