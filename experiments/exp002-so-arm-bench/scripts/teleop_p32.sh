#!/bin/bash
# Teleop: leader drives the follower at gain 32 with the speed cap on. No cameras. MOVES THE ARM.
/opt/homebrew/Caskroom/miniforge/base/envs/lerobot/bin/lerobot-teleoperate \
  --robot.type=so101_follower \
  --robot.port=/dev/tty.usbmodem5B901016941 \
  --robot.id=my_awesome_follower_arm \
  --robot.max_relative_target=5 \
  --robot.position_p_coefficient=32 \
  --teleop.type=so101_leader \
  --teleop.port=/dev/tty.usbmodem5B901009311 \
  --teleop.id=my_awesome_leader_arm
