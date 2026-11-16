# exp002 rollout trials

One row per 30-second rollout. Alan watches every run and reports the outcome; the log only shows timing and clamps.

## Checkpoints

| Name | Run folder (under `/Users/alancampbell/lerobot_outputs/`) | Trained on | Steps |
|---|---|---|---|
| v1 50k | `exp002-bowl-act-50k/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 39 | 50,000 |
| v2 30k | `exp002-bowl-act-50k-v2/checkpoints/030000` | `exp002-bowl-p32` episodes 1 to 64 | 30,000 |
| v2 50k | `exp002-bowl-act-50k-v2/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 64 | 50,000 |
| v3 50k (training) | `exp002-bowl-act-50k-v3/checkpoints/050000` | `exp002-bowl-p32` episodes 1 to 94 (65 to 94 in the new environment, C920 overhead cam) | 50,000 |

## Fixed lists

- Placement of the red Lego: `flat-horizontal`, `vertical`, `rotated-3`, `rotated-6`, `rotated-9`, `rotated-12`, `stacked`, `near-edge`, `near-bowl`, or `not recorded`.
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

Rows 10 to 13 ran in a new environment: a different location, different lighting, cameras moved, and the arms and bowl moved. Every demonstration was recorded in the original setup, so these runs test generalization. They are not part of the v2 comparison.

## v2 comparison (planned, not run)

Same placements for each checkpoint, about 10 trials each, Lego reset by hand between runs. Keep the checkpoint with more successful grasps; do not pick by training loss.
