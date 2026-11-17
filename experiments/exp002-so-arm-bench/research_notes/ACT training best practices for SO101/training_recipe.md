# Training recipes for imitation-learning policies on small SO-101 datasets with LeRobot (ACT, SmolVLA, Diffusion Policy, pi0/pi0.5)

Research date: 2026-11-17. Bench context: SO-101, ~125 demos (~109k frames) at 30 fps, two 640x480 cameras, one pick-and-place task. Current run: ACT from scratch, batch 8, lr 1e-5, 50k steps, Apple MPS at ~1.8 steps/s (~8 h).

## Recommended ACT hyperparameters (LeRobot defaults vs ACT paper; effect of batch size)

### Takeaway
The current run uses the LeRobot defaults, and those match the ACT paper (lr 1e-5, batch 8, chunk 100, KL weight 10, dropout 0.1). The main thing to change is training length: 50k steps at batch 8 is about 3.7 epochs of 109k frames, below the 5-10 epochs LeRobot's hardware guide calls typical. Raising the batch size is mainly a speed lever. No primary source shows a success-rate gain from it.

### Cited Findings
- LeRobot `ACTConfig` defaults on `main`: `chunk_size=100`, `n_action_steps=100`, `n_obs_steps=1`, `vision_backbone="resnet18"`, `pretrained_backbone_weights="ResNet18_Weights.IMAGENET1K_V1"`, `dim_model=512`, `n_heads=8`, `dim_feedforward=3200`, `n_encoder_layers=4`, `n_decoder_layers=1`, `use_vae=True`, `latent_dim=32`, `n_vae_encoder_layers=4`, `temporal_ensemble_coeff=None`, `dropout=0.1`, `kl_weight=10.0`, `optimizer_lr=1e-5`, `optimizer_weight_decay=1e-4`, `optimizer_lr_backbone=1e-5` — [configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py)
- `n_decoder_layers=1` follows the original code. The config comment says "there is a bug in the code that means only the first layer is used," so LeRobot sets it to 1 to "match the original implementation" — [configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py)
- Temporal ensembling: the config comment says "the value used in ACT when temporal ensembling is enabled is 0.01". `n_action_steps` must be 1 when ensembling is on, and validation raises an error otherwise. `n_action_steps` must also be no greater than `chunk_size` — [configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py)
- ACT in LeRobot has no LR scheduler: `get_scheduler_preset()` returns `None`. The optimizer is AdamW with `lr`, `weight_decay` and `fused`, so the LR stays constant for the whole run — [configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py)
- ACT paper (Zhao et al., 2023), Table III: lr 1e-5, batch size 8, 4 encoder layers, 7 decoder layers, feedforward 3200, hidden 512, 8 heads, chunk size 100, beta (KL weight) 10, dropout 0.1, ResNet18 backbone, Adam. The paper lists no step or epoch count. It uses 50 demos per real task (100 for Thread Velcro) and reports "training takes around 5 hours on a single 11G RTX 2080 Ti GPU" — [ACT paper, arXiv 2304.13705](https://arxiv.org/html/2304.13705)
- ACT paper ablations: success rose from 1% at chunk k=1 to 44% at k=100, then tapered slightly, with dips at k=200/400. Temporal ensembling added about 3.3% for ACT. Removing the CVAE barely mattered on scripted data, but with human data success fell from 35.3% to 2% ("the CVAE objective is crucial when learning from human demonstrations") — [ACT paper](https://arxiv.org/html/2304.13705)
- The ACT paper defines temporal-ensemble weights as w_i = exp(-m*i), where "a smaller m means faster incorporation" of new observations. Table III gives no value for m. The 0.01 figure comes from the LeRobot comment and the original code — [ACT paper](https://arxiv.org/html/2304.13705); [configuration_act.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/policies/act/configuration_act.py)
- LeRobot ACT docs: "Start with defaults", "Expect a few hours for 100k training steps on a single GPU", and "Start with batch size 8 and adjust based on your GPU memory." They describe ACT as about 80M params that "often achieves high success rates with just 50 demonstrations" — [LeRobot ACT docs](https://huggingface.co/docs/lerobot/act)
- LeRobot hardware guide: "Robotics imitation learning typically converges in 5–10 epochs over the dataset, not hundreds of thousands of raw steps". It gives `steps_per_epoch = ceil(total_frames / (num_gpus × batch_size))` — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- Same guide: if you shorten training, also shorten the LR schedule with `--policy.scheduler_decay_steps≈--steps`. This applies to policies that have a scheduler (SmolVLA, pi0). ACT has none — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- Seeed Studio guide (updated 2026-10-22): about 80,000 steps as a starting point for 50 episodes. Keep the LR unchanged when you change batch size, and scale steps inversely with batch size to hold epochs constant (batch 8 at 80k equals batch 4 at 160k). Use batch ~4 on ≤8 GB VRAM and ~16 on >12 GB — [Seeed Studio wiki, ACT training](https://wiki.seeedstudio.com/robotics/hands_on_act_training/)
- Community data points (anecdotal, n=1 each). A classmethod.jp write-up: 50 episodes, batch 8, 100k steps, 40% (4/10) success running on Mac MPS. A French lab write-up recommends batch 64 for ACT (minimum 16). A SO-101 cloth-folding project found chunk_size 10 worked far better than 100 for its task — [classmethod.jp](https://dev.classmethod.jp/en/articles/lerobot-so-arm101-act-training-eval/); [Unistra IHA](https://innovation.iha.unistra.fr/books/robotique-open-source/page/machine-learning-lerobot-avec-so-arm101); [tabithako](https://tabithako.github.io/projects/policy-training)
- SmolVLA paper baseline: ACT trained from scratch, single-task, on 50 SO-100 demos scored 70% pick-place, 50% stacking and 25% sorting. On SO-101 pick-place-lego it scored 70% in-distribution and 40% out-of-distribution. Training steps for the ACT baseline are not reported — [SmolVLA paper, arXiv 2506.01844](https://arxiv.org/html/2506.01844v1)

### Inferences
- Epoch arithmetic for this bench (109k frames): 50k × 8 = 400k samples ≈ 3.7 epochs. 100k × 8 ≈ 7.3 epochs, which sits inside the 5-10 epoch band. At batch 32, 5-10 epochs is about 17k-34k steps.
- At 1.8 steps/s on MPS, 100k steps at batch 8 would take about 15.5 h. That is the strongest argument for cloud training if you want to go to ~7 epochs.
- Batch 8 vs larger. The ACT paper and LeRobot both use 8 with lr 1e-5 and no scheduler. Seeed advises keeping the LR fixed and cutting steps in proportion when you raise the batch. Nobody here reports a controlled success-rate comparison across batch sizes, so treat a larger batch as a throughput change rather than a quality change. If you use 32-64, a modest LR increase (for example 2e-5 to 4e-5) is a reasonable experiment, but no source here validates it for ACT.
- Temporal ensembling (`--policy.n_action_steps=1 --policy.temporal_ensemble_coeff=0.01`) means a forward pass every control step, 30 per second at 30 fps. That matters for latency on MPS. A cheaper middle ground is a shorter `n_action_steps` (for example 20-50) with no ensembling. That suggestion is not benchmarked in any source.
- `kl_weight=10` and `dropout=0.1` are unchanged since the paper. No source found argues for changing them for SO-100-class tasks.

### Gaps
- No primary source gives an official recommended step count for SO-100/SO-101 ACT. The "100k steps" figure is from the docs' timing tip, and "80k for 50 episodes" is from Seeed, a vendor guide.
- No controlled study found on batch size vs success rate for ACT on real robots.
- The parameter count differs: LeRobot docs say about 80M, the SmolVLA paper says about 80M, and the user observes 52M. The gap may come from counting the unused VAE encoder or the decoder layers. Not verified.

## Image augmentation (dataset.image_transforms) for robustness to lighting and camera changes

### Takeaway
LeRobot ships a color-jitter, sharpness and small-affine augmentation pipeline that is **off by default**. Turn it on with `--dataset.image_transforms.enable=true`. It contains no random crop. No primary source found quantifies its effect on real-robot ACT success, but it is the built-in tool aimed at lighting and color shifts.

### Cited Findings
- `ImageTransformsConfig` defaults: `enable=False` ("Set this flag to `true` to enable transforms during training"), `max_num_transforms=3` (the most transforms sampled per frame), and `random_order=False` (Torchvision's suggested order is used) — [LeRobot transforms.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/transforms/transforms.py)
- Default transforms, each `weight=1.0`: brightness `ColorJitter (0.8, 1.2)`, contrast `ColorJitter (0.8, 1.2)`, saturation `ColorJitter (0.5, 1.5)`, hue `ColorJitter (-0.05, 0.05)`, sharpness `SharpnessJitter (0.5, 1.5)`, and affine `RandomAffine degrees (-5, 5), translate (0.05, 0.05)`. There is no crop transform among the defaults. All use torchvision.transforms.v2 — [LeRobot transforms.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/transforms/transforms.py)
- `DatasetConfig` holds `image_transforms: ImageTransformsConfig`, so the CLI path is `--dataset.image_transforms.*`. The same config also has `episodes`, `exclude_episodes` and `eval_split` — [LeRobot configs/default.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/configs/default.py)
- The repo also has `src/lerobot/scripts/lerobot_imgtransform_viz.py`, a visualizer for previewing the transforms, and `examples/dataset/use_dataset_image_transforms.py` (found in a GitHub code search, files not read) — [lerobot repo](https://github.com/huggingface/lerobot)

### Inferences
- How to enable: `--dataset.image_transforms.enable=true`, optionally with `--dataset.image_transforms.max_num_transforms=3` and `--dataset.image_transforms.random_order=true`. These flag names follow from draccus's nesting of the dataclass fields above. The exact strings were not checked against a doc page, so run `lerobot-train --help` to confirm.
- Fit to the bench problem. Brightness, contrast, saturation and hue jitter target lighting and white-balance changes, such as a new room or a different time of day. The ±5° and ±5% affine gives a little robustness to small camera bumps. It will not cover a re-mounted camera or a new viewpoint (for example the C920 move in PR #24). That needs demos recorded from the new pose.
- Because augmentation is disabled by default, the current run very likely has none. Turning it on is one of the cheapest changes to try. Expect training loss to sit slightly higher, and judge the result by rollouts.

### Gaps
- No primary source found measuring the effect of LeRobot's image_transforms on ACT real-robot success under lighting change.
- No source checked whether a random-crop transform can be added through config (for example a custom `type`) without code changes.

## Overfitting, epochs, and checkpoint selection (training loss vs validation loss vs rollouts)

### Takeaway
Neither training loss nor validation loss reliably picks the best checkpoint in robot imitation learning. Hugging Face's own experiments and Robomimic both show validation loss rising or flat while success keeps improving. Save several checkpoints and pick by real rollouts. LeRobot now has `--dataset.eval_split` for held-out episodes, which works as a sanity check, not a selector.

### Cited Findings
- HF study (Barannikov, 2024-12-01). ACT on Aloha Transfer Cube: 50 episodes, 100k steps, 3 seeds, 50 sim rollouts every 10k steps. Validation loss plateaued (0.2289, then -2.04% and -2.03% at 70k and 100k) while success rose from 53.33% at 30k by +12.94% and +16.67%. Diffusion on PushT: validation loss rose +134.57% from 20k to 50k while success rose +55.27%. Between 50k and 90k, validation loss fell while success also fell. Conclusion: "it is clear that we should not use validation loss to early stop training" — [HF blog: validation loss in robotics](https://huggingface.co/blog/m1b/validation-loss-robotics)
- The same post cites Robomimic: early-stopping on validation loss can be "50 to 100% worse" than the best checkpoint. It recommends a few evaluations plus frequent qualitative checks (smoother motion, new skills appearing) — [HF blog](https://huggingface.co/blog/m1b/validation-loss-robotics)
- Robomimic: the offline training objective "is only a surrogate for the true objective of interest", and policy performance "can change significantly from epoch to epoch" — [Robomimic paper (ar5iv)](https://ar5iv.labs.arxiv.org/html/2108.03298)
- ACT paper: "we load the policy that achieves the lowest validation loss and roll it out". The original ACT code selects by validation loss — [ACT paper](https://arxiv.org/html/2304.13705)
- LeRobot `DatasetConfig.eval_split: float = 0.0`, described as "Fraction of episodes held out per task for offline evaluation (0.0 = disabled)". It needs map-style datasets, not streaming — [LeRobot configs/default.py](https://raw.githubusercontent.com/huggingface/lerobot/main/src/lerobot/configs/default.py)
- A third-party blog says that in LeRobot v0.6.1 `eval_steps` defaulted to 0, so the held-out loss loop never ran. It also mentions a PR proposing `validation_fraction` and early stopping. This is secondary and possibly superseded by `eval_split` on main — [particula.tech](https://particula.tech/blog/which-robot-policy-checkpoint-to-deploy)
- Seeed: checkpoints are saved every 20k steps (`save_freq`) by default. "Evaluate an earlier checkpoint if later ones are underperforming or overfitting" — [Seeed Studio wiki](https://wiki.seeedstudio.com/robotics/hands_on_act_training/)
- CLIPort and BC-Z also report validation loss and error as poor proxies for task success. With multimodal actions, a different but valid action gets penalized. These come from a search summary and the papers were not read in full — [CLIPort](https://arxiv.org/pdf/2109.12098); [BC-Z](https://arxiv.org/pdf/2202.02005)

### Inferences
- Practical protocol for this bench. Save every 10k-20k steps, then roll out a fixed protocol (same N trials, same object positions) on 2-3 candidate checkpoints, for example 50%, 75% and 100% of training. Training loss is useful only to catch divergence or bugs (flat, or rising and rebounding).
- Use `eval_split` (for example 0.1, about 12 episodes) to spot gross overfitting. A sharp, sustained rise in held-out L1 is a warning sign. The HF results warn against early-stopping on it.
- Overfitting risk with ~125 demos and ~7 epochs looks low based on the HF ACT result (success still rising at 100k steps on 50 episodes). This is extrapolated from simulation.

### Gaps
- No real-robot SO-101 study found that tracks success against training steps for ACT.
- The exact behavior of `eval_split` (when it runs, what it logs) was not verified in the training script.

## From scratch vs fine-tuning a previous checkpoint (warm start, catastrophic forgetting)

### Takeaway
LeRobot supports warm starts with `--policy.pretrained_path` (weights only, step counter reset). `--resume=true` only continues the same run with the same config. Primary sources say nothing on forgetting for ACT. Common practice is to warm-start on the **combined** old and new dataset at a lower LR, not on new data alone.

### Cited Findings
- `--policy.path` loads weights **and** the checkpoint's config.json. `--policy.pretrained_path` loads weights only: features come from your dataset and stored settings reset to defaults, so `--policy.type` is required. This is documented on the pi0.5 page, but the mechanism is shared by `lerobot-train` — [LeRobot pi0.5 docs](https://huggingface.co/docs/lerobot/pi05)
- Resume: `lerobot-train --config_path=outputs/train/<run>/train_config.json --resume=true`. It uses the saved config and "additional command-line parameters are ignored". To change steps or batch, start a new run — [Seeed Studio wiki](https://wiki.seeedstudio.com/robotics/hands_on_act_training/)
- For fine-tuning an existing checkpoint, Seeed advises: "consider `1e-6` to `3e-6`, about 3–10 times lower" than ACT's 1e-5 — [Seeed Studio wiki](https://wiki.seeedstudio.com/robotics/hands_on_act_training/)
- A tutorial describes merging new targeted demos into the existing dataset and retraining, upsampling the new data via dataset weights — [Robotics Center: Data Flywheel](https://roboticscenter.ai/learn/paths/lerobot/unit-6-iterate)
- The SmolVLA paper shows pretraining helps on small data. SmolVLA without VLA pretraining averaged 40% (single-task) or 51.7% (multi-task), against 78.3% with pretraining, on SO-100 — [SmolVLA paper](https://arxiv.org/html/2506.01844v1)

### Inferences
- When a new environment or batch arrives, warm-start from the previous ACT checkpoint with `--policy.pretrained_path=<prev>/pretrained_model`, train on **all** data (old and new) for perhaps 1-3 epochs at lr 1e-5 or slightly lower, and compare by rollout against a from-scratch run. Replaying the old data is the standard guard against forgetting. Not verified for ACT in any source found.
- Normalization caveat. Stats come from the dataset. If the new data shifts the action or state ranges, a warm-started model sees different normalized targets, which argues for warm-starting on the combined dataset.
- A warm start on new data alone risks forgetting the old setup, which matters if you still need the old environment to work.

### Gaps
- No primary or controlled study found on catastrophic forgetting or warm-start vs scratch for ACT on real robots.
- Not checked whether `--policy.pretrained_path` works for ACT exactly as documented for pi05. It most likely does, since it is shared `PreTrainedConfig` logic, but this was not read in code.

## SmolVLA, pi0/pi0.5/pi0-FAST and Diffusion Policy on small datasets (results, compute, MPS)

### Takeaway
SmolVLA (450M) is the strongest published option at this data scale. On SO-100 with 50 demos per task it averaged 78.3% against ACT's 48.3% and pi0's 61.7%, and the docs recommend about 50 episodes and 20k steps (~4 h on one A100). pi0/pi0.5 need 24-40 GB+ and hours on A100/H100-class GPUs. Diffusion Policy has weak small-data evidence on SO-100 and slow inference.

### Cited Findings
**SmolVLA**
- 450M params, about 100M of them in the action expert. Pretrained on 481 community datasets, 22.9K episodes and 10.6M frames. Pretraining ran 200k steps at global batch 256, AdamW (β 0.9/0.95), 100-step warmup, then cosine decay from 1e-4 to 2.5e-6, on 4 GPUs. The whole project used about 30k GPU-hours. Images are resized to 512x512 — [SmolVLA paper](https://arxiv.org/html/2506.01844v1) (v1 submitted 2025-06-02)
- SO-100 real-world results (success %, pick-place / stacking / sorting / average): ACT single-task from scratch 70 / 50 / 25 / 48.3; pi0 (3.5B) 100 / 40 / 45 / 61.7; SmolVLA (0.45B) 75 / 90 / 70 / 78.3. SO-101 pick-place-lego: ACT 70 in-distribution / 40 out-of-distribution, SmolVLA 90 / 50. Each dataset had 50 demos (10 per each of 5 start positions). Real-world fine-tuning ran 200k steps (sim: 100k steps, batch 64) — [SmolVLA paper](https://arxiv.org/html/2506.01844v1)
- Caveat in the paper: the text says SmolVLA beats pi0 on SO-101, but Table 4 shows only ACT. The text also describes a three-dataset mix for SO-101 that conflicts with the table's "single-task" label — [SmolVLA paper](https://arxiv.org/html/2506.01844v1)
- Compared with pi0, SmolVLA is "around 40% faster to train" with 6x less memory. It is "designed to be trained on a single GPU and deployed on consumer-grade GPUs or even CPUs" — [SmolVLA paper](https://arxiv.org/html/2506.01844v1)
- Docs: record about 50 episodes. A 25-episode version "was not enough leading to a bad performance". The example fine-tune is `--policy.path=lerobot/smolvla_base --batch_size=64 --steps=20000`, and 20k steps "will roughly take ~4 hrs on a single A100 GPU". `--rename_map` is required to map your camera keys to `camera1/2/3`. Language conditioning: pass the same `--task` string at rollout as in recording. A Colab notebook is offered — [LeRobot SmolVLA docs](https://huggingface.co/docs/lerobot/smolvla)
- MPS: no official MPS benchmark for SmolVLA. Pass `--policy.device=mps` (accelerator docs). One community user reports about 20 h total for 16 SmolVLA runs plus 5 RT-1 runs on an M5 MacBook using MPS. mlx-smolvla is an MLX inference port (110.75 ms vs 204.58 ms for PyTorch-MPS per 50-action chunk on an M5 Pro), with training only as a LoRA preview — [LeRobot torch accelerators](https://huggingface.co/docs/lerobot/torch_accelerators); [Twu31/smolvla-cross-embodiment-mps](https://huggingface.co/Twu31/smolvla-cross-embodiment-mps); [HF forum: mlx-smolvla](https://discuss.huggingface.co/t/mlx-smolvla-smolvla-checkpoint-execution-and-validation-on-apple-silicon/179927)

**pi0 / pi0.5 / pi0-FAST**
- The hardware guide puts `pi0`, `pi0_fast` and `pi05` in the "Large VLA" group: about 24-40 GB peak VRAM at batch 8 with AdamW, an A100 40 GB+ suggested ("24 GB tight at BS 1"). An A100 40 GB at batch 4 takes about 4-8 h for 5 epochs on a 50-episode dataset. On 4×H100, pi05 ran 5000 steps at batch 32 in 3h 41m (update_s 2.548) with gradient checkpointing and bf16 — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- pi0.5 docs: the LIBERO example is "Sized for a single 80 GB GPU" (batch 64, 30k steps, `gradient_checkpointing=true`, `dtype=bfloat16`). `freeze_vision_encoder=true` plus `train_expert_only=true` cuts memory "at some cost in success rate". It needs a license accepted for the gated `google/paligemma-3b-pt-224`. The default quantile normalization needs q01/q99 stats, otherwise "ValueError: QUANTILES normalization mode requires q01 and q99 stats". Fix with `lerobot-edit-dataset --operation.type recompute_stats` or pass MEAN_STD. Default chunk_size is 50. The LeRobot pi0.5 implementation scores 97.5% on LIBERO against 96.85% for OpenPI — [LeRobot pi0.5 docs](https://huggingface.co/docs/lerobot/pi05)
- OpenPI-derived guidance: LoRA fine-tune needs more than 22.5 GB (RTX 4090), full fine-tune more than 70 GB (A100/H100 80 GB). A RoboTwin mirror says LoRA needs more than 46 GB (A6000) and lists a 2×4090 FSDP option. These sources conflict. One user reported about 37 GB just to load fine-tuned pi0 for serving — [RoboTwin pi0 doc](https://robotwin-platform.github.io/doc/usage/Pi0.html); [openpi issue #599](https://github.com/Physical-Intelligence/openpi/issues/599)
- SO-100 pi0 result (from the SmolVLA paper): 61.7% average, against 78.3% for SmolVLA — [SmolVLA paper](https://arxiv.org/html/2506.01844v1)

**Diffusion Policy**
- Hardware guide: about 8-14 GB at batch 8. A 4090 at batch 8 takes about 2-4 h for 5 epochs of 45k frames, roughly 4x ACT's 30-60 min. On 4×H100, 5000 steps at batch 32 took 16 min — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- Anecdotal SO-100 pick-place with 60 demos: ACT 100% vs CNN Diffusion Policy 25%. On SO-101 cloth folding, Diffusion inference (~300 ms) was too slow for real-time control — [flaviogheri](https://flaviogheri.github.io/projects/imitation_learning/); [tabithako](https://tabithako.github.io/projects/policy-training)
- HF validation-loss study: Diffusion on PushT used 206 episodes and its success swung non-monotonically over 100k steps — [HF blog](https://huggingface.co/blog/m1b/validation-loss-robotics)

### Inferences
- With ~125 demos on one task, SmolVLA fine-tuning is the most promising step up from ACT. In the paper's setup SmolVLA beat ACT on in-distribution and out-of-distribution SO-101 pick-place (90/50 vs 70/40). Note that SmolVLA's gain over ACT on the SO-100 single-task pick-place was small (75 vs 70). Its largest gains were on stacking and sorting.
- SmolVLA at 20k steps × batch 64 = 1.28M samples ≈ 11.7 epochs of 109k frames, which is above the 5-10 epoch guidance. 10-15k steps at batch 64 may be enough. Shorten `scheduler_decay_steps` to match.
- SmolVLA on MPS is likely feasible at small batch with `freeze_vision_encoder=True` (the default), but much slower than ACT. No benchmarked steps/s found. Cloud is the realistic path.
- pi0/pi0.5 is overkill for one pick-and-place task on a hobby budget: 24-80 GB VRAM, hours on A100/H100, gated model, quantile stats setup. The one SO-100 comparison found shows it behind SmolVLA.
- Diffusion Policy is not recommended here: 4x ACT's training time, weak small-data SO-100 anecdotes, slower inference.

### Gaps
- No published SmolVLA results found at exactly 100-125 demos for one task, and no official MPS training throughput.
- No LeRobot-native pi0-FAST SO-100 results found.
- The fine-tuning LR and optimizer settings for the SmolVLA real-world runs are not separately reported in the paper.

## Cloud GPU options and expected training time (ACT 100k steps, SmolVLA 20k steps)

### Takeaway
For ACT, a single L4 or A10G (24 GB) at $0.44-$1.50/h is enough. For SmolVLA, an A100 at about $1.2-$2.50/h fits. HF Jobs bills per minute with no setup, and `lerobot-train --job.target=<flavor>` submits directly. Rough cost: an ACT run of about 7 epochs is a few dollars, and SmolVLA at 20k steps is about $10 on an HF Jobs A100.

### Cited Findings
- HF Jobs GPU prices (official page, read 2026-11-17, billed per minute, only while Starting or Running, default timeout 30 min for `hf jobs run`): T4 small $0.40/h, T4 medium $0.60, 1×L4 $0.80, 4×L4 $3.80, 1×L40S $1.80, A10G small $1.00, A10G large $1.50, 2×A10G $3.00, A100 large (80 GB) $2.50, 4×A100 $10.00, H200 $5.00, RTX PRO 6000 (96 GB) $2.75 — [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)
- LeRobot submits to HF Jobs with `lerobot-train ... --job.target=a10g-large`. Flavors are `t4-small/medium` (ACT only), `l4x1/l4x4`, `a10g-small/large/largex2/largex4`, and `a100-large`. The LeRobot job default timeout is `2d`, overridable with `--job.timeout=4h`. Run `hf auth login` first — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- Wall-clock anchors (5 epochs, ~45k frames, 640x480, AdamW): 4090/3090 ACT batch 8 about 30-60 min; L4/A10G ACT batch 8 about 1-2 h; L4/A10G SmolVLA batch 4 about 3-6 h; A100 40 GB SmolVLA batch 16 about 1-2 h; A100 40 GB pi0/pi05 batch 4 about 4-8 h; Apple M1/M2/M3 Max ACT batch 4 about 6-14 h. All "±50%" — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- 4×H100 reference (5000 steps, batch 32, about 50 episodes): Diffusion 16m 17s, SmolVLA 27m 49s, pi05 3h 41m. `accelerate launch --num_processes=N` gives about N× speedup for compute-bound runs — [LeRobot hardware guide](https://huggingface.co/docs/lerobot/main/hardware_guide.md)
- SmolVLA 20k steps at batch 64 is about 4 h on one A100 — [LeRobot SmolVLA docs](https://huggingface.co/docs/lerobot/smolvla)
- Third-party on-demand price aggregates (2026, conflicting; check provider pages). H100: Lambda about $2.99-$4.29/GPU-h depending on SKU and date; RunPod about $2.39-$3.29 (community $1.80-2.10); Modal about $3.95. A100 80 GB: Lambda about $1.48-$1.52; RunPod about $1.49 ($1.19 spot). L4: RunPod $0.44, Lambda $0.52, market $0.44-$0.80 — [Spheron: Lambda H100 2026](https://www.spheron.network/blog/lambda-cloud-h100-pricing-2026/); [intuitionlabs comparison](https://intuitionlabs.ai/articles/cloud-gpu-rental-prices-comparison); [Spheron: RunPod vs Lambda 2026](https://www.spheron.network/blog/runpod-vs-lambda-labs-2026/); [jarvislabs 2026](https://jarvislabs.ai/ai-faqs/best-cloud-gpu-providers-2026)
- HF Inference Endpoints and Spaces list L4 at $0.70-$0.80/h and A100 80 GB at $3.60/h. These are different products from Jobs — [HF Inference Endpoints pricing](https://huggingface.co/docs/inference-endpoints/pricing)
- Colab notebooks exist for ACT and SmolVLA training — [LeRobot ACT docs](https://huggingface.co/docs/lerobot/act); [LeRobot SmolVLA docs](https://huggingface.co/docs/lerobot/smolvla)
- Seeed: for RTX 50-series use `--dataset.video_backend=pyav`. Check `nvidia-smi` utilization to catch dataloader bottlenecks — [Seeed Studio wiki](https://wiki.seeedstudio.com/robotics/hands_on_act_training/)

### Inferences
- ACT 100k steps at batch 8 on this dataset: the guide's L4 anchor (5 epochs × 45k frames ≈ 28k steps in 1-2 h) implies roughly 4-8 steps/s. That gives about 3.5-7 h for 100k steps on an L4 (~$3-6 on HF Jobs), and about 2-3.5 h on a 4090-class card. These are scaled estimates, ±50%. Raising the batch to 32 and cutting steps to about 25k (same epochs) should cut wall-clock further on a 24 GB card, since ACT uses only ~2-6 GB at batch 8.
- SmolVLA 20k steps at batch 64: about 4 h on an A100 ≈ $10 on HF Jobs A100-large ($2.50/h), or about $6 on RunPod/Lambda A100 at about $1.5/h before storage and egress.
- Data loading: 640x480 video decoding can bottleneck cheap GPUs. Use several `--num_workers` and check that `dataloading_s` is small relative to `update_s` in the logs.
- Against the current MPS setup (~8 h for 50k steps), an L4 or A10G should be roughly 2-4x faster per step at batch 8. A 4090 or A100 at batch 32 would bring a 7-epoch ACT run to about 1-2 h. Inferred from the anchors above.

### Gaps
- Modal's A100 and L4 prices and Lambda's current L4 availability were not confirmed from primary pricing pages. Third-party aggregate numbers conflict.
- No measured steps/s found for ACT on L4, A10G or A100 with 2×640x480 cameras. The figures above are scaled from the guide's anchors.
- Colab GPU tiers and compute-unit pricing were not researched.
