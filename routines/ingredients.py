"""Pick each ingredient and place it in the bowl.

The original xArm Studio export called out three phase transitions:
    FIRST EGG
    DROPPED EGG GOING TO MEAT NOW
    DROPPED MEAT NOW GOING AFTER OTHER INGREDIENTS
They're surfaced below as log announcements so the runtime output tells
the same story as the original comments.
"""
from positions import INGREDIENTS
from .primitives import pick_and_place


# Per-ingredient phase announcement at the moment that ingredient starts.
# Keys are ingredient `name` values from positions.INGREDIENTS.
PHASE_ANNOUNCE = {
    'egg':   'FIRST EGG',
    'meat':  'DROPPED EGG GOING TO MEAT NOW',
    'veg_1': 'DROPPED MEAT NOW GOING AFTER OTHER INGREDIENTS',
}


def load_ingredients(robot) -> bool:
    for item in INGREDIENTS:
        banner = PHASE_ANNOUNCE.get(item['name'])
        if banner:
            robot.log('-- {} --'.format(banner))
        if not pick_and_place(robot, **item):
            return False
    return True
