# 0003: The website never touches hardware

**Context.** The admin area should be able to trigger cheap experiments. The site
runs on Vercel; the devices are on the home LAN. Exposing the LAN, or letting a
web process drive hardware, makes a website bug a physical safety problem.

**Decision.** The web inserts a row into `commands`. The lab-agent at home opens
an outbound connection, claims it with `claim_next_command` (service role only),
runs the safety gate, executes, and logs every step. No inbound ports.

- Commands older than 60 seconds expire instead of running.
- Website commands are `remote`: manual-only tools (heat sources) are always denied.
- Confirmation is re-checked by the agent; the web's checkbox is advisory.
- A `STOP` file next to the agent denies everything.

**Consequences.** A compromised or broken website can at worst queue a command
that the gate then judges. Latency is one poll interval (about 2 s); Realtime can
replace polling later without changing the interface.
