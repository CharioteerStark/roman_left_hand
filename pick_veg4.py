#!/usr/bin/env python3
"""Stop-after-lift veg_4 pickup — starts from the veg_3 drop pose.

The script's first move is to DROP_APPROACH (where pick_and_place leaves
the arm at the end of the veg_3 drop), then it proceeds into veg_4's
approach, descends to the pick pose, closes the gripper, and retracts
straight back up. Does NOT transit to the bowl or drop — the run ends
with the arm stationary above veg_4's slot holding the vegetable so you
can inspect the grasp.

Run:  .venv/Scripts/python.exe pick_veg4.py
"""
import time

from xarm import version
from xarm.wrapper import XArmAPI

from config import ROBOT_IP
from robot_base import RobotMain
from positions import INGREDIENTS, DROP_APPROACH


GRIP_PREOPEN = 550   # initial gripper width before the run — keeps the jaws
                     # clear of the veg_4 holder on approach

# Multi-waypoint approach path from DROP_APPROACH to just above veg_4.
# Pose 1 is veg_3's approach; poses 2–4 thread across to veg_4 without
# clipping neighboring holders. Used in-order going in, in reverse going out.
APPROACH_PATH = [
    [  -1.9, 707.9, 407.7, 8.6, 89.5, 9.9],
    [  -1.9, 707.9, 358.7, 8.6, 89.5, 9.9],
    [-110.2, 707.9, 358.7, 8.6, 89.5, 9.9],
    [-133.1, 720.1, 329.9, 8.6, 89.5, 9.9],
]


def pick_veg_4(robot) -> bool:
    veg_4 = next(i for i in INGREDIENTS if i['name'] == 'veg_4')
    # OPEN TO 550 AT INITIAL
    if not robot.gripper(GRIP_PREOPEN, label='veg_4.preopen'): return False
    # START AT THE VEG_3 DROP POSE — recreates the real precondition
    if not robot.move(DROP_APPROACH, label='veg_3.drop_retract'): return False
    # DROPPED VEG_3 NOW GOING TO VEG_4 — thread the multi-step approach
    for i, pose in enumerate(APPROACH_PATH, start=1):
        if not robot.move(pose, label='veg_4.approach_{}'.format(i)): return False
    if not robot.move(veg_4['pick_pose'], wait=True, label='veg_4.descend'): return False
    if not robot.gripper(veg_4['grip_close'], label='veg_4.close'): return False
    # RETURN — walk the approach path in reverse, then back to the drop pose
    for i, pose in enumerate(reversed(APPROACH_PATH), start=1):
        if not robot.move(pose, label='veg_4.retract_{}'.format(i)): return False
    if not robot.move(DROP_APPROACH, label='veg_4.to_drop'): return False
    return True


def main() -> None:
    RobotMain.log('xArm-Python-SDK Version: {}'.format(version.__version__))
    arm = XArmAPI(ROBOT_IP, baud_checkset=False)
    time.sleep(0.5)
    robot = RobotMain(arm)
    try:
        RobotMain.log('-- veg_4 pickup (refinement run) --')
        if pick_veg_4(robot):
            RobotMain.log('-- stopped at DROP_APPROACH holding vegetable --')
        else:
            RobotMain.log('-- veg_4 pickup aborted --')
    finally:
        robot.shutdown()


if __name__ == '__main__':
    main()
