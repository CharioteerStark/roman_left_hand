"""Named waypoints for the cooking routine.

Pose format: [x, y, z, rx, ry, rz] in mm / degrees.
Coordinates are preserved from the original xArm Studio export.
"""

# -- Home --------------------------------------------------------------------
HOME_LOW  = [310.2, 549.8, 250.5, 0.0, 90.0, 0.0]
HOME_HIGH = [310.1, 537.0, 429.6, 0.1, 90.0, 0.0]

# -- Staging between the sauce and ingredient stages ------------------------
READY_HIGH = [469.2, 814.2, 682.5, -91.7, 90.0, 0.0]
READY_POSE = [469.2, 814.2, 470.5, -91.7, 90.0, 0.0]

# -- Sauces -----------------------------------------------------------------
BOTTLE_ORIENT   = [-91.7, 90.0, 0.0]   # all sauce bottles share this pick orientation
SAUCE_ENTRY_Z   = 682.5                # safe approach height coming from home
SAUCE_TRANSIT_Z = 600.0                # height used when transiting between bottles

POUR_OVER_LOW  = [611.0, 106.0, 288.7, 133.3, 89.7, 131.6]   # sauces 1-3
POUR_OVER_HIGH = [611.0, 106.0, 303.6, 133.3, 89.7, 131.6]   # sauce 4 (taller bottle)
POUR_TILT      = [611.0,  74.5, 288.4,  90.2, -45.8, 88.2]

SAUCES = [
    {'name': 'sauce_1', 'xy': (469.2, 1021.2), 'grab_z': 405.0, 'lift_z': 477.9, 'pour_over': POUR_OVER_LOW},
    {'name': 'sauce_2', 'xy': (331.6, 1021.2), 'grab_z': 405.0, 'lift_z': 477.0, 'pour_over': POUR_OVER_LOW},
    {'name': 'sauce_3', 'xy': (189.9, 1031.9), 'grab_z': 405.0, 'lift_z': 477.0, 'pour_over': POUR_OVER_LOW},
    # sauce_4 is picked at 413.4 but seated back at 405.0, and exits to a
    # dedicated pose (x nudged to 54.8, z=570.2) instead of the shared transit height
    {'name': 'sauce_4', 'xy': ( 55.8, 1036.0), 'grab_z': 413.4, 'lift_z': 477.0, 'pour_over': POUR_OVER_HIGH,
     'return_z': 405.0, 'exit_pose': [54.8, 1036.0, 570.2, -91.7, 90.0, 0.0]},
]

# -- Ingredients ------------------------------------------------------------
DROP_APPROACH = [560.2, 34.8, 319.5, 23.0, 89.7, -4.9]   # shared drop station over the bowl
EGG_APPROACH  = [544.4, 80.1, 319.5, 23.0, 89.7, -4.9]   # egg lands at a slightly different spot

INGREDIENTS = [
    {
        'name':          'egg',
        'approach':      [-95.2, 858.6, 470.5, -91.7, 90.0, 0.0],
        'pick_pose':     [-95.2, 858.6, 394.0, -91.7, 90.0, 0.0],
        'grip_close':    100,
        'via_out':       [317.9, 733.6, 432.5,   4.0, 86.9, 26.8],
        'drop_approach': EGG_APPROACH,
        'drop_pose':     [544.4,  80.1, 258.9,  23.0, 89.7, -4.9],
        'grip_release':  400,
    },
    {
        # meat is soft — pre-open wide and hold the close for 1.5s so the
        # jaws fully seat before we retract
        'name':          'meat',
        'approach':      [257.1, 781.6, 432.5,   4.0, 86.9, 90.6],
        'pick_pose':     [257.1, 781.6, 295.5,   4.0, 86.9, 90.6],
        'grip_preopen':  550,
        'grip_close':    0,
        'grip_hold_sec': 1.5,
        'via_out':       [446.9, 690.7, 432.5,   4.6, 86.8,  2.3],
        'drop_approach': DROP_APPROACH,
        'drop_pose':     [560.2,  34.8, 238.7,  23.0, 89.7, -4.9],
        'grip_release':  400,
    },
    {
        'name':          'veg_1',
        'approach':      [334.4, 695.6, 407.7,   8.6, 89.5,  9.9],
        'pick_pose':     [334.4, 695.6, 295.6,   8.6, 89.5,  9.9],
        'grip_close':    0,
        'drop_approach': DROP_APPROACH,
        'drop_pose':     [560.2,  34.8, 236.9,  23.0, 89.7, -4.9],
        'grip_release':  400,
    },
    {
        'name':          'veg_2',
        'approach':      [167.6, 707.9, 407.7,   8.6, 89.5,  9.9],
        'pick_pose':     [167.6, 707.9, 295.6,   8.6, 89.5,  9.9],
        'grip_close':    0,
        'drop_approach': DROP_APPROACH,
        'drop_pose':     [560.2,  34.8, 236.9,  23.0, 89.7, -4.9],
        'grip_release':  400,
    },
    {
        # pick_pose changes both xy and orientation vs. approach — preserved from original
        'name':          'veg_3',
        'approach':      [ -1.9, 707.9, 407.7,   8.6, 89.5,  9.9],
        'pick_pose':     [  2.0, 711.4, 282.8,  -1.9, 90.0,  0.0],
        'grip_close':    0,
        'drop_approach': DROP_APPROACH,
        'drop_pose':     [560.2,  34.8, 240.9,  23.0, 89.7, -4.9],
        'grip_release':  400,
    },
    {
        # veg_4 threads a multi-waypoint approach path from the bowl side
        # over to its slot; the reversed path is walked on retract so the
        # gripper returns the same way it came. Pose 1 is veg_3's approach —
        # the old single `via_out` folded into the path's head.
        'name':          'veg_4',
        'approach_path': [
            [  -1.9, 707.9, 407.7, 8.6, 89.5, 9.9],
            [  -1.9, 707.9, 358.7, 8.6, 89.5, 9.9],
            [-110.2, 707.9, 358.7, 8.6, 89.5, 9.9],
            [-133.1, 720.1, 329.9, 8.6, 89.5, 9.9],
        ],
        'pick_pose':     [-168.1, 707.9, 285.3,  8.6, 89.5,  9.9],
        'grip_preopen':  550,
        'grip_close':    0,
        'drop_approach': DROP_APPROACH,
        'drop_pose':     [ 560.2,  34.8, 248.9, 23.0, 89.7, -4.9],
        'grip_release':  400,
    },
]
