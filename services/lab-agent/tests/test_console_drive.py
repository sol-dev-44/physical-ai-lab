import pytest
from lab_agent.console.drive import DriveSession
from lab_agent.log import read_log


@pytest.fixture
def rig(drive_rig):
    r = drive_rig()
    return DriveSession(r.runner, r.lease, clock=r.clock), r.wheels, r.clock, r.runner


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
    stop = sent(runner, "base.stop")
    assert len(stop) == 1 and stop[0].actor == "system"


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
