"""Composable motion building blocks used by the cooking routines.

Each primitive returns True on success, False on failure. The move that
lands the tool at a grasp/release pose uses wait=True so the arm is
stationary when the gripper actuates.

Phase comments in CAPS match the remarks from the original xArm Studio
exports ("GRAB FIRST SAUCE", "POURING THE SAUCE YOU CAN MAKE THIS MOVE
FAST", etc.) so the refactored code reads with the same narrative the
Studio author annotated.
"""
import time

from config import POUR_FAST_SPEED


def pick_and_place(robot, *,
                   name, pick_pose, grip_close,
                   drop_approach, drop_pose, grip_release,
                   approach=None, approach_path=None,
                   via_out=None, grip_preopen=None, grip_hold_sec=None,
                   **_ignored) -> bool:
    """Pick an item at `pick_pose` and drop it at `drop_pose`.

    Sequence:
        [preopen] -> approach*  -> pick_pose(wait) -> close -> [hold] -> retract*
        -> [via_out] -> drop_approach -> drop_pose(wait) -> release
        -> drop_approach

    *approach*: pass either `approach` (single pose) OR `approach_path`
    (list of poses threaded in order). `retract*` walks `approach_path`
    in reverse, or returns to the single `approach` pose.

    `grip_preopen` widens the jaws before the descent so a stale grip state
    doesn't clip the item (used on soft picks like meat). `grip_hold_sec`
    dwells after the close so the jaws have time to seat fully before the
    retract. Both default to None = skip.
    """
    assert approach is not None or approach_path is not None, \
        '{}: pick_and_place needs approach or approach_path'.format(name)
    approach_list = approach_path if approach_path is not None else [approach]
    multi = len(approach_list) > 1

    # OPTIONAL PRE-OPEN — keep the jaws clear of the item on the way down
    if grip_preopen is not None:
        if not robot.gripper(grip_preopen, label='{}.preopen'.format(name)): return False

    # APPROACH AND GRAB
    for i, pose in enumerate(approach_list, start=1):
        suffix = '_{}'.format(i) if multi else ''
        if not robot.move(pose, label='{}.approach{}'.format(name, suffix)): return False
    if not robot.move(pick_pose, wait=True, label='{}.descend'.format(name)): return False
    if not robot.gripper(grip_close, label='{}.close'.format(name)): return False

    # OPTIONAL DWELL — let soft items seat in the jaws before we lift
    if grip_hold_sec is not None:
        robot.log('-- {}.hold for {}s --'.format(name, grip_hold_sec))
        time.sleep(grip_hold_sec)

    # RETRACT — walk the approach path in reverse (or back to the single approach)
    for i, pose in enumerate(reversed(approach_list), start=1):
        suffix = '_{}'.format(i) if multi else ''
        if not robot.move(pose, label='{}.retract{}'.format(name, suffix)): return False

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
               grip_bottle, grip_release,
               return_z=None, exit_pose=None) -> bool:
    """Pick a sauce bottle, pour over the bowl, return the bottle to its shelf.

    Sequence:
        above -> grab(wait) -> grip_bottle -> lift -> pour_over -> pour_tilt(fast)
        -> pour_over -> lift -> return_grab(wait) -> release -> exit

    `return_z` lets the bottle be seated back at a slightly different height
    than the pickup (sauce_4 picks at 413.4 but reseats at 405.0). `exit_pose`
    overrides the default "above at transit_z" retreat for bottles that need
    a bespoke clearance (sauce_4 exits at x=54.8, z=570.2).
    """
    x, y = xy
    rx, ry, rz = bottle_orient
    above       = [x, y, transit_z, rx, ry, rz]
    lift        = [x, y, lift_z,    rx, ry, rz]
    grab        = [x, y, grab_z,    rx, ry, rz]
    return_grab = grab if return_z is None else [x, y, return_z, rx, ry, rz]
    exit_move   = above if exit_pose is None else exit_pose

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
    if not robot.move(return_grab, wait=True, label='{}.return_grab'.format(name)): return False
    if not robot.gripper(grip_release, label='{}.release'.format(name)): return False
    # GOING TO NEXT SAUCE
    if not robot.move(exit_move, label='{}.exit'.format(name)): return False
    return True
