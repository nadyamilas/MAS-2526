from compas.datastructures import Assembly, Mesh
from compas.geometry import Frame, Point, Translation, Transformation
from compas_fab.backends import RosClient
from compas_fab.robots import Tool, PlanningScene, CollisionMesh, Configuration
import os, sys
from compas import json_load, json_dump
import math
import compas


compas.PRECISION = "12f"

# Constants
APPROACH_DISTANCE = 0.1  # Meters
group = None
start_configuration = None

# Specify the path to the assembly file and the path to the output file
path = os.path.dirname(__file__)
dire = os.path.join(path, "scripts")
sys.path.append(dire)

json_path = os.path.join(path, "data", "stick_assembly.json")
write_path = os.path.join(path, "data", "stick_assembly_with_trajectories.json")

# Import the scale_and_move_to_point function from the helpers.py file
from helpers import scale_and_move_to_point, generate_default_tolerances

# Load the assembly from the json file and scale it to Meters
assembly = json_load(json_path)["assembly"]
scaled_assembly = scale_and_move_to_point(assembly, Point(-0.300, -0.210, 0.010))


def calculate_pick_trajectory(pick_config, robot):
    """
    Calculate the pick trajectory for a given pick frame.
    Args:
        pick_frame (compas.geometry.Frame): The pick frame.
        robot (compas_fab.robots.Robot): The robot instance.
    Returns:
        tuple: The pick trajectory, the pick configuration and the approach pick configuration.
    """
    pick_config = pick_config

    pick_frame = robot.forward_kinematics(pick_config)
    approach_pick_frame = pick_frame.copy()
    approach_pick_frame.point.z += APPROACH_DISTANCE

    # Find IK solution for pick and approach pick frame
    start_configuration = robot.zero_configuration()

    
    approach_pick_config = robot.inverse_kinematics(
        approach_pick_frame, pick_config, group
    )

    # Generate cartesian trajectory from pick to approach pick frame
    max_step = 0.01
    frames = [
        robot.forward_kinematics(c, group, options=dict(solver="model"))
        for c in (approach_pick_config, pick_config)
    ]
    trajectory = robot.plan_cartesian_motion(
        frames,
        start_configuration=approach_pick_config,
        group=group,
        options=dict(
            max_step=max_step,
        ),
    )

    # Check if trajectory is complete
    if trajectory.fraction < 1:
        raise Exception(
            "Incomplete cartesian trajectory found. Only {:.1f}% of the trajectory could be planned".format(
                trajectory.fraction * 100
            )
        )

    # Return trajectory, pick configuration and approach pick configuration
    return trajectory, pick_config, approach_pick_config


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
    frame_in_tool0_frame=Frame(point=[1.75*.001, 1.29*.001, 153.2*.001], xaxis=[0.707, 0.707, 0], yaxis=[0.707, -0.707, 0]),
)

# Static pick frame location that you plan to use for all parts
# MEASURE THIS FROM YOUR ROBOT AND REPLACE THIS WITH YOUR OWN PICK FRAME
# pick_config = Frame(point=[-1.37*0.001, -444.50*0.001  , 9.70*0.001], xaxis=[1, 0, 0], yaxis=[0, 1, 0])
pick_config = Configuration.from_revolute_values([math.radians(-105.30),
                                                  math.radians(-84.7),
                                                  math.radians(127.68),
                                                  math.radians(-134.86),
                                                  math.radians(-88.22),
                                                  math.radians(-58.35)])


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

    # Calculate pick trajectory from the function above, we use the same pick frame for all parts
    print("Calculate pick trajectory")
    pick_trajectory, pick_config, approach_pick_config = calculate_pick_trajectory(
        pick_config, robot
    )
    print("Calculate pick trajectory: done")


    i = 0
    # go through all the items in the assembly.parts() generator object
    while True:
        part = scaled_assembly.find_by_key(
            i
        )  # get the part from the assembly at index i
        part.attributes["approach_pick_config"] = approach_pick_config
        part.attributes["pick_config"] = pick_config
        part.attributes["pick_trajectory"] = pick_trajectory
        try:
            # add attached stick to scene (current stick being held by the robot)
            mesh = part.shape.copy()
            T = Transformation.from_frame_to_frame(part.frame, tool.frame)
            mesh.transform(T)

            # Add attached stick to scene
            cmesh = CollisionMesh(Mesh.from_shape(mesh), id ="attached_stick")
            scene.attach_collision_mesh_to_robot_end_effector(cmesh)

            # Calculate place trajectory for the current part
            place_frame = part.frame.copy()
            safe_frame = part.attributes["safe_frame"]

            # Calculate move trajectory (free space motion)
            max_step = 0.001

            # Planner needs goal constraints to be specified as a list
            # Step 1 : move from pick approach to safe frame
            print(
            f"{i}. Calculate safe trajectory"
                )  # print the index of the part that is being processed
            # In this case we create constraints from a frame
            #print(safe_frame)
            goal_constraints = robot.constraints_from_frame(
                safe_frame,
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
            part.attributes["safe_trajectory"] = move_trajectory

            # Step 2 : safe plane to place frame
            print(
            f"{i}. Calculate place trajectory"
                )  # print the index of the part that is being processed
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
                start_configuration=move_trajectory.points[-1],
                group=robot.main_group_name,
                options=dict(
                    planner_id="RRTConnect",
                    avoid_collisions=True,
                ),
            )

            # Save everything to part
            part.attributes["place_trajectory"] = move_trajectory

            # Remove attached stick from scene
            scene.remove_attached_collision_mesh("attached_stick")

            # Calculate exit trajectory
            print(f"{i}. Calculate exit trajectory")

            place_frame = part.frame.copy()
            place_approach_frame = place_frame.transformed(
                Translation.from_vector(place_frame.zaxis.scaled(APPROACH_DISTANCE))
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
            exit_trajectory = robot.plan_motion(
                goal_constraints,
                start_configuration=approach_place_config,
                group=robot.main_group_name,
                options=dict(
                    planner_id="RRTConnect",
                    avoid_collisions=True,
                ),
            )

            # Save everything to part
            part.attributes["exit_trajectory"] = exit_trajectory

        except Exception as e:
            print(e)  # Print the exception message
            print("Failed to calculate trajectory")

        # Once stick is added, add it to the scene as a collision object
        cm = CollisionMesh(Mesh.from_shape(part.shape), id = "part%d" % i)
        scene.append_collision_mesh(cm)

        i += 1

        # Since we are only testing, we stop after 6 parts, you can remove this if statement to process the entire assembly
        if i >= assembly.attributes["num_parts"]:
            print("Only testing, stop here")
            break

    # Save the assembly to a json file
    json_dump(scaled_assembly, write_path, pretty=False)
