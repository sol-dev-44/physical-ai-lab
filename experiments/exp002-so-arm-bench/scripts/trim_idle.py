"""Copy a LeRobot v3 dataset with the idle frames cut from the start and end of each episode.

Why: most exp002 demos sit still at the rest pose for about 3 s before the operator moves.
ACT has no memory, so it learned that the start scene often means "wait", and v4 waited for
whole rollouts (2026-11-17). Cutting the lead-in removes those "wait" labels.

How: the source is never modified. The copy keeps every video file byte-identical; only the
parquet rows and the episode metadata change. Each episode's video from_timestamp moves
forward by the frames cut at its start, so the remaining frames line up with the same images.
Numeric stats (action, state) are recomputed; image stats are kept.

Motion onset is the first frame where any joint of the action (the leader command) is more
than --threshold degrees from the episode's first action. --lead frames before it are kept.
The end is the last frame more than --threshold from the final action; --tail seconds after
it are kept, so the policy still sees "task done, arm at rest".

Usage:
  python trim_idle.py --src DATASET_DIR --dst NEW_DIR [--dry-run]
  python trim_idle.py --src DATASET_DIR --dst NEW_DIR --verify
"""

import argparse
import json
import shutil
from pathlib import Path

import numpy as np
import pandas as pd

FPS_KEY = "fps"


def motion_window(actions: np.ndarray, threshold: float, lead: int, tail: int) -> tuple[int, int]:
    """Return [start, end) frame indexes to keep."""
    n = len(actions)
    from_first = np.abs(actions - actions[0]).max(axis=1)
    moving = np.flatnonzero(from_first > threshold)
    start = max(0, int(moving[0]) - lead) if len(moving) else 0
    from_last = np.abs(actions - actions[-1]).max(axis=1)
    still_after = np.flatnonzero(from_last > threshold)
    end = min(n, int(still_after[-1]) + 1 + tail) if len(still_after) else n
    if end - start < 2 * lead + 30:
        return 0, n
    return start, end


def load_data(root: Path) -> dict[Path, pd.DataFrame]:
    return {p: pd.read_parquet(p) for p in sorted((root / "data").glob("*/*.parquet"))}


def load_episodes(root: Path) -> dict[Path, pd.DataFrame]:
    return {p: pd.read_parquet(p) for p in sorted((root / "meta" / "episodes").glob("*/*.parquet"))}


def plan(
    root: Path, threshold: float, lead: int, tail_s: float
) -> tuple[dict[int, tuple[int, int, int]], int]:
    info = json.loads((root / "meta" / "info.json").read_text())
    fps = int(info[FPS_KEY])
    windows: dict[int, tuple[int, int, int]] = {}
    for df in load_data(root).values():
        for ep, g in df.groupby("episode_index"):
            g = g.sort_values("frame_index")
            actions = np.stack(g["action"].values)
            start, end = motion_window(actions, threshold, lead, int(round(tail_s * fps)))
            windows[int(ep)] = (start, end, len(g))
    return windows, fps


def report(windows: dict[int, tuple[int, int, int]], fps: int) -> None:
    head = np.array([w[0] for w in windows.values()]) / fps
    tail = np.array([w[2] - w[1] for w in windows.values()]) / fps
    kept = sum(w[1] - w[0] for w in windows.values())
    total = sum(w[2] for w in windows.values())
    print(f"episodes {len(windows)}, frames kept {kept} of {total} ({100 * kept / total:.1f}%)")
    print(f"cut at start: median {np.median(head):.1f} s, max {head.max():.1f} s")
    print(f"cut at end:   median {np.median(tail):.1f} s, max {tail.max():.1f} s")


def write(src: Path, dst: Path, windows: dict[int, tuple[int, int, int]], fps: int) -> None:
    shutil.copytree(src, dst)
    info_path = dst / "meta" / "info.json"
    info = json.loads(info_path.read_text())
    video_keys = [k for k, v in info["features"].items() if v["dtype"] == "video"]

    data = load_data(dst)
    new_ranges: dict[int, tuple[int, int]] = {}
    global_index = 0
    # Episodes are laid out in order across data files; keep that order for the global index.
    for path in sorted(data, key=lambda p: (p.parent.name, p.name)):
        df = data[path]
        parts = []
        for ep in sorted(df["episode_index"].unique()):
            g = df[df["episode_index"] == ep].sort_values("frame_index")
            start, end, _ = windows[int(ep)]
            g = g.iloc[start:end].copy()
            n = len(g)
            g["frame_index"] = np.arange(n, dtype=np.int64)
            g["timestamp"] = (np.arange(n) / fps).astype(np.float32)
            g["index"] = np.arange(global_index, global_index + n, dtype=np.int64)
            new_ranges[int(ep)] = (global_index, global_index + n)
            global_index += n
            parts.append(g)
        out = pd.concat(parts).reset_index(drop=True)
        out.to_parquet(path, index=False)

    from lerobot.datasets.compute_stats import compute_episode_stats

    numeric = {k: v for k, v in info["features"].items() if k in ("action", "observation.state")}
    all_rows = pd.concat(load_data(dst).values())
    updates: dict[str, dict[int, np.ndarray]] = {}
    for path, eps in load_episodes(dst).items():
        for i, row in eps.iterrows():
            ep = int(row["episode_index"])
            start, end, _ = windows[ep]
            n = end - start
            eps.at[i, "length"] = n
            eps.at[i, "dataset_from_index"], eps.at[i, "dataset_to_index"] = new_ranges[ep]
            for key in video_keys:
                new_from = float(row[f"videos/{key}/from_timestamp"]) + start / fps
                eps.at[i, f"videos/{key}/from_timestamp"] = new_from
                eps.at[i, f"videos/{key}/to_timestamp"] = new_from + n / fps
            g = all_rows[all_rows["episode_index"] == ep]
            stats = compute_episode_stats({k: np.stack(g[k].values) for k in numeric}, numeric)
            for key, s in stats.items():
                for stat, value in s.items():
                    col = f"stats/{key}/{stat}"
                    if col in eps.columns:
                        updates.setdefault(col, {})[i] = np.asarray(value).reshape(-1)
        # Whole-column assignment: .at collapses a 1-element array into a 0-d one,
        # which parquet rejects.
        for col, by_row in updates.items():
            dtype = np.asarray(eps[col].iloc[0]).dtype
            eps[col] = [
                by_row[i].astype(dtype) if i in by_row else v
                for i, v in zip(eps.index, eps[col], strict=True)
            ]
        updates.clear()
        eps.to_parquet(path, index=False)

    info["total_frames"] = global_index
    info_path.write_text(json.dumps(info, indent=4))

    from lerobot.datasets.dataset_tools import recompute_stats
    from lerobot.datasets.lerobot_dataset import LeRobotDataset

    recompute_stats(LeRobotDataset("local/" + dst.name, root=dst), skip_image_video=True)
    (dst / "TRIMMED.json").write_text(
        json.dumps(
            {
                "source": str(src),
                "fps": fps,
                "windows": {str(k): list(v) for k, v in sorted(windows.items())},
            },
            indent=1,
        )
    )


def verify(src: Path, dst: Path, samples: int = 40) -> None:
    """Check that trimmed frames show the same images and numbers as the source frames."""
    import torch
    from lerobot.datasets.lerobot_dataset import LeRobotDataset

    meta = json.loads((dst / "TRIMMED.json").read_text())
    windows = {int(k): v for k, v in meta["windows"].items()}
    a = LeRobotDataset("local/" + src.name, root=src)
    b = LeRobotDataset("local/" + dst.name, root=dst)
    assert b.meta.total_episodes == a.meta.total_episodes
    rng = np.random.default_rng(0)
    worst = 0.0
    for _ in range(samples):
        ep = int(rng.integers(0, a.meta.total_episodes))
        start, end, _ = windows[ep]
        k = int(rng.integers(0, end - start))
        ia = int(a.meta.episodes["dataset_from_index"][ep]) + start + k
        ib = int(b.meta.episodes["dataset_from_index"][ep]) + k
        fa, fb = a[ia], b[ib]
        assert int(fb["episode_index"]) == ep and int(fb["frame_index"]) == k
        for key in ("action", "observation.state"):
            assert torch.equal(fa[key], fb[key]), (ep, k, key)
        for key in a.meta.video_keys:
            worst = max(worst, float((fa[key] - fb[key]).abs().max()))
    print(f"verified {samples} random frames: numbers equal, worst image pixel diff {worst:.4f}")
    assert worst < 1e-3, "images do not line up"
    print(f"frames {b.meta.total_frames} (source {a.meta.total_frames})")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--dst", type=Path, required=True)
    ap.add_argument("--threshold", type=float, default=2.0, help="degrees")
    ap.add_argument("--lead", type=int, default=3, help="frames kept before motion onset")
    ap.add_argument("--tail", type=float, default=1.0, help="seconds kept after motion ends")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()
    if args.verify:
        verify(args.src, args.dst)
    else:
        windows, fps = plan(args.src, args.threshold, args.lead, args.tail)
        report(windows, fps)
        if not args.dry_run:
            if args.dst.exists():
                raise SystemExit(f"{args.dst} exists; refusing to overwrite")
            write(args.src, args.dst, windows, fps)
            print(f"wrote {args.dst}")
