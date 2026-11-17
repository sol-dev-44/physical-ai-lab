# Data curation for LeRobot imitation-learning datasets (idle frames, demo quality, trimming tooling)

Research date: 2026-11-17. Scope: SO-100/SO-101-class arms with ACT / Diffusion Policy / SmolVLA / pi0 trained in LeRobot (dataset format v3). Bench context: ~125 teleop demos, 30 fps, 30 s episodes, overhead + wrist cameras, single pick-and-place task; an ACT checkpoint froze at rest pose; most demos start with ~3 s of no motion.

## Is the "policy freezes / does not start" failure from idle starting frames documented, and what fixes were used?

### Takeaway
Yes, though mostly in GitHub issue threads and community tool write-ups rather than in papers. LeRobot issue #3429 (Apr 2026) has a user who saw idle episode starts make the arm "stay frozen" at inference. The fixes people reported were trimming idle frames at the start and keeping or debating the ones at the end. A maintainer closed the issue in Oct 2026, saying it "depends on the task" and pointing to an in-progress frame-trim PR. The ACT paper itself names pauses in demonstrations as a confounder that action chunking is meant to absorb. That suggests long, uniform idle prefixes are exactly the case where chunking helps least (inference, see below).

### Cited Findings
- LeRobot issue #3429 "How to filter static frames without action in a episode?" was opened 2026-04-22. It asks whether idle (static) frames at the start and end of real-robot episodes should be filtered. It was closed as completed on 2026-10-21. — [lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)
- In the same thread (2026-04-30), user Martina129 suggested keeping idle frames at the end, since they help the model settle at the final pose, and dropping them at the start. They reported that idle starts made the arm stay frozen too long during real-time inference. — [lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)
- Maintainer pkooij (2026-10-21) said whether to trim idle frames depends on the task. Frame-range trimming is being developed in PR #4939. — [lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)
- LeRobot issue #2213 "Poor ACT Policy Performance After Training (Robot Not Moving or Grasping Properly)" was opened 2025-10-16. Setup: SO-101 follower and leader, ACT, 49 episodes / ~39k frames, two 1080p cameras, 100k steps, `batch_size 1`, `chunk_size 50`, `n_action_steps 50`, `use_vae=false`. Symptom: the robot "stayed static or moved unpredictably." — [lerobot #2213](https://github.com/huggingface/lerobot/issues/2213)
  - A commenter (2026-05-08) suggested static or idle frames may bias the policy toward zero actions. They recommended their own `lerobot-doctor trim` / `score` tools. — [lerobot #2213](https://github.com/huggingface/lerobot/issues/2213)
  - Maintainer NikodemBartnik (2026-10-29) named the root causes as `--batch_size 1` and `use_vae=false`. He recommended batch size 8 or more, keeping the VAE, and starting from the default ACT config. — [lerobot #2213](https://github.com/huggingface/lerobot/issues/2213)
  - Another commenter (2026-04-05) suggested batch at least 8, 480x480 images, `chunk_size=20`, `n_action_steps=10`, and re-enabling the VAE. These are their opinions and were not verified in the thread. — [lerobot #2213](https://github.com/huggingface/lerobot/issues/2213)
- The ACT paper (Zhao, Kumar, Levine, Finn; arXiv 2304.13705, Apr 2023) says: "Predicting action sequences also helps tackle temporally correlated confounders, such as pauses in demonstrations that are hard to model with Markovian single-step policies." Sec. IV-A: "a single-step policy would struggle with temporally correlated confounders, such as pauses in the middle of a demonstration." Sec. V-C also notes a failure mode where "the robot can pause indefinitely for certain states." — [ACT paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2304.13705)
- ACT's original data: teleoperation and recording at 50 Hz. "Each episode takes 8-14 seconds", i.e. 400-700 steps. Chunk size listed as 100. Temporal ensembling uses weights w_i = exp(-m*i). — [ACT paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2304.13705)
- A Hugging Face community blog (RobotData, "Garbage In, Garbage Out", 2025-10-26) states that "Filtering idle intervals improves performance in openpi." It also notes that some idle time is intentional and repeated, such as letting inertia settle. — [HF blog: GIGO](https://huggingface.co/blog/robotdata/gigo)
- SCIZOR (arXiv 2505.22626; ICRA 2026) is a self-supervised curation method. The dominant suboptimal behaviours its classifier flags are "Pause", "Slow Motion" and "Manipulation Failure". Removing them gave an average 15.4% improvement across IL benchmarks. — [SCIZOR arXiv](https://arxiv.org/html/2505.22626v2); [UT RPL page](https://rpl.cs.utexas.edu/publications/2026/06/01/zhang-icra26-scizor/)
- Voxel51's LeRobot curation write-up (2026-10-08) cites OpenVLA removing all-zero no-op actions, and SCIZOR removing pauses, as precedent for treating dead frames as removable. — [Voxel51 blog](https://voxel51.com/blog/lerobot-dataset-curation-metrics)

### Inferences
- In this bench's data, the first ~90 frames (3 s at 30 fps) at rest pose all have nearly identical observations: same arm pose, same object on the mat. Their action targets, however, differ only by "time until motion starts". A memoryless policy, even a chunked one, cannot tell which of those 90 frames it is in. Under L1 regression it learns something near the average: mostly "stay", with a smeared, delayed onset. When the robot then re-observes the same rest scene, the loop repeats. That is a self-reinforcing fixed point. This matches the #3429 report and the "zero-action bias" comment in #2213.
- Action chunking with k = 100 at 30 fps covers ~3.3 s, so a 3 s idle prefix is almost a full chunk of "stay". ACT's argument about pauses assumes pauses are short relative to the chunk. A pause as long as the chunk defeats it.
- The #2213 maintainer diagnosis (batch 1, no VAE) is a separate, confounding cause of "robot doesn't move". Rule it out (check the training config) before attributing a freeze solely to idle frames.

### Gaps
- I found no LeRobot Discord summary or HF forum thread with a controlled before/after (same data, trimmed vs untrimmed) success-rate number for this failure.
- I did not find a paper that specifically studies idle prefixes (as opposed to mid-episode pauses) and freezing in chunked policies.
- The claim "filtering idle intervals improves performance in openpi" in the GIGO blog is stated without numbers. I did not trace its primary source.

## Methods and thresholds for trimming idle/static frames (start, end, mid-episode pauses)

### Takeaway
Practitioners detect idle frames from joint-space velocity, |q[t] - q[t-1]|/dt, or from action deltas. They threshold it with a debounce (several consecutive frames) and keep a short pad, about 0.25 s, before the first sustained motion. Absolute thresholds vary: the GIGO blog uses 0.1 on joint velocity. Better tools use per-joint or per-episode relative scales so slow operators aren't flagged. Mid-episode pauses are usually kept inside the trim window but can be dropped per frame at sampling time.

### Cited Findings
- **Daft `daft_physical_ai.trim` (motion trimming example):**
  - Uses `observation.state.joint_position` only, with no video decoding.
  - `motion_energy` = per-joint change since the previous frame, divided by that joint's typical step (`motion_scale`), combined into one value.
  - `is_active` requires 3 consecutive frames above threshold. The plotted threshold line is at 0.1, though the value isn't stated explicitly.
  - Pads 0.25 s before the first and after the last sustained motion.
  - Mid-episode pauses are kept inside the window but dropped in the per-frame `is_active` view.
  - Episodes with no motion are flagged `never_active` and kept whole.
  - On one DROID data file (321,344 frames): the window view dropped 4.0% of frames, the per-frame view dropped 11.2%.
  - Output: per-frame `is_active` plus per-episode `start_frame`, `end_frame`, `start_ts`, `end_ts`, `kept_frames`, `trim_fraction`, `never_active`.
  - Source: [Daft docs](https://docs.daft.ai/en/stable/examples/motion-trimming-physical-ai/)
- **HF GIGO blog:**
  - Idle score = 1 - fraction of steps where joint-velocity magnitude sqrt(sum (dq/dt)^2) is below a threshold, default 0.1.
  - In its corruption experiments, idle corruption was 0.5-1.0 s injected pauses with zeroed joint velocity.
  - Source: [HF blog: GIGO](https://huggingface.co/blog/robotdata/gigo)
- **Voxel51 curation tool:**
  - Idleness is judged relative to a multiple of each episode's own moving speed, "so a slow, careful operator isn't flagged just for being slow". The multiple isn't given.
  - Scored metrics: `idle_lead_s` and `longest_pause_s` at full weight. `idle_trail_s` and `end_motion_ratio` at half weight, because fixed-duration recording produces a timer-driven dead tail.
  - `idle_frac` is reported but never scored.
  - It proposes `keep_from_s` / `keep_to_s` windows but never writes them back.
  - A pause before a regrasp is treated as recovery and not penalized.
  - Source: [Voxel51 blog](https://voxel51.com/blog/lerobot-dataset-curation-metrics)
- **`lerobot-doctor` (per its author's own comments in LeRobot issues):**
  - `--checks actions,anomalies` flags "frozen actions" (the same value for >80% of timesteps), stuck actuators, zero-variance features and near-duplicate episodes.
  - A `trim` command (with `--dry-run`) detects static frames by an action-change threshold. The numeric value isn't stated. It trims start and end idle, optionally removes fully static episodes, and re-indexes metadata.
  - Source: [lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)
  - Caveat: a search found no independent page for this tool. Treat it as unverified third-party code.
- **SCIZOR** removes low-progress frames with a learned progress estimator (temporal-distance classification, no reward needed) and deduplicates on joint state-action representations. A review notes its curation thresholds were chosen empirically. — [SCIZOR arXiv](https://arxiv.org/html/2505.22626v2)
- **PR #3096** ("trim_episode_start", 2026-03-06, closed unmerged) offered only a fixed-seconds trim (`--operation.seconds 3.0`) with no motion detection. — [lerobot PR #3096](https://github.com/huggingface/lerobot/pull/3096)

### Inferences
- For an SO-101 at 30 fps, a practical recipe follows from the sources:
  1. Compute per-joint |action[t] - action[t-1]|. Using action (leader) rather than state avoids follower servo jitter.
  2. Normalize each joint by its median moving step.
  3. Mark a frame active when the normalized max exceeds ~0.1 for 3 or more consecutive frames.
  4. Cut everything before (first active frame - ~8 frames, about 0.25 s at 30 fps).
  
  The 0.1 / 3-frame / 0.25 s values come from Daft and GIGO defaults and should be tuned by plotting a few episodes.
- Keeping a short lead-in (a few frames at rest) still shows the policy "rest pose -> move", without hundreds of contradictory "rest -> stay" labels.
- For ACT with chunk_size 100, any idle prefix much shorter than the chunk (for example <0.5 s) should be benign, consistent with ACT's own pause argument.
- Mid-episode pauses that are genuine (hesitation, regrasp setup) are better kept or handled per frame (sampler mask) than cut. Cutting creates discontinuities in the video and state timeline that the chunk targets span.

### Gaps
- No source gives empirically validated thresholds specific to SO-101 servo noise. The values above come from other arms and datasets (DROID, generic LeRobot).
- I found no study measuring how lead-in length (0 vs 0.25 vs 1 s) affects ACT or Diffusion Policy start-up behaviour.

## Keep or cut end-of-episode "return to rest" and trailing idle?

### Takeaway
Opinions differ and no controlled study was found. Community practice leans toward cutting idle at the start and keeping some at the end, so the policy learns to settle. Tools down-weight trailing idle because fixed-length timers create it artificially. The maintainer position is "depends on the task".

### Cited Findings
- A user in #3429 recommends keeping end idle frames because they help the model settle at the final pose, and dropping start idle. — [lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)
- The maintainer response was that trimming "depends on the task". — [lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)
- Voxel51 scores trailing idle at half weight, because fixed-duration recording creates a dead tail from the timer itself. It separately flags episodes ending mid-motion (`end_motion_ratio`). — [Voxel51 blog](https://voxel51.com/blog/lerobot-dataset-curation-metrics)
- The GIGO blog notes that some idle time is intentional and repeated, such as settling inertia, and should be handled differently from distraction. — [HF blog: GIGO](https://huggingface.co/blog/robotdata/gigo)
- LeRobot's `lerobot-record` defaults to `--dataset.episode_time_s=60`. The right arrow / `n` key ends an episode early. This is the standard way to avoid a long timer-driven tail. — [LeRobot docs: il_robots](https://huggingface.co/docs/lerobot/il_robots)

### Inferences
- With fixed 30 s episodes on a task that probably takes ~8-12 s, the tail is likely mostly idle. Keeping ~0.5-1 s of settled rest after the drop (or after return-to-rest) gives a clear "done" state. Keeping 15+ s of tail over-weights the "stay" action in the dataset, which is the same fixed-point risk as at the start, but in the done state where it is desirable.
- If return-to-rest is kept consistently in every demo, the policy learns a terminal behaviour, and rollouts end at rest rather than hovering over the bowl. Inconsistent inclusion (some demos return, some stop over the bowl) produces multimodal end behaviour.
- A rest-pose end state that looks like the start state, with the object gone from the mat, is disambiguated only by the cameras. If the rest pose looks identical at start and end, the policy must rely on seeing the Lego in the bowl versus on the mat.

### Gaps
- I found no paper or controlled experiment on keeping versus cutting return-to-rest for ACT, Diffusion Policy or SmolVLA.
- I found nothing on whether trailing idle affects pi0 / SmolVLA "termination" behaviour.

## Automatic demo-quality filtering (success labels, duration outliers, smoothness/jerk, failed grasps, demo-scoring papers)

### Takeaway
There are two tiers:
1. **Cheap heuristics** that work on a hobby bench: duration robust-z, idle lead and pause, SPARC/LDLJ smoothness, acceleration spikes, gripper chatter, missed grasps, camera blur and darkness, and |action - next_state| saturation.
2. **Learned scorers** that are heavier: DemInf (mutual information, RSS 2025), CUPID (influence functions on closed-loop return, CoRL 2025), SCIZOR (progress plus dedup, ICRA 2026).

Recent papers (2026) argue that smoothness metrics like spectral arc length give much of the benefit at sub-second cost. Tool authors recommend using scores to order a human review queue rather than auto-deleting episodes.

### Cited Findings
- **Belkhale, Cui, Sadigh, "Data Quality in Imitation Learning"** (arXiv 2306.02437, Jun 2023) frames quality via distribution shift with two properties: action divergence (expert versus policy actions at a state) and transition diversity. It states "state diversity is not always beneficial". — [arXiv 2306.02437](https://arxiv.org/abs/2306.02437)
- **DemInf: Hejna et al., "Robot Data Curation with Mutual Information Estimators"** (arXiv 2502.08623, RSS 2025):
  - Scores each demo's contribution to state-action mutual information using k-NN MI estimators over VAE embeddings.
  - Partitions demos by quality consistent with human expert scores.
  - Gives a 5-10% improvement on RoboMimic and better real ALOHA and Franka results.
  - Source: [arXiv 2502.08623](https://arxiv.org/abs/2502.08623)
  - A secondary search summary says DemInf assumes all demos complete the task and works best with relative actions. I did not verify this against the paper. — [search summary of arXiv html](https://arxiv.org/html/2502.08623)
- **CUPID: Agia et al.** (arXiv 2506.19121, CoRL 2025):
  - Uses influence functions to estimate each demo's effect on the policy's expected return from evaluation rollouts.
  - Supports both filtering harmful demos and selecting new ones.
  - Training on less than 33% of curated data gives state-of-the-art diffusion policies on RoboMimic. Hardware gains are similar.
  - It can surface spurious correlations and robust strategies.
  - It requires policy rollouts and influence computations.
  - Source: [arXiv 2506.19121](https://arxiv.org/abs/2506.19121)
  - A search summary reports CUPID's observation that higher demo "quality" (as DemInf measures it) does not always mean higher policy success. — [CUPID pdf](https://arxiv.org/pdf/2506.19121)
- **Kulkarni, Dhar, Cui, "Learning from the Best: Smoothness-Driven Metrics for Data Quality in Imitation Learning"** (arXiv 2604.23000, Apr 2026, UCLA):
  - Spectral Arc Length (SAL) on the speed signal, plus Trajectory-Envelope Distance (TED), a Bézier envelope with contact segmentation and normalized DTW.
  - "Sub-second time per demonstration". SAL is O(T log T).
  - Retention ratios in its experiments ranged from 1/6 to 3/4 of demos, for example a real Pick & Place keeping 40 of 80.
  - Robot: xArm 7.
  - No head-to-head with DemInf or CUPID.
  - Source: [arXiv 2604.23000](https://arxiv.org/html/2604.23000)
- **"An Efficient Metric for Data Quality Measurement in Imitation Learning"** (arXiv 2605.01544, May 2026) exists in search results, but I did not read it. — [arXiv 2605.01544](https://arxiv.org/html/2605.01544v1)
- **SCIZOR** (ICRA 2026): suboptimal-transition removal (pause, slow motion, manipulation failure) plus state-action dedup, with an average +15.4% across benchmarks. It was applied to Open-X (more than 1M trajectories). — [SCIZOR arXiv](https://arxiv.org/html/2505.22626v2)
- **Voxel51 LeRobot curation metrics** (2026-10-08), thresholds "calibrated on a 102-episode development set":
  - Duration: `length_z` robust z within task group, warn at |z| >= 2, needs 20 or more episodes per group.
  - Smoothness: `sparc` is primary. `ldlj` gets half weight. `jerk_rms` is review only. Low-pass at min(10 Hz, 0.4*fps), which is 10 Hz at 30 fps.
  - Gripper: `gripper_flips_per_s` with hysteresis. `recovery_count` is never penalized.
  - Failed grasps: `missed_grasp_frac` = close commands where the gripper fully closes with no stall residual (heuristic, opt-in).
  - Tracking: `track_resid`, `accel_spike_frac`, `joint_limit_frac`.
  - Consistency: `action_divergence`.
  - Camera: blur, exposure, frozen feed, video-action lag.
  - Correlated metrics vote as one group. The episode score is the max group value.
  - It recommends scores to order review, not to auto-drop, and recommends A/B training on full versus curated sets.
  - Source: [Voxel51 blog](https://voxel51.com/blog/lerobot-dataset-curation-metrics)
- **HF GIGO blog** (2025-10-26):
  - Collision: a joint acceleration spike above 15x its median absolute acceleration.
  - Path efficiency: straight-line joint distance / path length.
  - Actuator saturation: |action - next state| > 7 degrees on any joint, score exp(-4 * ratio).
  - Darkness: mean grayscale below 50/255.
  - Blur: Laplacian variance.
  - All on 10 sampled frames per episode.
  - Corrupting 20% of episodes worsened training loss by ~30%. ACT on corrupted data needed significantly more steps to reach the same loss.
  - Source: [HF blog: GIGO](https://huggingface.co/blog/robotdata/gigo)
- **Other community tools** surfaced in search but were not inspected: `robot-data-diff` (per-episode idle ratios, action spikes), `lerobot-quality-gates` (PyPI), Calibra v0.7.1 (HF forum), and `alej96/quality-scoring-robot-learning` (has a `check_idle`). — [robot-data-diff](https://discourse.openrobotics.org/t/robot-data-diff-episode-aware-diffs-for-lerobot-datasets/58956); [lerobot-quality-gates](https://pypi.org/project/lerobot-quality-gates/); [Calibra](https://discuss.huggingface.co/t/calibra-v0-7-1-dataset-integrity-for-robot-learning/178376); [quality-scoring-robot-learning PR](https://github.com/alej96/quality-scoring-robot-learning/pull/29)
- **LeRobot recording tips:** at least 50 episodes, 10 per location, fixed cameras, consistent grasping behaviour, and add variation slowly. — [LeRobot docs: il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **LeRobot cadence reporting:** `lerobot-record` now reports achieved Hz per episode. A session that ran at 25 Hz still produces a dataset that claims 30 Hz, because timestamps derive from frame index. Check this before training. It is a data-quality issue that silently changes speed. — [LeRobot docs: il_robots](https://huggingface.co/docs/lerobot/il_robots)

### Inferences
- For ~125 single-task demos, the highest-value automatic filters are:
  1. Success label: record it, or detect the Lego in the bowl from the last overhead frame. Numbers only, consistent with the repo's camera policy.
  2. Duration robust-z, after trimming idle.
  3. `idle_lead_s` / `longest_pause_s`.
  4. Gripper close events: a missed grasp shows as full closure with no load, or as multiple regrasps.
  5. Cadence (achieved Hz) per episode.
  6. SPARC on joint speed.
  
  DemInf and CUPID are likely overkill at this scale. CUPID also needs an already-working policy plus rollouts, but it is the one method that directly targets closed-loop success.
- A demo that succeeds but has a regrasp is often worth keeping, since it teaches recovery. Voxel51 and SCIZOR disagree in spirit here: SCIZOR removes "manipulation failure" segments, while Voxel51 never penalizes recoveries.

### Gaps
- I did not verify DemInf's success-only assumption or its action-representation note against the paper text.
- I found no curation study run on SO-100/SO-101 or Koch hardware specifically.
- The ALOHA 2, Mobile ALOHA and UMI papers' data-processing sections were not reached within the tool-call budget. In particular, UMI is known to filter demos by SLAM validity and latency alignment, but that is unverified here.

## Tooling: can LeRobot trim frames within episodes (v3 format)? How do people do it? Record-time controls?

### Takeaway
As of 2026-11-17, there is no merged upstream "trim frames within an episode" operation in `lerobot-edit-dataset`.
- Two earlier PRs (#3024 by timestamp window, #3096 by fixed N seconds from the start) were closed unmerged on 2026-10-21.
- The work was consolidated into PR #4939 ("trim frames within episodes using stream copy", opened 2026-10-12), which was still open after its base PR #4498 was merged into main on 2026-11-03.

In the meantime, people use third-party editors that adjust v3 timestamp windows and drop parquet rows, or mask frames at training time. At record time, LeRobot offers keyboard controls only (right arrow / `n` to end early, left arrow / `r` to re-record, ESC / `q` to stop). I found no built-in motion-triggered start or foot-pedal support.

### Cited Findings
- **PR #4939** (nepyope, opened 2026-10-12, open/unmerged):
  - Adds `trim_episodes` to the Python API and `lerobot-edit-dataset`.
  - Ranges are episode-local, half-open, sorted and validated, for example `{0: [(10, 30), (40, 50)]}`.
  - Writes a new dataset and refuses existing output dirs.
  - Videos are stream-copied (remuxed, no re-encode) when cuts are GOP-aligned. Otherwise they fall back to re-encoding with the source encoder settings.
  - Stats are recomputed, with visual stats from sampled decoded frames. Episode metadata and tasks are updated.
  - It does not do automatic idle detection: ranges must be explicit.
  - Stacked on PR #4498 (delete-episodes stream copy), merged to main 2026-11-03.
  - Source: [lerobot PR #4939](https://github.com/huggingface/lerobot/pull/4939)
- **PR #3096** (pkooij, opened 2026-03-06, closed unmerged 2026-10-21):
  - `--operation.type trim_episode_start --operation.seconds 3.0`.
  - Logical trim: updates per-episode video timestamps in metadata and does "not re-encode/cut MP4 files", so file size doesn't shrink.
  - Skips too-short episodes.
  - A review found blocking bugs: a missing import of `compute_episode_stats`, a wrong `get_output_path()` arity, and image/video stats not recomputed.
  - Source: [lerobot PR #3096](https://github.com/huggingface/lerobot/pull/3096)
- **PR #3024** (nepyope, opened 2026-02-25, closed unmerged 2026-10-21):
  - `trim_episode` with `episode_index` + `start_timestamp`/`end_timestamp`, or an `episode_trims` map.
  - The reviewer noted that the ffmpeg trim helper was never called, so videos were copied whole, and that `stats.json` was not recomputed.
  - Source: [lerobot PR #3024](https://github.com/huggingface/lerobot/pull/3024)
- **Issue #2326** "Develop LeRobotDataset tools" listed delete, split, merge and feature modification as the dataset_tools operations, with trimming as a future addition. Seeed's guide shows `lerobot-edit-dataset --operation.type delete_episodes`. — [lerobot #2326](https://github.com/huggingface/lerobot/issues/2326); [Seeed wiki](https://wiki.seeedstudio.com/lerobot_dataset_tool/)
- **Third-party editors:**
  - `krohling/lerobot-dataset-editor` has `trim-frames -e <episode> -f start-end`.
  - `acrosson/lerobot-dataset-editor` targets v3.0, where an episode is a row range in a shared parquet plus a timestamp window in a shared video file. It trims by adjusting timestamps and removing rows, and needs at least 2 frames per episode.
  - Source: search summary of [krohling/lerobot-dataset-editor](https://github.com/krohling/lerobot-dataset-editor) and [acrosson/lerobot-dataset-editor](https://github.com/acrosson/lerobot-dataset-editor). I did not open the repos.
- **Daft** outputs a per-frame `is_active` flag "for training that samples frames", plus per-episode windows with `from_ts` for video seeking. This is the training-time-mask approach as opposed to rewriting the dataset. — [Daft docs](https://docs.daft.ai/en/stable/examples/motion-trimming-physical-ai/)
- **`lerobot-record` controls (current docs):**
  - Right arrow or `n` ends the episode or reset early. Left arrow or `r` re-records. ESC or `q` stops, encodes and uploads.
  - When no global key backend is available (Wayland, headless, or macOS without Accessibility permission), it falls back to reading keys from the focused terminal.
  - Flags: `--dataset.episode_time_s` (default 60), `--dataset.reset_time_s` (default 60), `--dataset.num_episodes` (default 50).
  - Source: [LeRobot docs: il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **The `record_loop` API** checks an `events` dict each step (`exit_early`, `rerecord_episode`, `stop_recording`), and the docs show a custom Python recording script built on `init_keyboard_listener()` and `record_loop`. — [LeRobot docs: il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **`lerobot-rollout --strategy.type=highlight`** records into a ring buffer and saves on a keystroke. This is a rollout-side analogue of "keep only the interesting part". — [LeRobot docs: il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **Foot pedals:** none built into LeRobot was found.
  - A DAgger project on LeRobot (RECAP) uses an iKKEGOL foot pedal for phase switching, while episodes are still driven by keyboard. — [RECAP stage 0](https://destiny000621.github.io/RECAP/stage0_collection.html)
  - TRI's `raiden` tool (not LeRobot) uses a foot pedal to start and stop episodes. — [tri-ml raiden recording guide](https://tri-ml.github.io/raiden/guide/recording)

### Inferences
- The cleanest real-time fix on this bench is to start motion immediately at episode start and press right arrow (or `n`) when done. Equivalently, shorten `episode_time_s` to about the task duration and lengthen `reset_time_s`.
- Motion-triggered recording can be done with a small custom `record_loop` wrapper: buffer frames until leader-arm action delta exceeds a threshold, then begin `dataset.add_frame` with a ~0.25 s pre-roll from the buffer. That would be custom code. Nothing upstream implements it (inference from the documented `events`/`record_loop` API).
- Until #4939 merges, there are three options for the existing 125 episodes:
  1. A third-party v3 editor that rewrites the from/to timestamps and parquet rows.
  2. A training-time frame mask. For example, filter by frame index with a custom sampler or `EpisodeAwareSampler`-style wrapper so ACT never samples idle-prefix frames as chunk starts. The chunk targets can still extend into kept frames.
  3. Checking out #4939's branch.
  
  Option 2 avoids touching videos. Note that ACT pads chunk targets past episode end, so masking at the end needs care.

### Gaps
- I could not confirm whether #4939's CLI flags are final, or when it will ship in a LeRobot release.
- I did not verify that `EpisodeAwareSampler` in current LeRobot supports per-frame masks (as opposed to `drop_n_first_frames` / `drop_n_last_frames`). The latter, if present, would be a direct training-time trim knob. Worth checking `lerobot/datasets/sampler.py` locally.
- I found no first-party LeRobot docs on motion-triggered recording or pedal input.

