"""Connection and motion parameters for the xArm cooking routine."""

# Robot connection
ROBOT_IP = '192.168.10.10'

# Motion (mm/s, mm/s^2 and deg/s, deg/s^2)
TCP_SPEED = 100
TCP_ACC = 2000
ANGLE_SPEED = 20
ANGLE_ACC = 500

# Studio export remarks the pour_tilt move with "YOU CAN MAKE THIS MOVE FAST".
# Used only for the pour_tilt step in pour_sauce; everything else stays at TCP_SPEED.
POUR_FAST_SPEED = 200

# Gripper positions (0 = closed, higher = more open)
GRIPPER_SPEED = 5000
GRIPPER_CLOSED = 0        # tight grip: meat / solid ingredients
GRIPPER_BOTTLE = 100      # sauce bottles
GRIPPER_READY = 300       # wide open, pose between stages
GRIPPER_RELEASE = 400     # drop an ingredient into the bowl
GRIPPER_HOME = 500        # fully open at home / between sauce bottles
