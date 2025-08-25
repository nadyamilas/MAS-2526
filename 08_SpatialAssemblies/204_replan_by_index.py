from compas.datastructures import Assembly, Mesh
from compas.geometry import Frame, Point, Translation, Transformation
from compas_fab.backends import RosClient
from compas_fab.robots import Tool, PlanningScene, CollisionMesh
import os, sys
from compas import json_load, json_dump
import math

# Constants
APPROACH_DISTANCE = 0.01 #Meters
start_configuration = None

# Specify the path to the assembly file and the path to the output file
path = os.path.dirname(__file__)
dire = os.path.join(path, "scripts")
sys.path.append(dire)

json_path = os.path.join(path, "data", "stick_assembly_with_trajectories.json")

# Import the scale_and_move_to_point function from the helpers.py file
from helpers import generate_default_tolerances

# Load the assembly from the json file and scale it to Meters
assembly = json_load(json_path)

######################################################################################
# Path planning for the assembly
######################################################################################

# load tool mesh from data folder in this directory and create tool instance
tool_mesh = Mesh.from_stl(os.path.join(path, "data", "smc_gripper.stl"))

# add tool to robot, use measured TCP frame
# REPLACE THIS WITH YOUR OWN TCP FRAME
tool = Tool(
    visual=tool_mesh,
    collision=tool_mesh,
    frame_in_tool0_frame=Frame(point=[0, 0, 0.147], xaxis=[0.707, 0.707, 0], yaxis=[-0.707, 0.707, 0]),
)

# Connect to ROS and load robot
# We use 'with' to make sure the connection to ROS is closed properly
with RosClient() as ros:
    # Load robot from ROS and attach tool
    robot = ros.load_robot(load_geometry=False)
    # Attach tool to robot
    robot.attach_tool(tool, group=robot.main_group_name)

    # Create planning scene and add table as a collision mesh
    scene = PlanningScene(robot)
    scene.reset()
    base_mesh = Mesh.from_stl(os.path.join(path, "data", "ur5_base.stl"))
    scene.add_collision_mesh(CollisionMesh(base_mesh, "table"))

    index_to_recalculate = 3
    i = 0
    # go through all the items in the assembly.parts() generator object
    while True:
        part = assembly.find_by_key(
            i
        )  # get the part from the assembly at index i
        if index_to_recalculate == i:
            try:
                print(f"{i}. Calculate place trajectory")  # print the index of the part that is being processed
                # add attached stick to scene (current stick being held by the robot)
                mesh = part.shape.copy()
                T = Transformation.from_frame_to_frame(part.frame, tool.frame)
                mesh.transform(T)

                # Add attached stick to scene
                cmesh = CollisionMesh(Mesh.from_shape(mesh), "attached_stick")
                scene.attach_collision_mesh_to_robot_end_effector(cmesh)
                # get pick config from part
                approach_pick_config = part.attributes["approach_pick_config"]
                # Calculate place trajectory for the current part
                place_frame = part.frame.copy()

                # Calculate move trajectory (free space motion)
                max_step = 0.005

                # Planner needs goal constraints to be specified as a list
                # In this case we create constraints from a frame
                goal_constraints = robot.constraints_from_frame(
                    place_frame,
                    tolerance_position=0.001,
                    tolerances_axes=[0.001, 0.001, 0.001],
                    use_attached_tool_frame=True,
                    group=robot.main_group_name,
                )

                # Plan motion
                move_trajectory = robot.plan_motion(
                    goal_constraints,
                    start_configuration=approach_pick_config,
                    group=robot.main_group_name,
                    options=dict(
                        planner_id="RRTConnect",
                        avoid_collisions=True,
                    ),
                )

                # Save everything to part
                part.attributes["move_trajectory"] = move_trajectory

                # Remove attached stick from scene
                scene.remove_attached_collision_mesh("attached_stick")

                # Calculate exit trajectory
                print(f"{i}. Calculate exit trajectory")

                place_frame = part.frame.copy()
                place_approach_frame = place_frame.transformed(
                    Translation.from_vector(-place_frame.zaxis.scaled(APPROACH_DISTANCE))
                )

                # Calculate place configuration from place configuration
                place_config = move_trajectory.points[-1]
                approach_place_config = robot.inverse_kinematics(
                    place_approach_frame,
                    start_configuration=place_config,
                    group=robot.main_group_name,
                    options=dict(avoid_collisions=False),
                )

                # Calculate move trajectory (free space motion)
                max_step = 0.005
                tolerance_above = generate_default_tolerances(
                    robot.get_configurable_joints(robot.main_group_name)
                )
                tolerance_below = generate_default_tolerances(
                    robot.get_configurable_joints(robot.main_group_name)
                )

                # Planner needs goal constraints to be specified as a list
                # In this case we create constraints from a configuration
                goal_constraints = robot.constraints_from_configuration(
                    approach_pick_config,
                    tolerances_above=tolerance_above,
                    tolerances_below=tolerance_below,
                    group=robot.main_group_name,
                )

                # Plan motion
                move_trajectory = robot.plan_motion(
                    goal_constraints,
                    start_configuration=approach_place_config,
                    group=robot.main_group_name,
                    options=dict(
                        planner_id="RRTConnect",
                        avoid_collisions=True,
                    ),
                )

                # Save everything to part
                part.attributes["exit_trajectory"] = move_trajectory

            except Exception as e:
                print(e)  # Print the exception message
                print("Failed to calculate trajectory")

        # Once stick is added, add it to the scene as a collision object
        print(f"{i}. Add part to scene")
        cm = CollisionMesh(Mesh.from_shape(part.shape), "part%d" % i)
        scene.append_collision_mesh(cm)

        i += 1

        # Since we are only testing, we stop after 6 parts, you can remove this if statement to process the entire assembly
        if i >= assembly.attributes["num_parts"]:
            print("Only testing, stop here")
            break

    # Save the assembly to a json file
    json_dump(assembly, json_path, pretty=False)
