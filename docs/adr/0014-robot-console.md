# 0014: The robot console on the home network

**Context.** The household robot (exp003) needs a control app: hold-to-drive from a phone,
live sensors, a live camera view for debugging. ADR 0003 keeps the website away from hardware
and forbids inbound ports for that path. Live driving cannot wait for a 2 s queue poll.

**Decision.**

- The lab agent on the robot serves a "robot console": a web app plus one WebSocket per browser,
  on the home network only. No port forwarding, no tunnel; remote driving (phase 4) needs its
  own decision.
- Access needs a pairing token printed when the console starts. The browser sends it in its
  first WebSocket message; anything else is closed.
- The console is a client of the runner like the CLI and the queue worker: every command goes
  through `Runner.request` and the safety gate and is logged.
- Driving is a lease: a drive command is good for 300 ms and heartbeats renew it. A
  `drive_lease` interlock refuses drive commands without a live lease, and a watchdog stops the
  wheels when it lapses.
- Tools tagged `halt` (stopping the wheels) skip every gate rule except argument validation, so a
  valid stop is never refused. Their arguments are still validated and the call is still logged.
- The live camera view is allowed on the home network for debugging. Frames stay in memory and
  are never written, synced or posted (ADR 0007).

**Consequences.** The robot opens a port on the LAN; anyone on the home Wi-Fi with the token can
drive it within the gate's limits. A crash of the agent stops its watchdog too, so until the
servo's own behaviour on lost communication is known, drive only with someone at the e-stop.
If the event log cannot be written, no stop can reach the wheels through the runner (every
command is logged first), so the wheel driver needs its own hardware timeout before real wheels
are connected (step 2).
