import math

import pytest
from exp001_vision_observer.cli import main, report, run_trials
from exp001_vision_observer.judge import judge
from exp001_vision_observer.tools import make_rig
from lab_agent.interlocks import Pose
from lab_agent.log import EventLog, read_log, validate_log
from lab_agent.runner import Runner


@pytest.fixture(autouse=True)
def sim(monkeypatch, tmp_path):
    monkeypatch.setenv("LAB_SIM", "1")
    monkeypatch.chdir(tmp_path)  # no STOP file, no .env


def p(x, y, h=0.0):
    return Pose(x, y, h, t=0.0)


def test_tracker_finds_the_simulated_robot():
    rig = make_rig(sim=True)
    for x, y, h in [(50, 35, 0), (20, 15, 90), (80, 55, -135)]:
        rig.robot.x_cm, rig.robot.y_cm, rig.robot.heading_deg = x, y, h
        pose = rig.live.refresh()
        assert pose is not None
        assert math.hypot(pose.x_cm - x, pose.y_cm - y) < 1.0
        assert abs((pose.heading_deg - h + 180) % 360 - 180) < 8


def test_lost_robot_gives_no_pose():
    rig = make_rig(sim=True)
    rig.camera.visible = False
    assert rig.live.refresh() is None
    assert rig.live.stats.fix_rate == 0


@pytest.mark.parametrize(
    ("tool", "before", "after", "ok"),
    [
        ("robot.forward", p(50, 35), p(68, 35), True),
        ("robot.forward", p(50, 35), p(52, 35), False),  # barely moved
        ("robot.forward", p(50, 35), p(40, 35), False),  # went backward
        ("robot.forward", p(50, 35, 90), p(50, 53, 90), True),  # heading +y
        ("robot.reverse", p(50, 35), p(40, 33, 30), True),
        ("robot.reverse", p(50, 35), p(50, 35), False),
        ("robot.reverse", p(50, 35), p(60, 35), False),  # went forward
        ("robot.forward", None, p(60, 35), False),
    ],
)
def test_judge(tool, before, after, ok):
    assert judge(tool, before, after).success is ok


def test_reverse_turn_is_left_and_positive():
    v = judge("robot.reverse", p(50, 35, 0), p(40, 34, 35))
    assert v.turn_deg == pytest.approx(35) and v.along_cm < 0


def test_gate_denies_motion_without_a_fix(tmp_path):
    rig = make_rig(sim=True)
    rig.camera.visible = False
    runner = Runner(rig.registry, EventLog(tmp_path / "r.jsonl", "exp001-t-nofix"))
    runner.start("exp001-vision-observer")
    result = runner.request("robot.forward", {"seconds": 1}, actor="cli")
    assert not result.allowed
    assert result.checked.payload.rule == "interlock"
    assert rig.robot.x_cm == 50  # never moved


def test_fence_stops_a_drive_toward_the_edge(tmp_path):
    rig = make_rig(sim=True)
    rig.robot.x_cm = 80  # 20 cm from the +x edge, facing it
    rig.live.refresh()
    runner = Runner(rig.registry, EventLog(tmp_path / "r.jsonl", "exp001-t-fence"))
    runner.start("exp001-vision-observer")
    result = runner.request("robot.forward", {"seconds": 1}, actor="cli")
    assert not result.allowed and "arena_fence" in result.checked.payload.reason


def trials(tmp_path, tool, n, *, dry_run=False, start_x=50.0):
    rig = make_rig(sim=True)
    rig.robot.x_cm = start_x
    run_id = f"exp001-t-{tool.split('.')[1]}{'-null' if dry_run else ''}"
    log = EventLog(tmp_path / f"{run_id}.jsonl", run_id)
    out = run_trials(rig, Runner(rig.registry, log, dry_run=dry_run), tool, n, 1.0, interval=0)
    return rig, log.path, out


def test_simulated_trials_log_valid_camera_observations(tmp_path):
    rig, path, out = trials(tmp_path, "robot.forward", 2, start_x=15)
    assert out == {"status": "completed", "trials": 2}
    assert validate_log(path.read_text().splitlines()) == []
    obs = [e for e in read_log(path) if e.type == "outcome.observed"]
    assert len(obs) == 2
    assert all(e.payload.method == "camera" and e.payload.success for e in obs)
    assert all(e.payload.along_cm > 10 for e in obs)  # extra payload keys are recorded


def test_null_test_scores_zero(tmp_path):
    rig, path, _ = trials(tmp_path, "robot.reverse", 3, dry_run=True)
    r = report([path])
    assert r["null_test_runs"] == 1 and r["camera_success_rate"] == 0
    assert (rig.robot.x_cm, rig.robot.y_cm) == (50, 35)


def test_trials_stop_at_the_fence(tmp_path):
    rig, path, out = trials(tmp_path, "robot.forward", 10)
    assert out["status"] == "aborted" and 0 < out["trials"] < 10
    assert rig.robot.x_cm < 100 - 10  # never crossed into the margin


def test_report_pairs_camera_and_human(tmp_path, monkeypatch):
    answers = iter(["y", "n"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    rig = make_rig(sim=True)
    log = EventLog(tmp_path / "h.jsonl", "exp001-t-human")
    run_trials(rig, Runner(rig.registry, log), "robot.reverse", 2, 0.5, interval=0, ask_human=True)
    r = report([log.path])
    assert r["human_labelled"] == 2 and r["agreement"] == 0.5 and r["camera_yes_human_no"] == 1


def test_snapshot_refuses_without_the_privacy_flag():
    with pytest.raises(SystemExit, match="ADR 0007"):
        main(["--sim", "snapshot"])


def test_crop_zoom_keeps_the_centre():
    import numpy as np
    from exp001_vision_observer.camera import crop_zoom

    f = np.zeros((1080, 1920, 3), np.uint8)
    f[540, 960] = 255
    z = crop_zoom(f, 1.5)
    assert z.shape[:2] == (720, 1280) and z[360, 640].any()


def _busy_floor(img):
    """A floor patch in the front-marker colour, and a glare spot, under the robot."""
    import cv2

    cv2.rectangle(img, (120, 80), (300, 400), (40, 255, 60), -1)
    cv2.circle(img, (450, 120), 30, (255, 255, 255), -1)


def _bg_tracker(rig, empty):
    from exp001_vision_observer.config import Background
    from exp001_vision_observer.tracker import BackgroundTracker

    small = Background(min_robot_px=300, max_robot_px=20_000, min_front_px=20)
    arena = rig.arena.model_copy(update={"tracking": "background", "background": small})
    return BackgroundTracker(arena, empty)


def test_background_tracker_ignores_a_same_coloured_floor_and_glare():
    rig = make_rig(sim=True)
    rig.camera.floor = _busy_floor
    rig.camera.visible = False
    tr = _bg_tracker(rig, rig.camera.read())
    rig.camera.visible = True
    for x, y, h in [(50, 35, 0), (25, 30, 120), (35, 45, -60)]:  # incl. over the patch
        rig.robot.x_cm, rig.robot.y_cm, rig.robot.heading_deg = x, y, h
        fix = tr.find(rig.camera.read())
        assert fix is not None
        assert math.hypot(fix.x_cm - x, fix.y_cm - y) < 3.0
        assert abs((fix.heading_deg - h + 180) % 360 - 180) < 15


def test_background_tracker_rejects_an_empty_arena_and_a_big_intruder():
    import cv2

    rig = make_rig(sim=True)
    rig.camera.visible = False
    empty = rig.camera.read()
    tr = _bg_tracker(rig, empty)
    assert tr.find(empty) is None  # nothing there
    rig.camera.visible = True
    f = rig.camera.read()
    cv2.rectangle(f, (90, 60), (560, 420), (30, 60, 200), -1)  # a person or a hand
    assert tr.find(f) is None
