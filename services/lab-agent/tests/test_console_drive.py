import pytest
from lab_agent.console.drive import DriveSession
from lab_agent.log import read_log


@pytest.fixture
def rig(drive_rig):
    r = drive_rig()
    return DriveSession(r.runner, r.lease, clock=r.clock), r.wheels, r.clock, r.runner


@pytest.fixture
def rig5(drive_rig):
    r = drive_rig()
    return DriveSession(r.runner, r.lease, clock=r.clock), r


def sent(runner, tool):
    return [e for e in read_log(runner.log.path) if e.type == "command.sent" and e.tool == tool]


def test_first_drive_goes_through_and_renews_the_lease(rig):
    s, wheels, _, _ = rig
    r = s.drive(0.1, 0.0)
    assert r is not None and r.ok and s.moving
    assert wheels.speeds[0] == pytest.approx(0.1)


def test_small_or_fast_changes_are_not_resent(rig):
    s, _, clock, runner = rig
    s.drive(0.10, 0.0)
    clock.t += 0.05
    assert s.drive(0.20, 0.0) is None  # under 100 ms since the last send
    clock.t += 0.1
    assert s.drive(0.205, 0.0) is not None  # 100 ms passed, big change from 0.10
    clock.t += 0.1
    assert s.drive(0.21, 0.0) is None  # change too small to send
    assert len(sent(runner, "base.drive")) == 2


def test_heartbeat_keeps_the_lease_alive(rig):
    s, _, clock, _ = rig
    s.drive(0.1, 0.0)
    for _ in range(10):
        clock.t += 0.1
        s.heartbeat()
        assert s.tick() is None
    assert s.moving


def test_watchdog_stops_the_wheels_when_the_lease_lapses(rig):
    s, wheels, clock, runner = rig
    s.drive(0.1, 0.0)
    clock.t += 0.31
    r = s.tick()
    assert r is not None and r.ok
    assert wheels.speeds == (0.0, 0.0) and not s.moving
    assert s.tick() is None  # only once
    assert len(sent(runner, "base.stop")) == 1
    requested = [
        e
        for e in read_log(runner.log.path)
        if e.type == "command.requested" and e.tool == "base.stop"
    ]
    assert len(requested) == 1 and requested[0].actor == "system"


def test_stop_cancels_the_lease_and_stops(rig):
    s, wheels, _, _ = rig
    s.drive(0.1, 0.0)
    r = s.stop()
    assert r is not None and r.ok and wheels.speeds == (0.0, 0.0) and not s.lease.alive()


def test_a_flood_of_stops_is_collapsed(rig):
    s, _, clock, runner = rig
    s.drive(0.1, 0.0)
    assert s.stop() is not None
    assert s.stop() is None  # already stopped, within 100 ms
    clock.t += 0.2
    assert s.stop() is not None  # later stops still go through
    assert len(sent(runner, "base.stop")) == 2


def test_a_refused_drive_is_returned_not_raised(rig, tmp_path):
    s, wheels, _, _ = rig
    (tmp_path / "STOP").touch()
    r = s.drive(0.1, 0.0)
    assert r is not None and not r.allowed and r.checked.payload.rule == "stop_file"
    assert wheels.history == [] and not s.moving


def test_a_change_dropped_by_the_time_dedupe_is_sent_later_by_tick(rig5):
    s, r = rig5
    s.drive(0.3, 0.0)
    r.clock.t += 0.05
    assert s.drive(0.1, 0.0) is None
    assert s.tick() is None  # still within 100 ms
    r.clock.t += 0.08
    res = s.tick()
    assert res is not None and res.ok
    assert r.wheels.speeds[0] == pytest.approx(0.1)
    assert s.tick() is None  # sent once


def test_a_move_to_zero_is_never_deduped(rig5):
    s, r = rig5
    s.drive(0.03, 0.0)
    r.clock.t += 0.2
    assert s.drive(0.0, 0.0) is not None
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving
    s.drive(0.3, 0.0)
    r.clock.t += 0.01
    assert s.drive(0.0, 0.0) is not None
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_a_zero_drive_while_stopped_does_nothing(rig5):
    s, r = rig5
    assert s.drive(0.0, 0.0) is None
    assert r.wheels.history == []


def test_a_refused_drive_while_moving_stops_the_wheels(rig5, tmp_path):
    s, r = rig5
    s.drive(0.3, 0.0)
    r.clock.t += 0.2
    (tmp_path / "STOP").touch()
    res = s.drive(0.1, 0.0)
    assert res is not None and not res.ok
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_an_invalid_drive_while_moving_stops_the_wheels(rig5):
    s, r = rig5
    s.drive(0.2, 0.0)
    r.clock.t += 0.2
    res = s.drive(0.5, 0.0)  # over the cap
    assert res is not None and not res.ok
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_the_stop_file_stops_the_wheels_on_tick(rig5, tmp_path):
    s, r = rig5
    s.drive(0.3, 0.0)
    (tmp_path / "STOP").touch()
    r.clock.t += 0.1
    s.heartbeat()
    res = s.tick()
    assert res is not None and res.ok
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_a_failed_stop_is_retried_by_tick(rig5):
    s, r = rig5
    s.drive(0.2, 0.0)
    r.stop_fails[0] = 1
    r.clock.t += 0.31
    res = s.tick()
    assert res is not None and not res.ok and s.moving
    assert r.wheels.speeds[0] == pytest.approx(0.2)
    assert s.tick() is None  # not more than once per min_interval_s
    r.clock.t += 0.11
    res = s.tick()
    assert res is not None and res.ok
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_a_stop_right_after_a_failed_stop_is_not_collapsed(rig5):
    s, r = rig5
    s.drive(0.2, 0.0)
    r.stop_fails[0] = 1
    res = s.stop()
    assert res is not None and not res.ok and s.moving
    res = s.stop()
    assert res is not None and res.ok and r.wheels.speeds == (0.0, 0.0)


def test_a_stop_after_a_drive_that_followed_a_stop_is_not_collapsed(rig5):
    s, r = rig5
    s.drive(0.1, 0.0)
    assert s.stop() is not None
    r.clock.t += 0.05
    assert s.drive(0.2, 0.0) is not None
    r.clock.t += 0.01
    res = s.stop()
    assert res is not None and res.ok and r.wheels.speeds == (0.0, 0.0)


def test_a_stop_that_failed_inside_drive_is_retried_while_heartbeats_continue(rig5):
    s, r = rig5
    s.drive(0.2, 0.0)
    r.stop_fails[0] = 1
    res = s.drive(0.0, 0.0)
    assert res is not None and not res.ok and s.moving
    r.clock.t += 0.11
    s.heartbeat()
    res = s.tick()
    assert res is not None and res.ok
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_a_stop_that_failed_after_a_refused_drive_is_retried(rig5):
    s, r = rig5
    s.drive(0.2, 0.0)
    r.stop_fails[0] = 1
    r.clock.t += 0.2
    res = s.drive(0.5, 0.0)  # over the cap, refused, and the stop that follows fails
    assert res is not None and not res.ok and s.moving
    r.clock.t += 0.11
    s.heartbeat()
    res = s.tick()
    assert res is not None and res.ok
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving


def test_a_finger_resting_near_the_centre_stops_instead_of_creeping(rig5):
    s, r = rig5
    s.drive(0.03, 0.0)
    r.clock.t += 0.2
    s.drive(0.012, 0.0)
    assert r.wheels.speeds == (0.0, 0.0) and not s.moving
