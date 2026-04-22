#!/usr/bin/env python3
"""Stop-after-lift meat pickup for refining the meat pose.

Assumes the arm has just finished the egg step and is hovering over the
bowl at EGG_APPROACH with the gripper wide from the egg release. Moves
to the meat approach, descends to the pick pose, closes the gripper,
and retracts straight back up to the approach height. Does NOT transit
out or drop — the run ends with the arm stationary above the meat slot
with the meat in the gripper so you can inspect the grasp.

Run:  .venv/Scripts/python.exe pick_meat.py
"""
import time

from xarm import version
from xarm.wrapper import XArmAPI

from config import ROBOT_IP
from robot_base import RobotMain
from positions import INGREDIENTS


GRIP_PREOPEN = 550   # wider than GRIPPER_HOME (500) so the jaws clear the meat
                     # comfortably before the descent
GRIP_CLOSE = 0     # refinement override: squeeze past 0 to get a firmer
                     # bite on the soft meat than positions.INGREDIENTS gives
GRIP_HOLD_SEC = 1.5  # extra dwell after the gripper closes so the jaws
                     # fully seat on the soft meat before we retract


def pick_meat(robot) -> bool:
    meat = next(i for i in INGREDIENTS if i['name'] == 'meat')
    # OPEN WIDE BEFORE APPROACH so a stale grip state doesn't clip the meat
    if not robot.gripper(GRIP_PREOPEN, label='meat.preopen'): return False
    # DROPPED EGG GOING TO MEAT NOW
    if not robot.move(meat['approach'], label='meat.approach'): return False
    if not robot.move(meat['pick_pose'], wait=True, label='meat.descend'): return False
    if not robot.gripper(GRIP_CLOSE, label='meat.close'): return False
    RobotMain.log('-- holding grip for {}s --'.format(GRIP_HOLD_SEC))
    time.sleep(GRIP_HOLD_SEC)
    if not robot.move(meat['approach'], label='meat.retract'): return False
    return True


def main() -> None:
    RobotMain.log('xArm-Python-SDK Version: {}'.format(version.__version__))
    arm = XArmAPI(ROBOT_IP, baud_checkset=False)
    time.sleep(0.5)
    robot = RobotMain(arm)
    try:
        RobotMain.log('-- meat pickup (refinement run) --')
        if pick_meat(robot):
            RobotMain.log('-- stopped at meat.approach holding meat --')
        else:
            RobotMain.log('-- meat pickup aborted --')
    finally:
        robot.shutdown()


if __name__ == '__main__':
    main()
