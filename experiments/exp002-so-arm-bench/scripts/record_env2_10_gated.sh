#!/bin/bash
# Records 10 episodes (gain 32) into exp002-bowl-p32 with the motion gate (record_gated.py): still frames before the first move are not saved, and each episode ends itself 1 s after the arm is folded back to rest (30 s is now only the limit).
# Run it once per block; change the bowl spot and lighting between blocks. Moves the arm via the leader.
# Cameras after the 2026-11-15 replug: box (overhead C920) = index 1, wrist = index 0.
/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/python "$(dirname "$0")/record_gated.py" \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5B901016941 \
  --robot.id=my_awesome_follower_arm \
  --robot.max_relative_target=5 \
  --robot.position_p_coefficient=32 \
  --robot.cameras='{"box": {"type": "opencv", "index_or_path": 1, "width": 640, "height": 480, "fps": 30, "warmup_s": 3}, "wrist": {"type": "opencv", "index_or_path": 0, "width": 640, "height": 480, "fps": 30}}' \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5B901009311 \
  --teleop.id=my_awesome_leader_arm \
  --dataset.repo_id=local/exp002-bowl-p32 \
  --dataset.root=/Users/alancampbell/lerobot_data/exp002-bowl-p32 \
  --dataset.single_task="pick up the red lego from the mat and put it in the blue bowl" \
  --dataset.num_episodes=10 \
  --dataset.episode_time_s=30 \
  --dataset.reset_time_s=15 \
  --dataset.push_to_hub=false \
  --resume=true
