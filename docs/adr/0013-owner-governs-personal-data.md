# 0013: The owner governs photos and personal data

Status: Accepted (decided by owner, 2026-11-17). Supersedes [0007](0007-child-privacy.md) and
[0012](0012-household-identity-and-memory.md). Replaces the privacy conditions in
[0010](0010-external-gpu-training.md) and [0011](0011-curated-arm-clips.md).

**Context.** ADRs 0007 and 0009 to 0012 turned privacy into hard rules for agents and code: no child
in any saved frame, nothing identifying in the repo, identity data locked to one store. As the lab
grows into a household robot that has to see, recognize and remember the family, those rules block
ordinary work, and the owner would rather govern photos and personal information by hand.

**Decision.**

- The owner decides, case by case, what photos, recordings and personal information (family
  members' and children's included) are captured, stored, synced, uploaded or published.
  Agents do what the owner asks with them, without extra conditions.
- The owner's standing default: personal information is not published. The repo and the site are
  public, so agents don't add personal information to them on their own initiative.
- What stays from the earlier ADRs: arm policies may train on external GPUs (0010), and curated clips
  may be published on the site under 0011's size limit and listing in `apps/web/public/clips/README.md`.
  Their conditions about people in frame are now the owner's call.
- exp003 keeps household identity data (profiles, face and voice embeddings, memories) in a local
  store by default. That is a design choice, not a rule. The Claude API may receive names and
  memories as text.
- Existing safeguards in code (exp001 drops frames and asks for `--nobody-in-frame` before writing
  one) stay until the owner asks to change them.
- Hardware safety decisions (0003, 0008, the safety gate and interlocks) are unchanged.

**Consequences.** Fewer automatic protections: anything personal that reaches the repo, the site or a
provider is caught by the owner's review, not by a rule. Public pages that cite ADR 0007 (the site
footer, the harness page, the research write-up) describe a practice the owner still follows, but
their references need updating when those pages are next edited.
