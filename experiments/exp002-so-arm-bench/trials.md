# exp002 rollout trials

One row per 30-second rollout. Alan watches every run and reports the outcome; the log only shows timing and clamps.

## Checkpoints

| Name | Run folder (under `/Users/alancampbell/lerobot_outputs/`) | Trained on | Steps |
|---|---|---|---|
| v1 50k | `exp002-bowl-act-50k/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 39 | 50,000 |
| v2 30k | `exp002-bowl-act-50k-v2/checkpoints/030000` | `exp002-bowl-p32` episodes 1 to 64 | 30,000 |
| v2 50k | `exp002-bowl-act-50k-v2/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 64 | 50,000 |
| v3 50k | `exp002-bowl-act-50k-v3/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 94 (65 to 94 in the new environment, C920 overhead cam) | 50,000 |
| v4 50k | `exp002-bowl-act-50k-v4/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 124 (95 to 124 rotation-weighted) | 50,000 |

## Fixed lists

- Placement of the red Lego: `flat-horizontal`, `vertical`, `rotated-3`, `rotated-6`, `rotated-9`, `rotated-12`, `stacked`, `near-edge`, `near-bowl`, or `not recorded`.
  The Lego always lies flat on the mat. `flat-horizontal`: long side left to right. `vertical`: long side pointing straight away from the arm. `rotated-12`: angled like a clock hand at about 1 o'clock.
- Outcome: `grasp-first` (grasped on the first attempt), `grasp-retry` (grasped after one or more misses), `missed` (never grasped in 30 s), `dropped` (grasped, then lost it before the bowl).
- In bowl: whether the Lego ended in the bowl.
- Settings: gain and speed cap are 32 and 5 unless noted. `chunk` is the default 100 actions per chunk. `nas10` is `n_action_steps=10`. `te` is temporal ensembling (`n_action_steps=1`, `temporal_ensemble_coeff=0.01`).

Rows marked `not recorded` were backfilled from the progress log and lack that detail.

## Trials

| # | Date | Checkpoint | Settings | Placement | Outcome | Attempts | In bowl | Notes |
|---|---|---|---|---|---|---|---|---|
| 1 | 2026-11-14 | v1 50k | chunk | not recorded | grasp-retry | 2 | yes | Bumped it going down, backed off, regrasped, returned to rest. Shaky. |
| 2 | 2026-11-14 | v1 50k | chunk | flat-horizontal | missed | about 2 | no | "Missed on a couple of attempts." |
| 3 | 2026-11-14 | v1 50k | chunk | flat-horizontal | grasp-first | 1 | not recorded | Grabbed right away. |
| 4 | 2026-11-14 | v1 50k | chunk | vertical | missed | 3 | no | |
| 5 | 2026-11-14 | v1 50k | chunk | stacked | grasp-first | 1 | not recorded | |
| 6 | 2026-11-14 | v1 50k | chunk | rotated-12 | missed | 3 | no | Gripper did not rotate to grab; missed next to the block. |
| 7 | 2026-11-14 | v1 50k | chunk | flat-horizontal | missed | about 4 | no | Bumped on the first grab, missed, overshot left twice. |
| 8 | 2026-11-14 | v1 50k | nas10 | not recorded | missed | 0 | no | Barely moved, shook periodically. |
| 9 | 2026-11-14 | v1 50k | te | not recorded | missed | 3 | no | Loop held 30 Hz. Missed left twice, wrist did not roll enough, hovered and shook. |
| 10 | 2026-11-15 | v2 30k | chunk | not recorded | not recorded | not recorded | no | New environment, see below. Failed. |
| 11 | 2026-11-15 | v2 50k | chunk | not recorded | not recorded | not recorded | no | New environment. Failed. |
| 12 | 2026-11-15 | v2 50k | chunk | not recorded | not recorded | not recorded | no | New environment. Failed. Sky cam warm-up raised to 3 s after a connect timeout. |
| 13 | 2026-11-15 | v2 50k | chunk | not recorded | not recorded | not recorded | no | New environment. Failed. |
| 14 | 2026-11-16 | v3 50k | chunk | not recorded | missed | not recorded | no | New environment. Missed to the right. |
| 15 | 2026-11-16 | v3 50k | te | not recorded | grasp-first | 1 | no | New environment. Grabbed it right away, never released, carried it back to rest; let go only when torque went off at the end. Loop held about 30 Hz. |
| 16 | 2026-11-16 | v3 50k | te | not recorded | missed | 3 | no | New environment, bowl moved to the right of the Lego (it was on the left in trial 15). Each attempt several inches too high and a couple of inches to the right, near the bowl. |
| 17 | 2026-11-16 | v3 50k | te | flat-horizontal | missed | 1 | no | Fixed test T1, bowl spot A. Grasped too high. |
| 18 | 2026-11-16 | v3 50k | te | vertical | grasp-first | 1 | yes | Fixed test T2, bowl spot A. Lego flat, long side pointing away from the arm. Perfect run end to end: grasp, place in the bowl, release, back to rest. |
| 19 | 2026-11-16 | v3 50k | te | rotated-12 | missed | 4 | no | Fixed test T3, bowl spot A. First attempt touched the Lego and bumped it to the right; each later attempt landed slightly farther off. |
| 20 | 2026-11-16 | v3 50k | te | flat-horizontal | grasp-first | 1 | yes | Fixed test T4, bowl spot B. Perfect run end to end. |
| 21 | 2026-11-16 | v3 50k | te | vertical | missed | about 3 | no | Fixed test T5, bowl spot B. Two full attempts and a partial third, all too far left and too high. |
| 22 | 2026-11-16 | v3 50k | te | rotated-12 | missed | 3 | no | Fixed test T6, bowl spot B. Height about right. Missed up and to the right by a couple of inches on all 3 attempts. |
| 23 | 2026-11-16 | v3 50k | te | flat-horizontal | grasp-first | 1 | no | Fixed test T7, bowl spot C. Grasped with an unneeded wrist rotation to the right, hesitated finding the bowl, released well above it; the Lego bounced off the bowl. |
| 24 | 2026-11-16 | v3 50k | te | vertical | missed | 3 | no | Fixed test T8, bowl spot C. Good wrist orientation and height; about 2 inches too far up the mat (north) on all 3 attempts. |
| 25 | 2026-11-16 | v3 50k | te | rotated-12 | missed | 3 | no | Fixed test T9, bowl spot C. Wrist did not turn enough. Height good. First 2 attempts 3 to 4 inches up and to the right; the last bumped the Lego. |
| 26 | 2026-11-17 | v4 50k | te | flat-horizontal | missed | 0 | no | Fixed-test T1 setup, bowl spot A. Never left rest. Loop clean at 30 Hz, no errors. Not counted as T1. |
| 27 | 2026-11-17 | v3 50k | te | flat-horizontal | not recorded | not recorded | not recorded | Control for row 26 on the same setup: moved normally. Outcome not recorded. |
| 28 | 2026-11-17 | v4 50k | te | flat-horizontal | missed | 0 | no | Rerun of row 26. Never left rest. |
| 29 | 2026-11-17 | v4 50k | chunk | flat-horizontal | missed | 0 | no | Default chunking. Stayed retracted, barely moved. |

Rows 10 to 13 ran in a new environment: a different location, different lighting, cameras moved, and the arms and bowl moved. Every demonstration was recorded in the original setup, so these runs test generalization. They are not part of the v2 comparison.

## v2 comparison (planned, not run)

Same placements for each checkpoint, about 10 trials each, Lego reset by hand between runs. Keep the checkpoint with more successful grasps; do not pick by training loss.

## v3 fixed test (2026-11-16)

v3 50k with temporal ensembling (`scripts/rollout_v3_50k_temporal_30s.sh`), 9 runs. The bowl goes back to the three spots used for recording blocks A, B and C, with each block's lighting as close as it can be set. Three placements per spot, the two other blocks at the same spots every run, the Lego reset by hand between runs.

| Run | Bowl spot | Placement |
|---|---|---|
| T1 | A | flat-horizontal |
| T2 | A | vertical |
| T3 | A | rotated-12 |
| T4 | B | flat-horizontal |
| T5 | B | vertical |
| T6 | B | rotated-12 |
| T7 | C | flat-horizontal |
| T8 | C | vertical |
| T9 | C | rotated-12 |

Results go in the trials table above as rows 17 to 25.

### Result

2 of 9 in the bowl, 3 of 9 grasped.

| Placement | Grasped | In bowl |
|---|---|---|
| flat-horizontal | 2 of 3 (T4, T7) | 1 of 3 (T4; T7 released high and bounced off) |
| vertical | 1 of 3 (T2) | 1 of 3 |
| rotated-12 | 0 of 3 | 0 of 3 |

| Bowl spot | In bowl |
|---|---|
| A | 1 of 3 |
| B | 1 of 3 |
| C | 0 of 3 (1 grasp) |

How the misses failed (some had more than one):
- Too high: T1, T5.
- Off by 2 to 4 inches on the mat, height right: T3, T6, T8, T9.
- Wrist did not turn enough: T9. Rotated-12 also missed in T3 and T6, and v1 had the same wrist-roll weakness (trial 6).
- After a bump, later attempts drifted farther off (T3).

Read (not verified): v3 does the whole task in this environment sometimes, at every bowl spot but C. Its weakest point is rotated placements, then a position error of a couple of inches. More demonstrations should target rotated placements, with a slow, clear final approach and release. Every fixed-test run used temporal ensembling; default chunking was not compared.

## v4 fixed test (2026-11-17, stopped)

Stopped before T1 counted: v4 never left the rest pose (rows 26, 28 and 29), while v3 moved on the same setup (row 27).
Offline, v4 planned to stay put on 63 of the 125 recorded episode starts. The demos begin with about 3 s of stillness
at rest, and the memoryless policy learned to wait. Details in the README progress log. v5 retrains on the same
episodes with the idle frames trimmed; the fixed test resumes with v5 after `scripts/audit.py --checkpoint` passes.
