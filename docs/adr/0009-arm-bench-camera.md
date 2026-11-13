# 0009: Arm bench camera frames may show adults, never children

Status: Accepted (approved by owner, 2026-11-12)

**Context.** exp002 is the SO-ARM bench. Imitation learning needs camera frames of the arm and the
workspace, and the operator's hands and body often appear in them during teleop. The rule in AGENTS.md
("nobody in frame") was written for exp001 snapshots, not for the arm bench. ADR 0007 covers children
and is not changed by this ADR.

**Decision.**

- ADR 0007 is unchanged. No child may appear in any saved frame, recording or snapshot, in any experiment.
- exp002 only: recordings may show adults, including the operator, when no child is in view.
- Saved frames stay in gitignored `media/`. They are never committed, synced, posted or published,
  unless a later ADR allows it.
- Live preview is not saved. Nothing is written until the operator starts a recording.
- Before a recording starts, the operator checks the view for children. If one is in view, the recording
  does not start.
- The "nobody in frame" flag stays for exp001 snapshots.

**Consequences.** Arm recordings can be made without staging the operator out of view. The protection for
children is the same, and frames still never leave the lab's machine. This is a narrow exception for one
experiment; any wider change needs its own ADR.
