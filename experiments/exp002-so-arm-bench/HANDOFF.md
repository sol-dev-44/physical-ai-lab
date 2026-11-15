# Session handoff: exp002 SO-ARM101 bench (as of 2026-11-15)

You are taking over an ongoing hands-on robotics session with Alan. Read this whole file before touching hardware. The bench README (`README.md` in this folder) has the full progress log; this file is the working brief.

## Who you are working with

- Alan wants short, direct answers. Give the answer first, then the one or two facts that support it.
- He does not want over-diagnosis. Do not blame hardware, cables, or calibration without evidence from a log or a read-only check. Earlier he called this out directly: "you're overanalyzing" and "consistently over diagnosing issues and pointing to hardware."
- He wants one step at a time. He wants a plan before a multi-step action, then his explicit "go."
- No em dashes or en dashes in any prose you draft for him.
- He is the only one who can see the arm and the Lego. You cannot see the arm. Your only view of a run is the terminal log and what he tells you. Ask him for the outcome of every run.

## Hard rules

1. **Motion needs an explicit go.** Anything that moves or torques a motor (rollout, teleop, record, calibration, motor setup) waits for a clear "go" from him in chat. "Make it 30" or "run them" is only a go for the run he named. Read-only checks (ping, probe, log reads, file reads) do not need a go.
2. **Reset between runs.** Rollouts are 30 seconds with no reset. Wait for him to reset the Lego and say go before each run after the first.
3. **No deleting data.** Archive instead (move to an archive folder). Never `rm` a dataset, checkpoint, or log.
4. **No commits or pushes unless he asks.** Edits to the README are fine; leave git alone.
5. **Stop safely.** If the arm looks wrong, or he says stop or interrupts, stop the process in the terminal tab (Ctrl-C or stop_terminal_tab) and tell him. The rollout ends with a return-to-rest and torque-off, so a clean stop is safe.
6. **Ask before big or outward-facing actions.** Uploading any dataset to an outside service, including a GPU provider, needs his explicit approval and the conditions in the project's ADR 0009 and 0010 notes.

## Hardware and ports

- Follower (white, does the work): `/dev/tty.usbmodem5B901016941`, id `my_awesome_follower_arm`.
- Leader (black, hand-moved): `/dev/tty.usbmodem5B901009311`, id `my_awesome_leader_arm`.
- Box camera: OpenCV index 0, Logitech, 1920x1080 native, mounted overhead about 50 to 70 cm, zoom set in Logi Tune.
- Wrist camera: index 1, 1280x720 native, mounted in the gripper slot. Recorded at 640x480.
- Ports and camera indexes change after a replug. Before any motion command, run `ls /dev/tty.usb*` and `probe_cams.py`.
- Camera access: commands that open cameras must run in the Terminal panel (`mcp__terminal__run_in_terminal`), not from Bash. Bash-launched camera access has failed before.
- A failed "Failed to enable torque" or "timed out" error usually means a bus or cable problem. The run stops before the arm moves. Ask Alan to check the cables before retrying.
- Power: the follower runs on the 12V adapter, the leader on 5V. Do not change cables with power on.

## Software

- LeRobot (Seeed fork, commit d490e472) at `/Users/alancampbell/lerobot`, conda env binaries at `/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/`.
- Commands: `lerobot-calibrate`, `lerobot-teleoperate`, `lerobot-record`, `lerobot-rollout` (the policy runner), `lerobot-train`, `lerobot-edit-dataset`, `lerobot-dataset-viz` (needs rerun-sdk, not installed).
- Keep the Mac awake for training with `caffeinate -dimsu`.
- Training log buffers under `grep` or `tail`. Read checkpoint folders or the raw log file instead of a live pipe.

## Calibration files (do not delete)

- `~/.cache/huggingface/lerobot/calibration/robots/so_follower/my_awesome_follower_arm.json`
- `~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/my_awesome_leader_arm.json`
- Earlier leader file kept as `my_awesome_leader_arm.json.reset-2026-11-12`.

## Current settings for recording and rollout (the baseline)

- Gain: `--robot.position_p_coefficient=32`. Gain 16 was the default and lagged badly. Gain 48 did not help.
- Speed cap: `--robot.max_relative_target=5`. This causes many "clamped" warnings in logs. Raising it to 10 is an untested lever.
- Cameras: box index 0, wrist index 1, both 640x480 at 30 fps.
- Recording: 30-second episodes, 15-second resets, bowl fixed in one spot, the Lego moved every episode.
- Rest to rest: each episode starts and ends with the arm retracted at its rest pose.

## Datasets (under `/Users/alancampbell/lerobot_data/`)

- `exp002-bowl-p32`: 65 episodes (0 to 64), 57,252 frames, gain 32. This is the current training dataset.
  - Episode 0 is a failure and is excluded from training.
  - Episode 37 had a fumble and recovery and is kept.
  - Episodes 10 to 64 were recorded rest-to-rest.
  - Episodes 40 to 64 are the orientation batch (2026-11-15). All 25 were successful demos.
- `exp002-bowl-p32-backup-2026-11-14`: the 40-episode copy made before the orientation batch. Do not delete it.
- `exp002-bowl-v1` (13 episodes, older, not used for training).
- `exp002-red-lego-test` (5 episodes, earliest test).
- `exp002-lag-*` (arm-only lag tests, no cameras).
- Archives: `/Users/alancampbell/lerobot_data/archive/`.

## Training runs (under `/Users/alancampbell/lerobot_outputs/`)

- `exp002-bowl-act-5k`: 5,000 steps on episodes 1 to 9. Jerky, never reached the Lego.
- `exp002-bowl-act-50k`: 50,000 steps on episodes 1 to 39, batch size 8, MPS, finished 2026-11-14 11:03 after 7h 44m. Checkpoints every 5,000 steps (005000 to 050000 plus `last`).
  - Current policy: `checkpoints/050000/pretrained_model`.
  - Training script: `scripts/train_act_50k.sh` in this folder.
- `exp002-bowl-act-50k-v2`: 50,000 steps from scratch on episodes 1 to 64, same settings. Started 2026-11-15 05:58, expected to finish around 14:30. Script: `scripts/train_act_50k_v2.sh`. Log: `/Users/alancampbell/lerobot_outputs/train_act_50k_v2_2026-11-15.log`.
- Training speed on the Mac: about 1.6 to 1.7 steps per second.

## Rollout results so far (50k checkpoint, 30 seconds, gain 32, cap 5)

| Test | Setting | Result |
|---|---|---|
| 1 | default (100 actions per chunk) | Reached the Lego, bumped it, regrasped, dropped it in the bowl, returned to rest. Shaky. |
| 2 | Lego flat and horizontal | Run 1 missed on a couple of tries. Run 2 grabbed right away. Run 3 (Lego vertical) missed three times. |
| 3 | Lego flat, stacked on two other blocks | Succeeded on the first try. |
| 4 | Lego flat, rotated to 12 o'clock | Gripper did not rotate to grab; missed three times next to the block. |
| 5 | Lego flat, horizontal | Bumped on the first grab, missed, overshot left twice. |
| 6 | `n_action_steps=10` | Barely moved and shook periodically. Worse. |
| 7 | temporal ensembling (`n_action_steps=1`, `temporal_ensemble_coeff=0.01`) | Loop held 30 Hz. Missed left twice, wrist did not roll enough, hovered and shook on the third try. |

Notes:
- The 5k checkpoint has not been rolled out again since the first test.
- Temporal ensembling is not a grasp improvement on these runs. It is smoother. Do not present it as the default.
- Rollout settings change only how the policy runs, not its weights. Better grasping needs more data and a retrain.

## Current plan (what is next)

1. Done: backup of the dataset (see above).
2. Done (2026-11-15): 25 orientation episodes (40 to 64), appended to `exp002-bowl-p32` with `--resume=true` and `--dataset.num_episodes=25`. Script: `scripts/record_orient_25.sh`. Placement schedule:
   - 6 flat and horizontal, spread across the mat
   - 6 vertical
   - 6 rotated at about 3, 6, 9 and 12 o'clock
   - 4 stacked on the other two blocks
   - 3 near the bowl or the mat edges
   The other two blocks stay in the scene as distractors, flat, moved to a new spot each episode. ACT does not read the task text, so they are what teach it to pick by color.
3. Done: Alan marked no sloppy episodes in the batch. For later batches, filter sloppy ones at training time, do not delete them.
4. Running: retrain on episodes 1 to 64 for 50,000 steps (`exp002-bowl-act-50k-v2`, see above).
5. Pick the number of steps. Test the 30k and 50k checkpoints on the same fixed placements, about 10 trials each, and keep the one with more successful grasps. Do not pick by training loss.
6. Keep adding batches until the dataset is near 100 episodes, then repeat steps 4 and 5.

Possible helpers (not yet verified):
- A camera-based success check after each run: whether the red Lego ends up inside the blue bowl. Test it before relying on it. Alan's own notes stay the final word.
- A fine-tune from the current checkpoint instead of a from-scratch run. Check whether this LeRobot version supports it before proposing it.
- A rented CUDA GPU for training. This is an outside upload, so it needs Alan's explicit approval first, plus the ADR 0010 conditions.

## Known gotchas

- The first `lerobot-rollout` attempt after a replug failed with "Could not connect on port". Retrying after confirming the ports worked. Confirm the ports every time.
- The follower's gripper motor (ID 6) once failed torque enable with a timeout. A cable check fixed it.
- Logs contain many "Relative goal position magnitude had to be clamped" warnings. This is the speed cap working.
- Loop rate dips to about 16 Hz at 100-action chunks. Temporal ensembling held 30 Hz.
- `lerobot-record` resumes with `--resume=true` and counts `--dataset.num_episodes` as new episodes to record in that run.
- Keyboard controls during recording: n for next episode, r to re-record, q to quit. Quitting ends the set early.
- The box camera has dropped out mid-session before. Its index was 0 on every probe so far.

## Where to look

- Bench progress log and gotchas: `README.md` in this folder.
- Run scripts: `scripts/` in this folder (`probe_cams.py`, `record_bowl_30more.sh`, `record_orient_25.sh`, `train_act_50k.sh`, `train_act_50k_v2.sh`, and the three `rollout_act50k_*` scripts). The rollout scripts point at the first 50k checkpoint; change `--policy.path` to test the v2 checkpoints.
- The wiki and its own handoff material: `/Users/alancampbell/Desktop/Iron Lion Ventures LLC/wiki`.
