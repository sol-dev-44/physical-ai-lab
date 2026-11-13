# 0010: Arm policies may train on external GPUs

Status: Accepted (approved by owner, 2026-11-13). Supersedes [0009](0009-arm-bench-camera.md).

**Context.** exp002 records camera frames and joint data for imitation learning. Training on the lab
Mac is slow, and a consistent training schedule needs a GPU. ADR 0009 said frames never leave the lab's
machine, which rules out an external GPU. ADR 0007 (no identifiable child data) is unchanged.

**Decision.**

- ADR 0007 is unchanged. No child may appear in any saved or uploaded frame, in any experiment.
- exp002 may show adults, including the operator, as in 0009.
- For exp002 only, recordings and derived files may be uploaded to an external GPU provider for training.
  Each upload must meet all of these:
  - The provider is named in the experiment's notes before the first upload.
  - The transfer is encrypted, and the provider's stored copy is encrypted where the provider supports it.
  - The operator checks every episode for children before upload. If a child is in view, the episode is not uploaded.
  - The provider's copy is deleted after each training run. Trained weights are copied back to the lab.
- Raw frames are never published, posted, committed, or added to the site, and they stay out of git.
  Only derived weights and aggregate numbers may be committed, and only when they are not identifying.
- The provider can be changed only by a new ADR, or by a note in the experiment that meets the conditions above.

**Consequences.** Training can run on a GPU, which makes the schedule consistent. Frames now leave the
lab, which is a larger exposure than 0009, so the conditions above are strict. If a provider's terms
change, or a child appears in any upload, training stops and this ADR is reviewed.
