#!/usr/bin/env python3
"""Ingredients-only run — picks up from where sauces left the arm.

PRECONDITION: the arm must already be parked at the pose that
pour_all_sauces leaves behind before this script is run:
    pose    : SAUCES[-1]['exit_pose']  (sauce_4 exit,
                                        [54.8, 1036.0, 570.2, -91.7, 90.0, 0.0])
    gripper : GRIPPER_HOME (500) — released from sauce 4

Typical use: run pour_all_sauces once (via main.py or the one-off command),
then invoke this script to iterate on just the ingredient half without
repeating the sauce pours.

Flow: transition -> ingredients -> return_home.

Run:  .venv/Scripts/python.exe run_ingredients.py
"""
import time

from xarm import version
from xarm.wrapper import XArmAPI

from config import ROBOT_IP
from robot_base import RobotMain
from routines.transitions import return_to_home, transition_to_ingredients
from routines.ingredients import load_ingredients


STAGES = [
    ('transition',   transition_to_ingredients),
    ('ingredients',  load_ingredients),
    ('return_home',  return_to_home),
]


def main() -> None:
    RobotMain.log('xArm-Python-SDK Version: {}'.format(version.__version__))
    arm = XArmAPI(ROBOT_IP, baud_checkset=False)
    time.sleep(0.5)
    robot = RobotMain(arm)
    try:
        for name, stage in STAGES:
            RobotMain.log('-- stage: {} --'.format(name))
            if not stage(robot):
                RobotMain.log('stage "{}" aborted'.format(name))
                return
        RobotMain.log('-- routine complete --')
    except Exception as e:
        RobotMain.log('MainException: {}'.format(e))
    finally:
        robot.shutdown()


if __name__ == '__main__':
    main()
