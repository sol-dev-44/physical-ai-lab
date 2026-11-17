"""Checks to run before training (data) and before robot time (checkpoint).

Moves nothing, writes nothing.

Data checks (always):
  - idle at episode start and end (frames before the first move / after the last move)
  - long pauses mid-episode
  - episode length outliers and the episode/frame counts
  - stats.json present and matching the frame count
Checkpoint checks (--checkpoint): feed every recorded episode start to the policy and measure how
  far its 100-step plan moves. A policy that plans to stay put on many starts will sit still on the
  arm (what happened to v4 on 2026-11-17).

Exit code 1 if any check fails, so it can gate a training script.
Usage:
  python audit.py --data DATASET_DIR [--checkpoint PRETRAINED_MODEL_DIR] [--episodes 0-124]
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

MOVE_DEG = 2.0  # a joint this far from its first/last value counts as moving
PAUSE_SPEED = 0.15  # degrees per frame; slower than this on every joint counts as paused
MAX_IDLE_START_S = 0.5
MAX_IDLE_END_S = 2.0
MAX_PAUSE_S = 2.0
WAIT_PLAN_DEG = 10.0  # a 100-step plan that moves less than this means "wait"
MAX_WAIT_FRACTION = 0.05


def parse_episodes(spec: str | None, total: int) -> list[int]:
    if not spec:
        return list(range(total))
    out: list[int] = []
    for part in spec.split(","):
        lo, _, hi = part.partition("-")
        out += list(range(int(lo), int(hi or lo) + 1))
    return out


def data_checks(root: Path, episodes: list[int]) -> list[str]:
    info = json.loads((root / "meta" / "info.json").read_text())
    fps = int(info["fps"])
    df = pd.concat(
        pd.read_parquet(p, columns=["episode_index", "frame_index", "action"])
        for p in sorted((root / "data").glob("*/*.parquet"))
    )
    failures: list[str] = []
    rows = []
    for ep in episodes:
        g = df[df.episode_index == ep].sort_values("frame_index")
        a = np.stack(g["action"].values)
        moving_from_start = np.flatnonzero(np.abs(a - a[0]).max(axis=1) > MOVE_DEG)
        moving_to_end = np.flatnonzero(np.abs(a - a[-1]).max(axis=1) > MOVE_DEG)
        head = (moving_from_start[0] if len(moving_from_start) else len(a)) / fps
        tail = (len(a) - 1 - moving_to_end[-1] if len(moving_to_end) else len(a)) / fps
        speed = np.abs(np.diff(a, axis=0)).max(axis=1)
        inner = speed[int(head * fps) : max(int(head * fps), len(speed) - int(tail * fps))]
        longest, run = 0, 0
        for s in inner:
            run = run + 1 if s < PAUSE_SPEED else 0
            longest = max(longest, run)
        rows.append((ep, len(a) / fps, head, tail, longest / fps))
    t = pd.DataFrame(rows, columns=["ep", "len_s", "idle_start_s", "idle_end_s", "longest_pause_s"])
    print(
        f"data: {len(t)} episodes, {int(t.len_s.sum() * fps)} frames, {t.len_s.sum() / 60:.1f} min"
    )
    for col, limit in (
        ("idle_start_s", MAX_IDLE_START_S),
        ("idle_end_s", MAX_IDLE_END_S),
        ("longest_pause_s", MAX_PAUSE_S),
    ):
        bad = t[t[col] > limit]
        print(
            f"  {col}: median {t[col].median():.2f}, max {t[col].max():.2f}, "
            f"over {limit} s: {len(bad)}"
            + (f" (eps {bad.ep.tolist()[:15]}{'...' if len(bad) > 15 else ''})" if len(bad) else "")
        )
        if col != "longest_pause_s" and t[col].median() > limit:
            failures.append(
                f"median {col} {t[col].median():.2f} s is over {limit} s; run trim_idle.py"
            )
    q1, q3 = t.len_s.quantile([0.25, 0.75])
    short = t[t.len_s < q1 - 1.5 * (q3 - q1)]
    print(f"  length: median {t.len_s.median():.1f} s, short outliers: {short.ep.tolist()}")
    stats = root / "meta" / "stats.json"
    if not stats.exists():
        failures.append("meta/stats.json missing")
    else:
        count = json.loads(stats.read_text())["action"]["count"][0]
        if count != info["total_frames"]:
            failures.append(
                f"stats count {count} != total_frames {info['total_frames']}; recompute stats"
            )
    return failures


def checkpoint_checks(root: Path, checkpoint: Path, episodes: list[int]) -> list[str]:
    import torch
    from lerobot.configs.policies import PreTrainedConfig
    from lerobot.datasets.lerobot_dataset import LeRobotDataset
    from lerobot.policies.act.modeling_act import ACTPolicy
    from lerobot.policies.factory import make_pre_post_processors

    ds = LeRobotDataset("local/" + root.name, root=root)
    cfg = PreTrainedConfig.from_pretrained(checkpoint)
    cfg.device = "mps" if torch.backends.mps.is_available() else "cpu"
    pol = ACTPolicy.from_pretrained(checkpoint, config=cfg).to(cfg.device).eval()
    pre, post = make_pre_post_processors(
        cfg,
        pretrained_path=checkpoint,
        preprocessor_overrides={"device_processor": {"device": cfg.device}},
    )
    plans = []
    for ep in episodes:
        item = ds[int(ds.meta.episodes["dataset_from_index"][ep])]
        obs = {k: v for k, v in item.items() if k.startswith("observation.")}
        obs["task"] = item["task"]
        with torch.no_grad():
            last = post(pol.predict_action_chunk(pre(obs))[:, -1]).cpu().flatten()
        plans.append(float((last - item["observation.state"]).abs().max()))
    plans_a = np.array(plans)
    waits = [ep for ep, p in zip(episodes, plans, strict=True) if p < WAIT_PLAN_DEG]
    frac = len(waits) / len(episodes)
    print(
        f"checkpoint: plan from episode starts: median {np.median(plans_a):.0f} deg, "
        f"waits (<{WAIT_PLAN_DEG:.0f} deg) on {len(waits)}/{len(episodes)}"
        + (f" (eps {waits[:15]})" if waits else "")
    )
    if frac > MAX_WAIT_FRACTION:
        return [
            f"policy plans to wait on {100 * frac:.0f}% of episode starts "
            f"(limit {100 * MAX_WAIT_FRACTION:.0f}%)"
        ]
    return []


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", type=Path, required=True)
    ap.add_argument("--checkpoint", type=Path)
    ap.add_argument("--episodes", help="e.g. 0-124 or 0-39,65-124 (default all)")
    args = ap.parse_args()
    total = json.loads((args.data / "meta" / "info.json").read_text())["total_episodes"]
    eps = parse_episodes(args.episodes, total)
    failures = data_checks(args.data, eps)
    if args.checkpoint:
        failures += checkpoint_checks(args.data, args.checkpoint, eps)
    print("\n".join(f"FAIL {f}" for f in failures) if failures else "PASS")
    sys.exit(1 if failures else 0)
