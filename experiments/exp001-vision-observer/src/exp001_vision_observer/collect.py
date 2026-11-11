"""Unattended data collection (step 2: the motion model) and the fit that uses it.

`run_collect` drives a mix of forward and reverse moves of varied length. Every move goes
through the gate, so the fence decides what's allowed: it alternates direction, and if a
move is denied it tries the other direction, then shorter. Each move is judged by the
camera and logged with its displacement, so the logs are the dataset.

It stops when the robot looks asleep (several sent moves in a row with no motion; the toy
switches itself off when idle), when nothing is allowed (needs re-centring), or after n.
"""

from __future__ import annotations

import math
import random
import statistics
import time
from pathlib import Path
from typing import Any

from lab_agent.log import read_log
from lab_agent.runner import Runner

from .judge import judge
from .tools import Rig

DURATIONS = (0.3, 0.5, 0.75, 1.0)
STILL_CM = 1.5  # a sent move that shifts the robot less than this didn't happen
ASLEEP_AFTER = 3  # consecutive still moves before we call it asleep


def run_collect(
    rig: Rig,
    runner: Runner,
    n: int,
    *,
    rng: random.Random | None = None,
    pause_s: float = 0.8,
    experiment: str = "exp001-vision-observer",
) -> dict[str, Any]:
    rng = rng or random.Random()
    runner.start(experiment, purpose="motion model data", n=n, simulated=rig.simulated)
    moves, still, last = 0, 0, "robot.reverse"
    status = "completed"
    while moves < n:
        if moves and pause_s:
            time.sleep(pause_s)
        before = rig.live.settle(3)
        first = "robot.forward" if last == "robot.reverse" else "robot.reverse"
        second = "robot.reverse" if first == "robot.forward" else "robot.forward"
        seconds = rng.choice(DURATIONS)
        tries = [(t, s) for s in sorted({seconds, 0.5, 0.3}, reverse=True) if s <= seconds
                 for t in (first, second)]  # fmt: skip
        result = None
        for tool, secs in tries:
            r = runner.request(tool, {"seconds": secs}, actor="cli", automated=True)
            if r.allowed:
                result, last, seconds = r, tool, secs
                break
        if result is None:
            status = "stuck"  # nothing fits: the robot needs moving back to the middle
            break
        if not result.ok:
            status = "failed"
            break
        after = rig.live.settle(5)
        v = judge(last, before, after)
        payload: dict[str, Any] = {
            "success": v.success,
            "method": "camera",
            "note": v.reason,
            "seconds": seconds,
        }
        payload |= {k: val for k, val in v.payload().items() if k != "reason"}
        if before is not None:
            payload |= {"x_cm": round(before.x_cm, 1), "y_cm": round(before.y_cm, 1),
                        "heading_deg": round(before.heading_deg, 1)}  # fmt: skip
        runner.log.append(
            "outcome.observed", "system", payload, parent_id=result.last.event_id, tool=last
        )
        moves += 1
        verdict = "ok" if v.success else "NO"
        print(f"{moves:3d}. {last.split('.')[1]:7s} {seconds:.2f}s -> {v.moved_cm:5.1f} cm,"
              f" turn {v.turn_deg:+5.1f} deg, {verdict}", flush=True)  # fmt: skip
        still = still + 1 if v.moved_cm < STILL_CM else 0
        if still >= ASLEEP_AFTER:
            status = "asleep"
            break
    runner.end("completed" if status == "completed" else "aborted")
    return {"status": status, "moves": moves}


def fit_motion(paths: list[Path]) -> dict[str, dict[str, float]]:
    """Per tool: speed along the heading (cm/s, + forward), sideways drift and turn rate,
    from camera observations that carry `seconds`. Fits along = v * (seconds - lag)."""
    rows: dict[str, list[tuple[float, float, float, float]]] = {}
    for p in paths:
        for e in read_log(p):
            if e.type != "outcome.observed" or e.payload.method != "camera":
                continue
            pl = e.payload
            secs = getattr(pl, "seconds", None)
            along = getattr(pl, "along_cm", None)
            if secs is None or along is None or getattr(pl, "moved_cm", 0) < STILL_CM:
                continue
            rows.setdefault(e.tool or "", []).append(
                (float(secs), float(along), float(pl.lateral_cm), float(pl.turn_deg))
            )
    out: dict[str, dict[str, float]] = {}
    for tool, r in rows.items():
        s = [x[0] for x in r]
        a = [x[1] for x in r]
        if len(r) >= 2 and len(set(s)) >= 2:
            slope, intercept = statistics.linear_regression(s, a)
            lag = -intercept / slope if slope else 0.0
        else:
            slope, lag = statistics.mean(a) / statistics.mean(s), 0.0
        per = [abs(x[1]) / x[0] for x in r]
        resid = [abs(x[1] - slope * (x[0] - lag)) for x in r]
        out[tool] = {
            "moves": len(r),
            "speed_cm_s": round(slope, 1),
            "lag_s": round(lag, 2),
            "max_speed_cm_s": round(max(per), 1),
            "lateral_cm_s": round(statistics.mean(x[2] / x[0] for x in r), 1),
            "turn_deg_s": round(statistics.mean(x[3] / x[0] for x in r), 1),
            "residual_cm": round(statistics.mean(resid), 1),
        }
    return out


def suggest_fence(fit: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """Fence motions from a fit: the fastest observed speed, the observed travel direction,
    and slack that covers sideways drift and turning (reverse arcs)."""
    out = {}
    for tool, f in fit.items():
        speed = max(abs(f["speed_cm_s"]), f["max_speed_cm_s"]) * 1.2
        direction = math.degrees(math.atan2(f["lateral_cm_s"], f["speed_cm_s"]))
        slack = min(1.5, 0.3 + abs(f["turn_deg_s"]) / 90)
        out[tool] = {
            "speed_cm_s": round(speed, 1),
            "direction_deg": round(direction, 1),
            "slack": round(slack, 2),
        }
    return out
