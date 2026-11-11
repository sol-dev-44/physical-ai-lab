"""exp001 command line. Run from services/lab-agent (same .env and events dir as `lab`).

  exp001 cameras                         which camera indexes open
  exp001 calibrate --corners ... --width W --height H [--camera N]
  exp001 snapshot --nobody-in-frame      one annotated frame to media/exp001/ (local only)
  exp001 check [--seconds 5]             is the robot tracked? fix rate, pose
  exp001 trials TOOL -n 10 --seconds 1 [--dry-run] [--human]
  exp001 report LOG...                   camera vs human agreement, null-test rate

Simulated unless RM4_HOST is set (or forced with --sim / LAB_SIM=1).
"""

from __future__ import annotations

import argparse
import json
import math
import time
from datetime import datetime
from pathlib import Path
from typing import Any

from lab_agent.config import Settings, load_dotenv
from lab_agent.log import EventLog, read_log
from lab_agent.runner import Runner, run_path

from .config import ARENA_JSON, Arena
from .judge import judge
from .tools import Rig, make_rig

EXPERIMENT = "exp001-vision-observer"
MEDIA = Path(__file__).resolve().parents[4] / "media" / "exp001"


def _rig(a: argparse.Namespace) -> Rig:
    load_dotenv()  # same .env as `lab`, so RM4_HOST picks real vs simulated everywhere
    try:
        return make_rig(sim=True if a.sim else None, realtime=True)
    except FileNotFoundError:
        raise SystemExit(f"No {ARENA_JSON.name}: run `exp001 calibrate` first") from None


def _pose(p: Any) -> str:
    return (
        "not tracked" if p is None else f"({p.x_cm:.1f}, {p.y_cm:.1f}) cm, {p.heading_deg:.0f} deg"
    )


def cmd_cameras(_a: argparse.Namespace) -> int:
    from .camera import list_cameras

    found = list_cameras()
    for i, w, h in found:
        print(f"camera {i}: {w}x{h}")
    if not found:
        print("no camera opened (macOS: allow camera access for the app running this)")
    return 0 if found else 1


def cmd_calibrate(a: argparse.Namespace) -> int:
    corners = [tuple(float(v) for v in c.split(",")) for c in a.corners]
    if len(corners) != 4 or any(len(c) != 2 for c in corners):
        raise SystemExit("--corners needs four x,y pixel pairs: origin, +x, +x+y, +y")
    base = Arena.load() if ARENA_JSON.exists() else None
    arena = Arena(
        width_cm=a.width,
        height_cm=a.height,
        corners_px=corners,  # type: ignore[arg-type]  # validated as 2-tuples above
        markers=base.markers if base else Arena.model_fields["markers"].default,
        camera_index=a.camera if a.camera is not None else (base.camera_index if base else 0),
    )
    arena.save()
    print(f"saved {ARENA_JSON}")
    return 0


def cmd_snapshot(a: argparse.Namespace) -> int:
    """The only command that writes a frame, and only when told nobody is in it (ADR 0007)."""
    import cv2

    if not a.nobody_in_frame:
        raise SystemExit("Refusing: pass --nobody-in-frame once you've checked (ADR 0007)")
    rig = _rig(a)
    frame = rig.live.camera.read()
    if frame is None:
        raise SystemExit("camera gave no frame")
    for i, (x, y) in enumerate(rig.arena.corners_px):
        cv2.circle(frame, (int(x), int(y)), 8, (0, 255, 255), 2)
        cv2.putText(frame, str(i), (int(x) + 10, int(y)), 0, 0.7, (0, 255, 255), 2)
    fix = rig.live.tracker.find(frame)
    if fix:
        for b, color in ((fix.head, (0, 255, 0)), (fix.tail, (255, 0, 255))):
            cv2.circle(frame, (int(b.x_px), int(b.y_px)), 12, color, 2)
    MEDIA.mkdir(parents=True, exist_ok=True)
    out = MEDIA / f"snapshot-{datetime.now():%Y%m%d-%H%M%S}.jpg"
    cv2.imwrite(str(out), frame)
    print(f"saved {out} ({frame.shape[1]}x{frame.shape[0]}); robot: {_pose(fix)}")
    rig.live.stop()
    return 0


def cmd_check(a: argparse.Namespace) -> int:
    rig = _rig(a)
    t0 = time.monotonic()
    rig.live.start()
    time.sleep(a.seconds)
    rig.live.stop()
    s, dt = rig.live.stats, time.monotonic() - t0
    print(f"{'simulated' if rig.simulated else 'camera'}: {s.frames} frames in {dt:.1f}s")
    print(f"  robot found in {s.fix_rate:.0%} of frames; last pose {_pose(rig.live.latest())}")
    if rig.robot:
        r, p = rig.robot, rig.live.latest()
        if p:
            err = math.hypot(p.x_cm - r.x_cm, p.y_cm - r.y_cm)
            print(f"  simulator truth ({r.x_cm:.1f}, {r.y_cm:.1f}); tracking error {err:.2f} cm")
    return 0 if s.fix_rate >= 0.9 else 1


def run_trials(
    rig: Rig,
    runner: Runner,
    tool: str,
    n: int,
    seconds: float,
    *,
    interval: float = 1.0,
    ask_human: bool = False,
    reposition: bool = False,
) -> dict[str, Any]:
    """N trials of one move, each judged by the camera (and optionally a human)."""
    runner.start(EXPERIMENT, trials=n, tool=tool, observer="camera", simulated=rig.simulated)
    done = 0
    for i in range(1, n + 1):
        if i > 1 and interval:
            time.sleep(interval)
        before = rig.live.settle(3)
        result = runner.request(tool, {"seconds": seconds}, actor="cli", automated=True)
        if not result.allowed:
            reason = getattr(result.checked.payload, "reason", "")
            print(f"trial {i}: denied by {result.checked.payload.rule}: {reason}")
            if reposition and result.checked.payload.rule == "interlock":
                input("  put the robot back in the middle, facing +x, then press Enter")
                continue
            runner.end("aborted")
            return {"status": "aborted", "trials": done}
        after = rig.live.settle(5)
        v = judge(tool, before, after)
        parent = result.last.event_id
        human = None
        if ask_human:  # asked before showing the camera's verdict, to avoid anchoring
            human = input(f"trial {i}/{n}: did it work? [y/n] ").strip().lower().startswith("y")
        payload: dict[str, Any] = {"success": v.success, "method": "camera", "note": v.reason}
        payload |= {k: val for k, val in v.payload().items() if k != "reason"}
        runner.log.append("outcome.observed", "system", payload, parent_id=parent, tool=tool)
        if human is not None:
            runner.log.append(
                "note",
                "human",
                {"text": f"human label: {'y' if human else 'n'}", "human_success": human},
                parent_id=parent,
            )
        verdict = "yes" if v.success else "no"
        print(f"trial {i}/{n}: camera {verdict} ({v.reason}, {v.moved_cm:.1f} cm)")
        done += 1
    runner.end("completed")
    return {"status": "completed", "trials": done}


def cmd_trials(a: argparse.Namespace) -> int:
    s = Settings.from_env()
    rig = _rig(a)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"exp001-{stamp}{'-null' if a.dry_run else ''}{'-sim' if rig.simulated else ''}"
    log = EventLog(run_path(s.events_dir, EXPERIMENT, run_id), run_id)
    runner = Runner(rig.registry, log, dry_run=a.dry_run)
    rig.live.start()
    try:
        out = run_trials(
            rig,
            runner,
            a.tool,
            a.n,
            a.seconds,
            interval=a.interval,
            ask_human=a.human,
            reposition=a.human,
        )
    finally:
        rig.live.stop()
    print(f"{out['status']}: {log.path}")
    print(json.dumps(report([log.path]), indent=2))
    return 0 if out["status"] == "completed" else 1


def report(paths: list[Path]) -> dict[str, Any]:
    """Camera vs human, per trial, paired by the command each observation is about."""
    camera: dict[str, bool] = {}
    human: dict[str, bool] = {}
    null_runs = 0
    for p in paths:
        for e in read_log(p):
            if e.type == "run.started" and getattr(e.payload, "null_test", False):
                null_runs += 1
            elif e.type == "outcome.observed" and e.payload.method == "camera" and e.parent_id:
                camera[e.parent_id] = e.payload.success
            elif e.type == "note" and e.parent_id:
                h = getattr(e.payload, "human_success", None)
                if isinstance(h, bool):
                    human[e.parent_id] = h
    both = [k for k in camera if k in human]
    tp = sum(camera[k] and human[k] for k in both)
    tn = sum(not camera[k] and not human[k] for k in both)
    fp = sum(camera[k] and not human[k] for k in both)
    fn = sum(not camera[k] and human[k] for k in both)
    return {
        "trials": len(camera),
        "null_test_runs": null_runs,
        "camera_success_rate": round(sum(camera.values()) / len(camera), 3) if camera else None,
        "human_labelled": len(both),
        "agreement": round((tp + tn) / len(both), 3) if both else None,
        "camera_yes_human_no": fp,
        "camera_no_human_yes": fn,
    }


def cmd_report(a: argparse.Namespace) -> int:
    print(json.dumps(report([Path(p) for p in a.logs]), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="exp001", description=__doc__.splitlines()[0])
    p.add_argument("--sim", action="store_true", help="force the simulator")
    sub = p.add_subparsers(required=True)

    sp = sub.add_parser("cameras", help="list camera indexes that open")
    sp.set_defaults(fn=cmd_cameras)

    sp = sub.add_parser("calibrate", help="save arena size and corner pixels to arena.json")
    sp.add_argument("--corners", nargs=4, required=True, metavar="X,Y")
    sp.add_argument("--width", type=float, required=True, help="cm along the first edge")
    sp.add_argument("--height", type=float, required=True, help="cm along the second edge")
    sp.add_argument("--camera", type=int)
    sp.set_defaults(fn=cmd_calibrate)

    sp = sub.add_parser("snapshot", help="save one annotated frame locally (nobody in frame)")
    sp.add_argument("--nobody-in-frame", action="store_true")
    sp.set_defaults(fn=cmd_snapshot)

    sp = sub.add_parser("check", help="track for a few seconds and report")
    sp.add_argument("--seconds", type=float, default=5)
    sp.set_defaults(fn=cmd_check)

    sp = sub.add_parser("trials", help="N camera-judged trials of one move")
    sp.add_argument("tool", choices=["robot.forward", "robot.reverse"])
    sp.add_argument("-n", type=int, default=10)
    sp.add_argument("--seconds", type=float, default=1.0)
    sp.add_argument("--interval", type=float, default=1.0)
    sp.add_argument("--dry-run", action="store_true", help="null test: nothing is sent")
    sp.add_argument("--human", action="store_true", help="also ask you, for the agreement score")
    sp.set_defaults(fn=cmd_trials)

    sp = sub.add_parser("report", help="camera vs human agreement over logs")
    sp.add_argument("logs", nargs="+")
    sp.set_defaults(fn=cmd_report)

    a = p.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    raise SystemExit(main())
