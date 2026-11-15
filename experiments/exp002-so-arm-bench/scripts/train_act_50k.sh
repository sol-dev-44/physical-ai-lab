#!/bin/bash
caffeinate -dimsu /opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/lerobot-train \
  --policy.type=act --policy.device=mps --policy.push_to_hub=false \
  --dataset.repo_id=local/exp002-bowl-p32 \
  --dataset.root=/Users/alancampbell/lerobot_data/exp002-bowl-p32 \
  --dataset.episodes='[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39]' \
  --steps=50000 --batch_size=8 --num_workers=0 --log_freq=200 --save_freq=5000 \
  --output_dir=/Users/alancampbell/lerobot_outputs/exp002-bowl-act-50k \
  --job_name=exp002-bowl-act-50k
