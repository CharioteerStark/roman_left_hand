"""Pour each configured sauce over the bowl, replacing the bottle each time.

Original Studio-export phase remarks preserved inline so the routine reads
with the same narrative the author annotated.
"""
from positions import SAUCES, BOTTLE_ORIENT, SAUCE_ENTRY_Z, SAUCE_TRANSIT_Z, POUR_TILT
from config import GRIPPER_BOTTLE, GRIPPER_HOME
from .primitives import pour_sauce


def pour_all_sauces(robot) -> bool:
    """Run the full sauce stage.

    Entry: arm at HOME_HIGH (or anywhere safe above the sauce line).
    Exit:  arm at SAUCE_TRANSIT_Z above the last bottle.
    """
    # YOU ARE IN A SAFE POSE — GO TO FIRST SAUCE
    x0, y0 = SAUCES[0]['xy']
    entry = [x0, y0, SAUCE_ENTRY_Z] + list(BOTTLE_ORIENT)
    if not robot.move(entry, label='sauces.entry'): return False

    for i, sauce in enumerate(SAUCES):
        if i == 0:
            robot.log('-- GRAB FIRST SAUCE --')
        else:
            robot.log('-- GO AND GRAB NEXT SAUCE ({}) --'.format(sauce['name']))
        ok = pour_sauce(
            robot,
            name=sauce['name'],
            xy=sauce['xy'],
            grab_z=sauce['grab_z'],
            lift_z=sauce['lift_z'],
            pour_over=sauce['pour_over'],
            pour_tilt=POUR_TILT,
            bottle_orient=BOTTLE_ORIENT,
            transit_z=SAUCE_TRANSIT_Z,
            grip_bottle=GRIPPER_BOTTLE,
            grip_release=GRIPPER_HOME,
        )
        if not ok:
            return False

    # READY FOR THE NEXT INGREDIENTS
    return True
