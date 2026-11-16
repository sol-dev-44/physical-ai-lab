#!/bin/bash
# Retrain ACT from scratch on exp002-bowl-p32 episodes 1 to 94 (episode 0 excluded): original setup plus 30 new-environment episodes (65 to 94, C920 overhead cam). 50k steps, checkpoints every 5k.
caffeinate -dimsu /opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/lerobot-train \
  --policy.type=act --policy.device=mps --policy.push_to_hub=false \
  --dataset.repo_id=local/exp002-bowl-p32 \
  --dataset.root=/Users/alancampbell/lerobot_data/exp002-bowl-p32 \
  --dataset.episodes='[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94]' \
  --steps=50000 --batch_size=8 --num_workers=0 --log_freq=200 --save_freq=5000 \
  --output_dir=/Users/alancampbell/lerobot_outputs/exp002-bowl-act-50k-v3 \
  --job_name=exp002-bowl-act-50k-v3
