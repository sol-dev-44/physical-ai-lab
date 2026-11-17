# Trim the stillness before tuning anything else

The v4 freeze is a data problem, not a hyperparameter problem. The bench's training recipe already matches the ACT paper and LeRobot defaults. The thing that went wrong is that about 3 s of identical "arm at rest, Lego on mat" frames at the start of each demo taught the policy that rest means wait. ACT's default chunk is 100 steps, about 3.3 s at 30 fps, so one idle prefix fills almost a whole chunk. The policy plans "stay", sees the same rest scene again, and plans "stay" again for the whole rollout. The fix the community has converged on is the one the lab has now built. Cut idle frames at the start, keep a short settled tail at the end, and stop recording them in the first place. After that, the remaining gains at this scale come from coverage (more yaw angles and scene conditions, plus DAgger-style corrections), not from more demos of the same placements or from bigger models. Evaluation needs the most discipline. Nine rollouts only tell a 2/9 policy from a 7/9 one, so checkpoints should be compared in paired, interleaved sessions with partial-credit scoring. Offline checks are useful for catching broken policies, like the lab's wait-plan probe, but not for ranking good ones. SmolVLA is the one alternative with published evidence of beating ACT on an SO-101 Lego task, and it needs a cloud GPU.

## Idle prefixes as long as a chunk create a "wait forever" fixed point

The failure is documented, though mostly in issue threads rather than papers. In LeRobot issue #3429, a user reported that idle frames at episode start made the arm "stay frozen" too long at inference. They recommended dropping start idle and keeping end idle so the model learns to settle. A maintainer closed the issue saying trimming "depends on the task" ([lerobot #3429](https://github.com/huggingface/lerobot/issues/3429)). In issue #2213, an SO-101 ACT policy that "stayed static or moved unpredictably" drew the same diagnosis from one commenter: static frames bias the policy toward zero actions ([lerobot #2213](https://github.com/huggingface/lerobot/issues/2213)).

The ACT paper explains why chunking normally handles pauses and why it fails here. The authors say predicting action sequences "helps tackle temporally correlated confounders, such as pauses in demonstrations", and they also note a failure mode where "the robot can pause indefinitely for certain states" ([ACT paper](https://ar5iv.labs.arxiv.org/html/2304.13705)). That argument assumes pauses are short relative to the chunk. The bench's median 3.2 s idle start is about 96 frames, against a 100-frame chunk. The 90-odd rest frames look the same to the cameras and differ only in "time until motion starts", which the policy cannot observe. Under L1 regression it learns mostly "stay".

Older imitation work reached the same conclusion. The Diffusion Policy authors write that idle actions "are known to be challenging for behavior cloning algorithms and therefore are often avoided or filtered out", and that BC-RNN and IBC got stuck on hardware when idle actions were left in ([Diffusion Policy](https://arxiv.org/html/2303.04137)). SCIZOR, a 2026 curation method, found that "Pause" and "Slow Motion" were among the most common bad segments, and removing them gave an average 15.4% gain across benchmarks ([SCIZOR](https://arxiv.org/html/2505.22626v2)).

One confound is worth ruling out first. In #2213 the maintainer blamed `--batch_size 1` and `use_vae=false`, not idle frames ([lerobot #2213](https://github.com/huggingface/lerobot/issues/2213)). The bench trains at batch 8 with the VAE on, so that cause does not apply. The ACT paper shows why the VAE matters: without it, success on human demos fell from 35.3% to 2% ([ACT paper](https://arxiv.org/html/2304.13705)).

Because v4's offline plan was "wait" on 50% of recorded starts, changing how actions are executed (temporal ensembling, shorter `n_action_steps`) cannot fix it. Those settings change how often the policy replans, but each new plan is still "wait".

### How to trim, and what to keep

Practitioners detect idle frames from joint motion with a debounce and a short pad. Daft's example marks a frame active after 3 consecutive frames above threshold and keeps 0.25 s before the first and after the last sustained motion ([Daft docs](https://docs.daft.ai/en/stable/examples/motion-trimming-physical-ai/)). Voxel51's tool judges idleness relative to each episode's own speed, so slow operators are not flagged, and scores trailing idle at half weight because fixed-length timers create it ([Voxel51](https://voxel51.com/blog/lerobot-dataset-curation-metrics)).

The lab's `trim_idle.py` uses a 2-degree move threshold on actions, keeps 3 frames (0.1 s) before motion, and keeps 1 s after motion ends. That matches the "drop start, keep a short end" advice. A 0.1 s lead is shorter than Daft's 0.25 s, but it still shows the rest-then-move transition without a run of contradictory "rest, stay" labels. The 1 s tail gives the policy a clear "done, at rest" state, which the cameras separate from the start state by the Lego being in the bowl.

Mid-episode pauses are a different case. A pause before a regrasp teaches recovery, and Voxel51 deliberately does not penalize it ([Voxel51](https://voxel51.com/blog/lerobot-dataset-curation-metrics)). Cutting frames out of the middle also breaks the timeline that chunk targets span. Flag long mid-episode pauses for review rather than cutting them, which is what `audit.py` does.

Upstream LeRobot has no merged in-episode trim yet. Two earlier PRs were closed unmerged, and the consolidated PR #4939 (stream-copy trim with explicit frame ranges, no automatic idle detection) was still open as of 2026-11-17 ([lerobot PR #4939](https://github.com/huggingface/lerobot/pull/4939)). The lab's own tool fills that gap.

### Filtering bad demos beyond idle time

For about 125 single-task demos, cheap heuristics are worth running. Learned scorers are overkill. The useful heuristics are duration outliers (robust z-score after trimming), smoothness (SPARC on joint speed), gripper chatter, missed grasps, and camera blur or darkness ([Voxel51](https://voxel51.com/blog/lerobot-dataset-curation-metrics); [HF GIGO blog](https://huggingface.co/blog/robotdata/gigo)). Tool authors recommend using scores to order a human review queue, not to delete episodes automatically.

Learned methods like CUPID need a working policy plus rollouts ([CUPID](https://arxiv.org/abs/2506.19121)). A 2026 smoothness paper argues spectral arc length gets much of the benefit in under a second per demo ([Kulkarni et al.](https://arxiv.org/html/2604.23000)).

One check is easy to miss. `lerobot-record` now reports achieved Hz per episode, and "a session that ran at 25 Hz still produces a dataset that claims 30", because timestamps come from frame index ([LeRobot docs](https://huggingface.co/docs/lerobot/il_robots)). A slow episode silently teaches faster motion than the operator made.

## 125 demos is enough volume; yaw and scene coverage are the gap

The standard recipe is 50 demos per task, 10 at each of 5 positions ([LeRobot docs](https://huggingface.co/docs/lerobot/il_robots)). The bench has 2.5 times that. The best published analogue is the SmolVLA paper's SO-101 Lego pick-and-place, where ACT scored 70% in-distribution and 40% out-of-distribution ([SmolVLA paper](https://arxiv.org/html/2506.01844)). That is a realistic ceiling for ACT on this task.

The data scaling study by Lin et al. found that with environment and object fixed, success "rises quickly, then plateaus". They concluded that more diverse environments and objects are "far more effective than merely increasing the number of demonstrations" ([Lin et al.](https://arxiv.org/html/2410.18647)). The bench's remaining failures (rotated placements, the room move) are coverage problems. More demos at already-covered placements will mostly plateau.

The "10 per position" pattern says nothing about orientation. One SO-101 project planned a batch with varied yaw because 18 episodes had not taught the wrist roll ([hujunhan/so101-policy](https://github.com/hujunhan/so101-policy)). Another user saw ACT copy the demonstrated grasp pose exactly when the object was rotated about 89 degrees ([TheWisp/lerobot #267](https://github.com/TheWisp/lerobot/issues/267)). A positions-by-yaw grid, logged per episode, makes coverage auditable. A Lego brick is roughly symmetric under a half turn, so yaw bins only need to span 0 to 180 degrees.

Consistency matters as much as coverage. Belkhale et al. found that "making actions more consistent tends to increase policy success" and that "state diversity is not always beneficial" when it costs action consistency ([Belkhale et al.](https://arxiv.org/html/2306.02437)). In practice that means one grasp rule per situation: same finger alignment on the brick, the nearer of the two symmetric wrist angles, wrist roll set during transit. Two valid grasp styles in the data give the policy two modes to average between. Averaging is a plausible cause of both the rotation failures and the 2 to 4 inch misses.

Start and end timing belong in the protocol. One SO-101 team found their policy started about 1 s before a demonstrator who had waited 2 s, and that a wrist 100 degrees off the demonstrated start pose caused a stall ([hujunhan/so101-policy](https://github.com/hujunhan/so101-policy)). The deployment start pose must match the recorded one.

Cameras should stay fixed and lit the same way between recording and deployment. LeRobot's guide says to mount cameras rigidly and warns that "lighting that differs between recording and deployment can make a policy fail" ([LeRobot cameras](https://huggingface.co/docs/lerobot/cameras)). LeRobot only exposes manual exposure and white balance for RealSense. On a C920 under macOS, `uvcc` can lock exposure, white balance and focus, and can export the settings for re-applying each session ([uvcc](https://github.com/joelpurra/uvcc)).

The most direct fix for failures the policy already makes is LeRobot's built-in DAgger mode, `lerobot-rollout --strategy.type=dagger`. It supports SO-101 leader arms: the leader moves to mirror the follower on pause, the operator takes over, and only the correction is recorded ([LeRobot HIL docs](https://huggingface.co/docs/lerobot/hil_data_collection)). Pointed at rotated placements and near misses, it produces the near-miss-to-alignment data that clean demos never contain. In this repo it must run as the only lab process on the hardware.

## The training recipe is already right except for epochs and augmentation

LeRobot's ACT defaults match the paper's Table III: lr 1e-5, batch 8, chunk 100, KL weight 10, dropout 0.1, ResNet18, constant LR with no scheduler ([configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py); [ACT paper](https://arxiv.org/html/2304.13705)). No source argues for changing these on SO-100-class tasks. Larger batches are a throughput change, and nobody reports a controlled success gain from them.

Training length is the setting to watch. LeRobot's hardware guide says imitation learning typically converges in 5 to 10 epochs over the dataset ([LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)). v4 ran 50k steps at batch 8 over about 109k frames, roughly 3.7 epochs. v5 runs the same steps over about 68k trimmed frames, roughly 5.9 epochs.

That has a side effect worth stating. The v5 script describes the trim as its one change from v4, but trimming also moved training from 3.7 to 5.9 epochs. If v5 beats v4, some of the gain could come from more passes over the moving frames. Both effects push the same way, so this does not undercut the fix, but the v4/v5 comparison has two causes, not one.

Image augmentation is off by default. `--dataset.image_transforms.enable=true` turns on brightness, contrast, saturation, hue and sharpness jitter plus a small affine shift (up to 5 degrees, 5% translation), with no random crop ([LeRobot transforms.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/transforms/transforms.py)). It targets the lighting shifts that hurt after the room move. It will not cover a re-mounted camera. No source measures its effect on real-robot ACT success, so judge it by rollouts, not by training loss, which will sit slightly higher.

For new batches, warm-starting is supported. `--policy.pretrained_path` loads weights only and resets the step counter. `--resume=true` reuses the saved config and ignores new command-line flags ([LeRobot pi0.5 docs](https://huggingface.co/docs/lerobot/pi05); [Seeed wiki](https://wiki.seeedstudio.com/robotics/hands_on_act_training/)). Seeed suggests 3 to 10 times lower LR for fine-tuning. Training on old plus new data together guards against forgetting and keeps normalization stats consistent.

### When to try SmolVLA, Diffusion Policy or pi0

SmolVLA is the only alternative with direct evidence on this task. On SO-100 with 50 demos per task, it averaged 78.3% against ACT's 48.3% and pi0's 61.7%. On SO-101 Lego pick-and-place it scored 90% in-distribution and 50% out-of-distribution, against ACT's 70% and 40% ([SmolVLA paper](https://arxiv.org/html/2506.01844)). Its gain on single-task pick-and-place on SO-100 was small (75 vs 70), and its biggest wins came on stacking and sorting. Expect a modest in-distribution gain and a better out-of-distribution showing.

The SmolVLA docs' example fine-tune is 20k steps at batch 64, about 4 hours on one A100 ([LeRobot SmolVLA docs](https://huggingface.co/docs/lerobot/smolvla)). On HF Jobs an A100 costs $2.50 an hour, so about $10 a run ([HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)). The camera keys must be mapped with `--rename_map`, and the `--task` string at rollout must match the recording. There is no benchmarked MPS training rate, so cloud is the realistic path.

pi0 and pi0.5 need 24 to 40 GB or more of VRAM, a gated PaliGemma license and quantile stats ([LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md); [LeRobot pi0.5 docs](https://huggingface.co/docs/lerobot/pi05)). The one SO-100 comparison puts pi0 behind SmolVLA. Diffusion Policy takes about 4 times ACT's training time. Small-data SO-100 anecdotes are weak, and one SO-101 project found its roughly 300 ms inference too slow for real-time control ([tabithako](https://tabithako.github.io/projects/policy-training)). Neither is worth it for one pick-and-place task.

ACT on a cloud GPU is also cheap. The hardware guide puts ACT at batch 8 on an L4 or A10G at 1 to 2 hours for 5 epochs of 45k frames ([LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)). That makes a 7 to 10 epoch run a few dollars, against about 8 hours on the Mac mini.

## Nine rollouts separate only very different checkpoints

Neither training loss nor validation loss picks the best checkpoint. In Hugging Face's own ACT experiment, validation loss plateaued while success kept rising by about 17 points. For Diffusion Policy, validation loss rose 135% while success also rose. The author concluded "we should not use validation loss to early stop training" ([HF blog](https://huggingface.co/blog/m1b/validation-loss-robotics)). SIMPLER measured validation MSE against real success at a Pearson r of only 0.308 ([SIMPLER](https://arxiv.org/html/2405.05941)).

The bench's freeze shows why. A "stay at rest" policy scores well on held-out loss when many frames are static, because those frames have near-zero error. Behavioural probes catch what loss misses. `audit.py`'s check, which runs the policy on every recorded start and fails if more than 5% of 100-step plans move under 10 degrees, is exactly that kind of smoke test. No study validates it as a ranking metric. It is a gate against broken policies, not a selector between good ones.

For finer offline ranking, CI-MSE scores error only on task-critical segments. It reached a Spearman rho of -0.87 against rollout success, against -0.61 for raw MSE ([CI-MSE](https://arxiv.org/pdf/2606.29898)). A cheap version is held-out L1 restricted to frames around gripper transitions.

Any offline prediction must run with ACT in inference mode, with no `action` key in the input. A LeRobot fix (#1588) addressed the VAE encoder path being triggered when a batch contained actions, which makes held-out numbers optimistic ([commit mirror](https://gitea.d-robotics.cc/chao.wu/Lerobot/commit/4c8f0020551bc6ba30ac2d7f54906aeed55ab85d)). The lab's probe passes only `observation.*` keys and the task, so it avoids this.

On the robot, sample size is the binding limit. Exact 95% intervals, computed for this report, run from 3% to 60% for 2/9 and from 21% to 86% for 5/9. A 2/9 versus 7/9 comparison is only borderline significant (Fisher p about 0.06). Treat any gap smaller than about 5 of 9 as a tie.

Kress-Gazit et al. give the method for getting more out of each trial:

- Interleave the policies in one session on matched initial conditions.
- Define success before evaluating.
- Score subgoals: one of their policies completed the task 4/23 times but grasped 23/23.
- Report failure modes with counts.

Their cautionary example is a policy that dropped from 13/20 to 0/8 after a lab reorganisation, which is the bench's room move in miniature ([Kress-Gazit et al.](https://arxiv.org/html/2409.09491v1)). Sequential tests like STEP stop early when one policy clearly wins, and N-SCORE extends that to partial credit ([STEP](https://arxiv.org/html/2503.10966v1); [N-SCORE](https://arxiv.org/pdf/2603.13616)).

## Silent LeRobot gotchas that look like a bad model

Several pitfalls make a good checkpoint look broken, and most raise no error.

**Loading path.** `--policy.type=act` plus `pretrained_path` skips the pre- and post-processors "so actions never reach the control loop". Use `--policy.path` ([Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)).

**Normalization.** Normalization now lives in processor pipelines, not in the weights ([LeRobot backward compatibility](https://huggingface.co/docs/lerobot/backwardcomp)). Mismatched processors can train and run without an error while degrading results. Any dataset edit needs recomputed stats.

**Loop rate.** The same Classmethod checkpoint scored 9/10 on CUDA at about 30 Hz and 4/10 on Mac MPS at about 15 Hz ([Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)). The bench's trial log shows the loop holding about 30 Hz, so this is not a live problem, but it is worth checking every session.

**Chunk execution.** With defaults, ACT predicts once every 100 steps and plays the chunk open-loop. Temporal ensembling needs `n_action_steps=1` and coefficient 0.01 ([configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py)), which the bench's rollout scripts already use.

**Cameras and ports.** macOS camera indices and serial port names change between connections, so re-check with `lerobot-find-cameras` and `lerobot-find-port` each session ([Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)). A UVC camera left to auto-negotiate can pick YUYV instead of MJPG and drop frames on shared USB ([HF forum](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)).

**Zero-variance stats.** A constant feature gets a standard deviation of zero, and normalizing it yields Inf. One audit found this in 4 of 5 popular LeRobot datasets ([Traceplane](https://traceplane.pages.dev/blog/we-audited-5-lerobot-datasets)).

The forum's suggested diagnostic order is a good habit. Record the version, compare teleop loop rate with the policy loop rate, inspect episodes for frozen frames, evaluate covered and held-out positions separately, and check calibration and camera geometry. Only then blame the ACT config ([HF forum](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)).

## Conclusion

Data shape matters more than model choice at this scale. A policy can only be as decisive as its labels. When a quarter to a third of the frames say "stay" in a state that looks like the start, a correctly trained ACT learns to wait, and no execution setting changes that. The lab's three tools (trim existing data, gate new recordings, fail any checkpoint that plans to wait) attack the same cause at three points. That is more robust than any single fix the community has published, and ahead of upstream LeRobot, which still has no merged trim.

The next limits are coverage and measurement. Yaw bins, one grasp rule and DAgger corrections address the failures the policy actually makes. Paired, subgoal-scored rollouts are the only way to know whether a change helped, because nine binary trials cannot see anything smaller than a large jump. If v5 moves but still misses rotated bricks, the evidence points to targeted data next and SmolVLA after that, not to more ACT steps.

## Checklist for the exp002 bench

Status key: **Done** means a lab tool already does it. **Partly** means a tool covers some of it. **To do** means nothing covers it yet.

### Data curation

| Item | Status |
|---|---|
| Cut idle frames at episode start, keep a short lead (3 frames) before motion | **Done**: `trim_idle.py` |
| Keep about 1 s of settled rest at the end, cut the rest of the tail | **Done**: `trim_idle.py` (1 s tail) |
| Leave mid-episode pauses in, flag long ones for review | **Done**: `audit.py` (pauses over 2 s) |
| Verify the trimmed copy (videos byte-identical, frames line up) | **Done**: `trim_idle.py --verify` |
| Fail training if idle start is over 0.5 s or idle end is over 2 s | **Done**: `audit.py`, gating `train_act_50k_v5.sh` |
| Flag episode length outliers; check stats.json exists and its count matches the frames | **Done**: `audit.py` |
| Fail on NaN, Inf or zero standard deviation in action and state stats | **To do**: add to `audit.py` |
| Check achieved Hz per episode is close to 30 | **To do**: add to `audit.py`, or read `lerobot-record`'s per-episode Hz |
| Check every episode has a gripper close and open | **To do**: add to `audit.py` |
| Record a success label per demo; drop or review failed demos | **To do**: a column in trials.md or the recording log |
| Score smoothness (SPARC) and gripper chatter to order a review queue | **To do**: optional |

### Collection protocol

| Item | Status |
|---|---|
| Never save idle lead-in frames | **Done**: `record_gated.py` |
| End each episode once the arm is back at rest and still for 1 s | **Done**: `record_gated.py` |
| Start each demo from the same home pose the rollout starts from | **To do**: write it into the protocol in README or HANDOFF |
| Grid of positions by yaw bins (0 to 180 degrees), tape marks on the mat, log the cell per episode | **To do** |
| One grasp rule: same finger alignment, nearer wrist angle, roll during transit | **To do**: write it into the protocol |
| Spread new demos across scene conditions (lighting, distractor layout), 10 to 20 each | **To do** |
| Lock C920 exposure, white balance and focus with `uvcc`; re-apply and log each session | **To do**: run from macOS Terminal per AGENTS.md |
| Record with `--dataset.push_to_hub=false` and a local root | **Done**: training already reads local data |
| DAgger rounds on rotated placements and near misses with `lerobot-rollout --strategy.type=dagger` | **To do**: after v5 is evaluated |

### Training recipe

| Item | Status |
|---|---|
| Train on trimmed data | **Done**: `train_act_50k_v5.sh` |
| Gate training on the data audit | **Done**: `train_act_50k_v5.sh` runs `audit.py` first |
| Keep ACT defaults: batch 8 or more, VAE on, lr 1e-5, chunk 100 | **Done**: `train_act_50k_v5.sh` |
| Train 5 to 10 epochs | **Done**: v5 is about 5.9 epochs. Note that this also changed from v4's 3.7, so v4 vs v5 has two causes |
| Save checkpoints often enough to compare by rollout | **Done**: every 5k steps |
| Turn on image augmentation (`--dataset.image_transforms.enable=true`) | **To do**: `train_act_50k_v5.sh` leaves it off on purpose, so v5 tests the trim alone. Its header names it the v6 candidate |
| Warm-start later runs with `--policy.pretrained_path` on old plus new data, lower LR | **To do** |
| Consider cloud ACT (L4 or A10G) for 7 to 10 epoch runs | **To do**: optional |
| SmolVLA fine-tune on the same trimmed data in the cloud, about $10 a run | **To do**: if v5 or v6 plateaus on rotations |

### Evaluation and checkpoint selection

| Item | Status |
|---|---|
| Fail any checkpoint that plans to wait on more than 5% of episode starts | **Done**: `audit.py --checkpoint` |
| Run offline predictions without the action key (no VAE path) | **Done**: `audit.py` passes only observations and task |
| Pick checkpoints by rollout, never by training or validation loss | **Done**: written into trials.md |
| Same placements for each checkpoint, Lego reset by hand | **Done**: trials.md protocol |
| Interleave checkpoints within one session, randomize order within each cell | **To do** |
| Score subgoals per trial: moved off rest, reached, grasped, lifted, placed, released | **To do**: add columns to trials.md |
| Re-run the incumbent checkpoint first each session as a drift control | **To do** |
| Report counts with exact intervals; treat gaps under about 5 of 9 as ties | **To do** |
| Add a gripper check to the offline probe: does a predicted chunk close the gripper? | **To do** |
| Held-out L1 around gripper transitions, as a tie-breaker only | **To do**: optional |

### Gotchas to check every session

| Item | Status |
|---|---|
| Load with `--policy.path`, never `--policy.type` plus a pretrained path | **Done**: rollout scripts use `--policy.path` |
| Temporal ensembling with `n_action_steps=1` and coefficient 0.01 | **Done**: `rollout_v4_50k_temporal_30s.sh` |
| Loop holds about 30 Hz | **Done**: logged per trial in trials.md |
| Re-check camera indices and serial port | **To do**: run `lerobot-find-cameras` and `lerobot-find-port` before each session |
| Cameras use MJPG, not YUYV | **To do**: check once per setup |
| Recompute stats after any dataset edit and confirm the checkpoint's processor stats match | **Partly**: `audit.py` checks stats count only |
| Record `lerobot-info` with each training run | **To do** |
| Only one lab process on the hardware at a time | **Done**: AGENTS.md rule |
