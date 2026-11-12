# exp002: SO-ARM101 Pro bench notes

Status: bench setup in progress (2026-11-11). Not an experiment run yet. No camera, no
trials, no sync. Nothing here is published.

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

## Ports (this Mac, this session)

- Follower (white): `/dev/tty.usbmodem5B901016941`
- Leader (black): `/dev/tty.usbmodem5B901009311`
- Mac port names are `/dev/tty.usbmodem*`. The wiki's `/dev/ttyACM*` names are Linux. On this Mac no `sudo chmod` was needed.
- Ports can change when a cable is moved. Confirm with `ls /dev/tty.usb*` before every command.
  To match a port to a board, unplug one board and see which name disappears.

## What worked

- Motor IDs were already set from the factory. Every motor answers on IDs 1 to 6, model 777 (STS3215).
- Read-only checks worked with `SerialMotorsBus` and `sync_read("Present_Position", normalize=False)`.
  Raw positions are 0 to 4095. Torque read as 0 on all joints.
- Follower calibration saved all six joints: pan 726 to 3464, shoulder lift 717 to 3123,
  elbow 1363 to 3574, wrist flex 739 to 3086, gripper 2032 to 3508.
- Teleop ran at 60 Hz with a per-update cap (see gotchas). It worked in a rough sense: the follower tracked the leader, but the calibration needs more work before it is accurate.

## Gotchas and lessons

- **Enter reuses the old calibration, and writes it to the motors.** The calibration prompt says:
  "Press ENTER to use provided calibration file ... or type 'c' and press ENTER to run calibration".
  Pressing Enter alone rewrites the old file to the motors and records nothing new. Type `c` first.
- **Calibration min and max only grow during a run.** Once a joint has been pushed to an extreme,
  that value stays. Ctrl-C cancels the run without saving; start over to fix it.
- **Full-turn ranges are a warning.** A joint recorded as 0 to 4095 (or 1 to 4094) has either
  wrapped around or been pushed past its normal bend. Keep each joint within its normal working range
  while calibrating.
- **Wrist roll is often not recorded.** If it is never moved, it keeps the default 0 to 4095. The wiki
  mentions that servo 5 may not report during calibration.
- **Teleop speed cap.** Teleop with a bad leader range is unsafe. We ran with
  `--robot.max_relative_target=5` (a deliberate deviation from the wiki command). The
  "Relative goal position magnitude had to be clamped" warnings show the cap working; the follower lags the hand.
- **A bus dropout on the follower.** Once, the follower's wrist roll (ID 5) timed out when torque was enabled,
  before anything moved. A read-only ping then found all six motors fine. Re-seating the 3-pin
  cables and reconnecting was followed by a clean teleop start. The cause was not confirmed.
- **Leader joints stopped reporting.** After a recalibration, the leader's elbow, wrist flex and gripper
  showed no change during a hand-moved read, while shoulder pan and wrist roll did. Torque was off and
  load was 0, so the motors weren't resisting. The next calibration gave the gripper a real range
  (2039 to 3246), and the elbow moved. The cause is not confirmed.
- **Do not use the Seeed wiki's `/dev/ttyACM*` commands on the Mac.** Use the `/dev/tty.usbmodem*` names above.
- **Avoid USB hubs** (the wiki's advice). Both boards are plugged directly into the Mac.
- **Power off or unplug the adapter before changing cables** (the wiki's rule). The USB cable carries no power.

## Known issue: wrist roll offset between leader and follower

- Teleop tracks accurately overall, but the two grippers don't line up. In the same hand pose, the
  leader's jaws are vertical and the follower's are horizontal (about 90 degrees apart).
- Cause, most likely: the wrist roll's "middle" pose was not set the same way on both arms during
  calibration. Calibration sets each joint's zero from the middle pose, so a physical difference at
  that step becomes a fixed offset in teleop.
- Why it matters: a demonstration recorded with this offset teaches the policy a rotated wrist. It must be
  fixed before recording data, not left as a known quirk.
- Fix plan: at the next calibration, set both wrist rolls to the same physical orientation at the middle
  pose (for example both jaws pointing the same way), then check the jaws line up in teleop.
  If a small offset remains, correct the wrist roll `homing_offset` in the calibration file and note the value here.

## Open items for tomorrow

1. Recalibrate the leader. Keep shoulder lift, wrist flex and elbow within their normal bend. Type `c` at the
   first prompt. Check the saved file before any teleop. Set the wrist roll to match the follower at the middle pose
   (see the known issue above).
2. Re-check the follower's ranges, wrist roll included. Recalibrate if the wrist roll is still the default.
3. Teleop with the speed cap, watching the elbow and wrist. Then remove the cap only when the ranges look right.
4. Confirm the follower's bus stays stable over a few minutes of motion.
5. Only after the calibration is solid: plan the arm adapter and the stop path for the lab harness
   (per AGENTS.md: adapter in `lab_agent/devices/` with no safety logic, interlocks, and a real stop path).
   Nothing is integrated into the harness yet.
