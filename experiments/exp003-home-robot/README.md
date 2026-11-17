# exp003: home robot

**Goal:** a small Wi-Fi robot that can talk with a child, drive around a room on carpet and hard
floor without hitting anything, be driven by remote, and later go where it is told by voice,
ending with a vision-language-action (VLA) policy trained on its own driving.

**Status (2026-11-17):** design settled, parts on order (due 2026-11-21 to 23; see
[docs/inventory.md](../../docs/inventory.md)), wheel hub modelled. Waiting on servo measurements
for the first test print. Nothing here runs against hardware yet.

## Design

- **Drive:** two STS3215 12V servos in wheel mode (the lab's spares), 120 mm wheels (PETG hub,
  TPU tire), one 40 to 50 mm swivel caster at the back. Works on carpet and hard floor. About
  0.28 m/s at 12V, measured on the bench before anything else.
- **Compute:** Raspberry Pi 5 on the robot for motors, sensors and the safety gate. The Mac does
  speech-to-text, vision and policy inference over Wi-Fi. Conversation goes through the Claude API.
- **Power:** 12.8V 10Ah LiFePO4 pack (about 128 Wh, ExpertPower, 1.07 kg) with a BMS. Main
  switch and 10A fuse, then an INA226 fuel gauge. Motor rail: e-stop, 12V buck-boost, 5A fuse. Compute rail: 5V 5A buck to
  the Pi. The e-stop cuts motor power only, so the Pi stays up and logs what happened.
  Estimated run time: about 6 h of active play, 8.5 h of chatting, 20 h listening. The 2A
  charger refills it in about 5.5 h; self-docking comes with mapping.
- **Sensing:** three forward ToF sensors in a soft TPU bumper, two bumper switches, two or three
  downward ToF cliff sensors (infrared reflectance sensors mistake dark carpet for a drop), a
  front camera (Logitech C920x), and later a 2D LiDAR.
- **Audio:** reSpeaker XVF3800 mic array on top of the head, small speaker.

## Rules this experiment adds (ADRs to write before the matching phase)

- **The safety gate runs on the robot.** A lab-agent on the Pi is the only path to the motors.
  Losing Wi-Fi means stop.
- **Remote driving goes over a private VPN (Tailscale), not the website.** The web stays
  queue-only (ADR 0003).
- **Voice stays in the house.** Wake word and speech-to-text run locally; only text reaches the
  Claude API, with no name in it. No audio is saved and no transcript is synced (extends ADR 0007).
- **No child in any saved or uploaded frame.** Driving demos for training are recorded with the
  room empty (as exp002, ADR 0010).

## Phases

| # | Phase | Done when |
|---|---|---|
| 0 | Bench: Xbox controller drives two servos in wheel mode with a dead-man button; voice loop on the Mac | Both work for 10 minutes |
| 1 | Chassis printed and assembled, teleop over Wi-Fi | 10 minutes of driving; dead-man and e-stop both stop it |
| 2 | Safety interlocks: bumpers, forward ToF, cliff, speed cap about 0.3 m/s, battery | Stops before a box 20/20; stops at a test edge 10/10 |
| 3 | Voice on the robot with parent controls | 15-minute conversation, no audio leaves the house |
| 4 | Remote driving over Tailscale | Stops within 300 ms when the link drops |
| 5 | Mapping with LiDAR, named places, self-docking | Reaches a named place 9/10 from 3 starts; docks 9/10 |
| 6 | Voice-commanded navigation through the gate | "Go to the couch" works 9/10 |
| 7 | VLA trained on teleop demos with spoken instructions | Beats a scripted baseline on a fixed test |

## Printed parts

See [cad/README.md](cad/README.md). First print: the hub coupon, once
[cad/MEASURING.md](cad/MEASURING.md) is done.

## Progress log

- 2026-11-17: design chosen (two-wheel plus caster for carpet and hard floor, LiFePO4 8Ah).
  Parametric hub and coupon modelled in CadQuery; `servo.toml` holds placeholders until measured.
