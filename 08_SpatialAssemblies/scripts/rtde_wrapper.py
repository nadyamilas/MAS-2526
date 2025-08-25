from rtde_control import RTDEControlInterface as RTDEControl
from rtde_control import Path, PathEntry
from rtde_io import RTDEIOInterface
from rtde_receive import RTDEReceiveInterface as RTDEReceive
import time
import threading
from compas.geometry import Frame, Transformation, Translation, Vector, Point
from compas.robots import Configuration
from compas_fab.robots import JointTrajectory
import compas
import sys, os, psutil


def get_config(ip="127.0.0.1"):
    ur_r = RTDEReceive(ip)
    robot_joints = ur_r.getActualQ()
    config = Configuration.from_revolute_values(robot_joints)
    return config

def get_tcp_offset(ip="127.0.0.1"):
    ur_c = RTDEControl(ip)
    tcp = ur_c.getTCPOffset()
    return tcp

def set_tcp_offset(pose, ip = "127.0.0.1"):
    ur_c = RTDEControl(ip)
    ur_c.setTcp(pose)

def move_to_joints(config, speed, accel, nowait, ip="127.0.0.1"):
    # speed rad/s, accel rad/s^2, nowait bool
    ur_c = RTDEControl(ip)
    ur_c.moveJ(config.joint_values, speed, accel, nowait)

def movel_to_joints(config, speed, accel, nowait, ip="127.0.0.1"):
    # speed rad/s, accel rad/s^2, nowait bool
    ur_c = RTDEControl(ip)
    ur_c.moveL_FK(config.joint_values, speed, accel, nowait)

def move_to_target(frame, speed, accel, nowait, ip="127.0.0.1"):
    # speed rad/s, accel rad/s^2, nowait bool
    pose = frame.point.x/1000, frame.point.y/1000, frame.point.z/1000, *frame.axis_angle_vector
    ur_c = RTDEControl(ip)
    ur_c.moveL(pose ,speed, accel, nowait)
    return pose


def pick_and_place_async(pick_frames, place_frames, speed, accel, ip, vaccum_io, safe_dist = 100):
    thread = threading.Thread(target=pick_and_place, args=(pick_frames, place_frames, speed, accel, ip, vaccum_io, safe_dist))
    thread.start()

def pick_and_place(pick_frames, place_frames, speed, accel, ip, vaccum_io, safe_dist = 100):
#move to pick safety plane
    if isinstance(pick_frames,Frame):
        pick_frames = [pick_frames]*len(place_frames)

    for pick, place in zip(pick_frames, place_frames):
        move_to_target(pick.transformed(Translation.from_vector(Vector(0,0,safe_dist))), speed, accel, False, ip = ip)
        #move to pick plane
        move_to_target(pick, speed, accel, False, ip = ip)
        #turn IO on
        set_digital_io(vaccum_io,True,ip=ip)
        #sleep on position to give some time to pick up
        time.sleep(0.5)
        #move to pick safety plane
        move_to_target(pick.transformed(Translation.from_vector(Vector(0,0,safe_dist))), speed, accel, False, ip = ip)
        #move to pre placement frame
        pre_place_frame = place.transformed(Translation.from_vector(Vector(0,0,safe_dist)))
        move_to_target(pre_place_frame, speed, accel, False, ip = ip)
        #move to placement frame
        move_to_target(place, speed, accel, False, ip = ip)
        #turn vaccuum off to place brick
        set_digital_io(vaccum_io,False,ip=ip)
        #sleep robot to make sure it is placed
        time.sleep(0.5)
        #move to post placement frame
        post_place_frame = place.transformed(Translation.from_vector(Vector(0,0,safe_dist)))
        move_to_target(post_place_frame, speed, accel, False, ip = ip)

def create_path(frames, velocities, accelerations, radii):
    # speed rad/s, accel rad/s^2, nowait bool
    path = Path()
    for i,(f,v,a,r) in enumerate(zip(frames,velocities,accelerations, radii)):
        pose = f.point.x/1000, f.point.y/1000, f.point.z/1000, *f.axis_angle_vector
        if i == 0 or i >= len(frames)-2:
            r = 0.0
        target = [*pose,v/1000,a/1000, r/1000]
        path.addEntry(PathEntry(PathEntry.MoveL, PathEntry.PositionTcpPose,target))
    return path

def move_to_path(frames, velocities, accelerations, radii, ip = "127.0.0.1", ur_c = None):
    # speed, accel, nowait bool
    path = create_path(frames, velocities, accelerations, radii)
    ur_c.movePath(path, True)
    return path

def moveL_and_sleep(frames, accelerations, velocities, sleep_times, nowait= False, ip="127.0.0.1"):
    #sleep_times is a list created in 202_send_printpath.py
    #add it as a list => sleep_times.append(item['sleep_time'])
    #in GH in the PrintPoint class add sleep_time as a property with the default value of 0.0
    #in GH when creating the way_points change the value of sleep_time for every way_point you need to sleep
    if isinstance(accelerations,float):
        accelerations = [accelerations]*len(frames)
    if isinstance(velocities,float):
        velocities = [velocities]*len(frames)

    ur_c = RTDEControl(ip)

    for i, (sleep_time, frame, speed, accel) in enumerate(zip(sleep_times, frames, velocities, accelerations)):
        #add this to start extruding after the safe point
        turn_extrusion_on(speed = 1, ip= ip)
        try:
            pose = frame.point.x/1000, frame.point.y/1000, frame.point.z/1000, *frame.axis_angle_vector
            ur_c.moveL(pose, speed/1000, accel/1000, nowait)
            if sleep_time > 0:
                set_digital_io(5, True, ip)
                time.sleep(sleep_time)
                turn_extrusion_on(speed = 1, ip= ip)
        except KeyboardInterrupt:
            safe_acc = 0.1
            ur_c.stopL(safe_acc)
            set_digital_io(5, True, ip)
            ur_c.stopScript()
            exit()


def turn_extrusion_on(speed, ip):
    set_digital_io(5,False,ip)
    if speed == 0:
        set_digital_io(6,False, ip)
        set_digital_io(7,True, ip)
    elif speed == 1:
        set_digital_io(6,True, ip)
        set_digital_io(7,False, ip)

def send_printpath(frames, velocities, accelerations, radii, toggles, ip = '127.0.0.1'):
    #set params
    rtde_frequency = 500.0
    dt = 1.0/rtde_frequency  # 2ms
    flags = RTDEControl.FLAG_VERBOSE | RTDEControl.FLAG_UPLOAD_SCRIPT
    ur_cap_port = 50002
    ip = "localhost"



    # ur_rtde realtime priorities
    rt_receive_priority = 90
    rt_control_priority = 90

    ur_c = RTDEControl(ip, rtde_frequency, flags, ur_cap_port, rt_control_priority)


  # Set application real-time priority
    os_used = sys.platform
    process = psutil.Process(os.getpid())
    if os_used == "win32":  # Windows (either 32-bit or 64-bit)
        process.nice(psutil.REALTIME_PRIORITY_CLASS)

    #if no list for accel provided, create a list for it with values repeated
    if isinstance(accelerations,float):
        accelerations = [accelerations]*len(frames)
    if isinstance(velocities,float):
        velocities = [velocities]*len(frames)

    for i in range(3):
        exec = move_to_path(frames, velocities, accelerations, radii, ur_c= ur_c)
        waypoint = -1 #initial waypoint
        cur_time = time.time()
        change_toggle = False
        new_waypoint = 0
        try:
            while new_waypoint < len(frames)-1 and new_waypoint>=0:
                new_waypoint = ur_c.getAsyncOperationProgress() #counter index
                print(new_waypoint)
                if new_waypoint != waypoint:
                    counter = new_waypoint-1
                    #print(counter)
                    if toggles[counter] != toggles[counter-1] or counter == 0:
                        change_toggle = True
                    #print(str((counter/len(frames))*100) + "%")
                    if  change_toggle:
                        if toggles[counter]:
                            turn_extrusion_on(speed = 0,ip= ip)
                        else:
                            set_digital_io(5, True, ip)
                if len(frames) - new_waypoint < 3:
                    break

            print('done')
            set_digital_io(5, True, ip)
        except KeyboardInterrupt:
            safe_acc = 0.1
            ur_c.stopL(safe_acc)
            set_digital_io(5, True, ip)
            ur_c.stopScript()
            exit()

        print('done')
        set_digital_io(5, True, ip)


def send_realtime_moveL(frames, vel, acc, ip = "127.0.0.1", ur_cap_port = 50002):
    rtde_frequency = 500.0
    dt = 1.0/rtde_frequency  # 2ms
    flags = RTDEControl.FLAG_VERBOSE | RTDEControl.FLAG_UPLOAD_SCRIPT
    ur_cap_port = 50002
    ip = "localhost"

    lookahead_time = 0.2
    gain = 2000

    # ur_rtde realtime priorities
    rt_receive_priority = 90
    rt_control_priority = 85

    rtde_r = RTDEReceive(ip, rtde_frequency, [], True, False, rt_receive_priority)
    rtde_c = RTDEControl(ip, rtde_frequency, flags, ur_cap_port, rt_control_priority)

    # Set application real-time priority
    os_used = sys.platform
    process = psutil.Process(os.getpid())
    if os_used == "win32":  # Windows (either 32-bit or 64-bit)
        process.nice(psutil.REALTIME_PRIORITY_CLASS)
    elif os_used == "linux":  # linux
        rt_app_priority = 80
        param = os.sched_param(rt_app_priority)
        try:
            os.sched_setscheduler(0, os.SCHED_FIFO, param)
        except OSError:
            print("Failed to set real-time process scheduler to %u, priority %u" % (os.SCHED_FIFO, rt_app_priority))
        else:
            print("Process real-time priority set to: %u" % rt_app_priority)

    counter = 0

    # Move to initial position
    init_pose = frames[0].point.x/1000, frames[0].point.y/1000, frames[0].point.z/1000, *frames[0].axis_angle_vector
    rtde_c.moveL(init_pose, vel/1000, acc/1000)

    counter = 1

    try:
        while counter < len(frames)-1:
            print(counter)
            t_start = rtde_c.initPeriod()
            path = []
            servo_target = frames[counter].point.x/1000, frames[counter].point.y/1000, frames[counter].point.z/1000, *frames[counter].axis_angle_vector
            target = [*servo_target, vel/1000, acc/1000]
            rtde_c.moveL(servo_target, vel/1000, acc/1000,  False)
            rtde_c.waitPeriod(t_start)
            counter += 1

    except KeyboardInterrupt:
        print("Control Interrupted!")
        rtde_c.stopL()
        rtde_c.stopScript()

def stopL(accel, ip = "127.0.0.1"):
    ur_c = RTDEControl(ip)
    ur_c.stopL(accel)

def get_digital_io(signal, ip="127.0.0.1"):
    ur_r = RTDEReceive(ip)
    return ur_r.getDigitalOutState(signal)

def set_digital_io(signal, value, ip="127.0.0.1"):
    io = RTDEIOInterface(ip)
    io.setStandardDigitalOut(signal, value)

def set_tool_digital_io(signal, value, ip="127.0.0.1"):
    io = RTDEIOInterface(ip)
    io.setToolDigitalOut(signal, value)

def get_tcp_frame(ip="127.0.0.1"):
    ur_r = RTDEReceive(ip)
    tcp = ur_r.getActualTCPPose()
    frame = Frame.from_axis_angle_vector(tcp[3:], point=tcp[0:3])
    return frame

def move_trajectory(trajectory: JointTrajectory, speed, accel, blend, ip = "127.0.0.1"):
    path = []
    ur_c = RTDEControl(ip)
    for config in trajectory.points:
        path.append(config.joint_values + [speed, accel, blend])
    if len(path):
        ur_c.moveJ(path)

def start_teach_mode(ip="127.0.0.1"):
    ur_c = RTDEControl(ip)
    ur_c.teachMode()

def stop_teach_mode(ip="127.0.0.1"):
    ur_c = RTDEControl(ip)
    ur_c.endTeachMode()

if __name__ == "__main__":
    pass
    frames = [Frame(Point(300.000, 200.000, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000)),Frame(Point(280.902, 258.779, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(230.902, 295.106, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(169.098, 295.106, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(119.098, 258.779, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(100.000, 200.000, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(119.098, 141.221, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(169.098, 104.894, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(230.902, 104.894, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(280.902, 141.221, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(300.000, 200.000, 0.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))
                ,Frame(Point(280.902, 141.221, 100.000), Vector(1.000, 0.000, 0.000), Vector(0.000, 1.000, 0.000))]

    base_frame = Frame(Point(548.032, 552.647, -2.884), Vector(-1.000, -0.013, 0.002), Vector(0.013, -1.000, 0.003))

    T =  Transformation.from_frame_to_frame(Frame.worldXY(), base_frame)

    frames = [f.transformed(T) for f in frames]

    T =  Translation.from_vector([0,-100,-0.75])

    frames = [f.transformed(T) for f in frames]

    velocities = [0.015]*12
    accelerations = [0.015]*12
    radii = [0.025]*12
    toggles = [True,True,True,True,True,True,True,True,True, True, False, False]


    #ip_address = "192.168.10.10"
    ip_address = "127.0.0.1"
    send_printpath(frames, velocities, accelerations,radii, toggles, ip=ip_address)
