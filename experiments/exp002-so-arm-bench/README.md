# exp002: SO-ARM101 Pro bench notes

Status (2026-11-15): both arms calibrated, teleop working, two cameras recording. A 50k-step ACT policy runs on the arm and grasps the Lego on flat placements, but misses rotated and vertical ones and moves jerkily. A 25-episode orientation batch is recorded (65 episodes total) and a second 50k retrain on episodes 1 to 64 is running. See the progress log below. Nothing here is published.

Run scripts for recording, training and rollout are in `scripts/`. They hold this Mac's ports, camera indexes and paths, so check those before running one.

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

## Progress log (2026-11-13 to 2026-11-15)

### Setup
- Box camera: Logitech, OpenCV index 0, 1920x1080, mounted about 50 to 70 cm overhead. Zoom and focus set in Logi Tune (not controllable from OpenCV on this Mac).
- Wrist camera: index 1, recorded at 640x480, mounted in the gripper slot.
- Camera indexes can change after a replug. Check with `probe_cams.py` before recording.
- Both cameras record together. Logi Tune is installed in /Applications.
- Mac hostname changed during the session (Mac-146 to Mac-153). Serial port names did not change.

### Calibration and tuning
- Leader and follower recalibrated on 2026-11-13. The follower's gripper still stops about 10 counts above its calibrated closed end. Cause not confirmed; accepted for now.
- Shoulder lift lag on the follower at the default gain (16): up to 100 to 155 degrees behind the leader on some runs.
- Gain 32 (`--robot.position_p_coefficient=32`): mean bowl-episode lag about 3 degrees, worst about 48. Gain 48 did not help the quick swing. Gain 32 is the recording setting.
- Speed cap `--robot.max_relative_target=5` stays on. The policy regularly asks for bigger steps, so the logs show many "clamped" warnings.

### Dataset `exp002-bowl-p32` (gain 32, bowl fixed, Lego moved each episode)
- 40 episodes (0 to 39), 35,037 frames. Reset 15 s, episode 30 s.
- Episode 0 is a failure and is excluded from training.
- Episodes 10 to 39 were recorded with the rest-to-rest pattern (see below).
- Episode 37 had a brief fumble and recovery, and is kept.
- Older `exp002-bowl-v1` (13 episodes) is not used for training.

### Training
- `exp002-bowl-act-5k`: 5,000 steps on episodes 1 to 9, batch size 8, MPS. About 1.7 steps per second. First rollout was jerky and never reached the Lego.
- `exp002-bowl-act-50k`: 50,000 steps on episodes 1 to 39, batch size 8, MPS. Finished 2026-11-14 at 11:03 after 7 h 44 min. Checkpoints every 5,000 steps.

### Rollouts (30 s, both cameras, gain 32, cap 5)
- 5k checkpoint: moved, shaky, never got close to the Lego.
- 50k, first run: reached the Lego, bumped it going down, backed off, regrasped, dropped it in the bowl, returned to rest. Shaky, but much better.
- 50k, Lego flat and horizontal: run 1 missed on a couple of attempts. Run 2 grabbed right away. Run 3 (Lego vertical) missed on three attempts.
- 50k, second batch: run 1 with the Lego flat, stacked on the other two blocks, succeeded on the first try. Run 2 with the Lego flat and rotated to 12 o'clock: the gripper did not rotate to grab, and it missed three times next to the block. Run 3 with the Lego flat and horizontal: bumped it on the first grab, missed, then overshot to the left twice.
- Loop rate dips to about 16 Hz during runs. Inference averages about 50 to 60 ms with occasional spikes to about 200 ms.
- 50k, `n_action_steps=10`: barely moved and shook periodically. Worse than the default.
- 50k, temporal ensembling (`n_action_steps=1`, `temporal_ensemble_coeff=0.01`): the loop held 30 Hz and motion was smoother, but it missed left twice, the wrist did not roll enough, and it hovered and shook on the third try. Not a grasp improvement, so not the default.
- Rollout settings change only how the policy runs, not its weights. Better grasping needs more data and a retrain.

### Orientation batch (2026-11-15)
- Backup first: `exp002-bowl-p32-backup-2026-11-14` (40 episodes), kept.
- Recorded 25 episodes (40 to 64) appended to `exp002-bowl-p32` with `--resume=true`, same settings as the bowl batch (gain 32, cap 5, both cameras at 640x480 and 30 fps, 30 s episodes, 15 s resets, rest to rest). Script: `scripts/record_orient_25.sh`.
- Red Lego placements: 6 flat and horizontal across the mat, 6 vertical, 6 rotated (about 3, 6, 9 and 12 o'clock), 4 stacked on the other two blocks, 3 near the bowl or the mat edges.
- The other two blocks stay in the scene as distractors, flat, moved to a new spot each episode. ACT does not read the task text, so the distractors are what teach it to pick by color.
- All 25 episodes were successful demos. None are excluded.
- Dataset is now 65 episodes (0 to 64), 57,252 frames. Episode 0 is still excluded from training.

### Retrain `exp002-bowl-act-50k-v2` (started 2026-11-15 05:58)
- From scratch, 50,000 steps on episodes 1 to 64 (56,352 frames), batch size 8, MPS, checkpoints every 5,000 steps. Script: `scripts/train_act_50k_v2.sh`.
- About 1.6 steps per second, so expect it to finish around 14:30.
- Log: `/Users/alancampbell/lerobot_outputs/train_act_50k_v2_2026-11-15.log`. Recording log: `/Users/alancampbell/lerobot_data/record_orient_25_2026-11-15.log`.
- Next: test the 30k and 50k checkpoints on the same fixed placements, about 10 trials each, and keep the one with more successful grasps. Do not pick by training loss.

### Read of the results (not verified)
- The policy works on some placements, but it misses rotated and vertical Lego positions. Those are under-covered in the training data.
- Jerkiness is still there. The speed-cap clamp is the likely cause, but a cap of 10 has not been tested yet.

### Next
1. Done: temporal ensembling tested (see rollouts above).
2. Done: orientation batch recorded (25 episodes, see above).
3. Running: retrain on episodes 1 to 64. Then compare the 30k and 50k checkpoints, about 10 trials each.
4. Keep adding batches until the dataset is near 100 episodes, then retrain and compare again.
5. Not started: test the speed cap at 10 on a rollout.
6. Not started: decide the training location. No upload has happened. Check the conditions in ADR 0010 first.

## Plan and next steps (2026-11-13)

(Partly superseded by the progress log above. Items 1 and 2 are done.)

Status: teleop works, a 5-episode test dataset is recorded, and a 5,000-step ACT checkpoint ran on the
arm for 30 seconds. It moved but never reached down to the Lego, so the next work is about data and reach,
not new hardware.

### Why it stalled (from the saved demos)

- Wrist flex: commands reached 117 degrees, but the follower only reached about 89.5. 1,445 of 4,500 frames
  asked for more than 94.5 degrees, which is past what the follower can reach.
- Wrist roll and elbow: the same pattern, a smaller gap (wrist roll commanded 121, reached 108; elbow
  commanded 96.5, reached 88).
- The policy learned targets the arm can't follow, so it stalls near the edge of its range.

### Plan (from the video walkthrough, adapted to this bench)

1. **Match the arms.** Recalibrate both arms. Sweep each joint through the follower's reachable range, not
   the full 0 to 4095 range. Keep demo commands inside what the follower can reach.
2. **Better data (30 to 50 episodes).** Vary the Lego's position and orientation each episode. Keep lighting
   fixed. Orientation mattered more than episode count in the video.
3. **Add two cameras.** A top-down box camera shows the whole table, so the policy can locate the Lego.
   The small wrist camera from the Seeed kit mounts in the slot at the end of the follower arm and shows
   the grasp itself. Both need mounts and a recording check. The wrist camera needs its own USB connection,
   so check that two cameras and both arms run on the Mac before recording.
4. **Check the dataset before training.** Run `lerobot-dataset-viz` on the dataset to confirm the camera view
   and the joint traces look right.
5. **Train on a GPU.** ACT with the device set to `cuda`. Expect 40 to 60 minutes on a mid-range card. The
   Mac's 5,000-step run stays as a baseline.
6. **Evaluate in a fixed way.** 10 trials per checkpoint, same Lego position and lighting, count successful
   grasps. Count a stuck retry as a miss after a hand reset.
7. **Iterate.** Record more demos where the policy fails. Then try SmolVLA, which generalizes better but needs
   the GPU.

### Next steps (start here tomorrow)

1. Recalibrate the leader and follower (go-ahead needed, the arms move). Check the saved ranges, and confirm
   the demo wrist commands stay under the follower's reach.
2. Run `lerobot-dataset-viz` on `/Users/alancampbell/lerobot_data/exp002-red-lego-test` and check the camera view.
3. Record about 30 demos with the Lego in different positions and orientations. Use `--resume=true` to append.
4. Choose the GPU provider and name it in these notes before any upload (ADR 0010). Check its live price.
5. Mount the top-down box camera and the wrist camera. Check both cameras run together. Keep the privacy
   rules in ADR 0009 and 0010 for every saved frame.

### Data and file locations (outside the repo, never committed)

- Current dataset: `/Users/alancampbell/lerobot_data/exp002-bowl-p32` (65 episodes, gain 32).
- Backup before the orientation batch: `/Users/alancampbell/lerobot_data/exp002-bowl-p32-backup-2026-11-14` (40 episodes).
- Earlier test dataset: `/Users/alancampbell/lerobot_data/exp002-red-lego-test` (5 episodes).
- Mac training outputs: `/Users/alancampbell/lerobot_outputs/` (`exp002-bowl-act-5k`, `exp002-bowl-act-50k`, `exp002-bowl-act-50k-v2` (running), and the older 100-step smoke run).
- Current checkpoint: `/Users/alancampbell/lerobot_outputs/exp002-bowl-act-50k/checkpoints/050000/pretrained_model`.

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

## Demonstration pattern: rest to rest

- Each episode in the bowl batch (gain 32, bowl fixed) starts and ends with the arm retracted to its rest pose.
  The operator returns the arm to rest after dropping the Lego in the bowl, so every episode begins and ends at the same pose.
- Episodes 10 to 39 were recorded this way. Episode 37 had a brief fumble and recovery, and is kept.
