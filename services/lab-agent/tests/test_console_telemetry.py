from lab_agent.console.protocol import State
from lab_agent.console.telemetry import FakeTelemetry


def test_fake_telemetry_fills_a_valid_state():
    reading = FakeTelemetry(clock=lambda: 12.0).read()
    state = State(
        type="state",
        t=0.0,
        lease_alive=False,
        moving=False,
        stop_file=False,
        **reading,
    )
    assert state.fake is True
    assert 12.0 < state.battery.volts < 13.6
    assert len(state.servos) == 2 and len(state.cliff_mm) == 3


def test_fake_battery_drifts_but_stays_in_range():
    volts = set()
    for t in range(0, 600, 37):
        reading = FakeTelemetry(clock=lambda t=t: float(t)).read()
        volts.add(round(reading["battery"]["volts"], 3))
    assert len(volts) > 1
    assert all(12.0 < v < 13.6 for v in volts)
