# Evaluation, checkpoint selection and known gotchas for real-robot ACT (LeRobot, SO-101), no simulator

Researched 2026-11-17. Scope: offline proxies, on-robot protocol and statistics, LeRobot/ACT pitfalls, data audits and smoke tests. Where a claim comes from a secondary summary rather than the primary paper or repo, it says so.

## Offline evaluation proxies: how well do they predict real success?

### Takeaway
Raw held-out action MSE/L1 predicts real-robot success poorly. It roughly separates "works at all" from "broken", but it ranks close checkpoints unreliably and can even rank them backwards. Restricting the error to task-critical segments (CI-MSE, 2026) helps a lot. No offline metric replaces robot rollouts. Without a simulator, the most useful cheap checks are behavioural: run the policy on recorded start frames and inspect the planned motion (like the lab's chunk-motion probe). They catch catastrophic failures such as freezing, not fine ranking.

### Cited findings
- SIMPLER (Li et al., arXiv 2405.05941, May 2024) states that for imitation learning "validation MSE is not a good proxy for a policy's real-world performance". On Google Robot tasks, validation MSE scored MMRV 0.375 and Pearson r 0.308 against real success. SIMPLER Visual Matching scored MMRV 0.056 and r 0.924. — [SIMPLER, arXiv 2405.05941](https://arxiv.org/html/2405.05941)
- Metric definitions (useful for auditing your own proxy against robot results). MMRV (Mean Maximum Rank Violation) averages each policy's worst-case rank violation, with each mis-ranking weighted by its real-world performance gap. Pearson r measures linear agreement between proxy and real success. — [SIMPLER](https://arxiv.org/html/2405.05941)
- Critical Interval MSE (Huang, Zheng, Chen, You, Gao; arXiv 2606.29898, 2026). CI-MSE scores error only on task-critical segments and adds "action-alignment procedures that better match rollout-time behavior". Across many checkpoints it reached Spearman rho -0.87 against rollout success, versus -0.61 for raw MSE. The authors say they "do not claim that offline validation can replace gold-standard robot rollouts". — [CI-MSE, arXiv 2606.29898](https://arxiv.org/pdf/2606.29898); project page https://ci-mse.github.io/
- Further CI-MSE numbers come from a secondary research-log summary, not checked against the PDF. The 27 checkpoints span three VLA families. On data-scale variants (20% to 100% of the data), raw MSE had rho +0.90 against success, meaning it ranked the variants backwards, while CI-MSE stayed at -0.90. On real tasks, pour-water reached r -0.99 and arrange-mouse rho -1.00. Fold-towel and unplug degraded when validation demos came from a different operator or protocol than training. The summary also recommends treating small proxy gaps as ties and auditing proxies with MMRV rather than Pearson. — [secondary summary (HF space, read 2026-08-07)](https://mcobzarenco-fontaine-blog.static.hf.space/papers/offline-validation.html)
- Train Offline, Test Online (TOTO, arXiv 2306.00942, 2023) found that real reward rises as validation error falls, and that an overtrained policy showed both higher validation error and a large drop in real reward. The authors caution that offline metrics "should not fully guide" development but signal whether a policy "might achieve any success". — [TOTO, arXiv 2306.00942](https://arxiv.org/pdf/2306.00942) (via search snippet)
- Validation loss on expert demos "is often poorly correlated with real-world performance". This framing is repeated across 2025-2026 real-to-sim evaluation papers. — [Real-to-Sim policy evaluation, arXiv 2511.04665](https://arxiv.org/html/2511.04665v2); [Real-is-Sim, arXiv 2504.03597](https://arxiv.org/html/2504.03597v1)
- A LeRobot offline-eval bug matters if you compute held-out loss or predicted actions with the policy in a mode that sees `action`. Commit "fix(act): disable VAE during offline inference (#1588)" says the presence of an `action` field in a dataset batch wrongly triggered ACT's VAE encoder path. The original paper skips variational inference at test time. Seen on a Gitea mirror of the repo; confirm against upstream. — [mirror of lerobot commit #1588](https://gitea.d-robotics.cc/chao.wu/Lerobot/commit/4c8f0020551bc6ba30ac2d7f54906aeed55ab85d)
- ACT inference uses the latent style variable z "set to zero during inference". — [LeRobot ACT docs](https://huggingface.co/docs/lerobot/en/act)

### Inferences
- Rank checkpoints with offline loss only within one training run and only to rule out clearly broken ones. Do not use it to pick between close checkpoints, especially across runs with different data mixes (v3 vs. v4 here). The CI-MSE result says data-scale changes are exactly where raw MSE can invert.
- A cheap no-sim CI-MSE analogue is to recompute action L1 only on frames around grasp and release (gripper-command transitions) and the approach segment, on held-out episodes. Then check whether the ranking differs from full-episode L1.
- Behavioural offline checks are better at catching freezing. Examples: chunk motion magnitude from start frames (the lab's probe), the fraction of start frames whose first chunk moves the arm more than a few degrees, and gripper open/close events in the predicted chunk. Held-out MSE can look fine for a policy that predicts "stay at rest" when many training frames are static, because those frames have near-zero error.
- When computing offline predictions, make sure ACT runs in inference mode with z = 0 and no action input (see #1588). Otherwise held-out loss is optimistic and not what the robot sees.
- Keep validation episodes from the same operator and protocol as the training data, or report them separately. CI-MSE correlations fell under operator mismatch.

### Gaps
- No primary source found that measures offline-proxy vs. real-success correlation specifically for ACT on SO-100/SO-101.
- I did not read the CI-MSE PDF in full. Its exact critical-interval definition and alignment procedures need a direct read before reimplementing.
- No published work validates "chunk motion on recorded starts" as a proxy. It is a practitioner check, sound as a smoke test, with no correlation study behind it.

## On-robot evaluation protocol and statistics

### Takeaway
Nine trials only detect very large differences. A 2/9 checkpoint and a 7/9 checkpoint are borderline significant (Fisher p ≈ 0.057, Barnard p ≈ 0.031). 2/9 against 6/9 is not significant. Use paired, interleaved A/B on the fixed 9-condition grid, report counts with exact intervals, score subgoals (reach, grasp, lift, place) for more signal per trial, and use a sequential test (STEP, or N-SCORE for partial credit) to stop early when one policy clearly wins.

### Cited findings
- Kress-Gazit et al., "Robot Learning as an Empirical Science: Best Practices for Policy Evaluation" (arXiv 2409.09491, Sept 2024, TRI/Cornell):
  - Report counts, not only percentages. Pairs with the same rates can support different conclusions: 150/30 vs. 110/60 separates, 5/1 vs. 6/3 does not.
  - A Bayesian comparison (uniform prior, Bernoulli likelihood) of 15/18 vs. 11/17 gave about a 0.11 probability that B beats A. 13/20 vs. 14/20 supported no conclusion.
  - Interleave rollouts of all policies in one session, blind to the evaluator. Use the same evaluator throughout, separate from the demonstrator.
  - Match initial conditions with overlays or scene marks, and state how evaluation conditions relate to the training distribution.
  - After a lab reorganisation, a policy that had scored 13/20 scored 0/8 on "matched" conditions. This exposed a distribution shift.
  - Define success in detail before evaluating. Use per-task subgoal rubrics: one policy succeeded at the full task 4/23 but grasped and flipped 23/23.
  - Report failure modes with frequencies. For example, policy A failed at grasping in 6 of 7 failures, policy B at placement in 6 of 6.
  - The paper gives no minimum trial count. — [arXiv 2409.09491](https://arxiv.org/html/2409.09491v1)
- Vincent et al., "How Generalizable Is My Behavior Cloning Policy? A Statistical Approach to Trustworthy Performance Evaluation" (arXiv 2405.05439, May 2024, TRI):
  - Gives worst-case lower bounds on success rate from few rollouts, with the uniformly most accurate binomial bound, which is always tighter than Clopper-Pearson.
  - At 95% confidence with n = 50: 38/50 gives p ≥ 0.641, and 4/50 gives p ≥ 0.035.
  - Recommendations: fix alpha and the sampling rule in advance, keep initial conditions i.i.d., do not stop based on outcomes unless you use confidence sequences, and report per-policy bounds.
  - Code: binomial_cis / github.com/TRI-ML/stochastic_verification. — [arXiv 2405.05439](https://arxiv.org/html/2405.05439v2)
- STEP, "Is Your Imitation Learning Policy Better than Mine? Policy Comparison with Near-Optimal Stopping" (Snyder et al., arXiv 2503.10966, 2025, TRI/Princeton). A sequential test for binary success with tunable Type-I/II error and a prior "risk budget". It needs up to 32% fewer trials than earlier sequential methods. — [arXiv 2503.10966](https://arxiv.org/html/2503.10966v1); [project page](https://tri-ml.github.io/step)
- "Beyond Binary Success: Sample-Efficient and Statistically Rigorous Robot Policy Comparison" (N-SCORE; Snyder, Badithela, Matni, Pappas, Majumdar, Itkina, Nishimura; RSS 2026). Extends sequential comparison to partial-credit progress and continuous metrics. Reports up to 70% less evaluation effort than batch methods and up to 50% less than binary sequential methods (abstract figures). — [arXiv 2603.13616](https://arxiv.org/pdf/2603.13616); [RSS 2026 proceedings](https://roboticsproceedings.org/rss22/p076.html)
- Badithela et al., "Reliable and Scalable Robot Policy Evaluation with Imperfect Simulators" (arXiv 2510.04354, Oct 2025). Uses prediction-powered inference to correct simulator bias with paired real and sim trials, saving about 20-25% of hardware trials. It notes that most papers report about 20-40 trials. This needs a sim, so it does not apply directly here. — [arXiv 2510.04354](https://arxiv.org/html/2510.04354v1)
- Practitioner advice on an SO-101 ACT forum thread (Aug 2026): evaluate covered and held-out positions separately, about 10 rollouts per bucket. Verify that calibration and camera placement match recording before blaming the model, since a viewpoint or calibration shift gives a repeatable offset that more demos will not fix. — [HF forum thread 178517](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- Reference points for SO-101 ACT success:
  - The same forum reply says ACT/ALOHA got 96/84/64/92% with 50 demos per task, and an SO-ARM101 60-demo experiment got 60% over 20 trials, with failures clustered in sparse regions. — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
  - Classmethod (Mar 2026): 50 episodes, 100k steps, 9/10 on CUDA at about 30 Hz vs. 4/10 on Mac MPS at about 15 Hz, 10 trials each. — [Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)
- Computed for this note with scipy (not from a source), 95% Clopper-Pearson intervals:
  - 0/9: [0, 0.34]
  - 2/9: [0.03, 0.60]
  - 5/9: [0.21, 0.86]
  - 9/9: [0.66, 1]
  - 10/20: [0.27, 0.73]
  - 9/10: [0.56, 1.00]
- Computed for this note with scipy, two-sided exact tests on 9 trials per arm:
  - 2/9 vs. 7/9: Fisher p = 0.057, Barnard p = 0.031
  - 2/9 vs. 6/9: Barnard p = 0.073
  - 2/9 vs. 9/9: Fisher p = 0.002

### Inferences
- With 9 trials per checkpoint, only treat differences of about 5/9 or more as real. Smaller gaps are ties. To separate, say, 50% from 75%, you need tens of trials per arm, or a sequential test.
- The fixed 3 x 3 grid suits a paired design: run A and B on the same (spot, orientation) cell back to back, randomise the order within each cell, and blind the operator if possible. Analyse with a paired (McNemar-style) or sequential test. Kress-Gazit's guidance on interleaving and matched conditions supports this.
- Record partial credit per trial (moved off rest, reached, grasped, lifted, placed, released) as Kress-Gazit's rubric suggests. N-SCORE can use these directly. The lab's "frozen at rest" failure becomes a distinct, countable failure mode instead of a plain 0.
- Re-run the incumbent checkpoint at the start of a session as a control. This catches environment drift, such as the 13/20 to 0/8 shift after the lab reorganisation, before you blame the new checkpoint.

### Gaps
- I did not read the STEP or N-SCORE papers in full for worked trial-count tables. Use their code or project page to plan stopping rules.
- I found no RoboArena-style paired-evaluation write-up with numbers for hobby-scale setups. RoboArena was not searched in depth.

## Known LeRobot/ACT gotchas

### Takeaway
The pitfalls that most often turn a well-trained ACT into a bad or frozen rollout:
- control-loop rate below the recording fps (MPS often manages only about 15 Hz);
- default open-loop chunk execution (100 steps between predictions);
- static or idle frames at episode starts;
- normalization or processor mismatches that run silently;
- loading with `--policy.type` instead of `--policy.path`;
- camera keys, indices or formats that differ from training;
- calibration or viewpoint drift.

### Cited findings
- **Chunk execution and temporal ensembling.**
  - LeRobot v0.6.1 ACT defaults are `chunk_size` = `n_action_steps` = 100 with no temporal ensembling, so a new chunk is predicted only every 100 steps. A stub test of 205 `select_action()` calls triggered predictions only at steps 0, 100 and 200. — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
  - `temporal_ensemble_coeff` requires `n_action_steps=1`, and the config raises NotImplementedError otherwise. The original ACT coefficient is 0.01. The code comment says the oldest action gets the largest weight and a negative value favours newer actions. — [Particula blog, via search snippet](https://particula.tech/blog/lerobot-n-action-steps-vs-chunk-size); the page returned HTTP 429, so confirm in `configuration_act.py`. The 0.01 / n_action_steps=1 combination also appears in an [ALOHA jitter write-up (CSDN, unverified)](https://adg.csdn.net/696f365b437a6b403369a859.html).
  - Upstream fix history: "Fix ACT temporal ensembling (#319)". — [mirror commit](https://gitea.d-robotics.cc/chao.wu/Lerobot/commit/c0101f094805b03bb679731516eb5bcbf053b678)
- **Loop rate vs. recording fps.**
  - Classmethod, Mar 2026, LeRobot v0.4.4, SO-ARM101: on Mac MPS, ACT plus two cameras ran at about 15 Hz against a 30 Hz training rate, scored 40% with a jerky initial movement, and the same model scored 90% on CUDA at about 30 Hz. CPU ran at about 8 Hz. The author attributes the gap to the rate mismatch, which is a hypothesis, not a controlled test. `--display_data=true` dropped recording from 30 Hz to 9.8 Hz. — [Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)
  - Dataset timestamps are frame_index / declared fps, not wall-clock time. A 5.6 Hz capture declared at 30 fps stretches time: about 2.50 s of wall-clock sampling became about 0.467 s of dataset time. Compare a no-policy teleop run with the ACT rollout to see whether slowness is in the policy path. — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- **Loading the checkpoint.** `--policy.type=act` plus `pretrained_path` skips pre- and post-processing, "so actions never reach the control loop". Use `--policy.path`. Also check that `pretrained_model/` did not end up nested after rsync. — [Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)
- **Normalization lives in processors now.** LeRobot policies "no longer have built-in normalization layers embedded in their weights". It is handled by external PolicyProcessorPipeline components, and a migration script (`migrate_policy_normalization.py`) exists for old checkpoints. — [LeRobot docs: backward compatibility](https://huggingface.co/docs/lerobot/backwardcomp). Processor or normalization mismatches "can train and run without an error while degrading results". — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- **Zero-variance stats.** A constant feature gets std = 0, and normalizing it yields Inf. This is silent in most code paths but can break task-conditioned training and dataset mixing. Found in 4 of 5 popular LeRobot datasets (for `task_index`). — [Traceplane audit, 2026-04-23 (vendor blog; methodology partly described)](https://traceplane.pages.dev/blog/we-audited-5-lerobot-datasets)
- **Editing datasets and stats.** The `edit_dataset` docs (Trossen) describe delete, merge and validate, with in-place overwrite unless an output directory is given. They do not mention recomputing stats. — [Trossen edit_dataset docs](https://docs.trossenrobotics.com/trossen_arm/main/tutorials/lerobot/edit_dataset.html). Merge pitfalls are covered at [Particula: dataset merge what breaks](https://particula.tech/blog/lerobot-dataset-merge-what-breaks) (not fetched).
- **Idle frames at episode start.**
  - Open LeRobot PR #3096 proposes a `trim_episode_start` edit op to remove startup or warm-up seconds. Merge status is unverified. — [PR #3096 mirror](https://github-users.yhajoa.workers.dev/huggingface/lerobot/pull/3096)
  - An older `EpisodeAwareSampler` takes `drop_n_first_frames`. — [sampler.py mirror](https://gitea.d-robotics.cc/chao.wu/Lerobot/src/commit/835f0eddfabc2bbf48b68094c4a2551fb4d273b3/src/lerobot/datasets/sampler.py)
  - One community SO-101 dataset found pre-teleop dead air made up 12.0% of frames and excluded those frames as chunk starts. — [claru dataset page](https://claru.ai/datasets/parv-09-phi-so101-8bin-v1-trim)
  - A Daft example finds idle stretches from per-frame joint-state motion. — [Daft motion trimming](https://docs.daft.ai/en/stable/examples/motion-trimming-physical-ai/)
- **Cameras.**
  - Camera names must match the observation keys used in training, and ports and indices are machine-specific. — [model card](https://huggingface.co/robododo/frozen_act_policy)
  - macOS camera indices and serial port names change between connections. Re-check with `lerobot-find-cameras` and `lerobot-find-port` each session. — [Classmethod](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/)
  - A UVC camera left to auto-negotiate may pick YUYV: about 147 Mbps vs. about 9 Mbps for MJPG at 640x480 and 30 fps, causing frame drops on shared USB 2.0 (LeRobot issue #4084, cited secondhand). — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- **Calibration.** Re-run calibration when movements are offset. — [LeRobot troubleshooting (mintlify mirror)](https://www.mintlify.com/huggingface/lerobot/resources/troubleshooting)
- **Frozen at neutral under async inference.** SmolVLA (issue #2374) and Pi0.5 (issue #2356) show this, with the robot stuck at neutral while the server keeps producing actions. The cause is on the client-side execution path, not ACT. — [#2374](https://github.com/huggingface/lerobot/issues/2374); [#2356 mirror](https://gsmarenas.netlify.app/host-https-github.com/huggingface/lerobot/issues/2356)
- **Version.** Record `lerobot-info` output. Issue #4168 reported 66% ACT on ALOHA with v0.6.1. — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- **Coverage over count.** LeRobot issue #545 reported no clear gain beyond 120 episodes on unseen combinations (cited secondhand). — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- **Jitter.** One author attributes LeRobot inference jitter partly to noisy demos and to jumps at chunk boundaries, and suggests mean filtering or interpolation. — [Open Robotics Discourse, Piper arm](https://discourse.openrobotics.org/t/optimization-of-piper-robotic-arm-motion-control-via-lerobot-transplantation/52268)

### Inferences
- A plausible mechanism for the lab's frozen-at-rest checkpoint, not confirmed by any source. If episodes start with idle frames at the rest pose, the policy learns that "rest pose plus empty scene" maps to "stay still". With `n_action_steps=100`, that motionless chunk is replayed open-loop for 100 steps (about 3.3 s at 30 fps). The next observation is again the rest pose, so the cycle repeats for the whole rollout. Two checks: measure the idle fraction at episode starts in the v4 training data versus v3, and test whether the same checkpoint moves with `n_action_steps` around 10-25 or with temporal ensembling.
- On the Mac mini, measure the actual rollout loop Hz. If it is well below the recording fps, either the policy runs slower in time than it was trained, or (with chunking) actions are spaced differently from training. Either can explain degraded or jerky behaviour.
- After any dataset edit (deleting episodes, trimming starts, merging), recompute and diff `meta/stats.json` and check that the trained checkpoint's processor stats match the dataset used for the probe.

### Gaps
- I did not find a primary LeRobot GitHub issue for "ACT frozen at rest after clean training" specifically. GitHub search through the web tool returned mostly mirrors.
- I could not fetch the Particula chunk_size article (HTTP 429). Its claims come from a search snippet, so verify in the installed `configuration_act.py`.
- I found no source on MPS-specific numerical issues (op fallbacks, nondeterminism) for ACT training, beyond inference speed. The `PYTORCH_ENABLE_MPS_FALLBACK` behaviour was not researched.
- I found no source confirming the exact CLI or API of a `recompute_stats` option in `lerobot-edit-dataset` for the current LeRobot version.
- Gripper not releasing: no specific source found in this pass.

## Recommended automated data audits and post-training smoke tests

### Takeaway
Practitioners and tools converge on a few checks:
- Before training, audit metadata against data, stats sanity (no NaN, Inf or zero std), fps and timestamp consistency, frame counts and frozen frames, and idle-start fraction.
- After training, check that the model loads through the same path as rollout, that the action rate matches the recording fps, and that it behaves sensibly on recorded start frames (moves, opens and closes the gripper).
- Then gate robot time on these checks plus a short, paired A/B against the incumbent.

### Cited findings
- The Traceplane checker (about 25 checks) covers:
  - metadata consistency: `info.json` against episodes, fps, features and action spec;
  - manifest integrity: no duplicate IDs, no zero-length episodes;
  - stats sanity: no NaN, Inf or zero variance, and the schema matches the features;
  - parquet readability and schema drift;
  - video file count and corruption;
  - dimension agreement between metadata and data.

  — [Traceplane audit (2026-04-23, vendor)](https://traceplane.pages.dev/blog/we-audited-5-lerobot-datasets)
- Diagnostic order from the Aug 2026 forum reply:
  1. Record the version.
  2. Confirm which command produced the slow-loop warning.
  3. Compare no-policy teleop against the ACT loop rate.
  4. Inspect episodes for frame counts and frozen or repeated frames.
  5. Evaluate covered and held-out positions separately.
  6. Verify calibration and camera geometry.
  7. Only then examine ACT config, checkpoint and version.

  — [HF forum thread](https://discuss.huggingface.co/t/what-is-the-expected-success-rate-for-a-act-trained-model-using-50-episodes/178517)
- Idle-motion detection: threshold per-frame joint-state motion to get an active flag and a trim window per episode. — [Daft motion trimming](https://docs.daft.ai/en/stable/examples/motion-trimming-physical-ai/)
- Pre-registration discipline: fix alpha, the tightness target and the sampling rule before collecting rollouts, and keep conditions i.i.d. — [Vincent et al. 2024](https://arxiv.org/html/2405.05439v2). Define success criteria in advance and visualise initial conditions. — [Kress-Gazit et al. 2024](https://arxiv.org/html/2409.09491v1)
- Offline critical-segment validation as a cheap CPU screen over existing prediction dumps. — [CI-MSE](https://arxiv.org/pdf/2606.29898); [secondary summary](https://mcobzarenco-fontaine-blog.static.hf.space/papers/offline-validation.html)

### Inferences
Assembled from the findings above for this bench. Not a published checklist.

**Pre-training audit (script, fails the run):**
1. `info.json` fps equals the camera fps and the robot loop fps that were used, and the median timestamp delta is about 1/fps per episode.
2. No NaN, Inf or zero std in `stats.json` for action and state features, and stats are recomputed after any edit.
3. Per-episode idle-start and idle-end fraction (joint-motion threshold), with a warning if the median is above about 5-10% or it changed against the previous dataset version.
4. Duplicate or frozen video frames (identical consecutive frames).
5. Camera keys and resolutions match the rollout config.
6. Gripper range in actions: each episode contains both open and close.
7. Spatial coverage plot of the bowl and Lego starts against the 3 x 3 test grid.

**Post-training smoke tests (before robot time):**
1. Load via `--policy.path` with the saved processors and print the stats they carry. Diff them against the dataset stats.
2. Run in eval mode with no action input (z = 0) on the first frame of every held-out episode and of each test-grid cell, if photos or recordings exist. Assert that the first chunk's joint displacement exceeds a threshold for at least most starts. This is the lab's frozen-probe.
3. Assert that the gripper command crosses open/close within the first N chunks of an open-loop replay.
4. Report held-out L1 on full episodes and on critical segments (around gripper transitions). Treat small differences as ties.
5. Measure policy inference latency on the Mac mini and the expected loop Hz.

**Robot gate:** paired and interleaved A/B on the 3 x 3 grid against the incumbent, with a subgoal rubric, reported as counts with exact intervals, plus optional sequential stopping (STEP or N-SCORE).

### Gaps
- I found no published, maintained LeRobot "dataset lint" built into the official CLI with documented checks. `lerobot-edit-dataset` validate and Traceplane are the closest. Traceplane is a third-party vendor tool tested on only 5 datasets.
- I found no community source quantifying how often idle-start frames cause frozen ACT rollouts. The mechanism above is an inference.
