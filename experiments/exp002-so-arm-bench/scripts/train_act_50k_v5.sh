#!/bin/bash
# Retrain ACT from scratch on exp002-bowl-p32-trimmed episodes 1 to 124 (episode 0 excluded, as in v4).
# Same demos as v4, with the idle frames cut from each episode's start and end by trim_idle.py
# (v4 learned to wait at rest from about 3 s of stillness at every episode start, 2026-11-17).
# One change from v4 only (the trim), so a v4/v5 difference has one cause. Image augmentation
# (--dataset.image_transforms.enable=true, smoke-tested) is the candidate for v6.
# 50k steps at batch 8 on 68k frames is about 5.9 epochs (LeRobot's guide: 5 to 10), against v4's 3.7.
# The 30k checkpoint (about 3.5 epochs) is the epoch-matched comparison with v4.
# The data audit must pass first; the script stops if it fails. 50k steps, checkpoints every 5k.
set -euo pipefail
PY=/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/python
DATA=/Users/alancampbell/lerobot_data/exp002-bowl-p32-trimmed
"$PY" "$(dirname "$0")/audit.py" --data "$DATA" --episodes 1-124
caffeinate -dimsu /opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/lerobot-train \
  --policy.type=act --policy.device=mps --policy.push_to_hub=false \
  --dataset.repo_id=local/exp002-bowl-p32-trimmed \
  --dataset.root="$DATA" \
  --dataset.episodes='[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124]' \
  --steps=50000 --batch_size=8 --num_workers=0 --log_freq=200 --save_freq=5000 \
  --output_dir=/Users/alancampbell/lerobot_outputs/exp002-bowl-act-50k-v5 \
  --job_name=exp002-bowl-act-50k-v5
