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

from .config import ARENA_JSON, BACKGROUND, PRESETS, Arena, Markers
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


def cmd_cameras(a: argparse.Namespace) -> int:
    from .camera import list_cameras, match_index

    if a.match:
        found = match_index(a.match)
        if found is None:
            print("no OpenCV camera opened (macOS: allow camera access for this app)")
            return 1
        i, score = found
        print(f"{a.match!r} is OpenCV camera {i} (picture match {score:.2f}; above 0.8 is sure)")
        return 0 if score >= 0.8 else 1
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
    markers = base.markers if base else Markers()
    if a.front:
        markers = markers.model_copy(update={"head": PRESETS[a.front]})
    if a.back:
        markers = markers.model_copy(update={"tail": PRESETS[a.back]})
    arena = Arena(
        width_cm=a.width,
        height_cm=a.height,
        corners_px=corners,  # type: ignore[arg-type]  # validated as 2-tuples above
        markers=markers,
        camera_index=a.camera if a.camera is not None else (base.camera_index if base else 0),
        zoom=a.zoom if a.zoom is not None else (base.zoom if base else 1.0),
        camera_name=a.camera_name or (base.camera_name if base else None),
        tracking=a.tracking or (base.tracking if base else "markers"),
    )
    arena.save()
    print(f"saved {ARENA_JSON} (tracking: {arena.tracking})")
    return 0


def cmd_background(a: argparse.Namespace) -> int:
    """Capture the empty arena for tracking="background". Robot out, nobody in frame."""
    import cv2

    from .camera import grab_by_name

    if not a.nobody_in_frame:
        raise SystemExit("Refusing: pass --nobody-in-frame once you've checked (ADR 0007)")
    load_dotenv()
    arena = Arena.load() if ARENA_JSON.exists() else None
    name = a.camera_name or (arena.camera_name if arena else None)
    if not name:
        raise SystemExit('Pass --camera-name "HD Pro Webcam C920" (or calibrate first)')
    zoom = a.zoom if a.zoom is not None else (arena.zoom if arena else 1.0)
    frame = grab_by_name(name, zoom)
    BACKGROUND.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(BACKGROUND), frame)
    print(f"saved empty-arena background {BACKGROUND} ({frame.shape[1]}x{frame.shape[0]})")
    print("Retake it if the lighting changes or the mats move.")
    return 0


def cmd_snapshot(a: argparse.Namespace) -> int:
    """The only command that writes a frame, and only when told nobody is in it (ADR 0007).
    Works before calibration (for reading the corner pixels): pass --camera."""
    import cv2

    if not a.nobody_in_frame:
        raise SystemExit("Refusing: pass --nobody-in-frame once you've checked (ADR 0007)")
    from .camera import grab_by_name

    load_dotenv()
    arena = Arena.load() if ARENA_JSON.exists() else None
    name = a.camera_name or (arena.camera_name if arena else None)
    if not name:
        raise SystemExit(
            'Pass --camera-name "HD Pro Webcam C920" (names: ffmpeg -f avfoundation '
            '-list_devices true -i "")'
        )
    zoom = a.zoom if a.zoom is not None else (arena.zoom if arena else 1.0)
    frame = grab_by_name(name, zoom)
    if frame is None:
        raise SystemExit("camera gave no frame")
    fix = None
    if arena:
        from .tracker import make_tracker

        for i, (x, y) in enumerate(arena.corners_px):
            cv2.circle(frame, (int(x), int(y)), 8, (0, 255, 255), 2)
            cv2.putText(frame, str(i), (int(x) + 10, int(y)), 0, 0.7, (0, 255, 255), 2)
        try:
            fix = make_tracker(arena).find(frame)
        except FileNotFoundError:
            fix = None
        if fix:
            for b, color in ((fix.head, (0, 255, 0)), (fix.tail, (255, 0, 255))):
                cv2.circle(frame, (int(b.x_px), int(b.y_px)), 12, color, 2)
    # a 100 px grid makes reading corner pixels off the image easy
    h, w = frame.shape[:2]
    for x in range(0, w, 100):
        cv2.line(frame, (x, 0), (x, h), (255, 255, 255), 1)
        cv2.putText(frame, str(x), (x + 2, 14), 0, 0.4, (255, 255, 255), 1)
    for y in range(0, h, 100):
        cv2.line(frame, (0, y), (w, y), (255, 255, 255), 1)
        cv2.putText(frame, str(y), (2, y + 14), 0, 0.4, (255, 255, 255), 1)
    MEDIA.mkdir(parents=True, exist_ok=True)
    out = MEDIA / f"snapshot-{datetime.now():%Y%m%d-%H%M%S}.jpg"
    cv2.imwrite(str(out), frame)
    print(f"saved {out} ({w}x{h}); robot: {_pose(fix) if arena else 'not calibrated'}")
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


def cmd_heading(a: argparse.Namespace) -> int:
    """Drive forward once and set heading_offset_deg so the tracked heading matches the
    direction of travel. Goes through the gate like any trial (logged as a run)."""
    s = Settings.from_env()
    rig = _rig(a)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_id = f"exp001-{stamp}-heading{'-sim' if rig.simulated else ''}"
    log = EventLog(run_path(s.events_dir, EXPERIMENT, run_id), run_id)
    runner = Runner(rig.registry, log)
    rig.live.start()
    try:
        runner.start(EXPERIMENT, purpose="heading calibration", simulated=rig.simulated)
        before = rig.live.settle(5)
        result = runner.request("robot.forward", {"seconds": a.seconds}, actor="cli")
        if not result.allowed:
            print(f"denied: {getattr(result.checked.payload, 'reason', '')}")
            print("Put the robot near one end, facing the far end, and try again.")
            runner.end("aborted")
            return 1
        after = rig.live.settle(5)
        if before is None or after is None:
            runner.end("aborted")
            raise SystemExit("robot not tracked before or after the move")
        dx, dy = after.x_cm - before.x_cm, after.y_cm - before.y_cm
        moved = math.hypot(dx, dy)
        if moved < 5:
            runner.end("aborted")
            raise SystemExit(f"only moved {moved:.1f} cm; can't tell the direction")
        travel = math.degrees(math.atan2(dy, dx))
        marker = (before.heading_deg + after.heading_deg) / 2  # includes the old offset
        arena = Arena.load() if ARENA_JSON.exists() and not rig.simulated else rig.arena
        offset = ((travel - marker + arena.heading_offset_deg) + 180) % 360 - 180
        runner.note(f"heading calibration: travel {travel:.1f} deg, markers {marker:.1f} deg")
        runner.end("completed")
        print(f"moved {moved:.1f} cm toward {travel:.0f} deg; markers said {marker:.0f} deg")
        if not rig.simulated:
            arena.model_copy(update={"heading_offset_deg": round(offset, 1)}).save()
            print(f"saved heading_offset_deg = {offset:.1f}")
        else:
            print(f"(simulated; would set heading_offset_deg = {offset:.1f})")
        return 0
    finally:
        rig.live.stop()


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

    sp = sub.add_parser("cameras", help="list camera indexes, or --match a macOS camera name")
    sp.add_argument("--match", metavar="NAME", help="find the OpenCV index for this camera")
    sp.set_defaults(fn=cmd_cameras)

    sp = sub.add_parser("calibrate", help="save arena size and corner pixels to arena.json")
    sp.add_argument("--corners", nargs=4, required=True, metavar="X,Y")
    sp.add_argument("--width", type=float, required=True, help="cm along the first edge")
    sp.add_argument("--height", type=float, required=True, help="cm along the second edge")
    sp.add_argument("--camera", type=int)
    sp.add_argument("--zoom", type=float, help="digital zoom used for the corner snapshot")
    sp.add_argument("--camera-name", help="macOS camera name (snapshots open it by name)")
    sp.add_argument("--tracking", choices=["markers", "background"])
    sp.add_argument("--front", choices=sorted(PRESETS), help="front marker colour")
    sp.add_argument("--back", choices=sorted(PRESETS), help="back marker colour (markers mode)")
    sp.set_defaults(fn=cmd_calibrate)

    sp = sub.add_parser("background", help="capture the empty arena (robot out, nobody in)")
    sp.add_argument("--nobody-in-frame", action="store_true")
    sp.add_argument("--camera-name")
    sp.add_argument("--zoom", type=float)
    sp.set_defaults(fn=cmd_background)

    sp = sub.add_parser("snapshot", help="save one annotated frame locally (nobody in frame)")
    sp.add_argument("--nobody-in-frame", action="store_true")
    sp.add_argument("--camera-name", help='macOS camera name, e.g. "HD Pro Webcam C920"')
    sp.add_argument("--zoom", type=float, help="digital zoom, e.g. 1.5")
    sp.set_defaults(fn=cmd_snapshot)

    sp = sub.add_parser("heading", help="drive forward once to measure the heading offset")
    sp.add_argument("--seconds", type=float, default=1.0)
    sp.set_defaults(fn=cmd_heading)

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
