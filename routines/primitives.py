"""Composable motion building blocks used by the cooking routines.

Each primitive returns True on success, False on failure. The move that
lands the tool at a grasp/release pose uses wait=True so the arm is
stationary when the gripper actuates.

Phase comments in CAPS match the remarks from the original xArm Studio
exports ("GRAB FIRST SAUCE", "POURING THE SAUCE YOU CAN MAKE THIS MOVE
FAST", etc.) so the refactored code reads with the same narrative the
Studio author annotated.
"""
from config import POUR_FAST_SPEED


def pick_and_place(robot, *,
                   name, approach, pick_pose, grip_close,
                   drop_approach, drop_pose, grip_release,
                   via_out=None, **_ignored) -> bool:
    """Pick an item at `pick_pose` and drop it at `drop_pose`.

    Sequence:
        approach -> pick_pose(wait) -> close -> approach
        -> [via_out] -> drop_approach -> drop_pose(wait) -> release
        -> drop_approach
    """
    # APPROACH AND GRAB
    if not robot.move(approach, label='{}.approach'.format(name)): return False
    if not robot.move(pick_pose, wait=True, label='{}.descend'.format(name)): return False
    if not robot.gripper(grip_close, label='{}.close'.format(name)): return False
    if not robot.move(approach, label='{}.retract'.format(name)): return False

    # OPTIONAL VIA POINT ON THE WAY TO THE BOWL
    if via_out is not None:
        if not robot.move(via_out, label='{}.via_out'.format(name)): return False

    # DROP INTO BOWL
    if not robot.move(drop_approach, label='{}.drop_approach'.format(name)): return False
    if not robot.move(drop_pose, wait=True, label='{}.drop_descend'.format(name)): return False
    if not robot.gripper(grip_release, label='{}.release'.format(name)): return False
    if not robot.move(drop_approach, label='{}.drop_retract'.format(name)): return False
    return True


def pour_sauce(robot, *,
               name, xy, grab_z, lift_z, pour_over,
               pour_tilt, bottle_orient, transit_z,
               grip_bottle, grip_release) -> bool:
    """Pick a sauce bottle, pour over the bowl, return the bottle to its shelf.

    Sequence:
        above -> grab(wait) -> grip_bottle -> lift -> pour_over -> pour_tilt(fast)
        -> pour_over -> lift -> grab(wait) -> release -> above
    """
    x, y = xy
    rx, ry, rz = bottle_orient
    above = [x, y, transit_z, rx, ry, rz]
    lift  = [x, y, lift_z,    rx, ry, rz]
    grab  = [x, y, grab_z,    rx, ry, rz]

    # GO TO SAUCE
    if not robot.move(above, label='{}.above'.format(name)): return False
    if not robot.move(grab, wait=True, label='{}.grab'.format(name)): return False
    # GRAB SAUCE
    if not robot.gripper(grip_bottle, label='{}.grip'.format(name)): return False
    # LIFT OUT OF SHELF AND CARRY OVER THE BOWL
    if not robot.move(lift, label='{}.lift'.format(name)): return False
    if not robot.move(pour_over, label='{}.pour_over'.format(name)): return False
    # POURING THE SAUCE — YOU CAN MAKE THIS MOVE FAST
    if not robot.move(pour_tilt, label='{}.pour_tilt'.format(name),
                      speed=POUR_FAST_SPEED): return False
    # PUTTING IT IN THE PREV POSITION
    if not robot.move(pour_over, label='{}.pour_untilt'.format(name)): return False
    # RETURN BOTTLE TO SHELF
    if not robot.move(lift, label='{}.return_lift'.format(name)): return False
    if not robot.move(grab, wait=True, label='{}.return_grab'.format(name)): return False
    if not robot.gripper(grip_release, label='{}.release'.format(name)): return False
    # GOING TO NEXT SAUCE
    if not robot.move(above, label='{}.exit'.format(name)): return False
    return True
