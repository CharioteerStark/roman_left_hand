"""Home poses and transitions between stages.

Original Studio-export phase remarks (INIT_POSE, POSE AFTER SAUCES,
GO TO INIT MODE) preserved inline.
"""
from positions import (
    HOME_LOW, HOME_HIGH,
    READY_HIGH, READY_POSE,
    SAUCES, SAUCE_ENTRY_Z, BOTTLE_ORIENT,
)
from config import GRIPPER_HOME, GRIPPER_READY


def go_home(robot) -> bool:
    """Move to the home pose and fully open the gripper."""
    # INIT_POSE
    if not robot.move(HOME_LOW, label='home.low'): return False
    if not robot.move(HOME_HIGH, label='home.high'): return False
    if not robot.gripper(GRIPPER_HOME, label='home.gripper'): return False
    return True


def return_to_home(robot) -> bool:
    """End-of-run return to the home pose."""
    # GO TO INIT MODE
    if not robot.move(HOME_HIGH, label='return.high'): return False
    if not robot.move(HOME_LOW, label='return.low'): return False
    return True


def transition_to_ingredients(robot) -> bool:
    """Bridge from end-of-sauces to start-of-ingredients.

    Retreats up over the first sauce (to clear the shelf), traverses toward
    the bowl area, and drops to the ingredient staging pose with the gripper
    set wide for picking.
    """
    # READY FOR THE NEXT INGREDIENTS — clear the last sauce shelf first
    x0, y0 = SAUCES[0]['xy']
    sauce_safe = [x0, y0, SAUCE_ENTRY_Z] + list(BOTTLE_ORIENT)
    if not robot.move(sauce_safe, label='transition.sauce_safe'): return False
    # POSE AFTER SAUCES
    if not robot.move(READY_HIGH, label='transition.ready_high'): return False
    if not robot.move(READY_POSE, label='transition.ready_pose'): return False
    if not robot.gripper(GRIPPER_READY, label='transition.gripper'): return False
    return True
