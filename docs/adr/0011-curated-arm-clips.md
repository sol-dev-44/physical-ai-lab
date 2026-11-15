# 0011: Curated arm clips may be published on the site

Status: Accepted (approved by owner, 2026-11-15). Amends [0010](0010-external-gpu-training.md) for curated clips only.

**Context.** The site is becoming the lab's portfolio and the companion to its research write-up. A few
seconds of the arm picking up a block explain exp002 better than any table. ADR 0010 says raw frames
are never published or added to the site, which rules that out. ADR 0007 (no identifiable child data)
is unchanged.

**Decision.**

- ADR 0007 is unchanged. No child may appear in any published clip, still or caption, ever.
- Short clips of arm experiments may be published on the site when every condition below holds:
  - The operator picks each clip by hand and watches every frame before it is added.
  - The frame shows the arm, the workspace and at most the operator's hands and forearms. No faces,
    no other people, and nothing that identifies the home (windows, screens, documents, mail).
  - Audio is removed.
  - A clip is at most 20 seconds and 5 MB, and is a re-encoded export, never a dataset episode file.
  - The clip lives in `apps/web/public/clips/` and is listed in `apps/web/public/clips/README.md`
    with its source (episode or rollout), date and the reviewer's check.
- Everything else in ADR 0010 stands: datasets, raw episodes and other frames are never published,
  posted or committed.
- A clip is removed from the site and git history is not relied on to hide it: if a clip turns out to
  break a rule, it is deleted, and the repo owner decides whether history needs rewriting.

**Consequences.** The site can show what the arm actually does. The review step is manual and has to be
done every time; there is no automatic publishing path from recordings to the site. Clips add a little
weight to the repo, which the size cap keeps small.
