"""XArm controller with the motion primitives used by the routines.

Each primitive returns True on success, False if the arm has errored out
or a move was rejected. Routines should early-return when a primitive
returns False so the run aborts cleanly.
"""
import time
import traceback

from config import TCP_SPEED, TCP_ACC, GRIPPER_SPEED


class RobotMain:
    def __init__(self, arm):
        self.alive = True
        self._arm = arm
        self._ignore_exit_state = False
        self._tcp_speed = TCP_SPEED
        self._tcp_acc = TCP_ACC
        self._init_arm()

    # -- connection / state management --------------------------------------
    def _init_arm(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)
        self._arm.register_error_warn_changed_callback(self._on_error)
        self._arm.register_state_changed_callback(self._on_state)

    def _on_error(self, data):
        if data and data['error_code'] != 0:
            self.alive = False
            self.log('err={}, quit'.format(data['error_code']))
            self._arm.release_error_warn_changed_callback(self._on_error)

    def _on_state(self, data):
        if not self._ignore_exit_state and data and data['state'] == 4:
            self.alive = False
            self.log('state=4, quit')
            self._arm.release_state_changed_callback(self._on_state)

    def shutdown(self):
        self.alive = False
        try:
            self._arm.release_error_warn_changed_callback(self._on_error)
            self._arm.release_state_changed_callback(self._on_state)
        except Exception:
            pass

    @property
    def arm(self):
        return self._arm

    @property
    def is_alive(self) -> bool:
        if not (self.alive and self._arm.connected and self._arm.error_code == 0):
            return False
        if self._ignore_exit_state:
            return True
        if self._arm.state == 5:
            for _ in range(5):
                if self._arm.state != 5:
                    break
                time.sleep(0.1)
        return self._arm.state < 4

    def _check_code(self, code: int, label: str) -> bool:
        if not self.is_alive or code != 0:
            self.alive = False
            state = self._arm.get_state()
            err = self._arm.get_err_warn_code()
            self.log(
                '{}, code={}, connected={}, state={}, error={}, ret1={}, ret2={}'
                .format(label, code, self._arm.connected, self._arm.state,
                        self._arm.error_code, state, err)
            )
        return self.is_alive

    # -- motion primitives --------------------------------------------------
    def move(self, pose, wait: bool = False, label: str = 'move',
             speed: int = None) -> bool:
        """Linear Cartesian move. Pass wait=True to block until motion
        completes — use before gripper operations so the gripper doesn't
        actuate mid-trajectory. Pass speed to override the default TCP_SPEED
        for a single move (used by pour_sauce's pour_tilt, which the original
        Studio export annotated 'YOU CAN MAKE THIS MOVE FAST')."""
        code = self._arm.set_position(
            *pose,
            speed=speed if speed is not None else self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=wait,
        )
        return self._check_code(code, label)

    def gripper(self, position: int, label: str = 'gripper') -> bool:
        code = self._arm.set_gripper_position(
            position, wait=True, speed=GRIPPER_SPEED, auto_enable=True,
        )
        return self._check_code(code, label)

    # -- logging ------------------------------------------------------------
    @staticmethod
    def log(*args):
        try:
            frame = traceback.extract_stack(limit=2)[0]
            ts = time.strftime('%Y-%m-%d %H:%M:%S')
            print('[{}][{}] {}'.format(ts, frame[1], ' '.join(map(str, args))))
        except Exception:
            print(*args)
