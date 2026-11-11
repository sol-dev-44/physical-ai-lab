# 0008: Timed actions are played by the device, from one frame

**Context.** The exp000 robot moves only while its IR code repeats, so `robot.forward
{"seconds": 1}` is a hold. The first version re-sent the learned code from the Mac every
0.11 s. On the bench (2026-11-10) that failed two ways:

- Each send to the RM4 Mini is a Wi-Fi round trip of 0.2 to 0.4 s, so 1 s became 2 sends
  and the robot moved in bursts ("two rounds of three surges").
- A learned code is every frame the remote sent while the button was down. One capture
  was 5.9 s long. The gate's 3 s cap bounds the `seconds` argument, not what a single
  packet plays, so one send could have moved the robot for twice the cap.

Learned captures also aren't uniform: the first frame can be glitched, and this remote
sends a few command frames and then a "still held" frame shared by every button.

**Decision.**

- A timed action is one call: `Blaster.hold(code, seconds)` sends a single frame once,
  with the device's repeat count set so it plays for `seconds` (BroadLink: byte 1 of the
  packet; 1 s = 8 frames of 127 ms for this robot). It returns the frames played, which
  the log records, and blocks until the motion should be over.
- The frame comes from `ir.one_frame`: the first frame that repeats in the capture. A
  capture with no repeating frame is refused, never guessed.
- The duration cap stays in the gate. The adapter only encodes; it holds no safety logic.

**Consequences.** Motion is smooth and its length no longer depends on the network or
on how long a button was held while learning. The play time is bounded by frames times
frame length, which is at most one frame longer than requested. The device can't be
stopped mid-hold by the Mac; holds are short (3 s cap) for that reason, and the arms
will need a real stop path before they get anything like this.
