# exp003: household robot

**Goal:** a small Wi-Fi robot that lives with the family. It knows each family member and the pets,
talks with each of them in a way that suits them, remembers them and the house, keeps to the
household's rules about where it may go and when, and can be driven by remote.

- **v1:** the rolling robot. Drives on carpet and hard floor without hitting anything, converses,
  recognizes people and pets, remembers, follows household rules, goes where it is told by voice,
  and ends with a vision-language-action (VLA) policy trained on its own driving.
- **v2:** adds an arm (or two) to pick up light toys and put them away.

**Status (2026-11-17):** design settled, parts on order (due 2026-11-21 to 23; see
[docs/inventory.md](../../docs/inventory.md)), wheel hub modelled. Waiting on servo measurements
for the first test print. Nothing here runs against hardware yet. Photos and personal data are the
owner's call ([ADR 0013](../../docs/adr/0013-owner-governs-personal-data.md)).

## Design: the body

- **Drive:** two STS3215 12V servos in wheel mode (the lab's spares), 120 mm wheels (PETG hub,
  TPU tire), one 1.5" swivel caster at the back. Works on carpet and hard floor. About 0.28 m/s at
  12V, measured on the bench before anything else.
- **Compute:** Raspberry Pi 5 on the robot for motors, sensors and the safety gate. The Mac does
  speech-to-text, recognition, vision and policy inference over Wi-Fi. Conversation goes through the
  Claude API.
- **Power:** 12.8V 10Ah LiFePO4 pack (about 128 Wh, ExpertPower, 1.07 kg) with a BMS. Main
  switch and 10A fuse, then an INA226 fuel gauge. Motor rail: e-stop, 12V buck-boost, 5A fuse.
  Compute rail: 5V 5A buck to the Pi. The e-stop cuts motor power only, so the Pi stays up and logs
  what happened. Estimated run time: about 6 h of active play, 8.5 h of chatting, 20 h listening.
  The 2A charger refills it in about 5.5 h; self-docking comes with mapping.
- **Sensing:** three forward ToF sensors in a soft TPU bumper, two bumper switches, two or three
  downward ToF cliff sensors (infrared reflectance sensors mistake dark carpet for a drop), a
  front camera (Logitech C920x), and later a 2D LiDAR.
- **Audio:** reSpeaker XVF3800 mic array on top of the head, small speaker.
- **Privacy mode:** a mic mute and a printed camera shutter that the gate can see, and a light that
  shows when the robot is listening.

## Design: who it knows and how it behaves

Recognition and memory run on the lab machine and the robot, and their data is kept in a local
store by default. The Claude API gets the person's name and role and a few relevant memories.
What gets saved, shared or published is the owner's call (ADR 0013); nothing personal goes in
this repo or on the site unless the owner puts it there.

- **Recognition.** Face and voice together, on device, from live frames that are then dropped.
  Pets by species detection plus appearance. Anyone not recognized with confidence is a guest.
  Candidates to compare: Apple Vision or an ArcFace-family model for faces, an ECAPA speaker
  embedding for voices, a YOLO detector for people and pets.
- **Profiles.** Each person has a role (parent, child, guest) and style settings a parent can edit.
  Starting defaults:

| Who | Tone and content | Movement |
|---|---|---|
| Child | Playful, short sentences, patient; asks questions back; age-appropriate topics only; honest that it is a robot; sends worries and big questions to a parent | Slower near the child; never blocks a doorway |
| Parent | Concise and direct; status reports; can ask anything the robot can do | Normal |
| Pet | Calm voice or silent | Keeps about 1 m away, never chases, slows when a pet is near |
| Guest or unknown | Polite and generic; nothing personal about the household | Normal, cautious |

- **Memory.** After an interaction the robot writes short notes about that person: facts ("likes
  dinosaurs"), preferences, one-line summaries of what happened. No transcripts, no audio. Parents
  can review, edit and delete memories on the lab machine; anyone can say "forget that". A child's
  event memories expire after 90 days unless a parent pins them. The robot never repeats one
  person's memories to another, except to parents about a child.
- **Household rules.** Built on the map: named rooms, no-go zones (stairs, bathrooms), zones by time
  (bedrooms at night), quiet hours, and what each role may ask for (a child can call the robot over,
  but can't send it into a no-go zone or change a rule). Rules are enforced by the safety gate as
  interlocks, and changed only by a parent on the lab machine, never by voice alone.

## Design: ready for v2

v2 mounts an SO-101 follower arm on the top deck (the lab's second SO-ARM101 pair is the candidate;
its leader records teleop demos). v1 leaves room for it:

- The top deck carries the SO-101 base bolt pattern and a fused 12V tap for the arm.
- Weight and balance are budgeted for about 1 kg of arm reaching forward. Before v2 starts, a tip
  test with a dummy weight decides whether the two-wheel base needs a wider stance or outriggers.
- The arm only moves light toys (under about 150 g) into a bin, and an interlock stops it whenever a
  person or pet is within reach.
- exp002's lessons apply: trim idle frames, audit data and checkpoints before training.

## Rules this experiment adds

- **The safety gate runs on the robot.** A lab-agent on the Pi is the only path to the motors.
  Losing Wi-Fi means stop. (ADR to write before phase 1.)
- **Remote driving goes over a private VPN (Tailscale), not the website.** The web stays
  queue-only (ADR 0003). (ADR to write before phase 4.)
- **Photos, recordings and personal data are the owner's call** (ADR 0013). Wake word and
  speech-to-text run locally by default.

## Phases

### v1

| # | Phase | Done when |
|---|---|---|
| 0 | Bench: Xbox controller drives two servos in wheel mode with a dead-man button; voice loop on the Mac | Both work for 10 minutes |
| 1 | Chassis printed and assembled, teleop over Wi-Fi | 10 minutes of driving; dead-man and e-stop both stop it |
| 2 | Safety interlocks: bumpers, forward ToF, cliff, speed cap about 0.3 m/s, battery | Stops before a box 20/20; stops at a test edge 10/10 |
| 3 | Voice on the robot: one guest-level personality, parent controls, privacy mode | 15-minute conversation; no audio leaves the house; mute stops listening 10/10 |
| 4 | Remote driving over Tailscale | Stops within 300 ms when the link drops |
| 5 | Mapping with LiDAR, named places, self-docking | Reaches a named place 9/10 from 3 starts; docks 9/10 |
| 6 | Household rules: zones, time zones, quiet hours, as gate interlocks | Refuses to enter a no-go zone 20/20; silent in quiet hours |
| 7 | Recognition of family and pets | Right person or pet in at least 95 of 100 encounters; mistakes one family member for another at most once; strangers treated as guests 20/20 |
| 8 | Per-person behaviour and memory | A parent can tell from transcripts whom the robot was talking to, 9/10; "forget that" works 10/10; never reveals one person's memories to another across 20 probing prompts |
| 9 | Voice-commanded navigation with role permissions | "Go to the couch" works 9/10; a child's request into a no-go zone is refused 10/10 |
| 10 | VLA trained on teleop demos with spoken instructions | Beats a scripted baseline on a fixed test |

### v2

| # | Phase | Done when |
|---|---|---|
| 11 | Arm on the deck, teleop with the leader arm, reach interlock | Tip test passes; arm stops within 0.5 s when a person comes within reach, 10/10 |
| 12 | Tidy-up demos ("put the blocks in the bin") and a trained policy | Policy picks and places a known toy 8/10 from fixed starts |
| 13 | Autonomous tidy-up: find toys on the map, drive, pick, place | Clears 5 scattered toys into the bin in one run, 4/5 runs |

## Printed parts

See [cad/README.md](cad/README.md). First print: the hub coupon, once
[cad/MEASURING.md](cad/MEASURING.md) is done.

## Progress log

- 2026-11-17: design chosen (two-wheel plus caster for carpet and hard floor, LiFePO4 battery).
  Parametric hub and coupon modelled in CadQuery; `servo.toml` holds placeholders until measured.
- 2026-11-17: scope widened to a household robot (recognition, per-person behaviour, memory,
  household rules) with a v2 arm for tidying toys. Privacy rules handed to the owner (ADR 0013,
  superseding 0007 and 0012); folder renamed from `exp003-home-robot`.
