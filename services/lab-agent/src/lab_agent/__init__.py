"""lab-agent: tool registry, safety gate, device adapters and the event log.

Nothing else in the lab talks to hardware. The website queues commands; this
process claims them, checks them, runs them, and logs every step.
"""
