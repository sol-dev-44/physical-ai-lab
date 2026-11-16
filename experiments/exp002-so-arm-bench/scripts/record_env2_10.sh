#!/bin/bash
# Records 10 episodes (gain 32) into exp002-bowl-p32 in the new environment, with the C920 overhead cam.
# Run it once per block; change the bowl spot and lighting between blocks. Moves the arm via the leader.
# Cameras after the 2026-11-15 replug: box (overhead C920) = index 1, wrist = index 0.
/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/lerobot-record \
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
