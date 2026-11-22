import pytest
from lab_agent.devices.fake import FakeWheels


def test_fake_wheels_record_speeds():
    w = FakeWheels()
    w.set_speeds(0.1, 0.2)
    assert w.speeds == (0.1, 0.2) and w.history == [(0.1, 0.2)]


def test_fake_wheels_reject_a_real_looking_id():
    with pytest.raises(ValueError):
        FakeWheels(id="wheels")
