from lab_agent.interlocks import LeaseRequired
from lab_agent.lease import DriveLease
from lab_agent.registry import Tool


class Clock:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


def test_lease_lives_for_its_ttl_after_each_renewal():
    c = Clock()
    lease = DriveLease(ttl_s=0.3, clock=c)
    assert not lease.alive()
    lease.renew()
    c.t += 0.29
    assert lease.alive()
    c.t += 0.02
    assert not lease.alive()
    lease.renew()
    assert lease.alive()


def test_cancel_ends_the_lease_at_once():
    lease = DriveLease(ttl_s=0.3, clock=Clock())
    lease.renew()
    lease.cancel()
    assert not lease.alive()


def test_interlock_refuses_guarded_tools_without_a_live_lease():
    c = Clock()
    lease = DriveLease(ttl_s=0.3, clock=c)
    rule = LeaseRequired(lease, frozenset({"base.drive"}))
    drive = Tool("base.drive", "drive", lambda _a: None)
    other = Tool("base.stop", "stop", lambda _a: None)
    assert "hold the drive button" in (rule.check(drive, None) or "")
    assert rule.check(other, None) is None
    lease.renew()
    assert rule.check(drive, None) is None
    c.t += 1.0
    assert rule.check(drive, None) is not None
