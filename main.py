#!/usr/bin/env python3
"""Cooking routine entry point: home -> sauces -> ingredients -> home.

Run from the project root:  python main.py
"""
import time

from xarm import version
from xarm.wrapper import XArmAPI

from config import ROBOT_IP
from robot_base import RobotMain
from routines.transitions import go_home, return_to_home, transition_to_ingredients
from routines.sauces import pour_all_sauces
from routines.ingredients import load_ingredients


STAGES = [
    ('home',         go_home),
    ('sauces',       pour_all_sauces),
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
