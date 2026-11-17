# Demonstration collection protocol for SO-100/SO-101 imitation learning (ACT, Diffusion Policy, SmolVLA, pi0)

Researched 2026-11-17. Bench context: SO-101 follower plus leader, about 125 demos at 30 fps, 30 s episodes, overhead C920 plus wrist cam, red Lego to blue bowl with distractors. The setup moved rooms and the old policy failed (covariate shift). 30 varied demos partly fixed it. Rotated placements fail most (wrist roll), and grasps miss by 2-4 in.

## How many demos do ACT / SmolVLA / Diffusion Policy need for single-task pick-and-place on SO-100-class arms?

### Takeaway
The standard number is 50 demos for one task: 10 at each of 5 positions. With that, ACT reaches about 70% in-distribution on SO-100/SO-101 pick-place, and pretrained SmolVLA reaches 75-90%. Out-of-distribution success drops to 40-50%. Past roughly 50 demos per setting, adding diversity (new environments, objects, poses) helps far more than adding demos of the same setting.

### Cited Findings
- **LeRobot official guidance:** "We suggest recording at least 50 episodes, with 10 episodes per location." `lerobot-record` also defaults to `--dataset.num_episodes=50`, `episode_time_s=60` and `reset_time_s=60`. The same tutorial says imitation learning "typically converges within 5–10 epochs over the data", so the 100k-step default is usually more than a small dataset needs. — [LeRobot docs: Imitation Learning on Real-World Robots](https://huggingface.co/docs/lerobot/il_robots)
- **Seeed Studio SO-101 course (updated Oct 19, 2026):** repeats the official guidance of at least 50 episodes and about 10 per marked point. — [Seeed wiki ch. 12](https://wiki.seeedstudio.com/robotics/soarm_physical_ai_course_chapter_12/)
- **SmolVLA paper (Shukor et al., June 2025), real-robot setup:** each task dataset has 10 trajectories at each of 5 starting positions, so 50 demos per task. — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **SmolVLA, SO-100 results (Table 3, success %).** ACT is single-task. pi0 (3.5B) and SmolVLA (0.45B) are multi-task.

  | Task | ACT | pi0 | SmolVLA |
  |---|---|---|---|
  | Pick-Place | 70 | 100 | 75 |
  | Stacking | 50 | 40 | 90 |
  | Sorting | 25 | 45 | 70 |
  | Average | 48.3 | 61.7 | 78.3 |

  The fetch summary said the number of trials per condition is not clearly stated. — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **SmolVLA, SO-101 Pick-Place-Lego (Table 4):**
  - ACT: 70% in-distribution, 40% out-of-distribution.
  - SmolVLA: 90% in-distribution, 50% out-of-distribution.

  This is the closest published analogue to this bench's task. — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **SmolVLA, effect of community pretraining (Table 5, SO-100):** without pretraining SmolVLA averages 51.7%. With pretraining on community datasets (481 datasets, about 22.9K episodes, 10.6M frames) it averages 78.3%. — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **ACT/ALOHA (Zhao et al., 2023):** 50 demos per real task (100 for Thread Velcro), each 8-14 s at 50 Hz. That is 10-20 minutes of data per task, or 30-60 minutes of wall-clock time. Success rates were 84-96% on most tasks, 64% on Prep Tape and 20% on Thread Velcro. — [ACT arXiv 2304.13705](https://arxiv.org/html/2304.13705)
- **Diffusion Policy (Chi et al., 2023), real-robot demo counts and success:**

  | Task | Demos | Success |
  |---|---|---|
  | Push-T | 136 | 95% |
  | Mug Flip | 250 | 90% |
  | Sauce Pour | 90 | 79% |
  | Sauce Spread | 90 | 100% |
  | Bimanual Egg Beater | 210 | 55% |
  | Bimanual Mat Unroll | 162 | 75% |
  | Bimanual Shirt Fold | 284 | 75% |

  Diffusion Policy used more demos than ACT, on harder or more multimodal tasks. — [Diffusion Policy arXiv 2303.04137](https://arxiv.org/html/2303.04137)
- **Data Scaling Laws (Lin et al., Oct 2024):**
  - With environment and object fixed, demo count shows no clear power law. Performance "rises quickly, then plateaus".
  - The authors recommend "50 demonstrations per environment-object pair". Performance plateaus at 400, 800 and 1,600 total demos for 8, 16 and 32 pairs.
  - About 32 environment-object pairs (1,600 demos) gave 85-92.5% success in unseen environments with unseen objects.

  — [Lin et al. arXiv 2410.18647](https://arxiv.org/html/2410.18647)
- **Community SO-101 ACT reports:** typical datasets are 30-50 episodes, with reported success roughly 40-80%. These numbers rest on small samples, for example "80% (five trials)" or 8 consecutive successes followed by a failure. — [web search summary of HF model cards and GitHub repos](https://huggingface.co/leganao/act-so101-pick-place-new); [aviadarn/so101-lerobot](https://github.com/aviadarn/so101-lerobot)
- **hujunhan/so101-policy (status 2026-11-10):**
  - It is a pre-registered ACT vs SmolVLA comparison with a target of 50-100 demos. It had 20 recorded so far, with no eval results yet.
  - On a 45-demo public dataset, held-out loss for ACT was flat from about 2k steps, and "Offline numbers cannot rank the two" policies.

  — [hujunhan/so101-policy](https://github.com/hujunhan/so101-policy)

### Inferences
- About 125 demos is already 2.5x the 50-demo baseline for one task in one environment. Per Lin et al., the remaining failures (rotations, new room) are almost certainly coverage problems, not volume problems. More demos of already-covered placements will mostly plateau.
- One way to read Lin et al. for this bench: treat each meaningfully different scene condition (room or lighting, mat or background, distractor layout) as an "environment". Treat each Lego pose bin as part of the object and state distribution. A budget of about 50 per condition is reasonable, but spreading demos across conditions matters more.
- Expect ACT alone to land near the SmolVLA paper's ACT numbers: 70% in-distribution and 40% out-of-distribution on an SO-101 Lego task. If higher out-of-distribution robustness is needed, the published evidence favors a pretrained VLA (SmolVLA) fine-tuned on the same data.

### Gaps
- No controlled published curve of ACT success vs demo count (for example 25/50/100/200) on SO-100/SO-101. Only single-point results and anecdotal community reports.
- Trial counts in the SmolVLA real-robot tables were not confirmed from the fetched text, so their confidence intervals are unknown.
- I found no SO-101-specific results for Diffusion Policy or pi0 fine-tuning vs demo count.

## Demo diversity: positions, orientations, distractors, lighting, camera placement, backgrounds. How to structure collection, and whether to vary or fix the camera

### Takeaway
The official guidance is staged:
1. Start from a fixed camera, consistent lighting and a small grid of positions (5 positions x 10 demos).
2. Once grasping is reliable, widen the variation gradually.
3. Vary each axis the policy will see at test time (pose, orientation, scene). Do not vary what will stay fixed at test time, such as camera mounts.

Research supports environment and object diversity over repetition, but warns that diversity bought with inconsistent actions hurts.

### Cited Findings
- **LeRobot, on fixed cameras and staged variation:** "Keep the cameras fixed and maintain consistent grasping behavior throughout the recordings." After reliable grasping, "you can start introducing more variations... such as additional grasp locations, different grasping techniques, and altering camera positions." Also: "Avoid adding too much variation too quickly, as it may hinder your results." — [LeRobot il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **LeRobot camera guide:**
  - "Fix the cameras in place. Mount them rigidly and don't move them between recording sessions, or between recording and deployment."
  - "Lighting that differs between recording and deployment can make a policy fail."
  - Use "diffuse, consistent light and avoid direct sunlight, strong reflections and moving shadows."

  — [LeRobot cameras docs](https://huggingface.co/docs/lerobot/cameras)
- **LeRobot community datasets blog (May 11, 2025):** use "preferably two camera views". The leader arm "should not appear in the frame", and no human limbs should be in frame. Maintain "neutral, stable lighting". Use a "static, non-distracting background, or introduce controlled variations". — [HF blog: LeRobot Community Datasets](https://huggingface.co/blog/lerobot-datasets)
- **SmolVLA collection layouts:**
  - Pick-place: box fixed, cube start position varied across 5 conditions.
  - Stacking: both cubes' positions varied.
  - Sorting: 5 cube positions, colors flipped across demos.
  - No explicit grid is described.

  — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **Lin et al., diversity over repetition:** increasing "the diversity of environments and objects is far more effective than merely increasing the number of demonstrations". The authors recommend collecting "in as many diverse environments as possible, with only one unique object in each environment". Multiple objects per environment help only when the environment count is small, and the gap is negligible at about 16 environments. Object generalization is easier than environment generalization: 8 objects already score above 0.8, and 32 score above 0.9. — [Lin et al. arXiv 2410.18647](https://arxiv.org/html/2410.18647)
- **Lin et al. Appendix B (as summarized in the first fetch of the paper):** randomize the gripper's initial pose and object positions, choose environments with rich visual features, standardize operator behavior and timing, keep distractors still, and close the gripper with slight force. A second fetch of the appendix text did not surface these lines, so treat the exact wording as unverified. — [Lin et al. arXiv 2410.18647](https://arxiv.org/html/2410.18647)
- **Belkhale et al. 2023, Data Quality in Imitation Learning:** "state diversity is not always beneficial". "If state coverage comes at the expense of action consistency, the result might be worse." — [arXiv 2306.02437](https://arxiv.org/html/2306.02437)
- **Robotics Center SO-101 guide (undated):** "consistent initial conditions are critical"; mark object start positions on the table. This conflicts in emphasis with the diversity advice above: it fits within-setting repeatability, not generalization. — [roboticscenter.ai SO-101 data collection](https://roboticscenter.ai/hardware/so-101/data-collection)
- **Orientation coverage, one SO-101 project:** the next batch was planned with "varied box yaw" because the operator rolls the wrist to match yaw and 18 episodes had not taught it. That project's 20 demos also covered only the far two-thirds of the workspace, with one episode in the near third. — [hujunhan/so101-policy](https://github.com/hujunhan/so101-policy)
- **Orientation failure, one user report:** an ACT policy carried over the demonstrated grasp pose exactly when a rigid object was rotated about 89 degrees from the demos. — [TheWisp/lerobot issue #267](https://github.com/TheWisp/lerobot/issues/267)
- **SO-100 wrist roll hardware:**
  - The servo has been reported as unstable, with unwanted rotation in teleop. — [lerobot issue #1333](https://github.com/huggingface/lerobot/issues/1333)
  - It may be physically stopped by printed-part contact rather than spinning freely. — [lerobot PR #4583](https://github.com/huggingface/lerobot/pull/4583)
  - Wrap-around limit errors have been reported. — [lerobot issue #1255](https://github.com/huggingface/lerobot/issues/1255)

### Inferences
- **Rotated-placement failures:** structure collection as positions x yaw bins. For example, 5-6 positions x 4 yaw bins (0, 45, 90, 135 deg; a Lego brick is roughly 180-deg symmetric) x 3-5 demos per cell, in the current room and lighting. Mark positions and yaw on the mat with tape so coverage can be audited. Log the position and yaw cell per episode in trials.md. The SmolVLA and LeRobot "10 per position" pattern covers position only and says nothing about yaw. The rotation failures suggest yaw is undersampled.
- **2-4 in grasp misses:** these are consistent with (a) undercovered regions of the workspace, as in the hujunhan coverage gap, and (b) policy averaging between modes. First audit current start positions with a scatter plot of episode-start Lego positions from the overhead cam. Then fill the holes rather than recording uniformly.
- **Camera:** for a fixed bench, keep both cameras rigidly fixed and identical between recording and deployment, as the LeRobot docs say. Camera-pose variation belongs only in a deliberate later phase, and only if the camera will move at test time.
- **Distractors:** vary distractor layout across episodes, but keep distractors still during an episode (Lin et al. appendix, unverified wording). Include some episodes with distractors near the red Lego, so the policy sees close-clutter states.
- **Lighting and room:** keep a small set of episodes in each new lighting condition (day and evening, lamp on and off). Lin et al.'s environment-diversity result suggests 10-20 demos per new condition is a better buy than 50 more in the old one.

### Gaps
- No published ablation on SO-100/SO-101 of grid vs random position sampling, or of yaw coverage specifically.
- No primary source quantifies how many demos per yaw bin ACT needs.
- Mobile ALOHA (co-training findings) was not fetched in this pass.

## Operator technique: consistent strategy, speed, pauses and hesitations, slow final approach, starting immediately, ending at rest; multimodality

### Takeaway
Consistency is the dominant quality factor. Use one grasp strategy per situation, with no pauses or idle segments. Start moving promptly after recording starts and end in a consistent rest pose. Human demos are multimodal: ACT's CVAE and Diffusion Policy model this to an extent, but needless multimodality (left vs right approach, varied grasp styles) still costs success at small data sizes.

### Cited Findings
- **LeRobot:** "maintain consistent grasping behavior throughout the recordings." A good rule of thumb: "you should be able to do the task yourself by only looking at the camera images." — [LeRobot il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **Belkhale et al., on action consistency:** "expert data should be curated to have more consistent actions," and "making actions more consistent tends to increase policy success."
  - Pauses and other action noise increase action divergence.
  - Policy (action) noise "often hurts performance despite similar state coverage", especially with small datasets.
  - Faster demos help only if they don't increase per-step divergence.

  — [arXiv 2306.02437](https://arxiv.org/html/2306.02437)
- **Diffusion Policy, on idle actions:** "single-step policies can easily overfit to this pausing behavior". Idle actions "are known to be challenging for behavior cloning algorithms and therefore are often avoided or filtered out". BC-RNN and IBC got stuck on hardware when idle actions were not removed. Longer action horizons (about 8 steps optimal) help with idle portions. — [Diffusion Policy arXiv 2303.04137](https://arxiv.org/html/2303.04137)
- **ACT, on stochastic human demos:** human demos are inherently stochastic. Without the CVAE objective, success on human data fell from 35.3% to 2%, while scripted data barely changed. Chunk size 100 was best (1% at k=1 vs 44% at k=100). — [ACT arXiv 2304.13705](https://arxiv.org/html/2304.13705)
- **Start and end timing (SO-101 dry run):**
  - "Start moving soon after 'Recording episode' and stop soon after returning" so demos do not include a random wait.
  - The policy started about 1 s before a demonstrator who had waited 2 s.
  - The start pose must match the demonstrations: a wrist 100 deg off caused a stall.

  — [hujunhan/so101-policy](https://github.com/hujunhan/so101-policy)
- **Robotics Center (undated), operator checks:**
  - Reset follower and leader to a home pose before each session, and use the warmup to adjust your grip.
  - Keep motion smooth: follower lag time-shifts action labels.
  - Keep episode lengths within ±30% of the median.
  - Check for a clear open-to-closed gripper transition rather than gradual drift.
  - Delete episodes with servo velocity spikes.

  — [roboticscenter.ai SO-101](https://roboticscenter.ai/hardware/so-101/data-collection)
- **Data Scaling Laws appendix (via first fetch):** standardize operator behavior and timing; close the gripper with slight force. — [Lin et al. arXiv 2410.18647](https://arxiv.org/html/2410.18647)

### Inferences
- **A concrete operator script for this bench:**
  1. Start from a fixed home pose (match the deployment start pose).
  2. Move within about 0.5 s of the start cue.
  3. Do a direct transit to a pre-grasp hover about 3-5 cm above the Lego.
  4. Set wrist roll to the Lego's yaw during the transit, not at the bottom.
  5. Make a short, steady vertical descent, close firmly, lift, transit to the bowl, release, and return to home.
  6. Stop recording shortly after reaching rest (press `→` to end early) rather than idling to the 30 s limit.
- At 30 s episode length, a 10-15 s task leaves long idle tails unless episodes are ended early. Per Diffusion Policy and Belkhale, long rest segments are idle data that can teach hesitation. Check the per-episode length distribution in the current dataset.
- **One grasp rule for orientation:** for example, always align the gripper fingers across the brick's short axis, and pick the nearest of the two symmetric wrist angles. This avoids the policy averaging between two wrist-roll solutions. Averaging between modes is a plausible cause of both the rotation failures and the 2-4 in misses.
- A "slow final approach" is not explicitly recommended in the primary sources found. It is consistent with Lin et al.'s timing standardization and with ACT's chunked actions, where a slower final segment gives the policy more frames of the critical alignment phase. Treat this as a reasonable heuristic, not an established result.

### Gaps
- No primary source quantifies the effect of approach speed or a hover-then-descend pattern on SO-arm grasp accuracy.
- No source gives an optimal episode length relative to task duration for ACT on SO-101.

## Recovery / corrective demos and DAgger-style collection on real robots; how to do it in LeRobot

### Takeaway
LeRobot now ships first-class human-in-the-loop (HIL) DAgger collection: `lerobot-rollout --strategy.type=dagger`, which works with SO-101 leader arms. Run the policy, pause, take over with the leader (which first moves to mirror the follower), record the recovery and correction, merge with the original demos and fine-tune. Repeat rounds targeting the current failure modes. This is the HG-DAgger / RaC pattern, and the most direct fix for covariate shift after a room move.

### Cited Findings
- **Rationale and scope:** standard BC trains on successes only, and errors compound into unseen states. HIL records "recovery movements and corrections" to teach recovery. Compatible teleoperators include `so100_leader` and `so101_leader`, which need active motors so that "the leader arm moves to match the robot" on pause, avoiding jumps. — [LeRobot HIL Data Collection](https://huggingface.co/docs/lerobot/hil_data_collection)
- **Workflow:**
  1. Train a base policy. The example uses ACT with `--steps=50000 --batch_size=32`.
  2. Run `lerobot-rollout --strategy.type=dagger ... --strategy.num_episodes=50`. Keys:
     - `Space`: pause or resume.
     - `Tab`: start or stop a correction while paused.
     - `ESC`: stop.
     - A foot pedal works via `--strategy.input_device=pedal`.
  3. By default only human segments are recorded, and each correction is its own episode. `--strategy.record_autonomous=true` records everything.
  4. Remove the `intervention` column with `lerobot-edit-dataset --operation.type remove_feature`, then merge with the demo dataset (`--operation.type merge`).
  5. Fine-tune from the base checkpoint (example `--steps=20000`). Repeat.

  — [LeRobot HIL Data Collection](https://huggingface.co/docs/lerobot/hil_data_collection)
- **When to intervene:** "irreversible mistake", "hesitating or showing uncertain behavior", "deviating from the expected trajectory". Corrections should be "confident, clean" and complete the subtask, without overcorrecting. — [LeRobot HIL Data Collection](https://huggingface.co/docs/lerobot/hil_data_collection)
- **Lineage cited by LeRobot:**
  - DAgger (Ross et al. 2011).
  - HG-DAgger (Kelly et al. 2019): the human intervenes only when needed.
  - RaC (Hu et al. 2025, arXiv 2509.07953): decomposes interventions into recovery and correction, which is the protocol the dagger strategy follows.
  - pi0.6/RECAP (Physical Intelligence 2025).

  — [LeRobot HIL Data Collection](https://huggingface.co/docs/lerobot/hil_data_collection)
- **Other rollout strategies:** `sentry` (continuous recording plus upload), `highlight` (ring buffer plus keystroke save) and `episodic`. Rollout datasets must be named `rollout_*`. — [LeRobot il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **Datasets in the same tutorial must share robot, cameras and fps to merge.** The camera names become dataset keys and must match at deployment. — [LeRobot HIL Data Collection](https://huggingface.co/docs/lerobot/hil_data_collection); [LeRobot il_robots](https://huggingface.co/docs/lerobot/il_robots)

### Inferences
- **Fit for this bench:** run the dagger strategy specifically on rotated placements and on the 2-4 in miss cases. When the gripper hovers misaligned, pause, take over, re-align over the brick and complete the grasp. That gives exactly the near-miss to correct-alignment data that clean demos never contain.
- **Repo constraint:** HIL collection touches hardware. AGENTS.md says to run only one lab process against hardware at a time, and lab hardware for the toy robot goes through lab-agent. Whether exp002's SO-101 rollouts sit under that constraint should be checked against the exp002 README and HANDOFF before adding a dagger loop.
- **Mixing ratio:** the LeRobot docs fine-tune on demos plus HIL merged without weighting. If corrections are few (for example 20 short episodes vs 125 demos), they may be diluted. Running several rounds, or oversampling corrections, is a common heuristic, but it is not documented in the sources found.

### Gaps
- No published SO-101 success-rate numbers before and after LeRobot's dagger strategy were found.
- RaC and HG-DAgger result numbers were not fetched from the primary papers, only their citation via LeRobot docs.
- No guidance on how many HIL episodes per round, or how many rounds.

## Camera choices: resolution, fps, fixed exposure and white balance, wrist camera importance, locking auto exposure on webcams

### Takeaway
Use 640x480 at 30 fps per camera, with two views (scene plus wrist), rigid mounts and stable, diffuse, neutral lighting. Lock exposure, white balance and focus so the image statistics don't drift with room light. LeRobot exposes manual exposure and white balance only for RealSense. For a C920 on macOS, use a UVC tool such as `uvcc` to set them outside LeRobot.

### Cited Findings
- **LeRobot camera guide:** "Keep the resolution modest. 640×480 at 30 fps is enough for most tasks." "A good camera setup matters more than a high resolution." The object, gripper and target should be visible in at least one camera. — [LeRobot cameras docs](https://huggingface.co/docs/lerobot/cameras)
- **Community datasets blog:** record at "at least 480x640 / 720p" and about 30 FPS. Use "consistent exposure and sharp focus" and two views. Name wrist cameras by orientation. — [HF blog: LeRobot Community Datasets](https://huggingface.co/blog/lerobot-datasets)
- **LeRobot camera controls:** manual `exposure`, `gain` and `white_balance` exist in `RealSenseCameraConfig`, and "Manual color controls disable the corresponding automatic exposure or white-balance mode". The documented `OpenCVCameraConfig` shows only fps, width, height, color mode and rotation, with no exposure or white-balance options. — [LeRobot cameras docs](https://huggingface.co/docs/lerobot/cameras)
- **Recording cadence:** `lerobot-record` reports achieved Hz per episode. "A session that ran at 25 Hz still produces a dataset that claims 30", because timestamps derive from frame index. Cameras are typically the slow step (74% of loop work in the example). — [LeRobot il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **ACT/ALOHA cameras:** 4 Logitech C922x webcams at 480x640 (two wrist, one front, one top-down). — [ACT arXiv 2304.13705](https://arxiv.org/html/2304.13705)
- **Diffusion Policy bimanual setup:** two scene cameras plus two wrist cameras. — [Diffusion Policy arXiv 2303.04137](https://arxiv.org/html/2303.04137)
- **SmolVLA:** community data was standardized to top, wrist and side views. — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **uvcc (C920 on macOS):** a UVC device configurator CLI that lists the Logitech C920 (1133:2093) as tested. It controls white balance/temperature, gain, exposure and focus, and can export and import settings. The C920 white_balance_temperature range is 2000-6500. — [joelpurra/uvcc](https://github.com/joelpurra/uvcc)
- **Webcam Settings:** a macOS GUI app that a reviewer bought a C920 to use for disabling auto-exposure. Support on recent macOS is unconfirmed. — [Webcam Settings (App Store)](https://apps.apple.com/app/id533696630)
- **Robotics Center (undated):** keep camera and joint timestamps aligned within 20 ms. — [roboticscenter.ai SO-101](https://roboticscenter.ai/hardware/so-101/data-collection)

### Inferences
- **Locking the C920:** export settings with uvcc after locking auto-exposure off, auto white balance off (for example a fixed 4000-5000 K) and autofocus off. Re-apply them before every recording and rollout session, because UVC settings typically reset on re-plug or reboot. The search did not confirm persistence. Record the applied values in trials.md so recording and deployment conditions can be compared.
- A locked exposure that was set in one room will look different in another. After a room move, re-lock in the new room and record a fresh batch rather than reusing old settings.
- **Wrist camera:** the wrist view is the main signal for final alignment and yaw. The 2-4 in misses and yaw failures argue for checking that the wrist cam is in focus at grasp distance (about 5-15 cm) and sees the brick's orientation clearly during descent.
- **Repo constraint:** AGENTS.md says camera commands run in macOS Terminal (not in this app) and camera frames are never committed or synced. exp001 has a "Gotchas and hints" section that should be read before changing camera setup.

### Gaps
- No primary source ablates wrist cam vs no wrist cam on SO-100/SO-101.
- No confirmation that LeRobot's OpenCV backend can set exposure or white balance on macOS AVFoundation. The docs show no such option.
- uvcc's current macOS compatibility (late 2026) was not verified from its README.

## Published SO-100/SO-101 community guidance (LeRobot docs, HF hackathon, SmolVLA community datasets, Seeed wiki)

### Takeaway
The community guidance is consistent and conservative:
- About 50 episodes, 10 per position.
- Fixed cameras, two views, stable neutral lighting, 640x480 at 30 fps.
- No leader arm or people in frame, and consistent grasping.
- Clear 25-50 character task strings.
- Widen variation only after reliable grasping.
- Use the dagger rollout strategy to fix failures.

### Cited Findings
- **LeRobot il_robots:**
  - The recipe is 50+ episodes, 10 per location. Keep cameras fixed, keep grasping consistent and keep the object visible. Then vary gradually.
  - Keyboard controls during recording: `→`/`n` ends early, `←`/`r` re-records, `ESC`/`q` stops.
  - `--resume=true` takes `num_episodes` as additional episodes.

  — [LeRobot il_robots](https://huggingface.co/docs/lerobot/il_robots)
- **HF community datasets blog (May 11, 2025; Aubakirova, Chapin, Shukor, Barannikov, Kuosmanen, Cadene, Cuenca):**
  - Two views, leader arm out of frame, neutral stable lighting, static or controlled background.
  - At least 480x640, about 30 FPS.
  - Task descriptions of 25-50 characters, no "task1".
  - Consistent feature names (`<modality>.<location>`).
  - Avoid episodes with only one or a few frames.
  - It gives no guidance on episode count.

  — [HF blog: LeRobot Community Datasets](https://huggingface.co/blog/lerobot-datasets)
- **SmolVLA community data curation:** the authors re-annotated noisy task strings ("task desc", "Hold", "Up") with Qwen2.5-VL-3B and remapped camera names to top, wrist and side. — [SmolVLA arXiv 2506.01844](https://arxiv.org/html/2506.01844)
- **Seeed Studio SO-101 course ch. 12 (Oct 19, 2026):**
  - At least 50 episodes, about 10 per marked point.
  - Fix both cameras.
  - Keep lighting stable and avoid people walking through the view.
  - Keep grasping consistent, and get grasps reliable before adding variation.
  - Use the "only from camera images" self-check.
  - It gives no exposure guidance.

  — [Seeed wiki ch. 12](https://wiki.seeedstudio.com/robotics/soarm_physical_ai_course_chapter_12/)
- **Seeed bimanual guide:** use `--dataset.root` with `--dataset.push_to_hub=false` for local-only data. Episode deletion uses the dataset edit tool, which backs up the originals. — [Seeed bimanual SO-ARM training](https://wiki.seeedstudio.com/lerobot_double_arm_so_arm_training/)
- **Robotics Center (undated, San Francisco):** per-session QA checklist: episode length within ±30% of median, delete velocity-spike episodes, replay to check tracking, check gripper transitions. — [roboticscenter.ai SO-101](https://roboticscenter.ai/hardware/so-101/data-collection)

### Inferences
- Because AGENTS.md says media must never be committed or synced, the bench should record with `--dataset.push_to_hub=false` and a local `--dataset.root`. Confirm against exp002's README.
- The Robotics Center QA checklist (length outliers, velocity spikes, gripper transition) is cheap to script over the existing 125-episode dataset. It may find bad episodes that hurt consistency.

### Gaps
- No written guidance from the Hugging Face SO-100 hackathon (June 2025) on collection protocol was found in this pass.
- The Robotics Center page is undated and its publisher's credentials are unclear, so treat it as secondary.
