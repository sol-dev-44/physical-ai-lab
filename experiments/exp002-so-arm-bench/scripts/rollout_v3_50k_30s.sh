#!/bin/bash
# Runs the v3 50k-step ACT checkpoint (episodes 1 to 94) on the follower arm for 30 seconds. MOVES THE ARM.
/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/lerobot-rollout \
  --strategy.type=base \
  --policy.path=/Users/alancampbell/lerobot_outputs/exp002-bowl-act-50k-v3/checkpoints/050000/pretrained_model \
  --policy.device=mps \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5B901016941 \
  --robot.id=my_awesome_follower_arm \
  --robot.max_relative_target=5 \
  --robot.position_p_coefficient=32 \
  --robot.cameras='{"box": {"type": "opencv", "index_or_path": 1, "width": 640, "height": 480, "fps": 30, "warmup_s": 3}, "wrist": {"type": "opencv", "index_or_path": 0, "width": 640, "height": 480, "fps": 30}}' \
  --task="pick up the red lego from the mat and put it in the blue bowl" \
  --fps=30 \
  --duration=30
