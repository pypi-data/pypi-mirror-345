import numpy as np
import pickle

robot = pickle.load(open("robot.pkl", "rb"))

for link in robot.links:
    print(f"### {link.name} ###")
    print(link.get_dynamics())

for joint in robot.joints:
    print(f"### {joint.name} ###")
    print(f"Joint Type: {joint.joint_type}")
    print(f"Max Effort: {joint.max_effort}")
    print(f"Max Velocity: {joint.max_velocity}")
    print(f"Limits: {joint.limits}")
    print(f"Z Axis: {joint.z_axis}")
    print(f"T World Joint: {joint.T_world_joint}")