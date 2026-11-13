# exp002: SO-ARM101 Pro bench notes

Status: both arms calibrated and teleop working (2026-11-12). Fine-tuning of the gripper is open.
Not an experiment run yet. No camera, no trials, no sync. Nothing here is published.

## Kit

- Seeed Studio SO-ARM101 Pro, assembled (SKU 100046482), bought as the LeRobot AI arm kit.
- Black arm = leader (hand-moved, 7.4V motors, read-only). White arm = follower (does the work, 12V motors).
- Leader motors per the Seeed wiki: joints 1 and 3 use 1:191, joint 2 uses 1:345, joints 4 to 6 use 1:147.
- Follower motors: 12V STS3215 family. Check the motor labels before changing voltage.
- Power: leader on the 5V 4A adapter, follower on the 12V 2A adapter (the bigger one, labelled theqingliupower).
  The wiki's rule: Pro leader 5V, Pro follower 12V. Double-check the adapter label before every power-up.
- The kit's power cables are multi-head. USB-C cables: the kit includes two; an Apple USB-C cable worked.

## Software

- LeRobot from the Seeed fork: `Seeed-Projects/lerobot`, commit `d490e472` (LeRobot 0.7.1).
  Installed at `~/lerobot` into a conda env named `lerobot` (Python 3.12), with `pip install -e ".[feetech]"`
  and ffmpeg from conda-forge (svtav1 encoder present). Kept outside the lab's uv workspace on purpose.
- Commands run from `/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/`:
  `lerobot-find-port`, `lerobot-setup-motors`, `lerobot-calibrate`, `lerobot-teleoperate`.
- Miniforge installed with `brew install --cask miniforge`.

## Ports (this Mac)

- Follower (white): `/dev/tty.usbmodem5B901016941`
- Leader (black): `/dev/tty.usbmodem5B901009311`
- Mac port names are `/dev/tty.usbmodem*`. The wiki's `/dev/ttyACM*` names are Linux. On this Mac no `sudo chmod` was needed.
- Ports can change when a cable is moved. Confirm with `ls /dev/tty.usb*` before every command.
  To match a port to a board, unplug one board and see which name disappears.

## Current calibration (2026-11-12, raw positions 0 to 4095)

| Joint | Leader min to max | Follower min to max | Note |
|---|---|---|---|
| Shoulder pan | 760 to 3379 | 783 to 3523 | Left goes past perpendicular; right stops at a physical limit |
| Shoulder lift | 863 to 2936 | 765 to 2863 | Normal bend |
| Elbow | 1866 to 4067 | 2046 to 4062 | Normal bend |
| Wrist flex | 873 to 2818 | 967 to 3007 | Normal bend |
| Gripper | 2038 to 3243 | 2026 to 3532 | Follower opens wider |
| Wrist roll | full turn | full turn | Middle set by pose, see below |

These numbers are only valid for the offsets saved in the current calibration files. Re-calibrating
moves the raw readings, so any stored goal in raw units must be re-measured after a calibration.

## What worked

- Motor IDs were already set from the factory. Every motor answers on IDs 1 to 6, model 777 (STS3215).
- Read-only checks worked with `SerialMotorsBus` and `sync_read("Present_Position", normalize=False)`.
  Raw positions are 0 to 4095. Torque reads as 0 on all joints when idle.
- The calibration that worked: type `c` at the prompt, set the middle pose with the arm neutral, sweep each
  joint within its normal bend, and check the saved file before any teleop.
- Teleop ran at 60 Hz with `--robot.max_relative_target=5`. Shoulder lift, elbow, wrist flex and wrist roll
  tracked the leader smoothly after the 2026-11-12 recalibration.

## Gotchas and lessons

- **Enter reuses the old calibration, and writes it to the motors.** The calibration prompt says:
  "Press ENTER to use provided calibration file ... or type 'c' and press ENTER to run calibration".
  Pressing Enter alone rewrites the old file to the motors and records nothing new. Type `c` first.
- **Calibration min and max only grow during a run.** Once a joint has been pushed to an extreme,
  that value stays. Ctrl-C cancels the run without saving; start over to fix it.
- **Start the middle step in neutral.** The middle pose sets each joint's zero. If the arm is not neutral
  at that step, every joint's zero is off by that amount. Most of the mismatches we chased on 11 and 12
  November came from this.
- **Full-turn ranges are a warning.** A joint recorded as 0 to 4095 (or 1 to 4094) has either
  wrapped around or been pushed past its normal bend. Shoulder lift and elbow both came out full-turn in
  several early runs. Keep each joint within its normal working range while calibrating.
- **Wrist roll is a full-turn joint.** Calibration always records it as 0 to 4095 and uses only the middle
  pose to set its offset. Turning it more than a quarter turn during the sweep is fine.
- **Wrist roll middle must be matched on both arms.** Put both wrist rolls at the same physical orientation
  at the middle pose, so the jaws point the same way. This fixed the 90-degree gripper offset from earlier.
- **Practice ranges before a calibration.** A read-only sweep of the leader (no torque change, no writes)
  showed the normal range of each joint before we set goals. The sweep for each joint is cheaper than
  calibrating and finding a bad range.
- **Calibration does not reset the motors.** `lerobot`'s `reset_calibration` sets homing offset to 0 and
  limits to the full 0 to 4095 range. It does not reset IDs or baud rate, and no factory reset command was
  found in the LeRobot code.
- **Teleop speed cap.** We ran with `--robot.max_relative_target=5` (a deliberate deviation from the wiki
  command). The "Relative goal position magnitude had to be clamped" warnings show the cap working.
- **A bus dropout on the follower.** Once, the follower's wrist roll (ID 5) timed out when torque was enabled,
  before anything moved. A read-only ping then found all six motors fine. The cause was not confirmed.
- **A joint that stopped reporting (not repeated after 12 November).** Early on, a leader joint's raw value
  stayed flat while the hand moved it, with torque off and load 0. Later reads and calibrations showed motion
  again. The cause was not confirmed. If it happens again, a register dump (position limits, offset,
  mode, voltage, temperature, load) is the first check, then the joint's horn and linkage.
- **Do not use the Seeed wiki's `/dev/ttyACM*` commands on the Mac.** Use the `/dev/tty.usbmodem*` names above.
- **Avoid USB hubs** (the wiki's advice). Both boards are plugged directly into the Mac.
- **Power off or unplug the adapter before changing cables** (the wiki's rule). The USB cable carries no power.

## Open items for fine-tuning (not blocking)

1. **Gripper reach at the mat.** The follower touches earlier than the leader when the arm is close, and
   later when it extends. Suspected cause: a small shoulder lift or elbow zero mismatch between the arms.
   Next check is the neutral pose of both arms, compared by eye and then by teleop at near and extended reach.
2. **Gripper closing gap.** The follower's jaws stop about 1/4 inch short of closed. The follower's motor
   stopped about 15 counts above its calibrated closed end, so the software range is not the whole story.
   Possible causes: the speed cap had not finished closing when teleop was stopped, or the jaw mechanism
   stops short. Test: hold the leader fully closed for 10 seconds, stop, then read the follower.
3. **Shoulder pan right stop.** The right end of the pan is likely a physical limit. Confirm before relying on it.

## Harness work (later, not started)

- Build the arm adapter in `lab_agent/devices/` with no safety logic in it.
- Add the arm tools to the registry, plus joint-limit, velocity and workspace interlocks.
- Add a real stop path before any autonomous motion.
- Make the speed cap wrap-aware, so a goal is the nearest equivalent angle to the present position.
  The wrist roll reversal (below) is the reason.
- Teleop demonstrations become events. A new event type needs the full contract process in AGENTS.md.

## Known issue: wrist roll wrap-around in teleop

- A full roll of the leader's wrist makes the follower stop midway and reverse.
- Cause, most likely: the wrist roll is a full-turn joint (LeRobot records it with `full_turn_motors`),
  so its raw reading wraps from 4095 to 0. When the leader crosses that point, the goal jumps by almost
  a full turn in the opposite direction. The follower's speed cap (`max_relative_target`) moves it toward
  the new goal the long way round, which looks like a reversal.
- Workaround for now: keep the leader's wrist roll within about 150 degrees either side of the middle.
- Fix (for the harness, not the bench): see the harness work list above.
