# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Python script that drives a UFactory xArm through a fixed cooking sequence:
`home → pour 4 sauces → transition → pick 6 ingredients into bowl → home`.
Talks to the robot's control box at `192.168.10.10` via `xarm-python-sdk`.

## Commands

Python isn't on PATH in Git Bash on this machine — always use the venv's interpreter directly.

```bash
# run the full routine (connects to the arm)
.venv/Scripts/python.exe main.py

# verify imports without touching the robot
.venv/Scripts/python.exe -c "import config, positions, robot_base; \
  from routines import primitives, sauces, ingredients, transitions; \
  print('ok', len(positions.SAUCES), len(positions.INGREDIENTS))"

# recreate env on a fresh machine
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
```

There is no test suite, linter, or build step.

## Architecture

Five layers, each only knowing about the one below it:

```
main.py               ── STAGES list: (name, function) tuples executed in order
routines/*.py         ── stage functions: pour_all_sauces, load_ingredients, go_home, ...
routines/primitives   ── pick_and_place, pour_sauce  (compose a full pick→place cycle)
robot_base.RobotMain  ── move(), gripper()  (one set_position / set_gripper_position call each)
xarm.wrapper.XArmAPI  ── SDK
```

**Control flow is a boolean chain.** Every primitive and routine returns `True` on success, `False` on any failure. Callers early-return on `False` so a single fault aborts the recipe cleanly. `RobotMain._check_code` sets `self.alive = False` on any non-zero SDK code or controller error-state, and subsequent moves short-circuit.

**Configuration is data, not code.** `positions.py` is the only file that should change when waypoints drift or a new ingredient is added. `SAUCES` and `INGREDIENTS` are lists of dicts consumed by `pour_sauce` / `pick_and_place` via `**kwargs`. Adding a new ingredient = appending a dict; no routine changes.

**`wait=True` convention.** `RobotMain.move(pose, wait=False)` queues motion for trajectory blending. Exactly two moves per primitive set `wait=True` — the ones landing at grasp and release poses — so the arm is stationary before the gripper actuates. If you change this, the gripper may fire mid-trajectory.

**Phase remarks convention.** Original xArm Studio exports annotated the routine with phase comments (`# INIT_POSE`, `# GRAB FIRST SAUCE`, `# POURING THE SAUCE YOU CAN MAKE THIS MOVE FAST`, `# FIRST EGG`, `# DROPPED EGG GOING TO MEAT NOW`, `# GO TO INIT MODE`, etc.). Those comments are preserved verbatim (all-caps) above the corresponding phase boundary in each routine/primitive, and surface at runtime as banner lines via `robot.log('-- ... --')`. When editing routines, keep the remarks aligned with the phase they annotate.

**Special cases in `INGREDIENTS`** (preserve when refactoring):
- `egg` drops at `EGG_APPROACH` (x=544.4), others use `DROP_APPROACH` (x=560.2).
- `veg_3`'s `pick_pose` changes xy AND orientation from its `approach` — intentional.
- `veg_4` has `via_out` back through `veg_3`'s approach to avoid a collision on the return path.

## Operational notes

- xArm Studio (`http://192.168.10.10:18333`) and the SDK cannot drive the arm simultaneously — stop any Blockly program before running `main.py`.
- Default `TCP_SPEED = 100` in `config.py`; drop to ~30 for first runs or after waypoint edits.
- `POUR_FAST_SPEED = 200` overrides `TCP_SPEED` only for the `pour_tilt` move in `pour_sauce` (the original Studio export annotated that move with "YOU CAN MAKE THIS MOVE FAST"). `RobotMain.move(pose, speed=...)` is the override mechanism — nothing else should use it.
- `RobotMain.__init__` calls `clean_error()` + `motion_enable(True)`, so rerunning `main.py` recovers from a faulted state without a manual reset.
- Log labels follow `<name>.<phase>` (e.g., `sauce_2.grab`, `veg_3.drop_descend`) — useful for locating where a run aborted. Phase-boundary banners (`-- FIRST EGG --`, `-- GRAB FIRST SAUCE --`, etc.) print at runtime via `robot.log(...)` to match the original export's narrative.
